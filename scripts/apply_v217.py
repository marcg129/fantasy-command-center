from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
index_path = ROOT / 'index.html'
changelog_path = ROOT / 'CHANGELOG.md'
projection_path = ROOT / 'scripts' / 'update_projections.py'
projection_workflow_path = ROOT / '.github' / 'workflows' / 'update-projections.yml'
calibration_path = ROOT / 'scripts' / 'update_calibration.py'
calibration_workflow_path = ROOT / '.github' / 'workflows' / 'update-calibration.yml'

# 1) Preserve a stable pregame projection snapshot for later error calibration.
p = projection_path.read_text(encoding='utf-8')
if 'HISTORY_DIR = ROOT / "data" / "projection-history"' not in p:
    p = p.replace('from pathlib import Path\n', 'from pathlib import Path\nfrom zoneinfo import ZoneInfo\n', 1)
    p = p.replace('OUT = ROOT / "data" / "projections.json"\n', 'OUT = ROOT / "data" / "projections.json"\nHISTORY_DIR = ROOT / "data" / "projection-history"\n', 1)
    marker = '\ndef main() -> int:\n'
    helper = r'''

def write_calibration_history(output: dict, now: datetime) -> Path | None:
    """Keep one stable pregame snapshot per NFL week for projection-error calibration.

    The archive refreshes through Thursday 6:00 PM America/New_York, then freezes.
    That gives the model a late-week pregame baseline without saving every 2-hour pull.
    If a weekly archive does not exist yet, create one even after the cutoff rather than
    losing the week entirely.
    """
    season = int(output.get("season") or 0)
    week = int(output.get("week") or 0)
    if season <= 0 or week < 1 or week > 18:
        return None

    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    path = HISTORY_DIR / f"{season}-W{week:02d}.json"
    local = now.astimezone(ZoneInfo("America/New_York"))
    cutoff = local.replace(hour=18, minute=0, second=0, microsecond=0)
    refresh_allowed = local.weekday() < 3 or (local.weekday() == 3 and local < cutoff)

    if path.exists() and not refresh_allowed:
        print(f"Calibration archive already frozen: {path}")
        return None

    archived = dict(output)
    archived["calibration_snapshot"] = True
    archived["snapshot_policy"] = "latest refresh through Thursday 18:00 America/New_York"
    archived["snapshot_local_time"] = local.isoformat()
    path.write_text(json.dumps(archived, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote calibration projection archive: {path}")
    return path
'''
    if marker not in p:
        raise SystemExit('Could not find update_projections main marker')
    p = p.replace(marker, helper + marker, 1)
    old = '    OUT.write_text(json.dumps(output, indent=2, sort_keys=True) + "\\n", encoding="utf-8")\n    print(f"Wrote {len(players)} projected players for {season} Week {week} to {OUT}")\n'
    new = '    OUT.write_text(json.dumps(output, indent=2, sort_keys=True) + "\\n", encoding="utf-8")\n    write_calibration_history(output, now)\n    print(f"Wrote {len(players)} projected players for {season} Week {week} to {OUT}")\n'
    if old not in p:
        raise SystemExit('Could not find projection output write block')
    p = p.replace(old, new, 1)
    projection_path.write_text(p, encoding='utf-8')

# 2) Ensure the projection workflow commits the weekly history archive too.
w = projection_workflow_path.read_text(encoding='utf-8')
w = w.replace('if git diff --quiet -- data/projections.json; then', 'if git diff --quiet -- data/projections.json data/projection-history; then')
w = w.replace('git add data/projections.json\n', 'git add data/projections.json data/projection-history\n')
projection_workflow_path.write_text(w, encoding='utf-8')

