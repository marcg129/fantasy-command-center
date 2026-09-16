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

# These are the core helpers directly or transitively required by loadWeekly().
# Keeping the list explicit is intentional: the v2.17.1 regression was valid
# JavaScript, but Weekly Check failed because projection helpers disappeared.
required_functions = [
    "connect",
    "myWeeklyContext",
    "resolveCurrentAnalysisWeek",
    "loadWeeklyGameContext",
    "loadWeeklyUsageContext",
    "loadNewsIntelligence",
    "loadProjectionIntelligence",
    "loadProjectionCalibration",
    "renderWeeklyRoster",
    "renderWeeklyIR",
    "renderAvailabilityPanel",
    "renderWeeklyOutlook",
    "renderStartSit",
    "renderUsagePanel",
    "renderWeeklyAdds",
    "renderNewsPanel",
    "renderPostDraftSteals",
    "renderWeeklyDrops",
    "renderWeeklyMoves",
    "renderWaiverClaims",
    "renderTradeIntelligence",
    "renderWeeklyTrending",
    "renderWeeklyTransactions",
    "renderGameEnvironment",
    "renderProjectionPanel",
    "renderWeeklySimulation",
    "renderLeagueMedian",
    "renderWeeklyMatchup",
    "renderWeeklyActionPlan",
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
    "loadWeekly",
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
    matches = re.findall(rf"\b(?:async\s+)?function\s+{re.escape(fn)}\s*\(", html)
    if len(matches) != 1:
        errors.append(f"expected exactly one function {fn}(), found {len(matches)}")

for fragment in required_fragments:
    if fragment not in html:
        errors.append(f"missing required weekly contract text: {fragment}")

# The controls must exist in markup and in script wiring/logic.
for wired_id in ("connectBtn", "weeklyRefreshBtn", "myName"):
    count = html.count(wired_id)
    if count < 2:
        errors.append(f"{wired_id} appears only {count} time(s); event wiring may be missing")

required_wiring = [
    "$('connectBtn').addEventListener('click',connect)",
    "$('weeklyRefreshBtn').addEventListener('click',loadWeekly)",
    "$('myName').addEventListener('keydown'",
]
for wiring in required_wiring:
    if wiring not in html:
        errors.append(f"missing required event wiring: {wiring}")

# Verify the top-level Weekly Check pipeline still calls every major renderer.
load_weekly_match = re.search(
    r"async\s+function\s+loadWeekly\s*\(\)\s*\{(.*?)\n\s*\}\n\n\s*\$\('connectBtn'\)",
    html,
    flags=re.S,
)
if not load_weekly_match:
    errors.append("could not isolate loadWeekly() for dependency assertions")
else:
    body = load_weekly_match.group(1)
    pipeline_calls = [
        "renderWeeklyRoster(ctx)",
        "renderWeeklyOutlook(ctx)",
        "renderStartSit(ctx)",
        "renderProjectionPanel(matchups,ctx)",
        "renderWeeklySimulation(matchups,ctx)",
        "renderLeagueMedian(matchups,ctx,simulation)",
        "renderWeeklyMatchup(matchups,ctx)",
        "renderWeeklyActionPlan(ctx,pool,drops,moves,steals,matchups,simulation)",
    ]
    for call in pipeline_calls:
        if call not in body:
            errors.append(f"loadWeekly() no longer calls required stage: {call}")

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
    "Weekly contract PASS: DOM anchors, Weekly Check dependency chain, critical "
    "projection/simulation helpers, event wiring, guardrail copy, and JavaScript syntax are intact."
)
