from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
index_path = ROOT / 'index.html'
changelog_path = ROOT / 'CHANGELOG.md'

html = index_path.read_text(encoding='utf-8')

# Version + Weekly hero copy.
html = html.replace('Multi-manager beta • week-aware management • v2.17.3', 'Multi-manager beta • week-aware management • v2.18', 1)
html = html.replace(
    'Weekly lineup, matchup, waiver, and roster-management command center. v2.17.3 adds automated Weekly regression contracts and Sleeper integration checks while preserving simulation-confidence guardrails, calibration, lineup consensus, median strategy, and reliable usage.',
    'Weekly lineup, matchup, waiver, and roster-management command center. v2.18 adds conservative one-week streaming recommendations for QB, TE, K, and DEF while preserving regression protection, lineup consensus, calibration, median strategy, and reliable usage.',
    1,
)

# Add Streamer Finder card immediately before Trade Intelligence.
trade_card = '''      <div class="card" style="margin-top:12px">\n        <div class="weekly-section-head">\n          <div>\n            <h3>Trade Intelligence</h3>'''
streamer_card = '''      <div class="card" style="margin-top:12px">\n        <div class="weekly-section-head">\n          <div>\n            <h3>Streamer Finder</h3>\n            <div class="tiny">One-week QB, TE, K, and DEF decisions. Compares your current starter with available options using league-scored projections first, then Weekly Outlook, game environment, and availability as supporting context. Small edges are treated as holds.</div>\n          </div>\n          <span class="pill" id="streamerPill">Streamers —</span>\n        </div>\n        <div id="weeklyStreamers" class="weekly-table"><div class="tiny">Run a weekly check.</div></div>\n      </div>\n\n'''
if 'id="weeklyStreamers"' not in html:
    if trade_card not in html:
        raise SystemExit('Could not find Trade Intelligence card anchor')
    html = html.replace(trade_card, streamer_card + trade_card, 1)

# Put Streamer Finder in the Waivers sub-tab.
old_waivers = "waivers:['weeklyAdds','weeklyDrops','weeklyMoves','weeklyClaims','postDraftScanCard'],"
new_waivers = "waivers:['weeklyAdds','weeklyDrops','weeklyMoves','weeklyClaims','weeklyStreamers','postDraftScanCard'],"
if old_waivers in html:
    html = html.replace(old_waivers, new_waivers, 1)
elif new_waivers not in html:
    raise SystemExit('Could not find Waivers panel assignment')

