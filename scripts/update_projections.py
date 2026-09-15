#!/usr/bin/env python3
"""Build data/projections.json for Fantasy Command Center.

Sleeper's public projection feed is useful but not part of the documented core
league API. This updater isolates that dependency in a GitHub Actions snapshot
so the browser app remains read-only and can fail gracefully if the projection
feed changes.
"""

from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "projections.json"
UA = "FantasyCommandCenter-ProjectionsBot/1.0 (+GitHub Actions)"

STATE_URL = "https://api.sleeper.app/v1/state/nfl"
LEGACY_TEMPLATE = "https://api.sleeper.app/v1/projections/nfl/regular/{season}/{week}"
CURRENT_TEMPLATE = "https://api.sleeper.com/projections/nfl/{season}/{week}?season_type=regular"

USEFUL_EXACT = {
    "pass_yd", "pass_td", "pass_int", "pass_2pt", "pass_sack",
    "rush_yd", "rush_td", "rush_2pt", "rush_att",
    "rec", "rec_yd", "rec_td", "rec_2pt", "rec_tgt",
    "fum", "fum_lost",
    "xpm", "xpmiss", "fgm", "fgmiss",
    "sack", "int", "fum_rec", "def_td", "safe", "blk_kick", "pts_allow",
    "kr_td", "pr_td", "st_td",
}
USEFUL_PREFIXES = (
    "fgm_", "fgmiss_", "pass_", "rush_", "rec_", "fum_", "idp_", "def_",
)


def get_json(url: str) -> object:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": UA, "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def current_state() -> dict:
    data = get_json(STATE_URL)
    if not isinstance(data, dict):
        raise RuntimeError("Sleeper NFL state response was not an object")
    return data


def row_stats(row: object) -> dict:
    if not isinstance(row, dict):
        return {}
    nested = row.get("stats")
    if isinstance(nested, dict):
        return nested
    return row


def is_useful(stats: dict) -> bool:
    for key, value in stats.items():
        if value is None:
            continue
        if key in USEFUL_EXACT or key.startswith(USEFUL_PREFIXES):
            try:
                float(value)
                return True
            except (TypeError, ValueError):
                continue
    return False


def normalize(payload: object) -> dict[str, dict]:
    out: dict[str, dict] = {}

    if isinstance(payload, dict):
        for raw_id, raw_row in payload.items():
            row = raw_row if isinstance(raw_row, dict) else {}
            player = row.get("player") if isinstance(row.get("player"), dict) else {}
            player_id = row.get("player_id") or player.get("player_id") or raw_id
            stats = row_stats(row)
            if not player_id or not is_useful(stats):
                continue
            out[str(player_id)] = {"stats": stats}
        return out

    if isinstance(payload, list):
        for raw_row in payload:
            if not isinstance(raw_row, dict):
                continue
            player = raw_row.get("player") if isinstance(raw_row.get("player"), dict) else {}
            player_id = raw_row.get("player_id") or player.get("player_id") or player.get("id")
            stats = row_stats(raw_row)
            if not player_id or not is_useful(stats):
                continue
            entry = {"stats": stats}
            if player:
                entry["player"] = {
                    k: player.get(k)
                    for k in ("player_id", "first_name", "last_name", "position", "team")
                    if player.get(k) is not None
                }
            out[str(player_id)] = entry
        return out

    return out


def fetch_projection_payload(season: int, week: int) -> tuple[object, str]:
    urls = [
        LEGACY_TEMPLATE.format(season=season, week=week),
        CURRENT_TEMPLATE.format(season=season, week=week),
    ]
    errors: list[str] = []
    for url in urls:
        try:
            payload = get_json(url)
            players = normalize(payload)
            if players:
                return payload, url
            errors.append(f"{url}: response contained no usable projected stat rows")
        except Exception as exc:
            errors.append(f"{url}: {type(exc).__name__}: {exc}")
    raise RuntimeError("; ".join(errors))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--season", type=int)
    parser.add_argument("--week", type=int)
    args = parser.parse_args()

    state = current_state()
    season = args.season or int(state.get("season") or datetime.now(timezone.utc).year)
    week = args.week or int(state.get("week") or state.get("display_week") or 1)
    if week < 1 or week > 18:
        raise SystemExit(f"Refusing invalid NFL week: {week}")

    payload, source_url = fetch_projection_payload(season, week)
    players = normalize(payload)
    if not players:
        raise SystemExit("Projection endpoint returned no usable player projections")

    now = datetime.now(timezone.utc)
    output = {
        "generated_at": now.isoformat().replace("+00:00", "Z"),
        "season": season,
        "week": week,
        "season_type": "regular",
        "source": "Sleeper weekly projections",
        "source_url": source_url,
        "undocumented_source": True,
        "player_count": len(players),
        "players": players,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {len(players)} projected players for {season} Week {week} to {OUT}")
    print(f"Source: {source_url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
