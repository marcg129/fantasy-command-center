#!/usr/bin/env python3
from __future__ import annotations

import csv
import io
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "usage.json"
STATE_URL = "https://api.sleeper.app/v1/state/nfl"
UA = "FantasyCommandCenter-UsageBot/1.0 (+GitHub Actions)"

STAT_FIELDS = [
    "season", "season_type", "week", "player_id", "player_name", "player_display_name",
    "position", "team", "carries", "targets", "receptions", "attempts",
    "rushing_yards", "receiving_yards", "passing_yards", "fantasy_points_ppr", "target_share",
]
SNAP_FIELDS = ["season", "week", "player", "pfr_player_id", "offense_pct"]


def get_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/csv,*/*"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8")


def get_json(url: str) -> dict:
    return json.loads(get_text(url))


def read_csv(url: str) -> list[dict]:
    return list(csv.DictReader(io.StringIO(get_text(url))))


def slim(rows: list[dict], fields: list[str]) -> list[dict]:
    out = []
    for row in rows:
        item = {k: row.get(k, "") for k in fields if k in row}
        if item:
            out.append(item)
    return out


def regular_week(row: dict) -> int | None:
    st = str(row.get("season_type") or row.get("game_type") or "REG").upper()
    if st not in {"REG", "REGULAR"}:
        return None
    try:
        return int(float(row.get("week") or 0))
    except Exception:
        return None


def main() -> int:
    state = get_json(STATE_URL)
    season = int(state.get("season") or datetime.now(timezone.utc).year)
    week = int(state.get("week") or state.get("display_week") or 1)
    prior = season - 1

    def stats_url(y: int) -> str:
        return f"https://github.com/nflverse/nflverse-data/releases/download/stats_player/stats_player_week_{y}.csv"

    def snaps_url(y: int) -> str:
        return f"https://github.com/nflverse/nflverse-data/releases/download/snap_counts/snap_counts_{y}.csv"

    current_stats = read_csv(stats_url(season))
    prior_stats = read_csv(stats_url(prior))
    current_snaps = read_csv(snaps_url(season))
    prior_snaps = read_csv(snaps_url(prior))

    # Current-season usage should only use completed prior weeks.
    current_stats = [r for r in current_stats if (regular_week(r) or 999) < week]
    current_snaps = [r for r in current_snaps if int(float(r.get("week") or 999)) < week]

    # Week 1 fallback only needs the tail of the prior regular season.
    prior_stats = [r for r in prior_stats if (regular_week(r) or 0) >= 15]
    prior_snaps = [r for r in prior_snaps if int(float(r.get("week") or 0)) >= 15]

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "season": season,
        "week": week,
        "prior_season": prior,
        "source": "nflverse player stats + snap counts",
        "current_stats": slim(current_stats, STAT_FIELDS),
        "prior_stats": slim(prior_stats, STAT_FIELDS),
        "current_snaps": slim(current_snaps, SNAP_FIELDS),
        "prior_snaps": slim(prior_snaps, SNAP_FIELDS),
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf-8")
    print(
        f"Wrote usage snapshot: {len(payload['current_stats'])} current stats, "
        f"{len(payload['current_snaps'])} current snaps, {len(payload['prior_stats'])} prior stats, "
        f"{len(payload['prior_snaps'])} prior snaps"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