# 3) Build empirical projection-error calibration from frozen Sleeper projections vs realized Sleeper stats.
calibration_path.write_text(r'''#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import statistics
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HISTORY_DIR = ROOT / "data" / "projection-history"
OUT = ROOT / "data" / "calibration.json"
UA = "FantasyCommandCenter-CalibrationBot/1.0 (+GitHub Actions)"
STATE_URL = "https://api.sleeper.app/v1/state/nfl"
PLAYERS_URL = "https://api.sleeper.app/v1/players/nfl"
LEGACY_STATS = "https://api.sleeper.app/v1/stats/nfl/regular/{season}/{week}"
CURRENT_STATS = "https://api.sleeper.com/stats/nfl/{season}/{week}?season_type=regular"
POSITIONS = ("QB", "RB", "WR", "TE", "K", "DEF")
DEFAULT_CV = {"QB": 0.32, "RB": 0.50, "WR": 0.55, "TE": 0.55, "K": 0.45, "DEF": 0.55}
MIN_WEEKS = 2
MIN_SAMPLES = 50
MIN_PROJECTED_PPR = 3.0


def get_json(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def finite(value):
    try:
        x = float(value)
        return x if math.isfinite(x) else None
    except (TypeError, ValueError):
        return None


def normalize_stats(payload) -> dict[str, dict]:
    out = {}
    if isinstance(payload, dict):
        for raw_id, raw in payload.items():
            row = raw if isinstance(raw, dict) else {}
            nested = row.get("stats") if isinstance(row.get("stats"), dict) else row
            out[str(row.get("player_id") or raw_id)] = nested
    elif isinstance(payload, list):
        for raw in payload:
            if not isinstance(raw, dict):
                continue
            player = raw.get("player") if isinstance(raw.get("player"), dict) else {}
            pid = raw.get("player_id") or player.get("player_id") or player.get("id")
            if not pid:
                continue
            out[str(pid)] = raw.get("stats") if isinstance(raw.get("stats"), dict) else raw
    return out


def fetch_week_stats(season: int, week: int) -> dict[str, dict]:
    errors = []
    for template in (LEGACY_STATS, CURRENT_STATS):
        url = template.format(season=season, week=week)
        try:
            rows = normalize_stats(get_json(url))
            if rows:
                return rows
            errors.append(f"{url}: no rows")
        except Exception as exc:
            errors.append(f"{url}: {type(exc).__name__}: {exc}")
    raise RuntimeError("; ".join(errors))


def player_position_map() -> dict[str, str]:
    payload = get_json(PLAYERS_URL)
    if not isinstance(payload, dict):
        return {}
    out = {}
    for pid, row in payload.items():
        if not isinstance(row, dict):
            continue
        pos = str(row.get("position") or "").upper()
        if pos == "DST":
            pos = "DEF"
        if pos in POSITIONS:
            out[str(pid)] = pos
    return out


def archive_files(season: int) -> list[Path]:
    if not HISTORY_DIR.exists():
        return []
    return sorted(HISTORY_DIR.glob(f"{season}-W*.json"))


def week_from_archive(path: Path) -> int | None:
    try:
        return int(path.stem.split("-W", 1)[1])
    except Exception:
        return None


def profile(samples: list[tuple[float, float]], default_cv: float, completed_week_count: int) -> dict:
    n = len(samples)
    projected = [x[0] for x in samples]
    errors = [x[1] - x[0] for x in samples]
    mean_proj = statistics.fmean(projected) if projected else 0.0
    bias = statistics.fmean(errors) if errors else 0.0
    mae = statistics.fmean(abs(e) for e in errors) if errors else 0.0
    rmse = math.sqrt(statistics.fmean(e * e for e in errors)) if errors else 0.0
    error_sd = statistics.pstdev(errors) if len(errors) > 1 else 0.0
    raw_cv = max(0.18, min(0.95, error_sd / mean_proj)) if mean_proj > 0 and error_sd > 0 else default_cv

    ready = completed_week_count >= MIN_WEEKS and n >= MIN_SAMPLES
    weight = min(0.75, n / (n + 150.0)) if ready else 0.0
    used = default_cv * (1.0 - weight) + raw_cv * weight
    return {
        "n": n,
        "mean_projection_ppr": round(mean_proj, 4),
        "bias_ppr": round(bias, 4),
        "mae_ppr": round(mae, 4),
        "rmse_ppr": round(rmse, 4),
        "error_sd_ppr": round(error_sd, 4),
        "empirical_cv": round(raw_cv, 4),
        "baseline_cv": default_cv,
        "blend_weight": round(weight, 4),
        "cv_used": round(used, 4),
        "mode": "empirical_blend" if ready else "heuristic_collecting",
    }


def main() -> int:
    state = get_json(STATE_URL)
    season = int(state.get("season") or datetime.now(timezone.utc).year)
    current_week = int(state.get("week") or state.get("display_week") or 1)
    season_type = str(state.get("season_type") or "regular").lower()

    files = archive_files(season)
    completed = []
    for path in files:
        week = week_from_archive(path)
        if not week:
            continue
        if season_type == "complete" or week < current_week:
            completed.append((week, path))

    samples = {pos: [] for pos in POSITIONS}
    week_counts = {}
    if completed:
        positions = player_position_map()
        for week, path in completed:
            snapshot = json.loads(path.read_text(encoding="utf-8"))
            actual = fetch_week_stats(season, week)
            used = 0
            for pid, row in (snapshot.get("players") or {}).items():
                pos = positions.get(str(pid))
                if pos not in samples:
                    continue
                proj_stats = row.get("stats") if isinstance(row, dict) else None
                if not isinstance(proj_stats, dict):
                    continue
                projected = finite(proj_stats.get("pts_ppr"))
                actual_row = actual.get(str(pid)) or {}
                realized = finite(actual_row.get("pts_ppr"))
                if projected is None or realized is None or projected < MIN_PROJECTED_PPR:
                    continue
                samples[pos].append((projected, realized))
                used += 1
            week_counts[str(week)] = used

    positions_out = {
        pos: profile(samples[pos], DEFAULT_CV[pos], len(completed))
        for pos in POSITIONS
    }
    sample_count = sum(x["n"] for x in positions_out.values())
    body = {
        "season": season,
        "current_week": current_week,
        "source": "Frozen Sleeper weekly projections vs realized Sleeper weekly stats (PPR error scale)",
        "snapshot_policy": "latest refresh through Thursday 18:00 America/New_York",
        "minimum_completed_weeks": MIN_WEEKS,
        "minimum_position_samples": MIN_SAMPLES,
        "completed_weeks": [w for w, _ in completed],
        "week_sample_counts": week_counts,
        "sample_count": sample_count,
        "positions": positions_out,
    }

    previous = None
    if OUT.exists():
        try:
            previous = json.loads(OUT.read_text(encoding="utf-8"))
        except Exception:
            previous = None
    comparable = dict(previous or {})
    comparable.pop("generated_at", None)
    if comparable == body:
        print("Calibration data unchanged.")
        return 0

    body["generated_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(body, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote calibration data: {len(completed)} completed weeks, {sample_count} samples")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
''', encoding='utf-8')

