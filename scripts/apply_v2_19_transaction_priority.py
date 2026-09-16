#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
CHANGELOG = ROOT / "CHANGELOG.md"


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly 1 match, found {count}")
    return text.replace(old, new, 1)


html = INDEX.read_text(encoding="utf-8")

html = replace_once(
    html,
    "Weekly lineup, matchup, waiver, and roster-management command center. v2.18.3 carries an exact Streamer Finder recommendation into Waiver Claim Planner for a safe roster-space review without assuming the incumbent starter should be dropped.",
    "Weekly lineup, matchup, waiver, and roster-management command center. v2.19 adds a Transaction Priority Queue that resolves competing streamer and waiver recommendations against real roster capacity before surfacing the next move.",
    "weekly hero version copy",
)

best_adds_anchor = '''      <div class="card" style="margin-top:12px">
        <div class="weekly-section-head">
          <div>
            <h3>Best available adds</h3>'''
move_priority_card = '''      <div class="card" style="margin-top:12px">
        <div class="weekly-section-head">
          <div>
            <div class="tiny">MOVE PRIORITY</div>
            <h3>Transaction Priority Queue</h3>
            <div class="tiny">Resolves competing streamer and waiver recommendations against the roster spots you actually have. Only one recommendation can consume each open slot; later moves must identify a protected safe drop or remain blocked.</div>
          </div>
          <span class="pill" id="movePriorityPill">Moves —</span>
        </div>
        <div id="weeklyMovePriority" class="weekly-table"><div class="tiny">Run a weekly check.</div></div>
      </div>

'''
html = replace_once(html, best_adds_anchor, move_priority_card + best_adds_anchor, "move priority card")

