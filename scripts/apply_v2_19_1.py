#!/usr/bin/env python3
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
index_path = root / "index.html"
changelog_path = root / "CHANGELOG.md"
source = index_path.read_text(encoding="utf-8")

# Keep the Weekly hero honest about the current behavior.
source = source.replace(
    "v2.19 adds a Transaction Priority Queue that resolves competing streamer and waiver recommendations against real roster capacity before surfacing the next move.",
    "v2.19.1 makes Transaction Priority position-aware: it evaluates the same-position incumbent first, distinguishes direct replacement from unrelated roster churn, and explains when a drop exists but is not justified."
)

source = source.replace(
    "Resolves competing streamer and waiver recommendations against the roster spots you actually have. Only one recommendation can consume each open slot; later moves must identify a protected safe drop or remain blocked.",
    "Resolves competing streamer and waiver recommendations against the roster spots you actually have. Streamers first compare against the incumbent they would replace; roster routing then chooses an open slot, justified direct replacement, justified roster churn, or an explicit hold reason."
)

helper = r'''
  function streamerDirectReplacementReview(ctx,r,review=null) {
    if(r?.status!=='STREAM' || !r?.current?.p) return null;
    const pos=String(r.pos||'').toUpperCase();
    const currentId=String(r.current.id||r.current.p?.player_id||'');
    if(!currentId) return null;

    const incumbent=dropCandidates(ctx).find(d=>String(d.id)===currentId) || null;
    if(!incumbent) return null;

    // Re-evaluate the incumbent after the hypothetical stream is added and started.
    // Starter / sole-required protection should not survive that hypothetical swap,
    // but keepers, reserve/injury stashes, and recent adds stay protected.
    const hardProtected=!!(
      incumbent.isKeeper || incumbent.isReserve || incumbent.irEligible ||
      incumbent.protectedInjuryStash || incumbent.recentlyAdded
    );
    if(hardProtected) {
      return {candidateName:incumbent.name,drop:null,justified:false,gap:null,keepValue:null,reason:'protected incumbent'};
    }

    const hypothetical={
      ...incumbent,
      isStarter:false,
      isOptimizedStarter:false,
      lineupProtected:false,
      soleRequired:false,
      displacedOneStarter:['QB','TE'].includes(pos),
      redundantQB:pos==='QB',
      redundantTE:pos==='TE'
    };
    const keepValue=effectiveKeepValue(hypothetical,ctx);
    const baseReview=review||streamerWaiverReviewForRecommendation(ctx,r);
    const addValue=Number(baseReview?.addValue);
    let gap=Number.isFinite(addValue)?addValue-keepValue:null;
    if(Number.isFinite(gap)) gap+=1.5; // same-position replacement fit

    const projectionEdge=Number(r.projectionEdge);
    const threshold=Number(r.threshold)||0;
    const reviewCut=Number(baseReview?.reviewCut ?? (state.weeklyMode==='postdraft'?5:8));

    // K/DEF are normally streamed as direct one-for-one roster replacements once
    // the football recommendation already clears its streaming threshold. QB/TE
    // incumbents must also be expendable on post-swap roster value so a one-week
    // edge never turns into an automatic Joe Burrow-style drop.
    const justified=['K','DEF'].includes(pos)
      ? (Number.isFinite(projectionEdge) && projectionEdge>=threshold)
      : (Number.isFinite(gap) && gap>=reviewCut);

    return {
      candidateName:incumbent.name,
      drop:justified?incumbent:null,
      justified,
      gap,
      keepValue,
      reason:justified?'same-position replacement clears routing guardrails':'incumbent remains more valuable than the one-week roster swap'
    };
  }
'''

if "function streamerDirectReplacementReview(" not in source:
    source = source.replace("\n  function reviewStreamerWaiverMove(ctx,r) {", "\n" + helper + "\n  function reviewStreamerWaiverMove(ctx,r) {")