# 4) Recompute calibration after each successful projection refresh. This serializes the two writers.
calibration_workflow_path.write_text(r'''name: Update fantasy simulation calibration

on:
  workflow_run:
    workflows: ["Update fantasy projection data"]
    types: [completed]
  workflow_dispatch:

permissions:
  contents: write

concurrency:
  group: fantasy-simulation-calibration
  cancel-in-progress: true

jobs:
  update-calibration:
    if: ${{ github.event_name == 'workflow_dispatch' || github.event.workflow_run.conclusion == 'success' }}
    runs-on: ubuntu-latest
    steps:
      - name: Check out repository
        uses: actions/checkout@v4
        with:
          ref: main
          fetch-depth: 0
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Build calibration JSON
        run: python scripts/update_calibration.py
      - name: Commit changed calibration data
        run: |
          if git diff --quiet -- data/calibration.json; then
            echo "No calibration-data changes to commit."
            exit 0
          fi
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add data/calibration.json
          git commit -m "Refresh simulation calibration"
          git pull --rebase origin main
          git push
''', encoding='utf-8')

# 5) Add calibration loading and use the empirical blend only once the data says it is ready.
html = index_path.read_text(encoding='utf-8')
html = html.replace('Multi-manager beta • week-aware management • v2.16.4', 'Multi-manager beta • week-aware management • v2.17', 1)
html = html.replace('Weekly lineup, matchup, waiver, and roster-management command center. v2.16.4 adds keyboard-friendly Sleeper connection while preserving current-week resolution, lineup consensus, simulation, and reliable usage.',
                    'Weekly lineup, matchup, waiver, and roster-management command center. v2.17 adds projection-error calibration infrastructure while preserving current-week resolution, lineup consensus, median strategy, and reliable usage.', 1)
html = html.replace('Pregame Monte Carlo cross-check using league-scored player projections plus conservative position-level variance assumptions. Probabilities are estimates, not guarantees, and are withheld once live scoring begins.',
                    'Pregame Monte Carlo cross-check using league-scored player projections plus calibration-aware position-level variance. Probabilities are estimates, not guarantees, and are withheld once live scoring begins.', 1)

state_old = "projectionFeed:null,projectionByPlayer:new Map(),projectionError:null,tradeStyle:'balanced'"
state_new = "projectionFeed:null,projectionByPlayer:new Map(),projectionError:null,calibrationFeed:null,calibrationError:null,tradeStyle:'balanced'"
if state_old not in html:
    raise SystemExit('Could not find state projection fields')
html = html.replace(state_old, state_new, 1)

