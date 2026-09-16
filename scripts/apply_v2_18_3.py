from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
CHANGELOG = ROOT / "CHANGELOG.md"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


html = INDEX.read_text(encoding="utf-8")

html = replace_once(
    html,
    "Weekly lineup, matchup, waiver, and roster-management command center. v2.18.2 clarifies Streamer Finder hold decisions by naming the incumbent and separating threshold misses from supporting-model conflicts.",
    "Weekly lineup, matchup, waiver, and roster-management command center. v2.18.3 carries an exact Streamer Finder recommendation into Waiver Claim Planner for a safe roster-space review without assuming the incumbent starter should be dropped.",
    "version banner",
)

html = replace_once(
    html,
    "tradeStyle:'balanced',tradeView:'scan',tradeExplorerPlayerId:null\n  };",
    "tradeStyle:'balanced',tradeView:'scan',tradeExplorerPlayerId:null,streamerWaiverReview:null,weeklyWaiverMoves:[],weeklyWaiverPool:[]\n  };",
    "state fields",
)

html = replace_once(
    html,
    "  function renderWaiverClaims(ctx,moves,pool) {\n    const profile=waiverLeagueProfile(ctx);\n    const threshold=waiverPriorityThreshold(profile);\n    const openSlots=Math.max(0,(ctx.activeCapacity||0)-(ctx.activePlayers||0));\n",
    "  function renderWaiverClaims(ctx,moves,pool) {\n    const profile=waiverLeagueProfile(ctx);\n    const threshold=waiverPriorityThreshold(profile);\n    const openSlots=Math.max(0,(ctx.activeCapacity||0)-(ctx.activePlayers||0));\n    state.weeklyWaiverMoves=moves||[];\n    state.weeklyWaiverPool=pool||[];\n",
    "cache waiver inputs",
)

old_empty = """    if(!ordered.length) {
      $('weeklyClaims').innerHTML=
        `<div class=\"goodbox\"><b>No waiver claim is justified right now.</b><br>${esc(profileBits.join(' • '))}. Holding your current priority/budget is a positive decision.</div>`;
      return [];
    }

    const sharedDrop=ordered[0]?.drop||null;

    $('weeklyClaims').innerHTML=
      `<div class=\"goodbox\" style=\"margin-bottom:8px\"><b>Waiver profile:</b> ${esc(profileBits.join(' • '))}. ${
"""