# Add conservative streaming logic before Trade Intelligence.
marker = '  function renderTradeIntelligence(ctx) {'
if 'function streamingRecommendationForPosition(ctx,pool,pos)' not in html:
    if marker not in html:
        raise SystemExit('Could not find Trade Intelligence function anchor')
    streamer_logic = r'''  function streamingThresholdForPosition(pos) {
    return ({QB:2.0,TE:1.5,K:1.5,DEF:2.0})[pos]||2.0;
  }

  function streamingStarterForPosition(ctx,pos) {
    const starters=(ctx.my?.starters||[]).map(String).filter(id=>id&&id!=='0');
    for(const id of starters) {
      const p=state.players[id];
      if(p && normalizedFantasyPos(p)===pos) return {id,p};
    }
    return null;
  }

  function streamingPlayerSnapshot(id,p) {
    if(!p) return null;
    const outlook=weeklyOutlookForPlayer(p);
    const projection=projectedPointsForId(id);
    const availability=availabilityAdjustmentForPlayer(p);
    const game=gameEnvAdjustmentForPlayer(p);
    return {
      id:String(id),p,
      projection:Number.isFinite(projection)?projection:null,
      outlook:Number.isFinite(Number(outlook?.score))?Number(outlook.score):null,
      availability:Number.isFinite(Number(availability))?Number(availability):0,
      game:Number.isFinite(Number(game))?Number(game):0,
      usable:playerUsableForRequiredStart(p)
    };
  }

  function streamingRecommendationForPosition(ctx,pool,pos) {
    const current=streamingStarterForPosition(ctx,pos);
    const currentSnap=current?streamingPlayerSnapshot(current.id,current.p):null;
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
      if(!best) return {pos,status:'NO STARTER',kind:'warn',threshold,current:null,best:null,projectionEdge:null,outlookEdge:null,reason:`No current ${pos} starter and no usable available replacement was found.`};
      return {pos,status:'STREAM',kind:'strong',threshold,current:null,best,projectionEdge:null,outlookEdge:null,reason:`No current ${pos} starter is set. Add ${pName(best.snap.p)} to restore required-position coverage; use Drop Review/Waiver Planner for the roster spot.`};
    }

    if(!best) return {pos,status:'HOLD',kind:'',threshold,current:currentSnap,best:null,projectionEdge:null,outlookEdge:null,reason:`No usable available ${pos} clears the basic availability screen.`};

    const projectionEdge=Number.isFinite(best.snap.projection)&&Number.isFinite(currentSnap.projection)
      ? best.snap.projection-currentSnap.projection:null;
    const outlookEdge=Number.isFinite(best.snap.outlook)&&Number.isFinite(currentSnap.outlook)
      ? best.snap.outlook-currentSnap.outlook:null;
    const currentUnavailable=!currentSnap.usable;
    const projectionClears=Number.isFinite(projectionEdge) && projectionEdge>=threshold;
    const outlookNotStronglyAgainst=!Number.isFinite(outlookEdge) || outlookEdge>=-8;
    const candidateHealthy=best.snap.availability>=-4;

    if(currentUnavailable && best.snap.usable) {
      return {pos,status:'STREAM',kind:'strong',threshold,current:currentSnap,best,projectionEdge,outlookEdge,reason:`Your current ${pos} starter is not usable for required-position planning. ${pName(best.snap.p)} is the best available coverage option.`};
    }
    if(projectionClears && outlookNotStronglyAgainst && candidateHealthy) {
      return {pos,status:'STREAM',kind:'strong',threshold,current:currentSnap,best,projectionEdge,outlookEdge,reason:`Projection edge clears the ${threshold.toFixed(1)}-point streaming threshold without a strong Outlook or availability conflict.`};
    }

    const edgeText=Number.isFinite(projectionEdge)?`${projectionEdge>=0?'+':''}${projectionEdge.toFixed(1)} projected pts`:'projection edge unavailable';
    return {pos,status:'HOLD',kind:projectionEdge>0?'watch':'',threshold,current:currentSnap,best,projectionEdge,outlookEdge,reason:`NO-ACTION STREAMING EDGE: ${edgeText}; requires +${threshold.toFixed(1)} with supporting context before recommending a one-week move.`};
  }

  function renderStreamerFinder(ctx,pool) {
    const positions=['QB','TE','K','DEF'];
    const rows=positions.map(pos=>streamingRecommendationForPosition(ctx,pool,pos));
    const streams=rows.filter(r=>r.status==='STREAM').length;
    setPill('streamerPill',streams?`${streams} stream${streams===1?'':'s'} to review`:'No streaming move',streams?'warn':'good');

    $('weeklyStreamers').innerHTML=rows.map(r=>{
      const currentName=r.current?pName(r.current.p):'none';
      const bestName=r.best?pName(r.best.snap.p):'none';
      const currentProj=Number.isFinite(r.current?.projection)?r.current.projection.toFixed(1):'—';
      const bestProj=Number.isFinite(r.best?.snap?.projection)?r.best.snap.projection.toFixed(1):'—';
      const projEdge=Number.isFinite(r.projectionEdge)?`${r.projectionEdge>=0?'+':''}${r.projectionEdge.toFixed(1)}`:'—';
      const outlookEdge=Number.isFinite(r.outlookEdge)?`${r.outlookEdge>=0?'+':''}${Math.round(r.outlookEdge)}`:'—';
      const gameEdge=Number.isFinite(r.best?.snap?.game)&&Number.isFinite(r.current?.game)?r.best.snap.game-r.current.game:null;
      const cls=r.kind==='strong'?'strong':(r.kind==='watch'?'watch':'');
      const meta=r.best
        ? `${esc(currentName)} ${currentProj} proj → ${esc(bestName)} ${bestProj} proj • projection edge ${projEdge} • Outlook edge ${outlookEdge}${Number.isFinite(gameEdge)?` • game-env ${gameEdge>=0?'+':''}${gameEdge.toFixed(1)}`:''}`
        : `${esc(currentName)} ${currentProj} proj • no usable available comparison`;
      return `<div class="waiver-row ${cls}">
        <div class="waiver-rank">${esc(r.pos)}</div>
        <div>
          <b>${esc(r.status)}${r.best?` ${esc(bestName)} <span class="pos ${r.pos}">${r.pos}</span>`:''}</b>
          <div class="meta">${meta}</div>
          <div class="whyline">${esc(r.reason)}${r.status==='STREAM'?' Roster-space decisions stay in Drop Review/Waiver Planner; this card never assumes the current starter should be dropped.':''}</div>
        </div>
        <div class="value-badge">${Number.isFinite(r.best?.snap?.projection)?r.best.snap.projection.toFixed(1):'—'}</div>
      </div>`;
    }).join('');
    return rows;
  }

'''
    html = html.replace(marker, streamer_logic + marker, 1)

# Add Streamer Finder to the Weekly Check pipeline after the shared FA pool exists.
old_pipeline = '      const pool=renderWeeklyAdds(ctx);\n      renderNewsPanel(ctx,pool);'
new_pipeline = '      const pool=renderWeeklyAdds(ctx);\n      renderStreamerFinder(ctx,pool);\n      renderNewsPanel(ctx,pool);'
if old_pipeline in html:
    html = html.replace(old_pipeline, new_pipeline, 1)
elif 'renderStreamerFinder(ctx,pool);' not in html:
    raise SystemExit('Could not find Weekly Adds pipeline anchor')

index_path.write_text(html, encoding='utf-8')

changelog = changelog_path.read_text(encoding='utf-8')
entry = '''## v2.18 — Streamer Finder\n**2026-09-16**\n\n- Add a dedicated Waivers-tab Streamer Finder for one-week QB, TE, K, and DEF decisions; RB/WR remain in the normal waiver/add-drop engine.\n- Compare the current starter with the strongest usable available option using league-scored projected points as the primary decision signal, with Weekly Outlook, game environment, and availability as supporting context.\n- Use conservative position thresholds (QB/DEF +2.0 projected points; TE/K +1.5) and label smaller apparent gains as `NO-ACTION STREAMING EDGE` rather than recommending churn.\n- Prevent players with meaningful availability penalties from becoming automatic stream recommendations, and require Outlook not to strongly contradict a projection-led move.\n- Treat a missing/unusable required-position starter as a coverage case, while keeping roster-space/drop decisions in the existing Drop Review and Waiver Planner instead of assuming the incumbent starter should be cut.\n- Add Streamer Finder to the Waivers sub-navigation and the permanent Weekly regression contract.\n\n'''
if '## v2.18 — Streamer Finder' not in changelog:
    changelog_marker = 'The project is currently in active beta development. Version numbers reflect iterative product updates rather than formal production releases.\n\n'
    if changelog_marker not in changelog:
        raise SystemExit('Could not find changelog insertion marker')
    changelog = changelog.replace(changelog_marker, changelog_marker + entry, 1)
    changelog_path.write_text(changelog, encoding='utf-8')

print('Applied v2.18 Streamer Finder.')
