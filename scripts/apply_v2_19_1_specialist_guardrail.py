#!/usr/bin/env python3
from pathlib import Path

path = Path('index.html')
source = path.read_text(encoding='utf-8')

old = """    // K/DEF are normally streamed as direct one-for-one roster replacements once
    // the football recommendation already clears its streaming threshold. QB/TE
    // incumbents must also be expendable on post-swap roster value so a one-week
    // edge never turns into an automatic Joe Burrow-style drop.
    const justified=['K','DEF'].includes(pos)
      ? (Number.isFinite(projectionEdge) && projectionEdge>=threshold)
      : (Number.isFinite(gap) && gap>=reviewCut);
"""

new = """    // K/DEF get a more permissive post-swap roster-value guardrail than QB/TE,
    // because carrying two specialists has a real opportunity cost. Projection
    // threshold alone is still not enough to auto-cut an incumbent with clearly
    // stronger retained value.
    const projectionClears=Number.isFinite(projectionEdge) && projectionEdge>=threshold;
    const specialistValueFloor=-Math.max(5,reviewCut);
    const specialistValueOkay=Number.isFinite(gap) && gap>=specialistValueFloor;
    const justified=['K','DEF'].includes(pos)
      ? (projectionClears && specialistValueOkay)
      : (Number.isFinite(gap) && gap>=reviewCut);
"""

if old not in source:
    raise SystemExit('expected direct-replacement guardrail block not found')

source = source.replace(old, new, 1)
path.write_text(source, encoding='utf-8')
