from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')


def one(old, new, label):
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 occurrence, found {count}')
    text = text.replace(old, new, 1)


one(
    'Multi-manager beta • in-season baselines + simulation • v2.15.3',
    'Multi-manager beta • lineup consensus + simulation • v2.16',
    'version subtitle',
)

one(
    'Weekly lineup, matchup, waiver, and roster-management command center. v2.15.3 isolates preseason draft strategy from the in-season weekly and trade models while preserving projections, simulation, and focused Weekly navigation.',
    'Weekly lineup, matchup, waiver, and roster-management command center. v2.16 adds a two-model Start/Sit consensus layer that cross-checks Weekly Outlook against league-scored projections without blending the two models into fake precision.',
    'weekly hero copy',
)

one(
    "Optimizes the selected week's legal starting lineup from your active Sleeper roster using the shared Weekly Outlook model. v2.15 adds a separate projection cross-check before projected points are allowed to drive the optimizer directly.",
    'Runs the shared Weekly Outlook optimizer and the league-scored projection optimizer side by side. Changes supported by both models are labeled consensus; disagreements are surfaced as review items instead of being silently blended into one score.',
    'start sit description',
)

one(
    """    const players=activeIds.map(id=>({
      id:String(id),
      p:state.players[String(id)],
      pos:normalizedFantasyPos(state.players[String(id)]),
      score:weeklyLineupScoreForId(id)
    })).filter(x=>x.p);""",
    """    const players=activeIds.map(id=>({
      id:String(id),
      p:state.players[String(id)],
      pos:normalizedFantasyPos(state.players[String(id)]),
      score:weeklyLineupScoreForId(id)
    })).filter(x=>x.p && playerUsableForRequiredStart(x.p));""",
    'outlook optimizer availability guard',
)

