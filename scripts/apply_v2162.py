from pathlib import Path
import re

index = Path('index.html')
text = index.read_text(encoding='utf-8')


def replace_once(old, new, label):
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 occurrence, found {count}')
    text = text.replace(old, new, 1)


replace_once(
    'Multi-manager beta • lineup consensus + reliable usage • v2.16.1',
    'Multi-manager beta • week-aware management • v2.16.2',
    'header version',
)

replace_once(
    'Weekly lineup, matchup, waiver, and roster-management command center. v2.16.1 keeps the two-model lineup consensus engine and moves nflverse usage into a same-origin automated snapshot so current-season workload data can load reliably in the browser.',
    'Weekly lineup, matchup, waiver, and roster-management command center. v2.16.2 resolves the active management week from Sleeper plus fresh same-season data snapshots, while preserving manual week selection, lineup consensus, simulation, and reliable usage.',
    'weekly hero copy',
)

pattern = re.compile(
    r"  function currentSleeperWeek\(nfl=state\.nflState\) \{.*?\n  \}\n\n  async function syncWeekToSleeperCurrent\(\) \{.*?\n  \}\n",
    re.S,
)
replacement = r'''  function validWeekNumber(value) {
    const week=Number(value);
    return Number.isFinite(week) && week>=1 && week<=18 ? Math.floor(week) : null;
  }

  function currentSleeperWeek(nfl=state.nflState) {
    // Sleeper's `week` / `leg` are the official state values. `display_week`
    // is deliberately allowed by Sleeper to differ, so keep it as fallback only.
    for(const value of [nfl?.week,nfl?.leg,nfl?.display_week]) {
      const week=validWeekNumber(value);
      if(week) return week;
    }
    return null;
  }

  function snapshotWeekHint(data,nfl,maxAgeHours) {
    const candidate=validWeekNumber(data?.week);
    if(!candidate) return null;

    const currentSeason=String(nfl?.season||state.league?.season||'');
    if(currentSeason && String(data?.season||'')!==currentSeason) return null;

    const generated=Date.parse(data?.generated_at||'');
    if(!Number.isFinite(generated)) return null;
    const ageHours=(Date.now()-generated)/36e5;
    if(ageHours < -1 || ageHours > maxAgeHours) return null;
    return candidate;
  }

  async function resolveCurrentAnalysisWeek(nfl=state.nflState) {
    const sleeperWeek=currentSleeperWeek(nfl);
    let projectionWeek=null;
    let usageWeek=null;

    // A fresh same-season projection or usage snapshot can legitimately roll to
    // the upcoming fantasy-management week before Sleeper's raw state pill does.
    // Only accept a hint at the same week or one week ahead to avoid bad/stale data.
    try {
      const data=await jget(projectionFileUrl());
      const hint=snapshotWeekHint(data,nfl,12);
      if(hint && (!sleeperWeek || (hint>=sleeperWeek && hint<=sleeperWeek+1))) {
        projectionWeek=hint;
        state.projectionFeed=data||state.projectionFeed;
      }
    } catch(e) {}

    try {
      const data=await jget(`./data/usage.json?ts=${Date.now()}`);
      const hint=snapshotWeekHint(data,nfl,18);
      if(hint && (!sleeperWeek || (hint>=sleeperWeek && hint<=sleeperWeek+1))) usageWeek=hint;
    } catch(e) {}

    const hints=[sleeperWeek,projectionWeek,usageWeek].filter(Boolean);
    const analysisWeek=hints.length?Math.max(...hints):null;
    let source='sleeper';
    if(analysisWeek && sleeperWeek && analysisWeek>sleeperWeek) {
      source=(projectionWeek===analysisWeek && usageWeek===analysisWeek)
        ? 'projection+usage'
        : (projectionWeek===analysisWeek?'projection':'usage');
    } else if(!sleeperWeek && analysisWeek) {
      source=projectionWeek===analysisWeek?'projection':'usage';
    }

    state.weekResolution={analysisWeek,sleeperWeek,projectionWeek,usageWeek,source};
    return analysisWeek;
  }

  function renderWeeklyWeekStatus(selectedWeek=state.weeklyWeek) {
    const nfl=state.nflState;
    const sleeperWeek=currentSleeperWeek(nfl);
    const resolved=state.weekResolution?.analysisWeek||sleeperWeek||validWeekNumber(selectedWeek);
    const selected=validWeekNumber(selectedWeek)||resolved;
    const seasonType=String(nfl?.season_type||'NFL').toLowerCase();

    let label='NFL state —';
    let kind='warn';
    if(resolved && selected && selected!==resolved) {
      label=`${seasonType} • selected W${selected} • current W${resolved}`;
      kind='warn';
    } else if(resolved && sleeperWeek && resolved!==sleeperWeek) {
      label=`${seasonType} • analysis W${resolved} • Sleeper state W${sleeperWeek}`;
      kind='good';
    } else if(resolved) {
      label=`${seasonType} • NFL week ${resolved}`;
      kind='good';
    } else if(selected) {
      label=`Week ${selected}`;
    }
    setPill('weeklyStatePill',label,kind);
  }

  async function syncWeekToSleeperCurrent() {
    try {
      const nfl=await jget(`${BASE}/state/nfl`);
      if(nfl) state.nflState=nfl;
      const week=await resolveCurrentAnalysisWeek(nfl);
      if(week) {
        state.weeklyWeek=week;
        if($('weekInput')) $('weekInput').value=String(week);
      }
      return week;
    } catch(e) {
      console.warn('Could not prefill current management week',e);
      return null;
    }
  }
'''
text, count = pattern.subn(replacement, text, count=1)
if count != 1:
    raise SystemExit(f'week resolver block: expected 1 replacement, found {count}')