new_core = r'''  // TRANSACTION_PRIORITY_CORE_START
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

    const allocated=ranked.map(c=>{
      if(slots>0) {
        slots-=1;
        return {...c,resource:'OPEN SLOT',dropName:null,blocked:false};
      }

      const directDrop=String(c.directDropName||'').trim();
      if(directDrop && !usedDrops.has(directDrop)) {
        usedDrops.add(directDrop);
        return {...c,resource:'DIRECT REPLACEMENT',dropName:directDrop,blocked:false};
      }

      const safeDrop=String(c.safeDropName||'').trim();
      if(safeDrop && !usedDrops.has(safeDrop)) {
        usedDrops.add(safeDrop);
        return {...c,resource:'ROSTER CHURN',dropName:safeDrop,blocked:false};
      }

      const evaluatedDrop=String(c.churnCandidateName||c.directCandidateName||'').trim();
      if(evaluatedDrop) {
        return {...c,resource:'NO JUSTIFIED DROP',dropName:null,blocked:true};
      }
      return {...c,resource:'NO SAFE DROP',dropName:null,blocked:true};
    });

    return [
      ...allocated.filter(c=>!c.blocked),
      ...allocated.filter(c=>c.blocked)
    ];
  }
  // TRANSACTION_PRIORITY_CORE_END'''

source, count = re.subn(
    r"  // TRANSACTION_PRIORITY_CORE_START\n.*?  // TRANSACTION_PRIORITY_CORE_END",
    new_core,
    source,
    count=1,
    flags=re.S,
)
if count != 1:
    raise SystemExit(f"transaction priority core replacement count={count}")

new_builder = r'''  function buildTransactionPriorityCandidates(ctx,streamers,moves) {
    const profile=waiverLeagueProfile(ctx);
    const reviewCut=state.weeklyMode==='postdraft'?5:8;
    const candidates=[];

    for(const r of (streamers||[])) {
      if(r?.status!=='STREAM' || !r?.best?.b) continue;
      const review=streamerWaiverReviewForRecommendation(ctx,r);
      if(!review) continue;
      const direct=streamerDirectReplacementReview(ctx,r,review);
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
        directDropName:direct?.justified && direct.drop ? direct.drop.name : null,
        directCandidateName:direct?.candidateName||null,
        directDropGap:Number.isFinite(direct?.gap)?direct.gap:null,
        safeDropName,
        churnCandidateName:review.drop?.name||null,
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
        directDropName:null,
        directCandidateName:null,
        safeDropName:m.drop && Number.isFinite(m.gap) && m.gap>=reviewCut ? m.drop.name : null,
        churnCandidateName:m.drop?.name||null,
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

  function renderTransactionPriorityQueue'''

source, count = re.subn(
    r"  function buildTransactionPriorityCandidates\(ctx,streamers,moves\) \{.*?\n  \}\n\n  function renderTransactionPriorityQueue",
    new_builder,
    source,
    count=1,
    flags=re.S,
)
if count != 1:
    raise SystemExit(f"transaction candidate builder replacement count={count}")

new_render = r'''  function renderTransactionPriorityQueue(ctx,streamers,moves) {
    const openSlots=Math.max(0,(ctx.activeCapacity||0)-(ctx.activePlayers||0));
    const candidates=buildTransactionPriorityCandidates(ctx,streamers,moves);
    const queue=allocateTransactionResources(candidates,openSlots);
    const ready=queue.filter(x=>!x.blocked).length;

    if(!queue.length) {
      setPill('movePriorityPill','No priority move','good');
      $('weeklyMovePriority').innerHTML='<div class="goodbox"><b>HOLD.</b> No streamer, coverage, or waiver move currently clears the action thresholds.</div>';
      return [];
    }

    setPill('movePriorityPill',`${ready} actionable • ${queue.length} ranked`,ready?'warn':'good');
    $('weeklyMovePriority').innerHTML=queue.slice(0,6).map((m,i)=>{
      let resourceText='NO SAFE DROP';
      let routeExplanation='No legal/protected drop candidate is available after roster resources are allocated.';
      if(m.resource==='OPEN SLOT') {
        resourceText='OPEN SLOT • no drop required';
        routeExplanation=m.type==='STREAM' && m.currentName
          ? `Start ${m.name} over ${m.currentName} this week while keeping the incumbent rostered.`
          : 'This move uses currently available roster capacity without cutting anyone.';
      } else if(m.resource==='DIRECT REPLACEMENT') {
        resourceText=`DIRECT REPLACEMENT • ${m.dropName}`;
        routeExplanation=`The same-position incumbent ${m.dropName} was re-evaluated after the hypothetical lineup swap and is expendable enough to replace directly.`;
      } else if(m.resource==='ROSTER CHURN') {
        resourceText=`ROSTER CHURN • ${m.dropName}`;
        routeExplanation=`Keep the incumbent and use ${m.dropName} as the justified lower-value roster churn path.`;
      } else if(m.resource==='NO JUSTIFIED DROP') {
        resourceText='NO JUSTIFIED DROP';
        routeExplanation='A drop candidate exists, but the value lost is greater than this move justifies. Do not force the transaction.';
      }

      const impactText=m.type==='STREAM'
        ? `one-week starter gain ${Number.isFinite(m.starterGain)?'+'+m.starterGain.toFixed(1)+' projected pts':'coverage driven'}${m.currentName?` vs ${m.currentName}`:''}`
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
          <div class="whyline">${esc(impactText)}${esc(costText)}. ${esc(routeExplanation)} Verify the transaction state in Sleeper before submitting.</div>
        </div>
        <div class="value-badge">${m.type==='STREAM'&&Number.isFinite(m.starterGain)?`+${m.starterGain.toFixed(1)}`:(Number.isFinite(m.rosterGain)?`${m.rosterGain>=0?'+':''}${Math.round(m.rosterGain)}`:'—')}<div class="tiny">${m.type==='STREAM'?'starter':'utility'}</div></div>
      </div>`;
    }).join('');
    return queue;
  }

  function renderStreamerFinder'''

