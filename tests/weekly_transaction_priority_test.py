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
console.log('transaction priority behavior ok');
"""

proc = subprocess.run(["node", "-e", node_script], capture_output=True, text=True)
assert proc.returncode == 0, proc.stderr or proc.stdout
print("weekly transaction priority contract ok")
