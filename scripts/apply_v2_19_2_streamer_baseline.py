#!/usr/bin/env python3
from pathlib import Path

index_path = Path('index.html')
source = index_path.read_text(encoding='utf-8')

starter_marker = """  function streamingStarterForPosition(ctx,pos) {
    const starters=(ctx.my?.starters||[]).map(String).filter(id=>id&&id!=='0');
    for(const id of starters) {
      const p=state.players[id];
      if(p && normalizedFantasyPos(p)===pos) return {id,p};
    }
    return null;
  }

"""

baseline_helper = """  function streamingStarterBaselineForPosition(ctx,pos) {
    const submitted=streamingStarterForPosition(ctx,pos);
    const score=x=>Number.isFinite(Number(x?.score))?Number(x.score):-999;
    const optimized=(optimizedLineup(ctx)||[])
      .filter(x=>x?.id && x.p && normalizedFantasyPos(x.p)===pos)
      .sort((a,b)=>score(a)-score(b));
    const chosen=optimized[0]||null;

    if(chosen) {
      return {
        baseline:{id:String(chosen.id),p:chosen.p},
        submitted,
        source:'OPTIMIZED'
      };
    }
    return {baseline:submitted,submitted,source:'SUBMITTED'};
  }

"""

if 'function streamingStarterBaselineForPosition(' not in source:
    if starter_marker not in source:
        raise SystemExit('streaming starter marker not found')
    source = source.replace(starter_marker, starter_marker + baseline_helper, 1)