core_and_renderer = r'''  // TRANSACTION_PRIORITY_CORE_START
  function transactionPriorityScore(c) {
    const starter=Number.isFinite(Number(c?.starterGain))?Math.max(0,Number(c.starterGain)):0;
    const roster=Number.isFinite(Number(c?.rosterGain))?Math.max(0,Number(c.rosterGain)):0;
    const competition=Number.isFinite(Number(c?.competitionLevel))?Math.max(0,Number(c.competitionLevel)):0;
    const cost=Number.isFinite(Number(c?.transactionCost))?Math.max(0,Number(c.transactionCost)):0;
    const coverage=c?.coverageNeed?35:0;
    return coverage + starter*10 + Math.min(30,roster)*0.6 + competition*1.25 - cost;
  }

  function allocateTransactionResources(candidates,openSlots=0) {
    let slots=Math.max(0,Math.floor(Number(openSlots)||0));
    const usedDrops=new Set();
    const ranked=(candidates||[])
      .map((c,index)=>({...c,priorityScore:transactionPriorityScore(c),_sourceOrder:index}))
      .sort((a,b)=>b.priorityScore-a.priorityScore || a._sourceOrder-b._sourceOrder);

    return ranked.map(c=>{
      if(slots>0) {
        slots-=1;
        return {...c,resource:'OPEN SLOT',dropName:null,blocked:false};
      }
      const safeDrop=String(c.safeDropName||'').trim();
      if(safeDrop && !usedDrops.has(safeDrop)) {
        usedDrops.add(safeDrop);
        return {...c,resource:'SAFE DROP',dropName:safeDrop,blocked:false};
      }
      return {...c,resource:'BLOCKED — NO SAFE DROP',dropName:null,blocked:true};
    });
  }
  // TRANSACTION_PRIORITY_CORE_END

  function buildTransactionPriorityCandidates(ctx,streamers,moves) {
    const profile=waiverLeagueProfile(ctx);
    const reviewCut=state.weeklyMode==='postdraft'?5:8;
    const candidates=[];

    for(const r of (streamers||[])) {
      if(r?.status!=='STREAM' || !r?.best?.b) continue;
      const review=streamerWaiverReviewForRecommendation(ctx,r);
      if(!review) continue;
      const competition=waiverCompetitionRisk(review.add);
      const coverageNeed=!r.current || !r.current.usable;
      const safeDropName=review.drop && Number.isFinite(review.gap) && review.gap>=review.reviewCut
        ? review.drop.name
        : null;
      candidates.push({
        id:String(review.add.player_id||review.add.pdata?.player_id||review.add.name),
        type:'STREAM',
        name:review.add.name,
        pos:review.add.pos,
        add:review.add,
        starterGain:Number.isFinite(r.projectionEdge)?Math.max(0,r.projectionEdge):(coverageNeed?7.5:0),
        rosterGain:Number.isFinite(review.gap)?review.gap:null,
        coverageNeed,
        competitionLevel:competition.level,
        transactionCost:0,
        safeDropName,
        currentName:review.currentName,
        reason:r.reason
      });
    }

    for(const m of (moves||[])) {
      if(!m?.add) continue;
      const coverageNeed=!!m.coverageNeed;
      if(!coverageNeed && (!Number.isFinite(m.gap) || m.gap<reviewCut)) continue;
      const competition=waiverCompetitionRisk(m.add);
      const premiumPriorityCost=profile.waiverPosition && profile.waiverPosition<=4 ? 1.5 : 0;
      const budgetCost=profile.waiverBudget!==null ? 0.5 : 0;
      candidates.push({
        id:String(m.add.player_id||m.add.pdata?.player_id||m.add.name),
        type:'WAIVER',
        name:m.add.name,
        pos:m.add.pos,
        add:m.add,
        starterGain:coverageNeed?7.5:0,
        rosterGain:Number.isFinite(m.gap)?m.gap:null,
        coverageNeed,
        competitionLevel:competition.level,
        transactionCost:premiumPriorityCost+budgetCost,
        safeDropName:m.drop && Number.isFinite(m.gap) && m.gap>=reviewCut ? m.drop.name : null,
        currentName:null,
        reason:coverageNeed?'Restores a required starting-position coverage gap.':'Clears the existing roster-utility review threshold.'
      });
    }

    const byPlayer=new Map();
    for(const c of candidates) {
      const existing=byPlayer.get(c.id);
      if(!existing || (c.type==='STREAM' && existing.type!=='STREAM') ||
         (c.type===existing.type && transactionPriorityScore(c)>transactionPriorityScore(existing))) {
        byPlayer.set(c.id,c);
      }
    }
    return [...byPlayer.values()];
  }

  function renderTransactionPriorityQueue(ctx,streamers,moves) {
    const openSlots=Math.max(0,(ctx.activeCapacity||0)-(ctx.activePlayers||0));
    const candidates=buildTransactionPriorityCandidates(ctx,streamers,moves);
    const queue=allocateTransactionResources(candidates,openSlots);
    const ready=queue.filter(x=>!x.blocked).length;

    if(!queue.length) {
      setPill('movePriorityPill','No priority move','good');
      $('weeklyMovePriority').innerHTML='<div class="goodbox"><b>HOLD.</b> No streamer, coverage, or waiver move currently clears the action thresholds.</div>';
      return [];
    }

    setPill('movePriorityPill',ready?`${ready} actionable • ${queue.length} ranked`:`${queue.length} ranked • none safe`,ready?'warn':'good');
    $('weeklyMovePriority').innerHTML=queue.slice(0,5).map((m,i)=>{
      const resourceText=m.resource==='OPEN SLOT'
        ? 'OPEN SLOT • no drop required'
        : (m.resource==='SAFE DROP'
            ? `SAFE DROP • ${m.dropName}`
            : 'BLOCKED — NO SAFE DROP');
      const impactText=m.type==='STREAM'
        ? `one-week starter gain ${Number.isFinite(m.starterGain)?'+'+m.starterGain.toFixed(1)+' projected pts':'coverage driven'}`
        : (m.coverageNeed
            ? 'required-position coverage restoration'
            : `roster-utility gain ${Number.isFinite(m.rosterGain)?(m.rosterGain>=0?'+':'')+Math.round(m.rosterGain):'—'}`);
      const costText=m.transactionCost>0?' • premium waiver/FAAB cost slightly lowers priority':'';
      const cls=m.blocked?'claim-watch':'strong move-priority-ready';
      return `<div class="waiver-row ${cls}">
        <div class="waiver-rank">MOVE<b>${i+1}</b></div>
        <div>
          <b>${m.blocked?'HOLD':'ADD'} ${esc(m.name)} <span class="pos ${m.pos}">${m.pos}</span></b>
          <div class="meta">${esc(resourceText)} • ${esc(m.type)}${m.coverageNeed?' • COVERAGE NEED':''}</div>
          <div class="whyline">${esc(impactText)}${esc(costText)}. ${m.blocked?'The higher-priority move consumes the available roster capacity and this move does not have a distinct protected churn path.':'This is the highest remaining transaction that fits the roster resources allocated ahead of it.'} Verify the transaction state in Sleeper before submitting.</div>
        </div>
        <div class="value-badge">${m.type==='STREAM'&&Number.isFinite(m.starterGain)?`+${m.starterGain.toFixed(1)}`:(Number.isFinite(m.rosterGain)?`${m.rosterGain>=0?'+':''}${Math.round(m.rosterGain)}`:'—')}<div class="tiny">${m.type==='STREAM'?'starter':'utility'}</div></div>
      </div>`;
    }).join('');
    return queue;
  }

'''
html = replace_once(html, "  function renderStreamerFinder(ctx) {", core_and_renderer + "  function renderStreamerFinder(ctx) {", "transaction priority functions")

