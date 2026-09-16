from pathlib import Path

path = Path(__file__).resolve().parents[1] / "tests" / "weekly_contract_test.py"
text = path.read_text(encoding="utf-8")

old = '''    if "streamerWaiverBtn" not in streamer_render_body or "scrollIntoView" not in streamer_render_body:
        errors.append("stream recommendations must include a working Review waiver move handoff")
'''
new = '''    if "streamerWaiverBtn" not in streamer_render_body:
        errors.append("stream recommendations must include a Review waiver move control")
    if "scrollIntoView" not in streamer_render_body and "reviewStreamerWaiverMove(ctx,rows[index])" not in streamer_render_body:
        errors.append("stream recommendations must include a working Review waiver move handoff")
'''

count = text.count(old)
if count != 1:
    raise SystemExit(f"weekly contract handoff assertion: expected exactly one match, found {count}")

path.write_text(text.replace(old, new, 1), encoding="utf-8")
print("Updated Weekly contract for delegated streamer waiver handoff")
