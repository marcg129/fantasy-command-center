from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
index_path = ROOT / 'index.html'
changelog_path = ROOT / 'CHANGELOG.md'

html = index_path.read_text(encoding='utf-8')
html = html.replace('Multi-manager beta • week-aware management • v2.17.2', 'Multi-manager beta • week-aware management • v2.17.3', 1)
html = html.replace(
    'Weekly lineup, matchup, waiver, and roster-management command center. v2.17.2 restores the projection helpers required by Weekly Check while preserving simulation-confidence guardrails, calibration, lineup consensus, median strategy, and reliable usage.',
    'Weekly lineup, matchup, waiver, and roster-management command center. v2.17.3 adds automated Weekly regression contracts and Sleeper integration checks while preserving simulation-confidence guardrails, calibration, lineup consensus, median strategy, and reliable usage.',
    1,
)
index_path.write_text(html, encoding='utf-8')

changelog = changelog_path.read_text(encoding='utf-8')
entry = '''## v2.17.3 — Weekly Regression Tests
**2026-09-16**

- Add a permanent GitHub Actions regression workflow for Weekly-mode changes instead of relying only on manual post-deploy checks.
- Add a structural Weekly contract test that verifies the complete `loadWeekly()` dependency chain, critical projection/simulation helpers, required DOM anchors, Enter/Connect and Weekly Check event wiring, confidence-guardrail copy, and frontend JavaScript syntax.
- Explicitly protect the projection helpers whose accidental removal caused the v2.17.1 Weekly Check regression.
- Add a live Sleeper integration smoke test that verifies the configured league, manager, owned roster, current matchup endpoint, and the same-origin projection, usage, and calibration snapshots used by Weekly mode.
- Run the regression suite automatically for `index.html`, test, and regression-workflow changes, and on pull requests that touch those paths.
- Keep the suite intentionally lightweight and dependency-free so it can fail quickly before future Weekly changes are treated as validated.

'''
if '## v2.17.3 — Weekly Regression Tests' not in changelog:
    marker = 'The project is currently in active beta development. Version numbers reflect iterative product updates rather than formal production releases.\n\n'
    if marker not in changelog:
        raise SystemExit('Could not find changelog insertion marker')
    changelog = changelog.replace(marker, marker + entry, 1)
    changelog_path.write_text(changelog, encoding='utf-8')

print('Applied v2.17.3 regression-test release metadata.')
