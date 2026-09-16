#!/usr/bin/env python3
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "index.html"
text = path.read_text(encoding="utf-8")

old = """    return ranked.map(c=>{\n      if(slots>0) {\n        slots-=1;\n        return {...c,resource:'OPEN SLOT',dropName:null,blocked:false};\n      }\n      const safeDrop=String(c.safeDropName||'').trim();\n      if(safeDrop && !usedDrops.has(safeDrop)) {\n        usedDrops.add(safeDrop);\n        return {...c,resource:'SAFE DROP',dropName:safeDrop,blocked:false};\n      }\n      return {...c,resource:'BLOCKED — NO SAFE DROP',dropName:null,blocked:true};\n    });\n"""
new = """    const allocated=ranked.map(c=>{\n      if(slots>0) {\n        slots-=1;\n        return {...c,resource:'OPEN SLOT',dropName:null,blocked:false};\n      }\n      const safeDrop=String(c.safeDropName||'').trim();\n      if(safeDrop && !usedDrops.has(safeDrop)) {\n        usedDrops.add(safeDrop);\n        return {...c,resource:'SAFE DROP',dropName:safeDrop,blocked:false};\n      }\n      return {...c,resource:'BLOCKED — NO SAFE DROP',dropName:null,blocked:true};\n    });\n\n    return [\n      ...allocated.filter(c=>!c.blocked),\n      ...allocated.filter(c=>c.blocked)\n    ];\n"""

if text.count(old) != 1:
    raise SystemExit(f"allocator replacement expected 1 match, found {text.count(old)}")
text = text.replace(old, new, 1)

old_copy = "The higher-priority move consumes the available roster capacity and this move does not have a distinct protected churn path."
new_copy = "This move does not have remaining open-slot capacity or a distinct protected churn path."
if text.count(old_copy) != 1:
    raise SystemExit(f"blocked-copy replacement expected 1 match, found {text.count(old_copy)}")
text = text.replace(old_copy, new_copy, 1)

path.write_text(text, encoding="utf-8")
print("Applied executable-first v2.19 queue fix")