start = text.index('  function renderStartSit(ctx) {')
end = text.index('\n  function renderWeeklyRoster(ctx) {', start)
new_block = r'''  function renderStartSit(ctx) {
    const current=currentLineupAssignments(ctx);
    const optimal=optimizedLineup(ctx);

    const currentIds=new Set(current.filter(x=>x.id).map(x=>x.id));
    const optimalIds=new Set(optimal.filter(x=>x.id).map(x=>x.id));

    const incoming=optimal.filter(x=>x.id && !currentIds.has(x.id));
    const outgoing=current.filter(x=>x.id && !optimalIds.has(x.id));
    const emptySlots=optimal.filter(x=>!x.id);

    const currentScore=current.filter(x=>x.id).reduce((s,x)=>s+x.score,0);
    const optimalScore=optimal.filter(x=>x.id).reduce((s,x)=>s+x.score,0);
    const gap=Math.max(0,optimalScore-currentScore);

    const projectionOptimal=projectionOptimalLineup(ctx);
    const projectionOptimalIds=new Set(projectionOptimal.filter(x=>x?.id).map(x=>String(x.id)));
    const currentIdList=current.filter(x=>x.id).map(x=>String(x.id));
    const projectionCurrent=projectionTotalForIds(currentIdList);
    const projectionReady=(
      state.projectionByPlayer?.size>0 &&
      currentIdList.length>0 &&
      projectionCurrent.coverage>=0.80 &&
      projectionOptimalIds.size===currentIdList.length
    );
    const projectionIncoming=projectionReady
      ? projectionOptimal.filter(x=>x?.id && !currentIds.has(String(x.id)))
      : [];
    const projectionOutgoing=projectionReady
      ? current.filter(x=>x.id && !projectionOptimalIds.has(String(x.id)))
      : [];
    const consensusIncoming=incoming.filter(x=>projectionReady && projectionOptimalIds.has(String(x.id)));
    const modelAgreement=projectionReady
      ? [...optimalIds].filter(id=>projectionOptimalIds.has(String(id))).length
      : null;

    if(emptySlots.length) {
      setPill('lineupStatusPill',`${emptySlots.length} lineup slot${emptySlots.length===1?'':'s'} unfilled`,'warn');
    } else if(consensusIncoming.length) {
      setPill('lineupStatusPill',`${consensusIncoming.length} consensus change${consensusIncoming.length===1?'':'s'}`,'warn');
    } else if(incoming.length || projectionIncoming.length) {
      setPill('lineupStatusPill','Model split — review','warn');
    } else {
      setPill('lineupStatusPill','Current lineup supported','good');
    }

    const outlookDelta=optimalScore-currentScore;
    let projectionSummary='';
    if(projectionReady) {
      const outlookOptimalProjection=projectionTotalForIds(optimal.filter(x=>x.id).map(x=>String(x.id)));
      const projectionOptimalProjection=projectionTotalForIds(projectionOptimal.filter(x=>x?.id).map(x=>String(x.id)));
      projectionSummary=
        ` • projected ${projectionCurrent.total.toFixed(1)} current`+
        `${outlookOptimalProjection.coverage>=0.80?` / ${outlookOptimalProjection.total.toFixed(1)} Outlook-opt`:''}`+
        `${projectionOptimalProjection.coverage>=0.80?` / ${projectionOptimalProjection.total.toFixed(1)} projection-opt`:''}`+
        ` • models agree on ${modelAgreement}/${optimalIds.size} starters`;
    }

    $('weeklyLineupSummary').innerHTML=
      `<b>Week ${state.weeklyWeek} lineup consensus check:</b> `+
      `${incoming.length?`${incoming.length} Outlook change${incoming.length===1?'':'s'}`:'Outlook holds current starters'} `+
      `${projectionReady?`• ${projectionIncoming.length?`${projectionIncoming.length} projection change${projectionIncoming.length===1?'':'s'}`:'projection model holds current starters'}`:'• projection consensus unavailable'} `+
      `• Outlook total ${Math.round(currentScore)} → ${Math.round(optimalScore)}`+
      `${outlookDelta>0?` (+${Math.round(outlookDelta)})`:''}`+
      projectionSummary+
      `${leagueMedianAppliesForWeek(state.weeklyWeek)?' • league median matchup active':''}`;

    const rows=[];
    const outlookIncomingIds=new Set(incoming.map(x=>String(x.id)));

    for(const inc of incoming) {
      let out=outgoing
        .filter(x=>x.p && eligibleForLineupSlot(normalizedFantasyPos(x.p),inc.slot))
        .sort((a,b)=>a.score-b.score)[0];

      if(!out) out=[...outgoing].sort((a,b)=>a.score-b.score)[0]||null;

      const individualGap=out ? inc.score-out.score : inc.score;
      const conf=lineupConfidence(individualGap);
      const projectionSupports=projectionReady && projectionOptimalIds.has(String(inc.id));
      const incProj=projectedPointsForId(inc.id);
      const outProj=out?projectedPointsForId(out.id):null;
      const projectionEdge=Number.isFinite(incProj) && Number.isFinite(outProj) ? incProj-outProj : null;
      const action=projectionReady && !projectionSupports ? 'REVIEW' : 'START';
      const modelTag=!projectionReady
        ? 'OUTLOOK ONLY'
        : (projectionSupports?'MODEL AGREEMENT':'MODEL SPLIT');
      const modelCls=projectionReady && !projectionSupports?'warn':'good';

      rows.push(`<div class="waiver-row ${projectionReady&&!projectionSupports?'lineup-alert':'lineup-swap'}">
        <div class="waiver-rank"><span class="lineup-slot">${esc(inc.slot)}</span><b>${action==='START'?'↑':'?'}</b></div>
        <div>
          <b>${action} ${esc(pName(inc.p))} <span class="pos ${normalizedFantasyPos(inc.p)}">${normalizedFantasyPos(inc.p)}</span></b>
          <div class="meta">${out?`OVER ${esc(pName(out.p))} • `:''}${esc(inc.p.team||'FA')}${normalizedInjuryStatus(inc.p)?' • '+esc(normalizedInjuryStatus(inc.p)):''}</div>
          <div style="margin-top:4px"><span class="simulation-model-chip ${modelCls}">${modelTag}</span></div>
          <div class="whyline">${esc(weeklyOutlookWhyText(inc.p)||'No additional weekly context available')} • Outlook edge ${individualGap>=0?'+':''}${Math.round(individualGap)}${Number.isFinite(projectionEdge)?` • projection edge ${projectionEdge>=0?'+':''}${projectionEdge.toFixed(1)} pts`:''} • decision <span class="${conf.cls}">${projectionReady&&!projectionSupports?'REVIEW':conf.label}</span> • data ${esc(weeklyOutlookForPlayer(inc.p)?.confidence?.label||'LOW')}.</div>
        </div>
        <div class="value-badge">${Math.round(inc.score)}<div class="tiny">outlook</div></div>
      </div>`);
    }

    if(projectionReady) {
      for(const inc of projectionIncoming.filter(x=>!outlookIncomingIds.has(String(x.id)))) {
        let out=projectionOutgoing
          .filter(x=>x.p && eligibleForLineupSlot(normalizedFantasyPos(x.p),inc.slot))
          .sort((a,b)=>(projectedPointsForId(a.id)??999)-(projectedPointsForId(b.id)??999))[0];
        if(!out) out=projectionOutgoing[0]||null;
        const incProj=projectedPointsForId(inc.id);
        const outProj=out?projectedPointsForId(out.id):null;
        const projectionEdge=Number.isFinite(incProj)&&Number.isFinite(outProj)?incProj-outProj:null;
        const outlookEdge=out?weeklyLineupScoreForId(inc.id)-weeklyLineupScoreForId(out.id):null;

        rows.push(`<div class="waiver-row lineup-alert">
          <div class="waiver-rank"><span class="lineup-slot">${esc(inc.slot)}</span><b>?</b></div>
          <div>
            <b>REVIEW ${esc(pName(inc.p))} <span class="pos ${normalizedFantasyPos(inc.p)}">${normalizedFantasyPos(inc.p)}</span></b>
            <div class="meta">PROJECTION MODEL${out?` OVER ${esc(pName(out.p))}`:''} • ${esc(inc.p.team||'FA')}</div>
            <div style="margin-top:4px"><span class="simulation-model-chip warn">MODEL SPLIT</span></div>
            <div class="whyline">Projection-only lineup change${Number.isFinite(projectionEdge)?` • projection edge ${projectionEdge>=0?'+':''}${projectionEdge.toFixed(1)} pts`:''}${Number.isFinite(outlookEdge)?` • Outlook edge ${outlookEdge>=0?'+':''}${Math.round(outlookEdge)}`:''}. The two models disagree, so this is a review flag rather than an automatic start recommendation.</div>
          </div>
          <div class="value-badge">${Number.isFinite(incProj)?incProj.toFixed(1):'—'}<div class="tiny">proj</div></div>
        </div>`);
      }
    }

    for(const cur of current) {
      if(!cur.id || !cur.p) continue;
      const inj=normalizedInjuryStatus(cur.p);
      if(!inj) continue;
      if(['OUT','IR','PUP','NFI','DOUBTFUL'].some(x=>inj.startsWith(x))) {
        rows.push(`<div class="waiver-row lineup-alert">
          <div class="waiver-rank">!</div>
          <div><b>LINEUP ALERT: ${esc(pName(cur.p))} <span class="pos ${normalizedFantasyPos(cur.p)}">${normalizedFantasyPos(cur.p)}</span></b>
            <div class="meta">${esc(cur.slot)} • ${esc(inj)}</div>
            <div class="whyline">This player is excluded from both optimized lineups while the designation remains ${esc(inj)}. Re-run the optimizer after roster or injury updates.</div>
          </div>
        </div>`);
      }
    }

    if(!rows.length) {
      rows.push(`<div class="waiver-row lineup-hold">
        <div class="waiver-rank">✓</div>
        <div><b>HOLD CURRENT LINEUP</b>
          <div class="whyline">No bench player currently clears the Outlook optimizer, and ${projectionReady?'the league-scored projection optimizer agrees with the current starter set':'projection consensus is not available at sufficient coverage'}. Current workload, availability, game environment, weather, and automated news remain visible as context.</div>
        </div>
      </div>`);
    }

    $('weeklyStartSit').innerHTML=rows.join('');
    return {current,optimal,incoming,outgoing,currentScore,optimalScore,projectionOptimal,projectionReady,consensusIncoming};
  }
'''
text = text[:start] + new_block + text[end:]