rec_start = source.index('  function streamingRecommendationForPosition(ctx,pool,pos) {')
rec_end = source.index('\n\n  function streamerWaiverReviewForRecommendation', rec_start)
new_recommendation = r"""  function streamingRecommendationForPosition(ctx,pool,pos) {
    const baselineInfo=streamingStarterBaselineForPosition(ctx,pos);
    const current=baselineInfo.baseline;
    const submittedCurrent=baselineInfo.submitted;
    const currentSnap=current?streamingPlayerSnapshot(current.id,current.p):null;
    const submittedSnap=submittedCurrent?streamingPlayerSnapshot(submittedCurrent.id,submittedCurrent.p):null;
    const baselineMeta={submittedCurrent:submittedSnap,baselineSource:baselineInfo.source};
    const candidates=(pool||[])
      .filter(b=>b.pos===pos && b.player_id && b.pdata)
      .map(b=>({b,snap:streamingPlayerSnapshot(b.player_id,b.pdata)}))
      .filter(x=>x.snap?.usable && x.snap.availability>=-6)
      .sort((a,b)=>{
        const ap=Number.isFinite(a.snap.projection)?a.snap.projection:-999;
        const bp=Number.isFinite(b.snap.projection)?b.snap.projection:-999;
        if(bp!==ap) return bp-ap;
        const ao=Number.isFinite(a.snap.outlook)?a.snap.outlook:-999;
        const bo=Number.isFinite(b.snap.outlook)?b.snap.outlook:-999;
        if(bo!==ao) return bo-ao;
        return (Number(b.b.weeklyValue)||0)-(Number(a.b.weeklyValue)||0);
      });
    const best=candidates[0]||null;
    const threshold=streamingThresholdForPosition(pos);

    if(!currentSnap) {
      if(!best) return {pos,status:'NO STARTER',kind:'warn',threshold,current:null,best:null,projectionEdge:null,outlookEdge:null,...baselineMeta,reason:`No current ${pos} starter and no usable available replacement was found.`};
      return {pos,status:'STREAM',kind:'strong',threshold,current:null,best,projectionEdge:null,outlookEdge:null,...baselineMeta,reason:`No current ${pos} starter is set. Add ${pName(best.snap.p)} to restore required-position coverage; use Drop Review/Waiver Planner for the roster spot.`};
    }

    if(!best) return {pos,status:'HOLD',kind:'',threshold,current:currentSnap,best:null,projectionEdge:null,outlookEdge:null,...baselineMeta,reason:`No usable available ${pos} clears the basic availability screen.`};

    const projectionEdge=Number.isFinite(best.snap.projection)&&Number.isFinite(currentSnap.projection)
      ? best.snap.projection-currentSnap.projection:null;
    const outlookEdge=Number.isFinite(best.snap.outlook)&&Number.isFinite(currentSnap.outlook)
      ? best.snap.outlook-currentSnap.outlook:null;
    const currentUnavailable=!currentSnap.usable;
    const projectionClears=Number.isFinite(projectionEdge) && projectionEdge>=threshold;
    const outlookNotStronglyAgainst=!Number.isFinite(outlookEdge) || outlookEdge>=-8;
    const candidateHealthy=best.snap.availability>=-4;

    if(currentUnavailable && best.snap.usable) {
      return {pos,status:'STREAM',kind:'strong',threshold,current:currentSnap,best,projectionEdge,outlookEdge,...baselineMeta,reason:`Your optimized ${pos} baseline is not usable for required-position planning. ${pName(best.snap.p)} is the best available coverage option.`};
    }
    if(projectionClears && !outlookNotStronglyAgainst) {
      const outlookAgainst=Math.abs(Number(outlookEdge)||0);
      return {
        pos,status:'HOLD',kind:'watch',threshold,current:currentSnap,best,projectionEdge,outlookEdge,...baselineMeta,reasonCode:'MODEL CONFLICT',
        reason:`Projection clears the +${threshold.toFixed(1)}-point streaming threshold, but Weekly Outlook favors ${pName(currentSnap.p)} by ${Math.round(outlookAgainst)} outlook points. HOLD the optimized incumbent rather than stream on projection alone.`
      };
    }
    if(projectionClears && outlookNotStronglyAgainst && !candidateHealthy) {
      return {
        pos,status:'HOLD',kind:'watch',threshold,current:currentSnap,best,projectionEdge,outlookEdge,...baselineMeta,reasonCode:'AVAILABILITY CONFLICT',
        reason:`Projection clears the +${threshold.toFixed(1)}-point streaming threshold, but ${pName(best.snap.p)} carries a meaningful availability penalty. HOLD the optimized incumbent unless that concern clears.`
      };
    }
    if(projectionClears && outlookNotStronglyAgainst && candidateHealthy) {
      return {pos,status:'STREAM',kind:'strong',threshold,current:currentSnap,best,projectionEdge,outlookEdge,...baselineMeta,reasonCode:null,reason:`Projection edge clears the ${threshold.toFixed(1)}-point streaming threshold against the optimized incumbent without a strong Outlook or availability conflict.`};
    }

    const edgeText=Number.isFinite(projectionEdge)?`${projectionEdge>=0?'+':''}${projectionEdge.toFixed(1)} projected pts`:'projection edge unavailable';
    return {pos,status:'HOLD',kind:projectionEdge>0?'watch':'',threshold,current:currentSnap,best,projectionEdge,outlookEdge,...baselineMeta,reasonCode:'NO-ACTION EDGE',reason:`NO-ACTION STREAMING EDGE: ${edgeText}; projection does not clear the +${threshold.toFixed(1)}-point threshold against the optimized incumbent with supporting context, so hold.`};
  }"""
source = source[:rec_start] + new_recommendation + source[rec_end:]

