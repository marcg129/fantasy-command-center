#!/usr/bin/env python3
# v2.19.1 position-aware transaction routing regression
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
source = INDEX.read_text(encoding="utf-8")

required = [
    'id="weeklyMovePriority"',
    'MOVE PRIORITY',
    'NO JUSTIFIED DROP',
    'NO SAFE DROP',
    'DIRECT REPLACEMENT',
    'ROSTER CHURN',
    'TRANSACTION_PRIORITY_CORE_START',
    'TRANSACTION_PRIORITY_CORE_END',
    'function renderTransactionPriorityQueue(',
    'function streamerDirectReplacementReview(',
    'const streamers=renderStreamerFinder(ctx);',
    'renderTransactionPriorityQueue(ctx,streamers,moves)',
    "'weeklyMovePriority'",
]
missing = [token for token in required if token not in source]
assert not missing, f"transaction priority contract missing: {missing}"

start_marker = '// TRANSACTION_PRIORITY_CORE_START'
end_marker = '// TRANSACTION_PRIORITY_CORE_END'
start = source.index(start_marker) + len(start_marker)
end = source.index(end_marker, start)
core = source[start:end]

fixture = [
    {
        "name": "Jake Ferguson",
        "type": "STREAM",
        "pos": "TE",
        "starterGain": 5.2,
        "rosterGain": -22,
        "coverageNeed": False,
        "competitionLevel": 1,
        "transactionCost": 0,
        "safeDropName": None,
        "churnCandidateName": "Jakobi Meyers",
        "directDropName": None,
    },
    {
        "name": "Tampa Bay Buccaneers",
        "type": "STREAM",
        "pos": "DEF",
        "starterGain": 3.7,
        "rosterGain": -68,
        "coverageNeed": False,
        "competitionLevel": 1,
        "transactionCost": 0,
        "safeDropName": None,
        "churnCandidateName": "Jakobi Meyers",
        "directDropName": None,
    },
]

node_script = f"""
{core}
const fixture = {json.dumps(fixture)};
const out = allocateTransactionResources(fixture, 1);
if (out.length !== 2) throw new Error('expected two ranked moves');
if (out[0].name !== 'Jake Ferguson') throw new Error('larger starter gain must rank first');
if (out[0].resource !== 'OPEN SLOT' || out[0].blocked) throw new Error('only top move should consume the open slot');
if (out[1].resource !== 'NO JUSTIFIED DROP' || !out[1].blocked) throw new Error('a visible churn candidate that does not justify the stream must be labeled NO JUSTIFIED DROP');

const withRosterChurn = allocateTransactionResources([
  {{name:'Jake Ferguson',type:'STREAM',pos:'TE',starterGain:5.2,rosterGain:12,coverageNeed:false,competitionLevel:1,transactionCost:0,safeDropName:'Jakobi Meyers',churnCandidateName:'Jakobi Meyers',directDropName:null}}
], 0);
if (withRosterChurn[0].resource !== 'ROSTER CHURN' || withRosterChurn[0].dropName !== 'Jakobi Meyers' || withRosterChurn[0].blocked) throw new Error('justified generic churn should be labeled ROSTER CHURN');

const directDefenseSwap = allocateTransactionResources([
  {{name:'Tampa Bay Buccaneers',type:'STREAM',pos:'DEF',starterGain:3.7,rosterGain:-68,coverageNeed:false,competitionLevel:1,transactionCost:0,safeDropName:null,churnCandidateName:'Jakobi Meyers',directDropName:'Jacksonville Jaguars'}}
], 0);
if (directDefenseSwap[0].resource !== 'DIRECT REPLACEMENT' || directDefenseSwap[0].dropName !== 'Jacksonville Jaguars' || directDefenseSwap[0].blocked) throw new Error('a justified same-position DEF replacement should be preferred over unrelated roster churn');

const valuableQbIncumbent = allocateTransactionResources([
  {{name:'Jordan Love',type:'STREAM',pos:'QB',starterGain:3.0,rosterGain:-40,coverageNeed:false,competitionLevel:1,transactionCost:0,safeDropName:null,churnCandidateName:'Bench WR',directDropName:null,currentName:'Joe Burrow'}}
], 0);
if (valuableQbIncumbent[0].resource !== 'NO JUSTIFIED DROP' || !valuableQbIncumbent[0].blocked) throw new Error('a valuable QB incumbent must not be auto-dropped just because the streamer projects better this week');

const noDropAtAll = allocateTransactionResources([
  {{name:'Emergency Stream',type:'STREAM',pos:'TE',starterGain:4.0,rosterGain:null,coverageNeed:false,competitionLevel:1,transactionCost:0,safeDropName:null,churnCandidateName:null,directDropName:null}}
], 0);
if (noDropAtAll[0].resource !== 'NO SAFE DROP' || !noDropAtAll[0].blocked) throw new Error('NO SAFE DROP is reserved for cases with no legal/protected drop candidate at all');

const executableFirst = allocateTransactionResources([
  {{name:'Blocked Stream',type:'STREAM',pos:'TE',starterGain:8.0,rosterGain:-20,coverageNeed:false,competitionLevel:1,transactionCost:0,safeDropName:null,churnCandidateName:'Bench Churn',directDropName:null}},
  {{name:'Actionable Waiver',type:'WAIVER',pos:'WR',starterGain:0,rosterGain:12,coverageNeed:false,competitionLevel:1,transactionCost:1,safeDropName:'Bench Churn',churnCandidateName:'Bench Churn',directDropName:null}}
], 0);
if (executableFirst[0].name !== 'Actionable Waiver' || executableFirst[0].blocked) throw new Error('an executable transaction must rank ahead of a blocked higher-score idea');
if (executableFirst[1].name !== 'Blocked Stream' || !executableFirst[1].blocked) throw new Error('blocked ideas should remain visible after actionable moves');

const sharedChurnOpportunity = allocateTransactionResources([
  {{name:'Tampa Bay Buccaneers',type:'STREAM',pos:'DEF',starterGain:3.7,rosterGain:82,coverageNeed:false,competitionLevel:1,transactionCost:0,safeDropName:'Michael Mayer',churnCandidateName:'Michael Mayer',directDropName:null,actionThreshold:2.0}},
  {{name:'Emmett Johnson',type:'WAIVER',pos:'RB',starterGain:0,rosterGain:82,coverageNeed:false,competitionLevel:1,transactionCost:2,safeDropName:'Michael Mayer',churnCandidateName:'Michael Mayer',directDropName:null,actionThreshold:8.0}}
], 0);
if (sharedChurnOpportunity[0].name !== 'Emmett Johnson' || sharedChurnOpportunity[0].resource !== 'ROSTER CHURN' || sharedChurnOpportunity[0].dropName !== 'Michael Mayer' || sharedChurnOpportunity[0].blocked) throw new Error('strong season-long waiver upgrade should preserve the shared churn slot over a moderate discretionary stream');
const tampaOpportunity = sharedChurnOpportunity.find(x=>x.name==='Tampa Bay Buccaneers');
if (!tampaOpportunity || tampaOpportunity.resource !== 'ROSTER OPPORTUNITY COST' || !tampaOpportunity.blocked) throw new Error('streamer that loses a shared churn slot must be labeled ROSTER OPPORTUNITY COST');
if (tampaOpportunity.opportunityWinnerName !== 'Emmett Johnson' || tampaOpportunity.opportunityDropName !== 'Michael Mayer') throw new Error('opportunity-cost block should identify the competing move and preserved churn resource');
console.log('transaction priority behavior ok');
"""