old_status = "      const nfl=state.nflState;\n      setPill('weeklyStatePill',nfl?`${nfl.season_type||''} • NFL week ${nfl.display_week||nfl.week||week}`:`Week ${week}`,nfl?'good':'warn');"
new_status = "      await resolveCurrentAnalysisWeek(state.nflState);\n      renderWeeklyWeekStatus(week);"
replace_once(old_status, new_status, 'weekly state pill')

# Update the footer/caveat version where present without depending on its whole sentence.
text = text.replace('v2.16.1 keeps the Aug. 29/30 half-PPR expert-consensus snapshot isolated to Draft Day and immediate post-draft analysis.',
                    'v2.16.2 keeps the Aug. 29/30 half-PPR expert-consensus snapshot isolated to Draft Day and immediate post-draft analysis.', 1)

required = [
    'resolveCurrentAnalysisWeek',
    'analysis W${resolved} • Sleeper state W${sleeperWeek}',
    'selected W${selected} • current W${resolved}',
    'projection+usage',
    'week-aware management • v2.16.2',
]
for needle in required:
    if needle not in text:
        raise SystemExit(f'missing semantic marker: {needle}')

index.write_text(text, encoding='utf-8')

changelog = Path('CHANGELOG.md')
cl = changelog.read_text(encoding='utf-8')
if '## v2.16.2 — Current Week Resolution' not in cl:
    entry = '''## v2.16.2 — Current Week Resolution
**2026-09-15**

- Resolve the default Weekly management week from Sleeper's official NFL state plus fresh same-season projection and usage snapshots instead of assuming the raw state pill is always the best management-week signal.
- Allow a fresh projection/usage snapshot to move the default at most one week ahead when Sleeper's raw state is still on the prior week, preventing Week 2 analysis from reconnecting to Week 1.
- Keep the Week field fully editable; a manually selected historical/future week is never overwritten by a normal Weekly check.
- Make the NFL-state pill explicit when values differ: it can show `analysis W2 • Sleeper state W1`, or `selected W3 • current W2` for a manual override, instead of misleadingly labeling the selected analysis as the raw Sleeper week.
- Prefer Sleeper `week` / `leg` as official state fields and treat `display_week` only as a fallback because Sleeper permits display week to differ from the underlying week.
- Preserve v2.16.1 usage snapshots, v2.16 lineup consensus, projections, simulation, league median, waiver, trade, news, and availability behavior.

'''
    marker = '## v2.16.1 — Usage Snapshot Reliability'
    if marker not in cl:
        raise SystemExit('v2.16.1 changelog marker missing')
    cl = cl.replace(marker, entry + marker, 1)
    changelog.write_text(cl, encoding='utf-8')
