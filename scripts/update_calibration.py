#!/usr/bin/env python3
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
