from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
HTML_PATH = ROOT / "index.html"
html = HTML_PATH.read_text(encoding="utf-8")

required_ids = [
    "connectBtn",
    "myName",
    "weeklyTab",
    "weeklyRefreshBtn",
    "weekInput",
    "weeklyRosterSummary",
    "weeklyRoster",
    "weeklyOutlookSummary",
    "weeklyOutlook",
    "weeklyLineupSummary",
    "weeklyStartSit",
    "weeklyMedian",
    "weeklyProjection",
    "weeklySimulation",
]

required_functions = [
    "projectionRowForId",
    "projectionPointsAllowedBandKey",
    "projectionScoringForId",
    "projectedPointsForId",
    "projectionTotalForIds",
    "projectionOptimalLineup",
    "projectedLeagueMedian",
    "projectionNonlinearKeys",
    "simulationCalibrationSummary",
    "simulationVarianceProfile",
]

required_fragments = [
    "CALIBRATION COLLECTING",
    "PROVISIONAL • LOW CONFIDENCE",
    "NO-ACTION TIE",
    "PREGAME ONLY",
    "Sleeper username / display name",
    "Run Weekly Check",
]

errors = []

for element_id in required_ids:
    if not re.search(rf'id=["\']{re.escape(element_id)}["\']', html):
        errors.append(f"missing required DOM id: {element_id}")

for fn in required_functions:
    matches = re.findall(rf"\bfunction\s+{re.escape(fn)}\s*\(", html)
    if len(matches) != 1:
        errors.append(f"expected exactly one function {fn}(), found {len(matches)}")

for fragment in required_fragments:
    if fragment not in html:
        errors.append(f"missing required weekly contract text: {fragment}")

# Both controls must appear in markup and again in script wiring/logic.
for wired_id in ("connectBtn", "weeklyRefreshBtn", "myName"):
    count = html.count(wired_id)
    if count < 2:
        errors.append(f"{wired_id} appears only {count} time(s); event wiring may be missing")

scripts = re.findall(r"<script>(.*?)</script>", html, flags=re.S)
if not scripts:
    errors.append("no inline JavaScript block found")
else:
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as tmp:
        tmp.write("\n".join(scripts))
        tmp_path = Path(tmp.name)
    result = subprocess.run(
        ["node", "--check", str(tmp_path)],
        text=True,
        capture_output=True,
    )
    tmp_path.unlink(missing_ok=True)
    if result.returncode:
        errors.append("frontend JavaScript syntax check failed:\n" + result.stderr.strip())

if errors:
    raise SystemExit("Weekly regression contract failed:\n- " + "\n- ".join(errors))

print(
    "Weekly contract PASS: DOM anchors, critical projection/simulation helpers, "
    "event-wiring anchors, guardrail copy, and JavaScript syntax are intact."
)
