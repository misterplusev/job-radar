"""Static documentation inspection only: Git objects/AST; never import scraper code.

Uses existing checkouts and bounded GitHub reads. Writes only this audit's inventory.
It does not execute providers, tests, browsers, database processes or deployments.
"""
import json
import runpy
from pathlib import Path

ROOT = Path(r'D:\abet_ops\jobs_scrapers')
DEST = Path(__file__).resolve().parent / 'source_inventory'
DEST.mkdir(parents=True, exist_ok=True)
mod = runpy.run_path(str(ROOT / 'generate_inventory.py'))
mod['write'].__globals__['OUT'] = DEST
mod['eligible'].__globals__['GENERATED'] += ('docs/job-scrapers/20261114_documentation_audit/',)
base = ROOT / '20261112_1130_stabilization_release' / 'repositories'
configs = [
    ('robotics-and-teams', 'misterplusev/job-radar', str(base/'job-radar'), 'origin/master'),
    ('tech', 'misterplusev/job-radar-tech', str(base/'job-radar-tech'), 'origin/master'),
    ('sportsbook-runtime', 'misterplusev/sportsbook-jobs-dashboard', str(base/'sportsbook-jobs-dashboard'), 'origin/prod/sportsbook-jobs'),
    ('sportsbook-frontend', 'misterplusev/sportsbook-jobs-dashboard', str(base/'sportsbook-jobs-dashboard'), 'origin/main'),
    ('abet-dashboard', 'misterplusev/abet-mlb-monitor-widgets', r'D:\abet_ops\abet-dashboard', 'origin/main'),
]
sources = []
for args in configs:
    entry = mod['git_inventory'](*args)
    entry['inspection_status'] = 'Fresh static repository snapshot; not by itself deployed-bundle parity proof'
    sources.append(entry)
    print(entry['id'], entry['revision'], len(entry['files']), flush=True)
for label, repo in [('robotics-standalone','misterplusev/robotics-jobradar-board'),('tech-standalone','misterplusev/jobradar-tech-board')]:
    entry = mod['remote_inventory'](label, repo, 'main')
    entry['inspection_status'] = 'Fresh GitHub snapshot; not by itself deployed-bundle parity proof'
    sources.append(entry)
    print(label, entry['revision'], len(entry['files']), flush=True)
mod['write'](sources)
path = DEST/'README.md'
text = path.read_text(encoding='utf-8').replace('# Source inventory — November 10, 2026', '# Repository source inventory — November 14, 2026 Pacific')
text = text.replace('[Live database dictionary](DATABASE.md) · [PostgreSQL catalog](database_catalog.json) · [SQLite catalog](sqlite_catalog.json) · ', '')
text = text.replace('All tracked files in listed source snapshots; source text line counts and symbol locations; operator helper overlay. Generated datasets/binaries/private files are metadata only. Dashboard repository inventory includes unrelated modules but deployment dependency map isolates jobs.', 'All tracked files in seven fresh repository snapshots, with line counts and symbol locations where eligible. Generated datasets/binaries/private files are metadata only. Dashboard totals include unrelated modules. Operator helpers and deployed Worker/Space bundles are not refreshed by this inventory.')
text += '\n## Boundaries\n\nPython symbols are parsed with AST; JavaScript declarations are a text scan, not an exhaustive semantic call graph. The dashboard inventory includes unrelated modules. Remote heads and source snapshots do not by themselves prove a hosted deployment uses that revision. Cloud Worker bundles, the Hugging Face deployment and operator helpers are separately documented in the operator appendix and dated system reference. Metadata-only exclusions are recorded per file. No credential values or personal job-hunt files are included.\n'
path.write_text(text, encoding='utf-8')
machine_path = DEST/'source_inventory.json'
machine = json.loads(machine_path.read_text(encoding='utf-8'))
machine['scope'] = 'Seven fresh repository snapshots; operator helpers and deployed Worker/Space bundles excluded from this refresh. Counts include eligible source, tests, documentation and configuration; they are not runtime-code-only LOC.'
machine_path.write_text(json.dumps(machine, indent=2)+'\n', encoding='utf-8')
counts = [{
    'source': s['id'], 'revision': s['revision'], 'files': len(s['files']),
    'counted_files': sum(r.get('lines') is not None for r in s['files']),
    'physical_lines': sum(r.get('lines') or 0 for r in s['files']),
    'symbols': sum(len(r.get('symbols', [])) for r in s['files']),
} for s in sources]
(DEST/'counts.json').write_text(json.dumps(counts, indent=2)+'\n', encoding='utf-8')
print(json.dumps(counts), flush=True)
