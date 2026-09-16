from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
index_path = ROOT / 'index.html'
changelog_path = ROOT / 'CHANGELOG.md'

html = index_path.read_text(encoding='utf-8')

# Version + Weekly hero copy.
html = html.replace('Multi-manager beta • week-aware management • v2.17', 'Multi-manager beta • week-aware management • v2.17.1', 1)
html = html.replace(
    'Weekly lineup, matchup, waiver, and roster-management command center. v2.17 adds projection-error calibration infrastructure while preserving current-week resolution, lineup consensus, median strategy, and reliable usage.',
    'Weekly lineup, matchup, waiver, and roster-management command center. v2.17.1 adds simulation-confidence guardrails and explicit no-action thresholds while preserving calibration, current-week resolution, lineup consensus, median strategy, and reliable usage.',
    1,
)

# Replace the calibration summary with explicit confidence and decision thresholds.
pattern = re.compile(r"  function simulationCalibrationSummary\(\) \{.*?\n  \}\n\n  function simulationVarianceProfile", re.S)
replacement = r'''  function simulationCalibrationSummary() {
    const defaults={QB:0.32,RB:0.50,WR:0.55,TE:0.55,K:0.45,DEF:0.55};
    const feed=state.calibrationFeed;
    const weeks=Array.isArray(feed?.completed_weeks)?feed.completed_weeks:[];
    const profiles=feed?.positions||{};
    const ready=Object.entries(profiles).filter(([,p])=>p?.mode==='empirical_blend');
    const cvText=Object.keys(defaults).map(pos=>{
      const v=Number(profiles?.[pos]?.cv_used);
      const cv=Number.isFinite(v)&&v>0?v:defaults[pos];
      return `${pos} ${Math.round(cv*100)}%`;
    }).join(', ');

    let mode='unavailable';
    let confidence='LOW';
    let label='HEURISTIC VARIANCE v1';
    let note=`Calibration file is not available yet; conservative baseline CVs remain active (${cvText}).`;

    if(feed && !ready.length) {
      mode='collecting';
      label=`CALIBRATION COLLECTING • ${weeks.length}W`;
      note=`Projection-error calibration is collecting frozen pregame snapshots. ${weeks.length}/${Number(feed.minimum_completed_weeks)||2} completed weeks are available; conservative baseline CVs remain active (${cvText}).`;
    } else if(feed && ready.length) {
      mode='blend';
      confidence=(weeks.length>=4 && ready.length>=5)?'HIGH':'MEDIUM';
      label=`CALIBRATION BLEND • ${weeks.length}W`;
      note=`Empirical projection-error variance is active for ${ready.length} position groups using ${Number(feed.sample_count)||0} samples across ${weeks.length} completed weeks. Current CVs: ${cvText}. Estimates are shrunk toward the conservative baseline to reduce early-season overfitting.`;
    }

    const edgeThreshold=confidence==='HIGH'?1.5:(confidence==='MEDIUM'?2.0:3.0);
    return {label,note,mode,confidence,edgeThreshold,weeks:weeks.length,readyPositions:ready.length};
  }

  function simulationVarianceProfile'''
html2, n = pattern.subn(replacement, html, count=1)
if n != 1:
    raise SystemExit(f'Could not replace simulationCalibrationSummary (matches={n})')
html = html2

# Make simulation styling confidence-aware and create a no-action decision threshold.
old = """    const cls=(h2hPct>=60 && (!Number.isFinite(medianPct)||medianPct>=60))
      ? 'simulation-good'
      : (risk?'simulation-warn':'simulation-neutral');
    setPill('simulationPill',`${ITER.toLocaleString()} pregame sims`,risk?'warn':'good');

    const swapText=incoming.length
      ? `Projection-optimal would start ${incoming.map(id=>esc(pName(state.players[id]))).join(', ')}${outgoing.length?` over ${outgoing.map(id=>esc(pName(state.players[id]))).join(', ')}`:''}.`
      : 'Projection-optimal uses the same starter set as your current lineup.';
"""
new = """    const cls=risk
      ? 'simulation-warn'
      : ((calibration.confidence!=='LOW' && h2hPct>=60 && (!Number.isFinite(medianPct)||medianPct>=60))?'simulation-good':'simulation-neutral');
    setPill('simulationPill',`${ITER.toLocaleString()} pregame sims`,risk?'warn':(calibration.confidence==='LOW'?'warn':'good'));

    const decisionThreshold=Number(calibration.edgeThreshold)||3.0;
    const candidateDeltas=[h2hDelta,doubleDelta];
    if(Number.isFinite(medianDelta)) candidateDeltas.push(medianDelta);
    const bestPositiveDelta=Math.max(0,...candidateDeltas.filter(Number.isFinite));
    const clearsDecisionThreshold=incoming.length>0 && bestPositiveDelta>=decisionThreshold;
    const confidenceChip=calibration.confidence==='HIGH'
      ? 'CALIBRATED • HIGH CONFIDENCE'
      : (calibration.confidence==='MEDIUM'?'CALIBRATED • MED CONFIDENCE':'PROVISIONAL • LOW CONFIDENCE');
    const edgeChip=!incoming.length
      ? 'NO LINEUP CHANGE'
      : (clearsDecisionThreshold?`SIM EDGE ≥${decisionThreshold.toFixed(1)}PP`:`NO-ACTION TIE <${decisionThreshold.toFixed(1)}PP`);

    const swapText=incoming.length
      ? (clearsDecisionThreshold
          ? `Projection-optimal would start ${incoming.map(id=>esc(pName(state.players[id]))).join(', ')}${outgoing.length?` over ${outgoing.map(id=>esc(pName(state.players[id]))).join(', ')}`:''}. Its best modeled probability lift is ${bestPositiveDelta.toFixed(1)} pp, clearing the current ${decisionThreshold.toFixed(1)} pp simulation decision threshold; this supports review, not an automatic lineup change.`
          : `Projection-optimal would start ${incoming.map(id=>esc(pName(state.players[id]))).join(', ')}${outgoing.length?` over ${outgoing.map(id=>esc(pName(state.players[id]))).join(', ')}`:''}, but its best modeled probability lift is only ${bestPositiveDelta.toFixed(1)} pp. That does not clear the current ${decisionThreshold.toFixed(1)} pp threshold, so the simulation treats it as a no-action tie.`)
      : 'Projection-optimal uses the same starter set as your current lineup.';
"""
if old not in html:
    raise SystemExit('Could not find simulation class/swap block')
