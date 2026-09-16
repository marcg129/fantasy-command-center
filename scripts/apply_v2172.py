from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
index_path = ROOT / 'index.html'
changelog_path = ROOT / 'CHANGELOG.md'

html = index_path.read_text(encoding='utf-8')

# Version + Weekly hero copy.
html = html.replace('Multi-manager beta • week-aware management • v2.17.1', 'Multi-manager beta • week-aware management • v2.17.2', 1)
html = html.replace(
    'Weekly lineup, matchup, waiver, and roster-management command center. v2.17.1 adds simulation-confidence guardrails and explicit no-action thresholds while preserving calibration, current-week resolution, lineup consensus, median strategy, and reliable usage.',
    'Weekly lineup, matchup, waiver, and roster-management command center. v2.17.2 restores the projection helpers required by Weekly Check while preserving simulation-confidence guardrails, calibration, lineup consensus, median strategy, and reliable usage.',
    1,
)

# v2.17.1 accidentally removed these projection helpers while replacing the
# calibration summary block. Restore the exact v2.17 implementations before
# simulationVarianceProfile().
if 'function projectionRowForId(id)' not in html:
    marker = '  function simulationVarianceProfile(pos,mean) {'
    if marker not in html:
        raise SystemExit('Could not find simulationVarianceProfile insertion marker')

    restored = r'''  function projectionRowForId(id) {
    return state.projectionByPlayer.get(String(id))||null;
  }

  function projectionPointsAllowedBandKey(points) {
    const n=Number(points);
    if(!Number.isFinite(n)) return null;
    if(n<=0) return 'pts_allow_0';
    if(n<=6) return 'pts_allow_1_6';
    if(n<=13) return 'pts_allow_7_13';
    if(n<=20) return 'pts_allow_14_20';
    if(n<=27) return 'pts_allow_21_27';
    if(n<=34) return 'pts_allow_28_34';
    return 'pts_allow_35p';
  }

  function projectionScoringForId(id) {
    const row=projectionRowForId(id);
    const stats=row?.stats;
    const scoring=state.league?.scoring_settings||{};
    if(!stats || typeof stats!=='object') return null;
    let points=0;
    let matched=0;
    const nonlinear=[];
    for(const [key,rawWeight] of Object.entries(scoring)) {
      const weight=Number(rawWeight);
      if(!Number.isFinite(weight) || weight===0) continue;
      if(key.startsWith('bonus_')) { nonlinear.push(key); continue; }
      if(key.startsWith('pts_allow_')) continue;
      const stat=Number(stats[key]);
      if(Number.isFinite(stat)) {
        points+=stat*weight;
        matched++;
      }
    }
    const allow=Number(stats.pts_allow);
    if(Number.isFinite(allow)) {
      const band=projectionPointsAllowedBandKey(allow);
      const weight=band?Number(scoring[band]):NaN;
      if(Number.isFinite(weight)) { points+=weight; matched++; }
    }
    if(!matched) return null;
    return {points,matched,nonlinear};
  }

  function projectedPointsForId(id) {
    return projectionScoringForId(id)?.points ?? null;
  }

  function projectionTotalForIds(ids=[]) {
    let total=0, projected=0;
    const clean=(ids||[]).map(String).filter(id=>id && id!=='0');
    for(const id of clean) {
      const pts=projectedPointsForId(id);
      if(Number.isFinite(pts)) { total+=pts; projected++; }
    }
    return {total,projected,slots:clean.length,coverage:clean.length?projected/clean.length:0};
  }

  function projectionOptimalLineup(ctx) {
    const slots=startingLineupSlots();
    const flexNames=new Set(['FLEX','W/R/T','WRRB_FLEX','REC_FLEX','W/R','WRRB','W/T','WRTE','R/T','RBTE','SUPER_FLEX','SUPERFLEX','Q/W/R/T']);
    const players=(ctx.players||[])
      .filter(id=>!ctx.reserve.has(String(id)))
      .map(id=>({
        id:String(id),p:state.players[String(id)],pos:normalizedFantasyPos(state.players[String(id)]),score:projectedPointsForId(id)
      }))
      .filter(x=>x.p && Number.isFinite(x.score) && playerUsableForRequiredStart(x.p));
    const order=slots.map((slot,index)=>({slot,index,flex:flexNames.has(slot)})).sort((a,b)=>Number(a.flex)-Number(b.flex));
    const used=new Set();
    const assignments=new Array(slots.length).fill(null);
    for(const s of order) {
      const eligible=players.filter(x=>!used.has(x.id) && eligibleForLineupSlot(x.pos,s.slot)).sort((a,b)=>b.score-a.score);
      const chosen=eligible[0]||null;
      if(chosen) { used.add(chosen.id); assignments[s.index]={slot:s.slot,index:s.index,id:chosen.id,p:chosen.p,score:chosen.score}; }
      else assignments[s.index]={slot:s.slot,index:s.index,id:null,p:null,score:null};
    }
    return assignments;
  }

  function projectedLeagueMedian(matchups) {
    const teams=(matchups||[]).filter(m=>Number.isFinite(Number(m?.roster_id))).map(m=>{
      const t=projectionTotalForIds(m.starters||[]);
      return {rosterId:Number(m.roster_id),...t};
    });
    if(!teams.length) return null;
    const usable=teams.filter(t=>t.slots>0 && t.coverage>=0.70);
    if(usable.length<Math.ceil(teams.length*0.80)) return {teams,usable,median:null};
    const vals=usable.map(t=>t.total).sort((a,b)=>a-b);
    const n=vals.length;
    const median=n%2?vals[Math.floor(n/2)]:(vals[n/2-1]+vals[n/2])/2;
    return {teams,usable,median};
  }

  function projectionNonlinearKeys() {
    const scoring=state.league?.scoring_settings||{};
    return Object.entries(scoring)
      .filter(([k,v])=>k.startsWith('bonus_') && Number(v)!==0)
      .map(([k])=>k);
  }

'''
    html = html.replace(marker, restored + marker, 1)

index_path.write_text(html, encoding='utf-8')

changelog = changelog_path.read_text(encoding='utf-8')
entry = '''## v2.17.2 — Weekly Check Regression Fix
**2026-09-16**

- Restore the projection helper functions accidentally removed by the v2.17.1 calibration-summary replacement.
- Fix the runtime failure that allowed Sleeper connection to succeed but prevented `Run Weekly Check` from rendering roster, Outlook, Start/Sit, availability, and simulation results.
- Restore league-scored projection lookup, lineup projection totals, projection-optimal lineup construction, projected league median, and nonlinear scoring-key detection.
- Preserve all v2.17.1 simulation confidence guardrails, no-action thresholds, calibration collection, current-week resolution, usage, median strategy, waivers, trades, and Enter-to-Connect behavior.
- Add semantic regression checks requiring every restored projection helper to exist before the hotfix can commit.

'''
if '## v2.17.2 — Weekly Check Regression Fix' not in changelog:
    marker = 'The project is currently in active beta development. Version numbers reflect iterative product updates rather than formal production releases.\n\n'
    if marker not in changelog:
        raise SystemExit('Could not find changelog insertion marker')
    changelog = changelog.replace(marker, marker + entry, 1)
    changelog_path.write_text(changelog, encoding='utf-8')

print('Applied v2.17.2 Weekly Check regression fix.')