proc = subprocess.run(["node", "-e", node_script], capture_output=True, text=True)
assert proc.returncode == 0, proc.stderr or proc.stdout

# Exercise the direct-replacement evaluator itself. K/DEF gets a more permissive
# post-swap value guardrail than QB/TE, but projection threshold alone is not enough.
direct_start = source.index('function streamerDirectReplacementReview(')
direct_end = source.index('\n\n  function reviewStreamerWaiverMove', direct_start)
direct_helper = source[direct_start:direct_end]

direct_guardrail_script = f"""
const state = {{weeklyMode:'weekly'}};
let incumbentKeepValue = 70;
function dropCandidates(ctx) {{
  return [{{
    id:'JAX', name:'Jacksonville Jaguars', pos:'DEF',
    isKeeper:false, isReserve:false, irEligible:false,
    protectedInjuryStash:false, recentlyAdded:false,
    isStarter:true, isOptimizedStarter:true, lineupProtected:true,
    soleRequired:true, displacedOneStarter:false,
    redundantQB:false, redundantTE:false
  }}];
}}
function effectiveKeepValue(drop,ctx) {{ return incumbentKeepValue; }}
function streamerWaiverReviewForRecommendation(ctx,r) {{ return {{addValue:20,reviewCut:8}}; }}
{direct_helper}
const recommendation = {{
  status:'STREAM', pos:'DEF', threshold:2.0, projectionEdge:3.7,
  current:{{id:'JAX',p:{{player_id:'JAX'}}}}
}};
let review = streamerDirectReplacementReview({{}},recommendation,{{addValue:20,reviewCut:8}});
if (review.justified || review.drop) throw new Error('valuable DEF incumbent must not be direct-replaced solely because the weekly projection threshold clears');

incumbentKeepValue = 24;
review = streamerDirectReplacementReview({{}},recommendation,{{addValue:20,reviewCut:8}});
if (!review.justified || !review.drop || review.drop.name !== 'Jacksonville Jaguars') throw new Error('modest K/DEF value disadvantage should still permit a direct replacement when the stream clears its weekly threshold');
console.log('specialist incumbent value guardrail ok');
"""

guardrail_proc = subprocess.run(["node", "-e", direct_guardrail_script], capture_output=True, text=True)
assert guardrail_proc.returncode == 0, guardrail_proc.stderr or guardrail_proc.stdout
print("weekly transaction priority contract ok")