new_empty = """    const streamerReview=state.streamerWaiverReview;
    const streamerDecision=streamerReview
      ? (streamerReview.openSlots>0
          ? 'OPEN SLOT'
          : (streamerReview.safeDrop?'SAFE DROP':'STREAM EDGE — NO SAFE DROP'))
      : '';
    const streamerDropText=streamerReview
      ? (streamerReview.openSlots>0
          ? `ADD ${streamerReview.add.name} • open roster slot`
          : (streamerReview.drop
              ? `ADD ${streamerReview.add.name} • ${streamerReview.safeDrop?'DROP':'review drop'} ${streamerReview.drop.name}`
              : `ADD ${streamerReview.add.name} • no eligible churn candidate`))
      : '';
    const streamerGapText=streamerReview && Number.isFinite(streamerReview.gap)
      ? ` • roster-utility gap ${streamerReview.gap>=0?'+':''}${Math.round(streamerReview.gap)}`
      : '';
    const streamerProjectionText=streamerReview && Number.isFinite(streamerReview.projectionEdge)
      ? `Projection edge ${streamerReview.projectionEdge>=0?'+':''}${streamerReview.projectionEdge.toFixed(1)} pts.`
      : 'Projection-led stream recommendation.';
    const streamerReviewHtml=streamerReview
      ? `<div class=\"waiver-row ${streamerReview.safeDrop?'claim-submit':'claim-watch'}\" style=\"margin-bottom:8px;border-width:2px\">
          <div class=\"waiver-rank\">STREAM<b>↕</b></div>
          <div>
            <b>${esc(streamerReview.add.name)} <span class=\"pos ${streamerReview.add.pos}\">${streamerReview.add.pos}</span></b>
            <div class=\"meta\">${esc(streamerDropText)}${streamerGapText}</div>
            <div class=\"usage-grid\">
              <span class=\"claim-chip warn\">STREAMER REVIEW</span>
              <span class=\"claim-chip ${streamerReview.safeDrop?'good':'warn'}\">${esc(streamerDecision)}</span>
            </div>
            <div class=\"whyline\">${esc(streamerProjectionText)} ${
              streamerReview.safeDrop
                ? (streamerReview.openSlots>0
                    ? 'The one-week stream can be reviewed without cutting anyone.'
                    : `The existing churn model identifies ${esc(streamerReview.drop.name)} as a sufficiently expendable roster spot.`)
                : `The stream itself grades well, but no existing safe churn candidate clears the +${streamerReview.reviewCut} roster-utility threshold. Do not force the transaction.`
            } The incumbent ${esc(streamerReview.currentName||streamerReview.pos)} is never assumed to be the drop.</div>
          </div>
          <div class=\"value-badge\">${Number.isFinite(streamerReview.projectionEdge)?`${streamerReview.projectionEdge>=0?'+':''}${streamerReview.projectionEdge.toFixed(1)}`:'—'}<div class=\"tiny\">proj edge</div></div>
        </div>`
      : '';

    if(!ordered.length) {
      $('weeklyClaims').innerHTML=
        streamerReviewHtml+
        `<div class=\"goodbox\"><b>No ordinary waiver claim is justified right now.</b><br>${esc(profileBits.join(' • '))}. Holding your current priority/budget is a positive decision.</div>`;
      return streamerReview?[streamerReview]:[];
    }

    const sharedDrop=ordered[0]?.drop||null;

    $('weeklyClaims').innerHTML=
      `<div class=\"goodbox\" style=\"margin-bottom:8px\"><b>Waiver profile:</b> ${esc(profileBits.join(' • '))}. ${
"""

html = replace_once(html, old_empty, new_empty, "streamer review planner block")

html = replace_once(
    html,
    "      }</div>`+\n      ordered.map((m,i)=>{",
    "      }</div>`+\n      streamerReviewHtml+\n      ordered.map((m,i)=>{",
    "prepend streamer review card",
)

helper_anchor = """  function renderStreamerFinder(ctx) {
    const pool=streamingCandidatePool(ctx);
"""
helper_code = """  function streamerWaiverReviewForRecommendation(ctx,r) {
    const add=r?.best?.b;
    if(!add || r?.status!=='STREAM') return null;
    const openSlots=Math.max(0,(ctx.activeCapacity||0)-(ctx.activePlayers||0));
    const drops=dropCandidates(ctx);
    const drop=primaryChurnCandidate(ctx,drops);
    const keepValue=drop?effectiveKeepValue(drop,ctx):null;
    let gap=drop && Number.isFinite(Number(add.weeklyValue))
      ? Number(add.weeklyValue)-keepValue
      : null;

    if(drop && Number.isFinite(gap)) {
      if(add.pos===drop.pos) gap+=1.5;
      if((drop.pos==='RB'||drop.pos==='WR') && ctx.counts[drop.pos]<=4 && add.pos!==drop.pos) gap-=3;
    }

    const reviewCut=state.weeklyMode==='postdraft'?5:8;
    const safeDrop=openSlots>0 || (!!drop && Number.isFinite(gap) && gap>=reviewCut);
    return {
      add,drop,openSlots,keepValue,gap,reviewCut,safeDrop,
      projectionEdge:r.projectionEdge,
      outlookEdge:r.outlookEdge,
      pos:r.pos,
      currentName:r.current?pName(r.current.p):null
    };
  }

  function reviewStreamerWaiverMove(ctx,r) {
    const review=streamerWaiverReviewForRecommendation(ctx,r);
    if(!review) return;
    state.streamerWaiverReview=review;
    renderWaiverClaims(ctx,state.weeklyWaiverMoves,state.weeklyWaiverPool);
    const target=$('weeklyClaims')?.closest('.card')||$('weeklyDrops')?.closest('.card');
    target?.scrollIntoView({behavior:'smooth',block:'start'});
  }

  function renderStreamerFinder(ctx) {
    const pool=streamingCandidatePool(ctx);
"""
html = replace_once(html, helper_anchor, helper_code, "streamer review helpers")

