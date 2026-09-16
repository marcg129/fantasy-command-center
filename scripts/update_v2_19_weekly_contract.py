#!/usr/bin/env python3
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "tests" / "weekly_contract_test.py"
text = path.read_text(encoding="utf-8")


def replace_once(old, new, label):
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly 1 match, found {count}")
    text = text.replace(old, new, 1)


replace_once(
    '    "weeklyStreamers",\n]',
    '    "weeklyStreamers",\n    "weeklyMovePriority",\n]',
    "required move priority DOM id",
)
replace_once(
    '    "renderStreamerFinder",\n    "renderTradeIntelligence",',
    '    "renderStreamerFinder",\n    "transactionPriorityScore",\n    "allocateTransactionResources",\n    "buildTransactionPriorityCandidates",\n    "renderTransactionPriorityQueue",\n    "renderTradeIntelligence",',
    "required transaction priority helpers",
)
replace_once(
    '    "Review waiver move",\n]',
    '    "Review waiver move",\n    "Transaction Priority Queue",\n    "BLOCKED — NO SAFE DROP",\n]',
    "required transaction priority copy",
)
replace_once(
    '        "renderStreamerFinder(ctx)",\n        "renderProjectionPanel(matchups,ctx)",',
    '        "renderStreamerFinder(ctx)",\n        "renderTransactionPriorityQueue(ctx,streamers,moves)",\n        "renderProjectionPanel(matchups,ctx)",',
    "required transaction priority pipeline stage",
)
replace_once(
    '        "renderWeeklyActionPlan(ctx,pool,drops,moves,steals,matchups,simulation)",',
    '        "renderWeeklyActionPlan(ctx,pool,drops,moves,steals,matchups,simulation,priorities)",',
    "updated action plan pipeline signature",
)

path.write_text(text, encoding="utf-8")
print("Updated Weekly contract for v2.19")
