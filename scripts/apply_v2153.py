from pathlib import Path
import re

path = Path("index.html")
text = path.read_text(encoding="utf-8")

def one(old, new, label):
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected 1 occurrence, found {count}")
    text = text.replace(old, new, 1)

def sub_one(pattern, replacement, label, flags=0):
    global text
    text2, count = re.subn(pattern, replacement, text, count=1, flags=flags)
    if count != 1:
        raise SystemExit(f"{label}: expected 1 regex match, found {count}")
    text = text2

one(
    "Multi-manager beta • simulation + weekly intelligence • v2.15.2",
    "Multi-manager beta • in-season baselines + simulation • v2.15.3",
    "version subtitle",
)

one(
    "Weekly lineup, matchup, waiver, and roster-management command center. v2.15.2 adds a conservative pregame simulation layer for H2H and league-median probabilities while preserving the focused Weekly navigation and existing decision engines.",
    "Weekly lineup, matchup, waiver, and roster-management command center. v2.15.3 isolates preseason draft strategy from the in-season weekly and trade models while preserving projections, simulation, and focused Weekly navigation.",
    "weekly hero copy",
)

one(
    '<span class="pill good">Strategy data: Aug 30</span>',
    '<span class="pill good">Draft board snapshot: Aug 30</span>',
    "top strategy pill",
)
one(
    '<span class="pill warn">Strategy rankings: Aug 30 snapshot</span>',
    '<span class="pill good">In-season model: current</span>',
    "weekly strategy pill",
)

sub_one(
    r"""  function weeklyBaseValue\(b\) \{
\s*if\(!b\) return 1;
\s*const market=Math\.min\(Number\(b\.ecrRank\)\|\|999,Number\(b\.sleeperRank\)\|\|999\);
\s*let value=100-\(market-1\)\*0\.40;
\s*if\(b\.pos==='RB'\|\|b\.pos==='WR'\) value\+=2;
\s*if\(b\.news\) value\+=\(Number\(b\.news\.delta\)\|\|0\)\*0\.55;

\s*const p=b\.pdata\|\|\{\};
\s*const dc=Number\(p\.depth_chart_order\);""",
    """  function inSeasonMarketRank(p,b) {
    const sleeper=Number(b?.sleeperRank);
    const search=Number(p?.search_rank);
    const vals=[sleeper,search].filter(x=>Number.isFinite(x)&&x>0&&x<900);
    return vals.length?Math.min(...vals):220;
  }

  function weeklyBaseValue(b) {
    if(!b) return 1;
    const p=b.pdata||{};
    const market=inSeasonMarketRank(p,b);
    // Current Sleeper/search market rank is deliberately a light anchor.
    // Draft ECR and preseason news adjustments do not enter Normal Weekly value.
    let value=100-(Math.min(market,250)-1)*0.32;
    if(b.pos==='RB'||b.pos==='WR') value+=2;

    const dc=Number(p.depth_chart_order);""",
    "weekly base cleanup",
)

sub_one(
    r"""\s*if\(\(b\.pos==='RB'\|\|b\.pos==='WR'\) && ctx\.activeCounts\[b\.pos\]<5\) reasons\.push\(`\$\{b\.pos\} depth fits roster`\);
\s*if\(b\.news\?\.label\) reasons\.push\(b\.news\.label\.toLowerCase\(\)\);
\s*if\(\(b\.ecrRank\|\|999\)<=150\) reasons\.push\(`market rank \$\{b\.ecrRank\}`\);""",
    """
    if((b.pos==='RB'||b.pos==='WR') && ctx.activeCounts[b.pos]<5) reasons.push(`${b.pos} depth fits roster`);
    const currentMarketRank=inSeasonMarketRank(b.pdata||{},b);
    if(currentMarketRank<=150) reasons.push(`current market rank ${Math.round(currentMarketRank)}`);""",
    "weekly free-agent reasons",
)

one(
    ".sort((a,b)=>b.weeklyValue-a.weeklyValue || a.ecrRank-b.ecrRank);",
    ".sort((a,b)=>b.weeklyValue-a.weeklyValue || (mode==='postdraft'?a.ecrRank-b.ecrRank:inSeasonMarketRank(a.pdata||{},a)-inSeasonMarketRank(b.pdata||{},b)));",
    "weekly free-agent tie break",
)

one(
    """<div class="meta">${esc(b.team)} • ECR ${b.ecrRank} • Sleeper ${b.sleeperRank}${b.pdata?.injury_status?' • '+esc(b.pdata.injury_status):''}</div>""",
    """<div class="meta">${esc(b.team)} • current market ${Math.round(inSeasonMarketRank(b.pdata||{},b))}${state.weeklyMode==='postdraft'?` • draft ECR ${b.ecrRank}`:''}${b.pdata?.injury_status?' • '+esc(b.pdata.injury_status):''}</div>""",
    "best adds metadata",
)