html = replace_once(
    html,
    "    $('weeklyStreamers').innerHTML=rows.map(r=>{",
    "    $('weeklyStreamers').innerHTML=rows.map((r,index)=>{",
    "streamer row index",
)

html = replace_once(
    html,
    "          ${r.status==='STREAM'?`<button class=\"ghost streamerWaiverBtn\" type=\"button\" style=\"margin-top:7px;min-height:34px;padding:6px 9px\">Review waiver move</button>`:''}",
    "          ${r.status==='STREAM'?`<button class=\"ghost streamerWaiverBtn\" type=\"button\" data-streamer-index=\"${index}\" style=\"margin-top:7px;min-height:34px;padding:6px 9px\">Review waiver move</button>`:''}",
    "streamer button identity",
)

old_handler = """    document.querySelectorAll('.streamerWaiverBtn').forEach(btn=>btn.addEventListener('click',()=>{
      const target=$('weeklyClaims')?.closest('.card')||$('weeklyDrops')?.closest('.card');
      target?.scrollIntoView({behavior:'smooth',block:'start'});
    }));
"""
new_handler = """    document.querySelectorAll('.streamerWaiverBtn').forEach(btn=>btn.addEventListener('click',()=>{
      const index=Number(btn.dataset.streamerIndex);
      if(!Number.isInteger(index) || !rows[index]) return;
      reviewStreamerWaiverMove(ctx,rows[index]);
    }));
"""
html = replace_once(html, old_handler, new_handler, "streamer handoff handler")

html = replace_once(
    html,
    "  async function loadWeekly() {\n    if(!state.connected) return showError('Connect to Sleeper first.');\n    const week=Math.max(1,Math.min(18,Number($('weekInput').value)||1));",
    "  async function loadWeekly() {\n    if(!state.connected) return showError('Connect to Sleeper first.');\n    state.streamerWaiverReview=null;\n    const week=Math.max(1,Math.min(18,Number($('weekInput').value)||1));",
    "clear stale streamer review",
)

INDEX.write_text(html, encoding="utf-8")

changelog = CHANGELOG.read_text(encoding="utf-8")
entry = """## v2.18.3 — Streamer → Waiver Planner Handoff
**2026-09-16**

- Carry the exact `STREAM` candidate selected in Streamer Finder into Waiver Claim Planner instead of only scrolling to the planner.
- Pin a dedicated `STREAMER REVIEW` card that evaluates the candidate against an open roster slot or the existing canonical safe churn candidate.
- Reuse `dropCandidates()`, `primaryChurnCandidate()`, and `effectiveKeepValue()` so the handoff follows the same roster-protection logic as Drop Review and ordinary add/drop decisions.
- Surface `STREAM EDGE — NO SAFE DROP` when the one-week stream grades well but no protected roster move clears the existing churn threshold.
- Never assume the incumbent QB/TE/K/DEF starter is the player to cut; the planner can show the stream edge without forcing a transaction.
- Preserve ordinary Waiver Claim Planner rankings when no Streamer Finder handoff is selected, and clear stale pinned reviews on the next Weekly Check.
- Add a permanent regression contract covering exact-candidate propagation, safe-drop reuse, and no-auto-incumbent-drop behavior.

"""
anchor = "The project is currently in active beta development. Version numbers reflect iterative product updates rather than formal production releases.\n\n"
if entry.splitlines()[0] not in changelog:
    if anchor not in changelog:
        raise SystemExit("changelog anchor not found")
    changelog = changelog.replace(anchor, anchor + entry, 1)
CHANGELOG.write_text(changelog, encoding="utf-8")

print("Applied v2.18.3 Streamer → Waiver Planner handoff")
