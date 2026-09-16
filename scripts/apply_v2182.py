from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
index_path = ROOT / 'index.html'
changelog_path = ROOT / 'CHANGELOG.md'

html = index_path.read_text(encoding='utf-8')

html = html.replace('Multi-manager beta • week-aware management • v2.18.1', 'Multi-manager beta • week-aware management • v2.18.2', 1)
html = html.replace(
    'Weekly lineup, matchup, waiver, and roster-management command center. v2.18.1 gives Streamer Finder its own QB/TE/K/DEF candidate pool and a direct waiver-review handoff while preserving conservative thresholds and regression protection.',
    'Weekly lineup, matchup, waiver, and roster-management command center. v2.18.2 clarifies Streamer Finder hold decisions by naming the incumbent and separating threshold misses from supporting-model conflicts.',
    1,
)

old_decision = '''    if(projectionClears && outlookNotStronglyAgainst && candidateHealthy) {\n      return {pos,status:'STREAM',kind:'strong',threshold,current:currentSnap,best,projectionEdge,outlookEdge,reason:`Projection edge clears the ${threshold.toFixed(1)}-point streaming threshold without a strong Outlook or availability conflict.`};\n    }\n\n    const edgeText=Number.isFinite(projectionEdge)?`${projectionEdge>=0?'+':''}${projectionEdge.toFixed(1)} projected pts`:'projection edge unavailable';\n    return {pos,status:'HOLD',kind:projectionEdge>0?'watch':'',threshold,current:currentSnap,best,projectionEdge,outlookEdge,reason:`NO-ACTION STREAMING EDGE: ${edgeText}; requires +${threshold.toFixed(1)} with supporting context before recommending a one-week move.`};'''
new_decision = '''    if(projectionClears && !outlookNotStronglyAgainst) {\n      const outlookAgainst=Math.abs(Number(outlookEdge)||0);\n      return {\n        pos,status:'HOLD',kind:'watch',threshold,current:currentSnap,best,projectionEdge,outlookEdge,reasonCode:'MODEL CONFLICT',\n        reason:`Projection clears the +${threshold.toFixed(1)}-point streaming threshold, but Weekly Outlook favors ${pName(currentSnap.p)} by ${Math.round(outlookAgainst)} outlook points. HOLD the incumbent rather than stream on projection alone.`\n      };\n    }\n    if(projectionClears && outlookNotStronglyAgainst && !candidateHealthy) {\n      return {\n        pos,status:'HOLD',kind:'watch',threshold,current:currentSnap,best,projectionEdge,outlookEdge,reasonCode:'AVAILABILITY CONFLICT',\n        reason:`Projection clears the +${threshold.toFixed(1)}-point streaming threshold, but ${pName(best.snap.p)} carries a meaningful availability penalty. HOLD the incumbent unless that concern clears.`\n      };\n    }\n    if(projectionClears && outlookNotStronglyAgainst && candidateHealthy) {\n      return {pos,status:'STREAM',kind:'strong',threshold,current:currentSnap,best,projectionEdge,outlookEdge,reasonCode:null,reason:`Projection edge clears the ${threshold.toFixed(1)}-point streaming threshold without a strong Outlook or availability conflict.`};\n    }\n\n    const edgeText=Number.isFinite(projectionEdge)?`${projectionEdge>=0?'+':''}${projectionEdge.toFixed(1)} projected pts`:'projection edge unavailable';\n    return {pos,status:'HOLD',kind:projectionEdge>0?'watch':'',threshold,current:currentSnap,best,projectionEdge,outlookEdge,reasonCode:'NO-ACTION EDGE',reason:`NO-ACTION STREAMING EDGE: ${edgeText}; projection does not clear the +${threshold.toFixed(1)}-point threshold with supporting context, so hold the incumbent.`};'''
if old_decision not in html:
    raise SystemExit('Could not find streamer decision block')
html = html.replace(old_decision, new_decision, 1)

