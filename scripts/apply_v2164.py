from pathlib import Path

index_path = Path('index.html')
changelog_path = Path('CHANGELOG.md')

html = index_path.read_text(encoding='utf-8')

old_listener = "  $('connectBtn').addEventListener('click',connect);\n"
new_listener = old_listener + "  $('myName').addEventListener('keydown',e=>{\n    if(e.key!=='Enter') return;\n    e.preventDefault();\n    if(!$('connectBtn').disabled) connect();\n  });\n"

if "$('myName').addEventListener('keydown'" not in html:
    if html.count(old_listener) != 1:
        raise SystemExit(f'Expected exactly one Connect listener, found {html.count(old_listener)}')
    html = html.replace(old_listener, new_listener, 1)

html = html.replace('Multi-manager beta • week-aware management • v2.16.3',
                    'Multi-manager beta • week-aware management • v2.16.4', 1)
html = html.replace('Weekly lineup, matchup, waiver, and roster-management command center. v2.16.3 resolves the active management week from Sleeper plus fresh same-season data snapshots, while preserving manual week selection, lineup consensus, simulation, and reliable usage.',
                    'Weekly lineup, matchup, waiver, and roster-management command center. v2.16.4 adds keyboard-friendly Sleeper connection while preserving current-week resolution, lineup consensus, simulation, and reliable usage.', 1)

index_path.write_text(html, encoding='utf-8')

changelog = changelog_path.read_text(encoding='utf-8')
entry = """## v2.16.4 — Enter-to-Connect Shortcut
**2026-09-16**

- Allow pressing `Enter` in the Sleeper username / display-name field to run the same connection flow as clicking the Connect button.
- Prevent the keyboard shortcut from submitting twice while a connection attempt is already in progress.
- Preserve the existing Connect button, manager datalist suggestions, current-week resolution, weekly navigation, lineup consensus, simulation, median strategy, usage, waivers, trades, news, weather, and availability behavior.

"""
if '## v2.16.4 — Enter-to-Connect Shortcut' not in changelog:
    marker = '## v2.16.3 — Median Strategy Integration\n'
    if marker not in changelog:
        raise SystemExit('Could not find v2.16.3 changelog marker')
    changelog = changelog.replace(marker, entry + marker, 1)
    changelog_path.write_text(changelog, encoding='utf-8')