projection_row_marker = "  function projectionRowForId(id) {\n"
calibration_js = r'''  function calibrationFileUrl() {
    return `./data/calibration.json?ts=${Date.now()}`;
  }

  async function loadProjectionCalibration() {
    state.calibrationError=null;
    state.calibrationFeed=null;
    try {
      const data=await jget(calibrationFileUrl());
      const seasonOk=String(data?.season||'')===String(state.league?.season||state.nflState?.season||'');
      if(seasonOk) state.calibrationFeed=data;
      return seasonOk;
    } catch(e) {
      state.calibrationError=e;
      return false;
    }
  }

  function simulationCalibrationSummary() {
    const defaults={QB:0.32,RB:0.50,WR:0.55,TE:0.55,K:0.45,DEF:0.55};
    const feed=state.calibrationFeed;
    const weeks=Array.isArray(feed?.completed_weeks)?feed.completed_weeks:[];
    const profiles=feed?.positions||{};
    const ready=Object.entries(profiles).filter(([,p])=>p?.mode==='empirical_blend');
    const cvText=Object.keys(defaults).map(pos=>{
      const v=Number(profiles?.[pos]?.cv_used);
      const cv=Number.isFinite(v)&&v>0?v:defaults[pos];
      return `${pos} ${Math.round(cv*100)}%`;
    }).join(', ');
    if(!feed) return {
      label:'HEURISTIC VARIANCE v1',
      note:`Calibration file is not available yet; conservative baseline CVs remain active (${cvText}).`
    };
    if(!ready.length) return {
      label:`CALIBRATION COLLECTING • ${weeks.length}W`,
      note:`Projection-error calibration is collecting frozen pregame snapshots. ${weeks.length}/${Number(feed.minimum_completed_weeks)||2} completed weeks are available; conservative baseline CVs remain active (${cvText}).`
    };
    return {
      label:`CALIBRATION BLEND • ${weeks.length}W`,
      note:`Empirical projection-error variance is active for ${ready.length} position groups using ${Number(feed.sample_count)||0} samples across ${weeks.length} completed weeks. Current CVs: ${cvText}. Estimates are shrunk toward the conservative baseline to reduce early-season overfitting.`
    };
  }

'''
if calibration_js.strip() not in html:
    if projection_row_marker not in html:
        raise SystemExit('Could not find projectionRowForId marker')
    html = html.replace(projection_row_marker, calibration_js + projection_row_marker, 1)

old_variance = r'''  function simulationVarianceProfile(pos,mean) {
    const key=String(pos||'').toUpperCase();
    const cv={QB:0.32,RB:0.50,WR:0.55,TE:0.55,K:0.45,DEF:0.55}[key] ?? 0.52;
    const floor={QB:4.5,RB:3.5,WR:3.5,TE:3.0,K:2.5,DEF:3.5}[key] ?? 3.5;
    const lower={QB:-8,RB:-1,WR:-1,TE:-1,K:-2,DEF:-8}[key] ?? -1;
    return {cv,sd:Math.max(floor,Math.abs(Number(mean)||0)*cv),lower};
  }
'''
new_variance = r'''  function simulationVarianceProfile(pos,mean) {
    const key=String(pos||'').toUpperCase();
    const baseline={QB:0.32,RB:0.50,WR:0.55,TE:0.55,K:0.45,DEF:0.55}[key] ?? 0.52;
    const calibrated=Number(state.calibrationFeed?.positions?.[key]?.cv_used);
    const cv=Number.isFinite(calibrated)&&calibrated>0?calibrated:baseline;
    const floor={QB:4.5,RB:3.5,WR:3.5,TE:3.0,K:2.5,DEF:3.5}[key] ?? 3.5;
    const lower={QB:-8,RB:-1,WR:-1,TE:-1,K:-2,DEF:-8}[key] ?? -1;
    return {cv,sd:Math.max(floor,Math.abs(Number(mean)||0)*cv),lower};
  }
'''
if old_variance not in html:
    raise SystemExit('Could not find simulationVarianceProfile block')
html = html.replace(old_variance, new_variance, 1)

promise_old = '''        loadWeeklyUsageContext(week,ctx),\n        loadNewsIntelligence(),\n        loadProjectionIntelligence()\n'''
promise_new = '''        loadWeeklyUsageContext(week,ctx),\n        loadNewsIntelligence(),\n        loadProjectionIntelligence(),\n        loadProjectionCalibration()\n'''
if promise_old not in html:
    raise SystemExit('Could not find weekly Promise.all projection block')