html = html.replace(old, new, 1)

old_chips = """<span class=\"simulation-model-chip\">${esc(calibration.label)}</span>
<span class=\"simulation-model-chip\">12% SAME-TEAM SHARED FACTOR</span>
<span class=\"simulation-model-chip\">PREGAME ONLY</span>"""
new_chips = """<span class=\"simulation-model-chip\">${esc(calibration.label)}</span>
<span class=\"simulation-model-chip\">${esc(confidenceChip)}</span>
<span class=\"simulation-model-chip\">${esc(edgeChip)}</span>
<span class=\"simulation-model-chip\">12% SAME-TEAM SHARED FACTOR</span>
<span class=\"simulation-model-chip\">PREGAME ONLY</span>"""
if old_chips not in html:
    raise SystemExit('Could not find simulation chip block')
html = html.replace(old_chips, new_chips, 1)

old_note = "<div class=\"whyline\" style=\"margin-top:6px\"><b>Calibration note:</b> ${esc(calibration.note)} Treat small probability differences as noise rather than actionable edges.${medianReady&&adequateTeams.length<teams.length?` League-median simulation uses the ${adequateTeams.length} teams meeting the strict projection-coverage threshold, so that percentage is lower confidence.`:''}</div>"
new_note = "<div class=\"whyline\" style=\"margin-top:6px\"><b>Confidence guardrail:</b> ${esc(calibration.note)} Current lineup-change threshold: ${decisionThreshold.toFixed(1)} percentage points. Differences below that threshold are explicitly treated as a no-action tie rather than an edge.${medianReady&&adequateTeams.length<teams.length?` League-median simulation uses the ${adequateTeams.length} teams meeting the strict projection-coverage threshold, so that percentage is lower confidence.`:''}</div>"
if old_note not in html:
    raise SystemExit('Could not find calibration note block')
html = html.replace(old_note, new_note, 1)

index_path.write_text(html, encoding='utf-8')

changelog = changelog_path.read_text(encoding='utf-8')
entry = '''## v2.17.1 — Simulation Confidence Guardrails
**2026-09-16**

- Label simulation probabilities as `PROVISIONAL • LOW CONFIDENCE` while empirical calibration is still collecting instead of presenting early-season probabilities with false precision.
- Automatically upgrade confidence to `CALIBRATED • MED CONFIDENCE` once empirical position variance begins blending, and reserve `HIGH CONFIDENCE` for at least four completed calibration weeks with five position groups ready.
- Add an explicit simulation lineup-change threshold: 3.0 percentage points while confidence is low, 2.0 pp at medium confidence, and 1.5 pp at high confidence.
- Treat projection-optimal lineup probability changes below the active threshold as a `NO-ACTION TIE` rather than an actionable edge.
- If a projection-optimal lineup clears the active threshold, surface it as simulation support for review without allowing the simulator to override the separate Start/Sit consensus engine automatically.
- Avoid positive/green simulation styling solely from favorable probabilities while calibration confidence remains low; under-pressure outcomes can still show warning context.
- Preserve the 6,000-iteration pregame simulation, 12% same-team shared factor, empirical-calibration collection, projection coverage requirements, league-median modeling, and live-scoring guardrail.

'''
if '## v2.17.1 — Simulation Confidence Guardrails' not in changelog:
    marker = 'The project is currently in active beta development. Version numbers reflect iterative product updates rather than formal production releases.\n\n'
    if marker not in changelog:
        raise SystemExit('Could not find changelog insertion marker')
    changelog = changelog.replace(marker, marker + entry, 1)
    changelog_path.write_text(changelog, encoding='utf-8')

print('Applied v2.17.1 simulation confidence guardrails.')
