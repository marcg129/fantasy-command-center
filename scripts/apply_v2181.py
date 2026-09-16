from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
index_path = ROOT / 'index.html'
changelog_path = ROOT / 'CHANGELOG.md'

html = index_path.read_text(encoding='utf-8')

html = html.replace('Multi-manager beta • week-aware management • v2.18', 'Multi-manager beta • week-aware management • v2.18.1', 1)
html = html.replace(
    'Weekly lineup, matchup, waiver, and roster-management command center. v2.18 adds conservative one-week streaming recommendations for QB, TE, K, and DEF while preserving regression protection, lineup consensus, calibration, median strategy, and reliable usage.',
    'Weekly lineup, matchup, waiver, and roster-management command center. v2.18.1 gives Streamer Finder its own QB/TE/K/DEF candidate pool and a direct waiver-review handoff while preserving conservative thresholds and regression protection.',
    1,
)
html = html.replace(
    'One-week QB, TE, K, and DEF decisions. Compares your current starter with available options using league-scored projections first, then Weekly Outlook, game environment, and availability as supporting context. Small edges are treated as holds.',
    'One-week QB, TE, K, and DEF decisions. Uses a dedicated streaming candidate pool so strong incumbents still receive real free-agent comparisons. League-scored projections lead; Weekly Outlook, game environment, and availability provide supporting context. Small edges are treated as holds.',
    1,
)

candidate_anchor = '  function streamingRecommendationForPosition(ctx,pool,pos) {'
if 'function streamingCandidatePool(ctx)' not in html:
    if candidate_anchor not in html:
        raise SystemExit('Could not find streaming recommendation anchor')
    candidate_pool = r'''  function streamingCandidatePool(ctx) {
    const rostered=rosteredPlayerIds();
    const recentSelfDrops=recentlyDroppedByMeIds(24);
    return dynamicPlayerBoard()
      .filter(b=>b.player_id && !rostered.has(String(b.player_id)))
      .filter(b=>['QB','TE','K','DEF'].includes(b.pos))
      .filter(b=>!recentSelfDrops.has(String(b.player_id)))
      .sort((a,b)=>{
        const ap=projectedPointsForId(a.player_id), bp=projectedPointsForId(b.player_id);
        if(Number.isFinite(bp)&&Number.isFinite(ap)&&bp!==ap) return bp-ap;
        if(Number.isFinite(bp)&&!Number.isFinite(ap)) return -1;
        if(!Number.isFinite(bp)&&Number.isFinite(ap)) return 1;
        const ao=weeklyOutlookForPlayer(a.pdata||{})?.score, bo=weeklyOutlookForPlayer(b.pdata||{})?.score;
        if(Number.isFinite(bo)&&Number.isFinite(ao)&&bo!==ao) return bo-ao;
        if(Number.isFinite(bo)&&!Number.isFinite(ao)) return -1;
        if(!Number.isFinite(bo)&&Number.isFinite(ao)) return 1;
        return inSeasonMarketRank(a.pdata||{},a)-inSeasonMarketRank(b.pdata||{},b);
      });
  }

'''
    html = html.replace(candidate_anchor, candidate_pool + candidate_anchor, 1)

old_render_sig = '  function renderStreamerFinder(ctx,pool) {\n    const positions=[\'QB\',\'TE\',\'K\',\'DEF\'];'
new_render_sig = '  function renderStreamerFinder(ctx) {\n    const pool=streamingCandidatePool(ctx);\n    const positions=[\'QB\',\'TE\',\'K\',\'DEF\'];'
if old_render_sig in html:
    html = html.replace(old_render_sig, new_render_sig, 1)
elif new_render_sig not in html:
    raise SystemExit('Could not update renderStreamerFinder signature')

old_why = '''          <div class="whyline">${esc(r.reason)}${r.status==='STREAM'?' Roster-space decisions stay in Drop Review/Waiver Planner; this card never assumes the current starter should be dropped.':''}</div>\n        </div>'''
new_why = '''          <div class="whyline">${esc(r.reason)}${r.status==='STREAM'?' Roster-space decisions stay in Drop Review/Waiver Planner; this card never assumes the current starter should be dropped.':''}</div>\n          ${r.status==='STREAM'?`<button class="ghost streamerWaiverBtn" type="button" style="margin-top:7px;min-height:34px;padding:6px 9px">Review waiver move</button>`:''}\n        </div>'''
if old_why in html:
    html = html.replace(old_why, new_why, 1)
elif 'streamerWaiverBtn' not in html:
    raise SystemExit('Could not add streamer waiver handoff button')

old_render_end = '''    }).join('');\n    return rows;\n  }\n\n  function renderTradeIntelligence(ctx) {'''
new_render_end = '''    }).join('');\n    document.querySelectorAll('.streamerWaiverBtn').forEach(btn=>btn.addEventListener('click',()=>{\n      const target=$('weeklyClaims')?.closest('.card')||$('weeklyDrops')?.closest('.card');\n      target?.scrollIntoView({behavior:'smooth',block:'start'});\n    }));\n    return rows;\n  }\n\n  function renderTradeIntelligence(ctx) {'''
if old_render_end in html:
    html = html.replace(old_render_end, new_render_end, 1)
elif 'streamerWaiverBtn' not in html or 'scrollIntoView' not in html:
    raise SystemExit('Could not add streamer waiver handoff wiring')

html = html.replace('      renderStreamerFinder(ctx,pool);', '      renderStreamerFinder(ctx);', 1)

index_path.write_text(html, encoding='utf-8')

changelog = changelog_path.read_text(encoding='utf-8')
entry = '''## v2.18.1 — Streamer Candidate Pool Fix\n**2026-09-16**\n\n- Give Streamer Finder its own QB/TE/K/DEF candidate pool instead of reusing the normal waiver pool that intentionally suppresses backup-QB recommendations behind a strong QB1.\n- Always compare an incumbent QB such as Joe Burrow against actually unrostered streaming options before returning `HOLD`, rather than showing `no usable available comparison` solely because ordinary QB redundancy logic hid the candidates.\n- Keep the dedicated streaming pool free of ordinary QB/TE roster-redundancy penalties while preserving availability/usability screening inside the streaming recommendation itself.\n- Add a compact `Review waiver move` handoff to every `STREAM` result; the button scrolls to Waiver Planner/Drop Review and never auto-selects a player to cut.\n- Extend the permanent Weekly regression contract to require the dedicated streamer pool, prohibit strong-QB suppression inside it, verify the handoff wiring, and protect the updated Weekly pipeline.\n\n'''
if '## v2.18.1 — Streamer Candidate Pool Fix' not in changelog:
    marker = 'The project is currently in active beta development. Version numbers reflect iterative product updates rather than formal production releases.\n\n'
    if marker not in changelog:
        raise SystemExit('Could not find changelog insertion marker')
    changelog = changelog.replace(marker, marker + entry, 1)
    changelog_path.write_text(changelog, encoding='utf-8')

print('Applied v2.18.1 Streamer Candidate Pool Fix.')