render_start = source.index('  function renderStreamerFinder(ctx) {')
render_end = source.index('\n\n  function renderTradeIntelligence(ctx)', render_start)
new_render = r"""  function renderStreamerFinder(ctx) {
    const pool=streamingCandidatePool(ctx);
    const positions=['QB','TE','K','DEF'];
    const rows=positions.map(pos=>streamingRecommendationForPosition(ctx,pool,pos));
    const streams=rows.filter(r=>r.status==='STREAM').length;
    setPill('streamerPill',streams?`${streams} stream${streams===1?'':'s'} to review`:'No streaming move',streams?'warn':'good');

    $('weeklyStreamers').innerHTML=rows.map((r,index)=>{
      const currentName=r.current?pName(r.current.p):'none';
      const submittedName=r.submittedCurrent?pName(r.submittedCurrent.p):'none';
      const bestName=r.best?pName(r.best.snap.p):'none';
      const currentProj=Number.isFinite(r.current?.projection)?r.current.projection.toFixed(1):'—';
      const bestProj=Number.isFinite(r.best?.snap?.projection)?r.best.snap.projection.toFixed(1):'—';
      const projEdge=Number.isFinite(r.projectionEdge)?`${r.projectionEdge>=0?'+':''}${r.projectionEdge.toFixed(1)}`:'—';
      const outlookEdge=Number.isFinite(r.outlookEdge)?`${r.outlookEdge>=0?'+':''}${Math.round(r.outlookEdge)}`:'—';
      const gameEdge=Number.isFinite(r.best?.snap?.game)&&Number.isFinite(r.current?.game)?r.best.snap.game-r.current.game:null;
      const cls=r.kind==='strong'?'strong':(r.kind==='watch'?'watch':'');
      const baselineContext=r.baselineSource==='OPTIMIZED' && submittedName!=='none' && submittedName!==currentName
        ? `optimized baseline; Sleeper currently starts ${submittedName}`
        : '';
      const meta=r.best
        ? `${esc(currentName)} ${currentProj} proj → ${esc(bestName)} ${bestProj} proj • projection edge ${projEdge} • Outlook edge ${outlookEdge}${Number.isFinite(gameEdge)?` • game-env ${gameEdge>=0?'+':''}${gameEdge.toFixed(1)}`:''}${baselineContext?` • ${esc(baselineContext)}`:''}`
        : `${esc(currentName)} ${currentProj} proj • no usable available comparison${baselineContext?` • ${esc(baselineContext)}`:''}`;
      const headlineName=r.status==='HOLD'?currentName:bestName;
      const decisionChip=r.reasonCode?`<span class="claim-chip ${r.reasonCode==='MODEL CONFLICT'?'warn':''}">${esc(r.reasonCode)}</span> `:'';
      return `<div class="waiver-row ${cls}">
        <div class="waiver-rank">${esc(r.pos)}</div>
        <div>
          <b>${esc(r.status)}${headlineName&&headlineName!=='none'?` ${esc(headlineName)} <span class="pos ${r.pos}">${r.pos}</span>`:''}</b>
          <div class="meta">${meta}</div>
          <div class="whyline">${decisionChip}${esc(r.reason)}${r.status==='STREAM'?' Roster-space decisions stay in Drop Review/Waiver Planner; this card never assumes the optimized incumbent should be dropped.':''}</div>
          ${r.status==='STREAM'?`<button class="ghost streamerWaiverBtn" type="button" data-streamer-index="${index}" style="margin-top:7px;min-height:34px;padding:6px 9px">Review waiver move</button>`:''}
        </div>
        <div class="value-badge">${Number.isFinite(r.best?.snap?.projection)?r.best.snap.projection.toFixed(1):'—'}</div>
      </div>`;
    }).join('');
    document.querySelectorAll('.streamerWaiverBtn').forEach(btn=>btn.addEventListener('click',()=>{
      const index=Number(btn.dataset.streamerIndex);
      if(!Number.isInteger(index) || !rows[index]) return;
      reviewStreamerWaiverMove(ctx,rows[index]);
    }));
    return rows;
  }"""
source = source[:render_start] + new_render + source[render_end:]

index_path.write_text(source, encoding='utf-8')

changelog_path = Path('CHANGELOG.md')
changelog = changelog_path.read_text(encoding='utf-8')
entry = """## v2.19.2 — Optimized Streamer Finder Baseline
**2026-09-17**

- Compare QB/TE/K/DEF streaming candidates against the app's optimized same-position starter instead of blindly using the currently submitted Sleeper starter.
- Preserve the submitted Sleeper starter as visible context when it differs from the optimized baseline, making stale lineup state obvious rather than silently driving the streaming math.
- Fall back to the submitted starter when the optimizer cannot supply a usable same-position baseline.
- Keep transaction routing aligned with the optimized incumbent so Streamer Finder, Start/Sit, Drop Review, and Move Priority do not disagree about which player a streamer would actually replace.
- Add a permanent regression for the Bowers/Mayer/Schultz case: Schultz beating submitted starter Mayer is not actionable when optimized starter Bowers remains the stronger TE baseline.

"""
if '## v2.19.2 — Optimized Streamer Finder Baseline' not in changelog:
    marker = '## v2.19.1 — Position-Aware Transaction Routing\n'
    if marker not in changelog:
        raise SystemExit('v2.19.1 changelog marker not found')
    changelog = changelog.replace(marker, entry + marker, 1)
    changelog_path.write_text(changelog, encoding='utf-8')