source, count = re.subn(
    r"  function renderTransactionPriorityQueue\(ctx,streamers,moves\) \{.*?\n  \}\n\n  function renderStreamerFinder",
    new_render,
    source,
    count=1,
    flags=re.S,
)
if count != 1:
    raise SystemExit(f"transaction queue render replacement count={count}")

old_route = r'''      const route=topMovePriority.resource==='OPEN SLOT'
        ? 'use the open roster slot'
        : (topMovePriority.resource==='SAFE DROP'
            ? `drop ${topMovePriority.dropName}`
            : 'do not force the transaction — no safe roster path remains');'''
new_route = r'''      const route=topMovePriority.resource==='OPEN SLOT'
        ? 'use the open roster slot and keep the incumbent'
        : (topMovePriority.resource==='DIRECT REPLACEMENT'
            ? `directly replace ${topMovePriority.dropName}`
            : (topMovePriority.resource==='ROSTER CHURN'
                ? `keep the incumbent and drop ${topMovePriority.dropName}`
                : (topMovePriority.resource==='NO JUSTIFIED DROP'
                    ? 'hold — a drop exists, but this move does not justify the roster cost'
                    : 'hold — no legal/protected drop path exists')));'''
if old_route not in source:
    raise SystemExit("action-plan route block not found")
source = source.replace(old_route, new_route, 1)

index_path.write_text(source, encoding="utf-8")

changelog = changelog_path.read_text(encoding="utf-8")
entry = """## v2.19.1 — Position-Aware Transaction Routing\n**2026-09-17**\n\n- Keep the Streamer Finder's same-position starter comparison as the first football decision, then resolve the separate roster-space decision explicitly.\n- Re-evaluate the incumbent after a hypothetical streamer add so pre-transaction starter/sole-position protection does not incorrectly prevent a legitimate direct replacement.\n- Allow K/DEF streams that already clear the streaming model to use a guarded `DIRECT REPLACEMENT` path instead of sacrificing unrelated RB/WR depth.\n- Require QB/TE incumbents to clear post-swap roster-value guardrails before direct replacement, preventing a one-week projection edge from turning into an automatic drop of a valuable starter.\n- Distinguish `ROSTER CHURN`, `NO JUSTIFIED DROP`, and literal `NO SAFE DROP`, eliminating the apparent contradiction between Move Priority and Drop Review.\n- Keep open-slot routing first: when space exists, add the streamer, start him over the incumbent for the week, and retain the incumbent.\n\n"""
if "## v2.19.1 — Position-Aware Transaction Routing" not in changelog:
    marker = "The project is currently in active beta development. Version numbers reflect iterative product updates rather than formal production releases.\n\n"
    if marker not in changelog:
        raise SystemExit("changelog insertion marker not found")
    changelog = changelog.replace(marker, marker + entry, 1)
    changelog_path.write_text(changelog, encoding="utf-8")

print("Applied v2.19.1 position-aware transaction routing")
