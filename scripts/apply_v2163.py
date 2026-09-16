from pathlib import Path
import re

index_path = Path('index.html')
changelog_path = Path('CHANGELOG.md')
text = index_path.read_text(encoding='utf-8')

# Bump the visible app version only in the application file.
text = text.replace('v2.16.2', 'v2.16.3')

new_median = r'''  function renderLeagueMedian(matchups,ctx,simulation=null) {
    const configured=leagueMedianConfigured();
    if(!configured) {
      setPill('medianPill','Median OFF','');
      $('weeklyMedian').innerHTML='<div class="tiny">This league does not have Sleeper league-median scoring enabled.</div>';
      return null;
    }

    if(!leagueMedianAppliesForWeek(state.weeklyWeek)) {
      setPill('medianPill','Configured • playoffs','warn');
      $('weeklyMedian').innerHTML='<div class="notice">League-median scoring is configured for the regular season, but it does not apply to this playoff week.</div>';
      return null;
    }

    const snap=leagueMedianSnapshot(matchups);
    setPill('medianPill','Median matchup ON','good');
    if(!snap) {
      $('weeklyMedian').innerHTML='<div class="tiny">Median rule detected, but weekly matchup scores are not populated yet.</div>';
      return null;
    }

    const status=!snap.anyScoring
      ? {label:'PREGAME',cls:'median-neutral',detail:'All league scores are still 0.00.'}
      : snap.margin>0
        ? {label:'ABOVE MEDIAN',cls:'median-high',detail:`Currently +${snap.margin.toFixed(2)} above the live median.`}
        : snap.margin<0
          ? {label:'BELOW MEDIAN',cls:'median-low',detail:`Currently ${snap.margin.toFixed(2)} below the live median.`}
          : {label:'TIED WITH MEDIAN',cls:'median-neutral',detail:'Currently exactly on the live median.'};

    const projected=projectedLeagueMedian(matchups);
    const projectedMedian=Number.isFinite(projected?.median)?projected.median:null;
    const myProjected=projectionTotalForIds(ctx.my?.starters||[]);
    const myProjectionReady=myProjected.slots>0 && myProjected.coverage>=0.70;
    const simReady=Number.isFinite(simulation?.medianPct);
    const rankText=snap.anyScoring?`${snap.rank}/${snap.teams.length}`:`—/${snap.teams.length}`;

    let forecast='';
    if(!snap.anyScoring && (myProjectionReady || Number.isFinite(projectedMedian) || simReady)) {
      forecast=`
        <div class="tiny labelish" style="margin-top:10px">PREGAME MEDIAN FORECAST</div>
        <div class="median-grid">
          <div class="median-stat"><div class="k">Your starter projection</div><div class="v">${myProjectionReady?myProjected.total.toFixed(1):'—'}</div></div>
          <div class="median-stat"><div class="k">Projected league median</div><div class="v">${Number.isFinite(projectedMedian)?projectedMedian.toFixed(1):'—'}</div></div>
          <div class="median-stat"><div class="k">Beat league median</div><div class="v">${simReady?simulation.medianPct.toFixed(1)+'%':'—'}</div></div>
        </div>
        <div class="whyline" style="margin-top:8px">${simReady
          ? `Probability comes from the same ${Number(simulation.iterations||0).toLocaleString()}-iteration pregame simulation used by Weekly Simulation. It is a heuristic estimate, not a guarantee.`
          : 'Median probability is withheld unless the stricter league-wide simulation coverage requirements are met.'}</div>`;
    } else if(snap.anyScoring) {
      forecast='<div class="whyline" style="margin-top:8px">Pregame probability is intentionally not carried forward after live scoring begins. Use the live median margin and score rank above during games.</div>';
    }

    $('weeklyMedian').innerHTML=`<div class="waiver-row ${status.cls}">
      <div class="waiver-rank">LM</div>
      <div>
        <b>${status.label}</b>
        <div class="whyline">${esc(status.detail)} Sleeper's <code>league_average_match</code> setting was detected automatically.</div>
        <div class="median-grid">
          <div class="median-stat"><div class="k">Your live score</div><div class="v">${snap.myPoints.toFixed(2)}</div></div>
          <div class="median-stat"><div class="k">Live league median</div><div class="v">${snap.median.toFixed(2)}</div></div>
          <div class="median-stat"><div class="k">League score rank</div><div class="v">${rankText}</div></div>
        </div>
        ${forecast}
      </div>
    </div>`;
    return {...snap,projectedMedian,medianPct:simReady?simulation.medianPct:null};
  }'''

