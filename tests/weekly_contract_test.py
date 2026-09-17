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
    "weeklyStreamers",
    "weeklyMovePriority",
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
    "streamingThresholdForPosition",
    "streamingStarterForPosition",
    "streamingPlayerSnapshot",
    "streamingCandidatePool",
    "streamingRecommendationForPosition",
    "streamerDirectReplacementReview",
    "renderStreamerFinder",
    "transactionPriorityScore",
    "allocateTransactionResources",
    "buildTransactionPriorityCandidates",
    "renderTransactionPriorityQueue",
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
    "Streamer Finder",
    "NO-ACTION STREAMING EDGE",
    "MODEL CONFLICT",
    "QB:2.0,TE:1.5,K:1.5,DEF:2.0",
    "Roster-space decisions stay in Drop Review/Waiver Planner",
    "Review waiver move",
    "Transaction Priority Queue",
    "DIRECT REPLACEMENT",
    "ROSTER CHURN",
    "NO JUSTIFIED DROP",
    "NO SAFE DROP",
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

# Verify the dedicated streamer pool exists and does not reuse the QB-suppression rule
# from the ordinary waiver pool. Streamer Finder must compare strong incumbent QBs too.
streamer_pool_match = re.search(
    r"function\s+streamingCandidatePool\s*\(ctx\)\s*\{(.*?)\n\s*\}\n\n\s*function\s+streamingRecommendationForPosition",
    html,
    flags=re.S,
)
if not streamer_pool_match:
    errors.append("could not isolate streamingCandidatePool()")
else:
    streamer_pool_body = streamer_pool_match.group(1)
    if "strongQBAlreadySolved" in streamer_pool_body or "qbSolved" in streamer_pool_body:
        errors.append("streamingCandidatePool() must not suppress QB comparisons for a strong incumbent QB")
    if "['QB','TE','K','DEF']" not in streamer_pool_body:
        errors.append("streamingCandidatePool() must be limited to QB/TE/K/DEF")

streamer_reco_match = re.search(
    r"function\s+streamingRecommendationForPosition\s*\(ctx,pool,pos\)\s*\{(.*?)\n\s*\}\n\n\s*function\s+streamerWaiverReviewForRecommendation",
    html,
    flags=re.S,
)
if not streamer_reco_match:
    errors.append("could not isolate streamingRecommendationForPosition()")
else:
    streamer_reco_body = streamer_reco_match.group(1)
    if "projectionClears && !outlookNotStronglyAgainst" not in streamer_reco_body:
        errors.append("streamer decisions must distinguish a cleared projection threshold from an Outlook conflict")
    if "MODEL CONFLICT" not in streamer_reco_body:
        errors.append("streamer model conflicts must carry an explicit MODEL CONFLICT label")

streamer_render_match = re.search(
    r"function\s+renderStreamerFinder\s*\(ctx\)\s*\{(.*?)\n\s*\}\n\n\s*function\s+renderTradeIntelligence",
    html,
    flags=re.S,
)
if not streamer_render_match:
    errors.append("could not isolate renderStreamerFinder(ctx)")
else:
    streamer_render_body = streamer_render_match.group(1)
    if "streamingCandidatePool(ctx)" not in streamer_render_body:
        errors.append("renderStreamerFinder() must use the dedicated streaming candidate pool")
    if "streamerWaiverBtn" not in streamer_render_body:
        errors.append("stream recommendations must include a Review waiver move control")
    if "scrollIntoView" not in streamer_render_body and "reviewStreamerWaiverMove(ctx,rows[index])" not in streamer_render_body:
        errors.append("stream recommendations must include a working Review waiver move handoff")
    if "r.status==='HOLD'?currentName:bestName" not in streamer_render_body:
        errors.append("HOLD streamer headlines must name the incumbent starter, not the available comparison")

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
        "renderStreamerFinder(ctx)",
        "renderTransactionPriorityQueue(ctx,streamers,moves)",
        "renderProjectionPanel(matchups,ctx)",
        "renderWeeklySimulation(matchups,ctx)",
        "renderLeagueMedian(matchups,ctx,simulation)",
        "renderWeeklyMatchup(matchups,ctx)",
        "renderWeeklyActionPlan(ctx,pool,drops,moves,steals,matchups,simulation,priorities)",
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
    "projection/simulation/streaming helpers, event wiring, guardrail copy, and JavaScript syntax are intact."
)