html = replace_once(
    html,
    "  function renderWeeklyActionPlan(ctx,pool,drops,moves,steals=[],matchups=[],simulation=null) {\n    const items=[];\n    const post=state.weeklyMode==='postdraft';",
    "  function renderWeeklyActionPlan(ctx,pool,drops,moves,steals=[],matchups=[],simulation=null,priorities=[]) {\n    const items=[];\n    const post=state.weeklyMode==='postdraft';\n    const topMovePriority=(priorities||[])[0]||null;\n    if(topMovePriority) {\n      const route=topMovePriority.resource==='OPEN SLOT'\n        ? 'use the open roster slot'\n        : (topMovePriority.resource==='SAFE DROP'\n            ? `drop ${topMovePriority.dropName}`\n            : 'do not force the transaction — no safe roster path remains');\n      items.push(`<b>Move priority #1:</b> ${topMovePriority.blocked?'HOLD ':''}${esc(topMovePriority.name)} ${esc(topMovePriority.pos)} • ${esc(route)}.${topMovePriority.type==='STREAM'&&Number.isFinite(topMovePriority.starterGain)?` Projected starter gain: +${topMovePriority.starterGain.toFixed(1)}.`:''}`);\n    }",
    "action plan priority input",
)

html = replace_once(
    html,
    "      waivers:['weeklyAdds','weeklyDrops','weeklyMoves','weeklyClaims','weeklyStreamers','postDraftScanCard'],",
    "      waivers:['weeklyMovePriority','weeklyAdds','weeklyDrops','weeklyMoves','weeklyClaims','weeklyStreamers','postDraftScanCard'],",
    "waivers navigation mapping",
)

html = replace_once(html, "      renderStreamerFinder(ctx);", "      const streamers=renderStreamerFinder(ctx);", "capture streamer results")
html = replace_once(
    html,
    "      const claims=renderWaiverClaims(ctx,moves,pool);\n      const trades=renderTradeIntelligence(ctx);",
    "      const claims=renderWaiverClaims(ctx,moves,pool);\n      const priorities=renderTransactionPriorityQueue(ctx,streamers,moves);\n      const trades=renderTradeIntelligence(ctx);",
    "render priority queue",
)
html = replace_once(
    html,
    "      renderWeeklyActionPlan(ctx,pool,drops,moves,steals,matchups,simulation);",
    "      renderWeeklyActionPlan(ctx,pool,drops,moves,steals,matchups,simulation,priorities);",
    "action plan priority call",
)

INDEX.write_text(html, encoding="utf-8")

changelog = CHANGELOG.read_text(encoding="utf-8")
anchor = "The project is currently in active beta development. Version numbers reflect iterative product updates rather than formal production releases.\n\n"
entry = '''## v2.19 — Transaction Priority Queue
**2026-09-16**

- Add a unified Move Priority card that ranks actionable Streamer Finder and ordinary waiver/add-drop recommendations against the same roster-capacity budget.
- Rank true one-week starter improvements primarily by projected starter gain, then use roster-utility improvement, coverage urgency, competition, and a modest transaction-cost signal as supporting factors.
- Allocate open roster slots sequentially so only the highest-priority move can consume a single free slot; later moves must identify a distinct protected churn path or show `BLOCKED — NO SAFE DROP`.
- Deduplicate the same free agent when he appears in both Streamer Finder and ordinary waiver logic, preserving the richer streaming context for QB/TE/K/DEF decisions.
- Feed Move Priority #1 into This Week's Action Plan while preserving the detailed Streamer Finder, Waiver Claim Planner, Add/Drop, and Drop Review evidence underneath.
- Add a real JavaScript behavior regression fixture for the Week 2 two-streamers/one-open-slot case: Jake Ferguson (+5.2) ranks ahead of Tampa Bay (+3.7), gets the open slot, and Tampa Bay is blocked unless a safe drop exists.

'''
if "## v2.19 — Transaction Priority Queue" not in changelog:
    if anchor not in changelog:
        raise SystemExit("changelog anchor missing")
    changelog = changelog.replace(anchor, anchor + entry, 1)
CHANGELOG.write_text(changelog, encoding="utf-8")

print("Applied v2.19 Transaction Priority Queue")