one(
    ".filter(x=>!(x.pos==='TE' && ctx.counts.TE>=1 && !hasCoverageNeed(ctx,'TE') && x.ecrRank>60))",
    ".filter(x=>!(x.pos==='TE' && ctx.counts.TE>=1 && !hasCoverageNeed(ctx,'TE') && (post?x.ecrRank:inSeasonMarketRank(x.pdata||{},x))>60))",
    "weekly TE candidate filter",
)

sub_one(
    r"""  function tradeMarketRank\(p,b\) \{
\s*const ecr=Number\(b\?\.ecrRank\);
\s*const sleeper=Number\(b\?\.sleeperRank\);
\s*const search=Number\(p\?\.search_rank\);
\s*const vals=\[ecr,sleeper,search\]\.filter\(x=>Number\.isFinite\(x\)&&x>0&&x<900\);
\s*return vals\.length\?Math\.min\(\.\.\.vals\):220;
\s*\}""",
    """  function tradeMarketRank(p,b) {
    // Rest-of-season trade value uses current market rank, never the preseason draft ECR.
    return inSeasonMarketRank(p,b);
  }""",
    "trade market rank cleanup",
)

one(
    "v2.15.2 adds a pregame Monte Carlo probability cross-check, but its position-level variance assumptions are still heuristic rather than calibrated from historical projection errors; live in-game win probability, an independent second projection feed, route participation, and richer red-zone opportunity remain future layers.",
    "v2.15.2 adds a pregame Monte Carlo probability cross-check, but its position-level variance assumptions are still heuristic rather than calibrated from historical projection errors; live in-game win probability, an independent second projection feed, route participation, and richer red-zone opportunity remain future layers. v2.15.3 removes the Aug. 30 draft ECR and preseason news adjustments from Normal Weekly and Trade Intelligence baselines; those draft-era inputs remain isolated to Draft Day and immediate post-draft analysis.",
    "beta caveat cleanup copy",
)

one(
    "v2.15.2 weekly beta uses Aug. 29/30 half-PPR expert consensus for the top of the board, removes league keepers from the available-player market, and then personalizes recommendations to whichever manager connects: their keeper positions, drafted roster, traded picks, exact future-pick spacing, and close-pick leverage.",
    "v2.15.3 keeps the Aug. 29/30 half-PPR expert-consensus snapshot isolated to Draft Day and immediate post-draft analysis. Normal Weekly and Trade Intelligence use current Sleeper/search market rank as a lighter season-long anchor, then apply live role, usage, availability, current-news, game-context, projection, and roster-utility layers.",
    "footer baseline copy",
)

if "const ecrOverrides =" not in text or "const newsAdjustments =" not in text:
    raise SystemExit("Draft strategy snapshot was accidentally removed")
weekly_section = text[text.index("function weeklyBaseValue"):text.index("function postDraftMarketCutoff")]
if "b.news" in weekly_section or "b.ecrRank" in weekly_section:
    raise SystemExit("Stale draft signal remains in weeklyBaseValue section")
trade_section = text[text.index("function tradeMarketRank"):text.index("function tradeRankCurve")]
if "ecrRank" in trade_section or "const ecr=" in trade_section:
    raise SystemExit("Preseason ECR still enters tradeMarketRank")
if "Strategy rankings: Aug 30 snapshot" in text:
    raise SystemExit("Stale weekly strategy label remains")

path.write_text(text, encoding="utf-8")

changelog = Path("CHANGELOG.md")
cl = changelog.read_text(encoding="utf-8")
if "## v2.15.3 — In-Season Baseline Cleanup" not in cl:
    entry = """## v2.15.3 — In-Season Baseline Cleanup
**2026-09-15**

- Isolate the Aug. 29/30 expert-consensus ECR snapshot and embedded preseason news adjustments to Draft Day / immediate post-draft analysis.
- Remove preseason `newsAdjustments` from Normal Weekly scoring and free-agent rationale.
- Replace the Weekly base-value market anchor with current Sleeper/search market rank at a lighter weight, allowing live role, usage, availability, current news, game environment, weather, projections, and roster construction to carry more of the in-season decision signal.
- Remove stale draft ECR from Trade Intelligence market ranking while preserving its existing current usage, availability, news, age, position-scarcity, keeper, and roster-impact adjustments.
- Use current in-season market rank for normal-weekly free-agent tie breaks and TE-depth filtering; retain draft ECR only where the user explicitly runs the immediate Post-Draft scan.
- Change Best Available Adds metadata from preseason ECR-first wording to current market rank, with draft ECR shown only in Post-Draft mode.
- Replace the Weekly `Strategy rankings: Aug 30 snapshot` badge with `In-season model: current` and relabel the global snapshot badge as `Draft board snapshot: Aug 30`.
- Keep the v2.15 projection layer as an independent cross-check rather than silently making projected points the primary Weekly Outlook input.
- Preserve the v2.15.2 pregame simulation engine, league-median logic, navigation, positional coverage, waiver, and Start/Sit guardrails.

"""
    marker = "## v2.15.2 — Weekly Simulation Engine"
    if marker not in cl:
        raise SystemExit("v2.15.2 changelog marker not found")
    cl = cl.replace(marker, entry + marker, 1)
    changelog.write_text(cl, encoding="utf-8")
