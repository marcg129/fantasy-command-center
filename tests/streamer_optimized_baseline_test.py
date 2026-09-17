#!/usr/bin/env python3
# v2.19.2 optimized Streamer Finder baseline regression
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
source = INDEX.read_text(encoding="utf-8")

required = [
    "function streamingStarterBaselineForPosition(",
    "const baselineInfo=streamingStarterBaselineForPosition(ctx,pos);",
    "submittedCurrent:",
    "baselineSource:",
    "optimized baseline",
    "Sleeper currently starts",
]
missing = [token for token in required if token not in source]
assert not missing, f"optimized streamer baseline contract missing: {missing}"

start = source.index("function streamingStarterForPosition(")
end = source.index("\n\n  function streamerWaiverReviewForRecommendation", start)
streaming_block = source[start:end]

node_script = f"""
const state = {{players: {{
  MAYER: {{player_id:'MAYER', first_name:'Michael', last_name:'Mayer', position:'TE', team:'LV'}},
  BOWERS: {{player_id:'BOWERS', first_name:'Brock', last_name:'Bowers', position:'TE', team:'LV', injury_status:'Questionable'}},
  SCHULTZ: {{player_id:'SCHULTZ', first_name:'Dalton', last_name:'Schultz', position:'TE', team:'HOU'}}
}}}};
function normalizedFantasyPos(p) {{ return String(p?.position||'').toUpperCase()==='DST'?'DEF':String(p?.position||'').toUpperCase(); }}
function optimizedLineup(ctx) {{
  return [{{slot:'TE',index:0,id:'BOWERS',p:state.players.BOWERS,score:90}}];
}}
function pName(p) {{ return [p?.first_name,p?.last_name].filter(Boolean).join(' '); }}
function weeklyOutlookForPlayer(p) {{
  const values={{MAYER:60,BOWERS:90,SCHULTZ:75}};
  return {{score:values[p?.player_id]??0}};
}}
function projectedPointsForId(id) {{
  const values={{MAYER:8.0,BOWERS:14.5,SCHULTZ:13.7}};
  return values[String(id)] ?? null;
}}
function availabilityAdjustmentForPlayer(p) {{ return 0; }}
function gameEnvAdjustmentForPlayer(p) {{ return 0; }}
function playerUsableForRequiredStart(p) {{ return true; }}
function dynamicPlayerBoard() {{ return []; }}
function rosteredPlayerIds() {{ return new Set(); }}
function recentlyDroppedByMeIds() {{ return new Set(); }}
function inSeasonMarketRank() {{ return 100; }}
{streaming_block}

const ctx = {{
  my:{{starters:['MAYER']}},
  players:['MAYER','BOWERS'],
  reserve:new Set()
}};
const pool=[{{pos:'TE',player_id:'SCHULTZ',pdata:state.players.SCHULTZ,weeklyValue:50}}];
const result=streamingRecommendationForPosition(ctx,pool,'TE');
if (result.current?.id !== 'BOWERS') throw new Error('optimized Bowers must be the streaming baseline instead of submitted Mayer');
if (result.submittedCurrent?.id !== 'MAYER') throw new Error('submitted Sleeper starter must remain available as context');
if (result.baselineSource !== 'OPTIMIZED') throw new Error('baseline source should identify optimizer selection');
if (result.status !== 'HOLD') throw new Error('Schultz must not stream merely because he beats stale submitted starter Mayer');
if (Math.abs(result.projectionEdge - (-0.8)) > 0.001) throw new Error('projection edge must be measured against Bowers');

// If optimizer data cannot supply a usable same-position starter, preserve the
// existing submitted-lineup behavior as a safe fallback.
optimizedLineup = function(ctx) {{ return []; }};
const fallback=streamingRecommendationForPosition(ctx,pool,'TE');
if (fallback.current?.id !== 'MAYER') throw new Error('submitted starter should remain the fallback baseline');
if (fallback.baselineSource !== 'SUBMITTED') throw new Error('fallback source should be SUBMITTED');
console.log('optimized streamer baseline behavior ok');
"""

proc = subprocess.run(["node", "-e", node_script], capture_output=True, text=True)
assert proc.returncode == 0, proc.stderr or proc.stdout
print("optimized streamer baseline contract ok")
