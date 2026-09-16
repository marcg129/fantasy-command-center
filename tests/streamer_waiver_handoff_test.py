from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
html = (ROOT / "index.html").read_text(encoding="utf-8")

errors = []

required_functions = [
    "streamerWaiverReviewForRecommendation",
    "reviewStreamerWaiverMove",
]
for fn in required_functions:
    matches = re.findall(rf"\bfunction\s+{re.escape(fn)}\s*\(", html)
    if len(matches) != 1:
        errors.append(f"expected exactly one function {fn}(), found {len(matches)}")

for fragment in [
    "streamerWaiverReview:null",
    "weeklyWaiverMoves:[]",
    "weeklyWaiverPool:[]",
    "STREAMER REVIEW",
    "STREAM EDGE — NO SAFE DROP",
    "data-streamer-index",
]:
    if fragment not in html:
        errors.append(f"missing streamer-waiver handoff fragment: {fragment}")

review_match = re.search(
    r"function\s+streamerWaiverReviewForRecommendation\s*\(ctx,r\)\s*\{(.*?)\n\s*\}\n\n\s*function\s+reviewStreamerWaiverMove",
    html,
    flags=re.S,
)
if not review_match:
    errors.append("could not isolate streamerWaiverReviewForRecommendation(ctx,r)")
else:
    body = review_match.group(1)
    for required in [
        "dropCandidates(ctx)",
        "primaryChurnCandidate(ctx,drops)",
        "effectiveKeepValue(drop,ctx)",
        "openSlots",
        "freeAgentScore(add,ctx",
        "addValue",
    ]:
        if required not in body:
            errors.append(f"streamer waiver review must use existing safe-drop/value logic: {required}")
    if "Number(add.weeklyValue)" in body:
        errors.append("streamer waiver review must not rely on weeklyValue from the dedicated streaming pool")
    if "drop:r.current" in body or "drop=current" in body:
        errors.append("streamer waiver review must never assume the incumbent starter is the drop")

handoff_match = re.search(
    r"function\s+reviewStreamerWaiverMove\s*\(ctx,r\)\s*\{(.*?)\n\s*\}\n\n\s*function\s+renderStreamerFinder",
    html,
    flags=re.S,
)
if not handoff_match:
    errors.append("could not isolate reviewStreamerWaiverMove(ctx,r)")
else:
    body = handoff_match.group(1)
    for required in [
        "state.streamerWaiverReview",
        "renderWaiverClaims(ctx,state.weeklyWaiverMoves,state.weeklyWaiverPool)",
        "scrollIntoView",
    ]:
        if required not in body:
            errors.append(f"Review waiver move handoff is incomplete: {required}")

claims_match = re.search(
    r"function\s+renderWaiverClaims\s*\(ctx,moves,pool\)\s*\{(.*?)\n\s*\}\n\n\s*function\s+weeklyContextForRosterId",
    html,
    flags=re.S,
)
if not claims_match:
    errors.append("could not isolate renderWaiverClaims(ctx,moves,pool)")
else:
    body = claims_match.group(1)
    for required in [
        "state.weeklyWaiverMoves",
        "state.weeklyWaiverPool",
        "state.streamerWaiverReview",
        "STREAMER REVIEW",
        "STREAM EDGE — NO SAFE DROP",
    ]:
        if required not in body:
            errors.append(f"Waiver Claim Planner does not consume pinned streamer review: {required}")

streamer_match = re.search(
    r"function\s+renderStreamerFinder\s*\(ctx\)\s*\{(.*?)\n\s*\}\n\n\s*function\s+renderTradeIntelligence",
    html,
    flags=re.S,
)
if not streamer_match:
    errors.append("could not isolate renderStreamerFinder(ctx)")
else:
    body = streamer_match.group(1)
    if "data-streamer-index" not in body:
        errors.append("Streamer Finder buttons must identify the exact recommendation being reviewed")
    if "reviewStreamerWaiverMove(ctx,rows[index])" not in body:
        errors.append("Streamer Finder must pass the exact recommendation into Waiver Planner")

load_weekly_match = re.search(
    r"async\s+function\s+loadWeekly\s*\(\)\s*\{(.*?)\n\s*\}\n\n\s*\$\('connectBtn'\)",
    html,
    flags=re.S,
)
if not load_weekly_match:
    errors.append("could not isolate loadWeekly() for stale streamer-review reset")
elif "state.streamerWaiverReview=null" not in load_weekly_match.group(1):
    errors.append("each new Weekly Check must clear any stale pinned streamer review")

if errors:
    raise SystemExit("Streamer waiver handoff contract failed:\n- " + "\n- ".join(errors))

print("Streamer waiver handoff PASS: exact candidate propagation, computed roster value, safe-drop review, no-auto-incumbent-drop, and stale-review reset contracts are intact.")