html = html.replace(promise_old, promise_new, 1)

iter_old = '    const ITER=6000;\n    let h2hWins=0,medianWins=0,doubleWins=0,zeroWins=0;'
iter_new = '    const ITER=6000;\n    const calibration=simulationCalibrationSummary();\n    let h2hWins=0,medianWins=0,doubleWins=0,zeroWins=0;'
if iter_old not in html:
    raise SystemExit('Could not find simulation iteration marker')
html = html.replace(iter_old, iter_new, 1)
html = html.replace('<span class="simulation-model-chip">HEURISTIC VARIANCE v1</span>', '<span class="simulation-model-chip">${esc(calibration.label)}</span>', 1)
old_note = '<div class="whyline" style="margin-top:6px"><b>Calibration note:</b> probabilities use position-level variance assumptions (QB 32%, RB 50%, WR/TE/DEF 55%, K 45% coefficient of variation with minimum variance floors). They are not yet calibrated from this season\'s projection errors, so treat small probability differences as noise rather than actionable edges.${medianReady&&adequateTeams.length<teams.length?` League-median simulation uses the ${adequateTeams.length} teams meeting the strict projection-coverage threshold, so that percentage is lower confidence.`:\'\'}</div>'
new_note = '<div class="whyline" style="margin-top:6px"><b>Calibration note:</b> ${esc(calibration.note)} Treat small probability differences as noise rather than actionable edges.${medianReady&&adequateTeams.length<teams.length?` League-median simulation uses the ${adequateTeams.length} teams meeting the strict projection-coverage threshold, so that percentage is lower confidence.`:\'\'}</div>'
if old_note not in html:
    raise SystemExit('Could not find simulation calibration note')
html = html.replace(old_note, new_note, 1)

html = html.replace('v2.15.2 adds a pregame Monte Carlo probability cross-check, but its position-level variance assumptions are still heuristic rather than calibrated from historical projection errors;',
                    'v2.17 starts preserving one frozen pregame projection snapshot per week and compares completed weeks with realized Sleeper stats; simulation variance remains conservatively heuristic until at least two completed weeks and enough position-level samples are available, then blends empirical error into the baseline;', 1)
html = html.replace('  v2.16.3 keeps the Aug. 29/30 half-PPR expert-consensus snapshot isolated to Draft Day and immediate post-draft analysis.',
                    '  v2.17 keeps the Aug. 29/30 half-PPR expert-consensus snapshot isolated to Draft Day and immediate post-draft analysis and begins conservative projection-error calibration for the pregame simulation.', 1)
index_path.write_text(html, encoding='utf-8')

# 6) Changelog.
changelog = changelog_path.read_text(encoding='utf-8')
entry = '''## v2.17 — Simulation Calibration Foundation
**2026-09-16**

- Begin collecting one stable pregame Sleeper projection snapshot per NFL week for empirical simulation calibration instead of permanently relying on fixed variance assumptions.
- Refresh the weekly calibration snapshot through Thursday 6:00 PM Eastern, then freeze it so later projection changes cannot rewrite the baseline being evaluated.
- Add an automated calibration job that compares completed frozen projections with realized Sleeper weekly PPR results using matching Sleeper player IDs.
- Estimate projection-error dispersion by QB, RB, WR, TE, K, and DEF, while requiring at least two completed archived weeks and 50 samples at a position before empirical variance can influence simulations.
- Shrink empirical variance estimates toward the conservative v1 baseline rather than switching abruptly to noisy early-season estimates.
- Load `data/calibration.json` into Weekly Simulation and show whether variance is still `CALIBRATION COLLECTING` or has advanced to an empirical blend.
- Keep the existing minimum variance floors, 12% same-team shared factor, projection-coverage requirements, pregame-only guardrail, lineup consensus, median strategy, waivers, trades, news, weather, and usage behavior.
- Calibration collection starts with the current Week 2 projection cycle; do not fabricate a Week 1 archive after the fact because it would not represent the projection information that existed before Week 1 games.

'''
if '## v2.17 — Simulation Calibration Foundation' not in changelog:
    marker = '## v2.16.4 — Enter-to-Connect Shortcut\n'
    if marker not in changelog:
        raise SystemExit('Could not find v2.16.4 changelog marker')
    changelog = changelog.replace(marker, entry + marker, 1)
    changelog_path.write_text(changelog, encoding='utf-8')

print('Applied v2.17 simulation calibration foundation.')
