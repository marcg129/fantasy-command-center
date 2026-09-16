from pathlib import Path

path = Path(__file__).resolve().parents[1] / "index.html"
text = path.read_text(encoding="utf-8")

old = """    const keepValue=drop?effectiveKeepValue(drop,ctx):null;
    let gap=drop && Number.isFinite(Number(add.weeklyValue))
      ? Number(add.weeklyValue)-keepValue
      : null;
"""
new = """    const keepValue=drop?effectiveKeepValue(drop,ctx):null;
    const addMap=trendMap(state.trendingAdds);
    const dropMap=trendMap(state.trendingDrops);
    const addValue=freeAgentScore(add,ctx,addMap,dropMap,state.weeklyMode);
    let gap=drop && Number.isFinite(addValue)
      ? addValue-keepValue
      : null;
"""
count = text.count(old)
if count != 1:
    raise SystemExit(f"streamer handoff value source: expected exactly one match, found {count}")
text = text.replace(old, new, 1)

old_return = """      add,drop,openSlots,keepValue,gap,reviewCut,safeDrop,
"""
new_return = """      add,drop,openSlots,keepValue,addValue,gap,reviewCut,safeDrop,
"""
count = text.count(old_return)
if count != 1:
    raise SystemExit(f"streamer handoff return value: expected exactly one match, found {count}")
text = text.replace(old_return, new_return, 1)

path.write_text(text, encoding="utf-8")
print("Applied v2.18.3 streamer roster-value fix")