one(
    "v2.15.2 adds a pregame Monte Carlo probability cross-check, but its position-level variance assumptions are still heuristic rather than calibrated from historical projection errors; live in-game win probability, an independent second projection feed, route participation, and richer red-zone opportunity remain future layers. v2.15.3 removes the Aug. 30 draft ECR and preseason news adjustments from Normal Weekly and Trade Intelligence baselines; those draft-era inputs remain isolated to Draft Day and immediate post-draft analysis.",
    "v2.15.2 adds a pregame Monte Carlo probability cross-check, but its position-level variance assumptions are still heuristic rather than calibrated from historical projection errors; live in-game win probability, an independent second projection feed, route participation, and richer red-zone opportunity remain future layers. v2.15.3 removes the Aug. 30 draft ECR and preseason news adjustments from Normal Weekly and Trade Intelligence baselines; those draft-era inputs remain isolated to Draft Day and immediate post-draft analysis. v2.16 keeps Weekly Outlook and league-scored projections as separate models, then surfaces agreement and disagreement directly in Start/Sit instead of mathematically blending unlike scores.",
    'beta caveat v216',
)

one(
    "v2.15.3 keeps the Aug. 29/30 half-PPR expert-consensus snapshot isolated to Draft Day and immediate post-draft analysis. Normal Weekly and Trade Intelligence use current Sleeper/search market rank as a lighter season-long anchor, then apply live role, usage, availability, current-news, game-context, projection, and roster-utility layers.",
    "v2.16 keeps the Aug. 29/30 half-PPR expert-consensus snapshot isolated to Draft Day and immediate post-draft analysis. Normal Weekly and Trade Intelligence use current Sleeper/search market rank as a lighter season-long anchor, while Start/Sit now cross-checks the Weekly Outlook optimizer against the independent league-scored projection optimizer and labels consensus versus model splits explicitly.",
    'footer v216',
)

