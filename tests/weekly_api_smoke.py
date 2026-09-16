# v2.17.3 baseline: this file change intentionally exercises the permanent regression workflow.
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://api.sleeper.app/v1"
LEAGUE_ID = os.environ.get("FCC_SMOKE_LEAGUE_ID", "1314532597539291136")
USERNAME = os.environ.get("FCC_SMOKE_USER", "coreyg129")


def get_json(url, timeout=25):
    req = Request(url, headers={"User-Agent": "fantasy-command-center-regression/1.0"})
    with urlopen(req, timeout=timeout) as response:
        if response.status != 200:
            raise RuntimeError(f"GET {url} returned HTTP {response.status}")
        return json.loads(response.read().decode("utf-8"))


league = get_json(f"{BASE}/league/{LEAGUE_ID}")
if str(league.get("league_id")) != LEAGUE_ID:
    raise SystemExit("Sleeper league endpoint did not return the configured league")

users = get_json(f"{BASE}/league/{LEAGUE_ID}/users")
rosters = get_json(f"{BASE}/league/{LEAGUE_ID}/rosters")
nfl_state = get_json(f"{BASE}/state/nfl")

if not isinstance(users, list) or not users:
    raise SystemExit("Sleeper league users endpoint returned no managers")
if not isinstance(rosters, list) or not rosters:
    raise SystemExit("Sleeper league rosters endpoint returned no rosters")

manager = None
for user in users:
    display = str(user.get("display_name") or "")
    metadata_name = str((user.get("metadata") or {}).get("team_name") or "")
    if USERNAME.lower() in {display.lower(), metadata_name.lower()}:
        manager = user
        break

if manager is None:
    raise SystemExit(f"Configured smoke manager {USERNAME!r} was not found in league users")

manager_id = str(manager.get("user_id") or "")
manager_roster = next((r for r in rosters if str(r.get("owner_id") or "") == manager_id), None)
if manager_roster is None:
    raise SystemExit("Configured smoke manager does not currently own a Sleeper roster")

week = int(nfl_state.get("week") or nfl_state.get("leg") or 1)
week = min(18, max(1, week))
matchups = get_json(f"{BASE}/league/{LEAGUE_ID}/matchups/{week}")
if not isinstance(matchups, list):
    raise SystemExit("Sleeper matchup endpoint did not return a list")

# Same-origin data snapshots used by Weekly Check must remain parseable and populated.
projection_path = ROOT / "data" / "projections.json"
usage_path = ROOT / "data" / "usage.json"
calibration_path = ROOT / "data" / "calibration.json"

for path in (projection_path, usage_path, calibration_path):
    if not path.exists():
        raise SystemExit(f"required Weekly data snapshot is missing: {path.relative_to(ROOT)}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise SystemExit(f"invalid JSON in {path.relative_to(ROOT)}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"snapshot root must be an object: {path.relative_to(ROOT)}")

projections = json.loads(projection_path.read_text(encoding="utf-8"))
if int(projections.get("player_count") or 0) < 100:
    raise SystemExit("projection snapshot is unexpectedly sparse")
if not isinstance(projections.get("players"), dict) or not projections["players"]:
    raise SystemExit("projection snapshot has no player map")

usage = json.loads(usage_path.read_text(encoding="utf-8"))
if not usage:
    raise SystemExit("usage snapshot is empty")

calibration = json.loads(calibration_path.read_text(encoding="utf-8"))
if "positions" not in calibration or not isinstance(calibration["positions"], dict):
    raise SystemExit("calibration snapshot is missing position profiles")

print(
    "Weekly API smoke PASS: league, manager, roster, current matchup endpoint, "
    "projection snapshot, usage snapshot, and calibration snapshot are available."
)
