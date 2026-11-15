"""Cloud-only read of three affected career sources; no storage or notification calls."""
import datetime as dt
import json
import os
from pathlib import Path
import time
from jobradar.fetch_worker import fetch_provider
from jobradar.providers.workday import WorkdayProvider

if os.environ.get('GITHUB_ACTIONS') != 'true':
    raise SystemExit('Cloud CI only')
results = []
for slug in ('bostondynamics','autostore','rockwellautomation'):
    started = time.monotonic()
    item = {'source':slug, 'observed_at':dt.datetime.now(dt.timezone.utc).isoformat()}
    try:
        jobs = fetch_provider(WorkdayProvider(slug), 'recovery-read-only-proof', timeout=180)
        assert jobs and len({j.url for j in jobs}) == len(jobs)
        item.update(passed=True, jobs=len(jobs))
    except Exception as exc:
        item.update(passed=False, error=str(exc)[-1200:])
    item['seconds'] = round(time.monotonic()-started, 3)
    results.append(item)
Path('proof').mkdir(exist_ok=True)
Path('proof/workday-live.json').write_text(json.dumps(results, indent=2))
print(json.dumps(results, indent=2))
raise SystemExit(0 if all(r['passed'] for r in results) else 1)