if 'v2.16' not in text:
    raise SystemExit('v2.16 version text missing')
if '.filter(x=>x.p && playerUsableForRequiredStart(x.p));' not in text:
    raise SystemExit('availability guard missing from Outlook optimizer')
if 'MODEL AGREEMENT' not in text or 'MODEL SPLIT' not in text:
    raise SystemExit('consensus labels missing')

path.write_text(text, encoding='utf-8')

changelog = Path('CHANGELOG.md')
cl = changelog.read_text(encoding='utf-8')
if '## v2.16 — Lineup Consensus Engine' not in cl:
    entry = '''## v2.16 — Lineup Consensus Engine
**2026-09-15**

- Add a two-model Start/Sit consensus layer instead of mathematically blending Weekly Outlook scores with projected fantasy points.
- Run the existing Weekly Outlook optimizer and league-scored projection optimizer side by side for the selected week.
- Label lineup changes supported by both models as `MODEL AGREEMENT` and surface disagreements as `MODEL SPLIT` review items rather than automatic starts.
- Surface projection-only lineup changes inside Start/Sit so users no longer have to reconcile a separate projection card manually.
- Show projected-point edges next to Outlook edges when both compared players have current-week projections.
- Add lineup-summary context for current projected points, Outlook-optimal projected points, projection-optimal projected points, and starter-set agreement when projection coverage is sufficient.
- Exclude OUT / IR / PUP / NFI / DOUBTFUL players from the Weekly Outlook optimized lineup, matching the existing positional-coverage and projection-optimizer availability guardrails.
- Keep Weekly Outlook, projection points, and simulation probabilities as distinct concepts; no conversion of heuristic Outlook scores into fantasy points or win probability is introduced.
- Preserve v2.15.3 in-season baseline cleanup, waiver, trade, league-median, simulation, usage, weather, news, and roster-management behavior.

'''
    marker = '## v2.15.3 — In-Season Baseline Cleanup'
    if marker not in cl:
        raise SystemExit('v2.15.3 changelog marker not found')
    cl = cl.replace(marker, entry + marker, 1)
    changelog.write_text(cl, encoding='utf-8')