old_render = '''      const meta=r.best\n        ? `${esc(currentName)} ${currentProj} proj → ${esc(bestName)} ${bestProj} proj • projection edge ${projEdge} • Outlook edge ${outlookEdge}${Number.isFinite(gameEdge)?` • game-env ${gameEdge>=0?'+':''}${gameEdge.toFixed(1)}`:''}`\n        : `${esc(currentName)} ${currentProj} proj • no usable available comparison`;\n      return `<div class="waiver-row ${cls}">\n        <div class="waiver-rank">${esc(r.pos)}</div>\n        <div>\n          <b>${esc(r.status)}${r.best?` ${esc(bestName)} <span class="pos ${r.pos}">${r.pos}</span>`:''}</b>\n          <div class="meta">${meta}</div>\n          <div class="whyline">${esc(r.reason)}${r.status==='STREAM'?' Roster-space decisions stay in Drop Review/Waiver Planner; this card never assumes the current starter should be dropped.':''}</div>'''
new_render = '''      const meta=r.best\n        ? `${esc(currentName)} ${currentProj} proj → ${esc(bestName)} ${bestProj} proj • projection edge ${projEdge} • Outlook edge ${outlookEdge}${Number.isFinite(gameEdge)?` • game-env ${gameEdge>=0?'+':''}${gameEdge.toFixed(1)}`:''}`\n        : `${esc(currentName)} ${currentProj} proj • no usable available comparison`;\n      const headlineName=r.status==='HOLD'?currentName:bestName;\n      const decisionChip=r.reasonCode?`<span class="claim-chip ${r.reasonCode==='MODEL CONFLICT'?'warn':''}">${esc(r.reasonCode)}</span> `:'';\n      return `<div class="waiver-row ${cls}">\n        <div class="waiver-rank">${esc(r.pos)}</div>\n        <div>\n          <b>${esc(r.status)}${headlineName&&headlineName!=='none'?` ${esc(headlineName)} <span class="pos ${r.pos}">${r.pos}</span>`:''}</b>\n          <div class="meta">${meta}</div>\n          <div class="whyline">${decisionChip}${esc(r.reason)}${r.status==='STREAM'?' Roster-space decisions stay in Drop Review/Waiver Planner; this card never assumes the current starter should be dropped.':''}</div>'''
if old_render not in html:
    raise SystemExit('Could not find streamer render block')
html = html.replace(old_render, new_render, 1)

index_path.write_text(html, encoding='utf-8')

changelog = changelog_path.read_text(encoding='utf-8')
entry = '''## v2.18.2 — Streamer Decision Clarity\n**2026-09-16**\n\n- Make `HOLD` headlines name the incumbent starter being kept rather than the free-agent comparison, so examples read `HOLD Joe Burrow` and `HOLD Jake Bates`.\n- Separate true projection-threshold misses from cases where the projection clears the streaming threshold but Weekly Outlook strongly disagrees.\n- Label projection-vs-Outlook disagreements as `MODEL CONFLICT` and explain which model favors the incumbent instead of incorrectly saying the projection still needs to clear the threshold.\n- Add an `AVAILABILITY CONFLICT` hold reason when the projection clears the threshold but the available option carries a meaningful availability penalty.\n- Keep `STREAM` headlines focused on the incoming free agent and preserve the existing Review waiver move handoff.\n- Extend the permanent Weekly regression contract to protect incumbent HOLD naming and explicit model-conflict handling.\n\n'''
if '## v2.18.2 — Streamer Decision Clarity' not in changelog:
    marker = 'The project is currently in active beta development. Version numbers reflect iterative product updates rather than formal production releases.\n\n'
    if marker not in changelog:
        raise SystemExit('Could not find changelog insertion marker')
    changelog = changelog.replace(marker, marker + entry, 1)
    changelog_path.write_text(changelog, encoding='utf-8')

print('Applied v2.18.2 Streamer Decision Clarity.')