pattern = re.compile(r"  function renderLeagueMedian\(matchups,ctx\) \{.*?\n  \}\n\n  function renderWeeklyMatchup", re.S)
text, count = pattern.subn(new_median + "\n\n  function renderWeeklyMatchup", text, count=1)
if count != 1:
    raise SystemExit(f'Could not replace renderLeagueMedian; replacements={count}')

old_sig = "  function renderWeeklyActionPlan(ctx,pool,drops,moves,steals=[],matchups=[]) {"
new_sig = "  function renderWeeklyActionPlan(ctx,pool,drops,moves,steals=[],matchups=[],simulation=null) {"
if old_sig not in text:
    raise SystemExit('Could not find renderWeeklyActionPlan signature')
text = text.replace(old_sig, new_sig, 1)

anchor = r'''    } else if(medianSnap?.anyScoring && Math.abs(medianSnap.margin)<=6) {
      items.push(`<b>League median race:</b> you are within ${Math.abs(medianSnap.margin).toFixed(2)} points of the live median. Treat marginal start/sit edges as more consequential this week.`);
    }
'''
addition = anchor + r'''
    if(medianSnap && !medianSnap.anyScoring && Number.isFinite(simulation?.medianPct)) {
      const medianPct=Number(simulation.medianPct);
      if(medianPct<45) {
        items.push(`<b>Pregame median path:</b> the heuristic simulation puts your chance to beat the Week ${state.weeklyWeek} median at ${medianPct.toFixed(1)}%. Prioritize meaningful consensus or role/upside edges, but do not chase tiny projection differences.`);
      } else if(medianPct<=55) {
        items.push(`<b>Pregame median path:</b> ${medianPct.toFixed(1)}% to beat the projected league median places this week in the median swing zone. Small lineup decisions matter, but model-split changes still require a real edge.`);
      } else if(medianPct>=65) {
        items.push(`<b>Pregame median path:</b> ${medianPct.toFixed(1)}% to beat the projected league median is a favorable baseline. Avoid forcing marginal high-variance swaps solely to chase ceiling.`);
      }
    }
'''
if anchor not in text:
    raise SystemExit('Could not find median action-plan anchor')
text = text.replace(anchor, addition, 1)

old_render = r'''      renderGameEnvironment(ctx,matchups);
      renderLeagueMedian(matchups,ctx);
      renderProjectionPanel(matchups,ctx);
      renderWeeklySimulation(matchups,ctx);
      renderWeeklyMatchup(matchups,ctx);
      renderWeeklyActionPlan(ctx,pool,drops,moves,steals,matchups);'''
new_render = r'''      renderGameEnvironment(ctx,matchups);
      renderProjectionPanel(matchups,ctx);
      const simulation=renderWeeklySimulation(matchups,ctx);
      renderLeagueMedian(matchups,ctx,simulation);
      renderWeeklyMatchup(matchups,ctx);
      renderWeeklyActionPlan(ctx,pool,drops,moves,steals,matchups,simulation);'''
if old_render not in text:
    raise SystemExit('Could not find weekly render sequence')
text = text.replace(old_render, new_render, 1)

index_path.write_text(text, encoding='utf-8')

changelog = changelog_path.read_text(encoding='utf-8')
entry = '''## v2.16.3 — Median Strategy Integration
**2026-09-16**

- Bring the already-existing league-median live panel and pregame simulation probability into one coherent median view instead of making the manager reconcile separate cards.
- Keep live score, live median, and live league rank as the in-game source of truth.
- Add a pregame median forecast showing the connected lineup projection, projected league median, and simulated probability of beating the median when coverage requirements are met.
- Reuse the existing 6,000-iteration Weekly Simulation output rather than creating a second probability model.
- Remove the stale v2.14-era message claiming Probability Above Median is not available now that the projection and simulation layers exist.
- Avoid showing a misleading 1/10-style league rank before scoring begins; pregame rank is displayed as unavailable until teams actually score.
- Add conservative pregame median context to the Weekly Action Plan for under-pressure, swing-zone, and clearly favorable median paths.
- Do not automatically override Start/Sit on the basis of median probability; model-split lineup changes still require a meaningful projection, role, availability, or consensus edge.
- Preserve current-week resolution, usage snapshots, lineup consensus, H2H simulation, waivers, trades, news, weather, and availability behavior.

'''
marker = '## v2.16.2 — Current Week Resolution\n'
if '## v2.16.3 — Median Strategy Integration' not in changelog:
    if marker not in changelog:
        raise SystemExit('Could not find changelog insertion marker')
    changelog = changelog.replace(marker, entry + marker, 1)
    changelog_path.write_text(changelog, encoding='utf-8')
