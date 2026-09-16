#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
source = INDEX.read_text(encoding="utf-8")

required = [
    'id="weeklyMovePriority"',
    'MOVE PRIORITY',
    'BLOCKED — NO SAFE DROP',
    'TRANSACTION_PRIORITY_CORE_START',
    'TRANSACTION_PRIORITY_CORE_END',
    'function renderTransactionPriorityQueue(',
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
        "starterGain": 5.2,
        "rosterGain": -22,
        "coverageNeed": False,
        "competitionLevel": 1,
        "transactionCost": 0,
        "safeDropName": None,
    },
    {
        "name": "Tampa Bay Buccaneers",
        "type": "STREAM",
        "starterGain": 3.7,
        "rosterGain": -68,
        "coverageNeed": False,
        "competitionLevel": 1,
        "transactionCost": 0,
        "safeDropName": None,
    },
]

node_script = f"""
{core}
const fixture = {json.dumps(fixture)};
const out = allocateTransactionResources(fixture, 1);
if (out.length !== 2) throw new Error('expected two ranked moves');
if (out[0].name !== 'Jake Ferguson') throw new Error('larger starter gain must rank first');
if (out[0].resource !== 'OPEN SLOT' || out[0].blocked) throw new Error('only top move should consume the open slot');
if (out[1].resource !== 'BLOCKED — NO SAFE DROP' || !out[1].blocked) throw new Error('second move must be blocked when the slot is consumed and no safe drop exists');

const withDrop = allocateTransactionResources([
  {{name:'Jake Ferguson',type:'STREAM',starterGain:5.2,rosterGain:12,coverageNeed:false,competitionLevel:1,transactionCost:0,safeDropName:'Jakobi Meyers'}},
  {{name:'Tampa Bay Buccaneers',type:'STREAM',starterGain:3.7,rosterGain:-68,coverageNeed:false,competitionLevel:1,transactionCost:0,safeDropName:null}}
], 0);
if (withDrop[0].resource !== 'SAFE DROP' || withDrop[0].dropName !== 'Jakobi Meyers' || withDrop[0].blocked) throw new Error('safe churn candidate should make a no-slot move actionable');

const executableFirst = allocateTransactionResources([
  {{name:'Blocked Stream',type:'STREAM',starterGain:8.0,rosterGain:-20,coverageNeed:false,competitionLevel:1,transactionCost:0,safeDropName:null}},
  {{name:'Actionable Waiver',type:'WAIVER',starterGain:0,rosterGain:12,coverageNeed:false,competitionLevel:1,transactionCost:1,safeDropName:'Bench Churn'}}
], 0);
if (executableFirst[0].name !== 'Actionable Waiver' || executableFirst[0].blocked) throw new Error('an executable transaction must rank ahead of a blocked higher-score idea');
if (executableFirst[1].name !== 'Blocked Stream' || !executableFirst[1].blocked) throw new Error('blocked ideas should remain visible after actionable moves');
console.log('transaction priority behavior ok');
"""

proc = subprocess.run(["node", "-e", node_script], capture_output=True, text=True)
assert proc.returncode == 0, proc.stderr or proc.stdout
print("weekly transaction priority contract ok")
