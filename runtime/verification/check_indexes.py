"""Isolated PostgreSQL proof. Refuses execution outside GitHub-hosted Linux CI."""
import json
import os
import platform
from pathlib import Path
import psycopg

if os.environ.get('GITHUB_ACTIONS') != 'true' or platform.system() != 'Linux':
    raise SystemExit('Cloud CI only; never start or use a local-machine test database')
report = []
with psycopg.connect(os.environ['PROOF_DATABASE_URL'], autocommit=True) as db:
    for table, size in [('robotics_jobs', 28000), ('tech_jobs', 5500), ('team_jobs', 2300), ('jobs', 5500)]:
        db.execute(f'create table {table} (id bigint primary key, posted_at text, scraped_at timestamptz, is_active boolean, company text, title text)')
        db.execute(f"insert into {table} select i, case when i%%10=0 then null else (current_date-i%%90)::text end, now()-i*interval '1 minute', i%%3<>0, 'Fixture', 'Fixture' from generate_series(1,%s) i", (size,))
    db.execute(Path('db/migrations/20261114_job_read_indexes.sql').read_text())
    for table in ('robotics_jobs', 'tech_jobs', 'team_jobs', 'jobs'):
        db.execute(f'analyze {table}')
        for name, query, expected in [
            ('active_newest', f'select id,posted_at from {table} where is_active=true order by posted_at desc nulls last,id desc limit 50', table+'_active_newest_idx'),
            ('freshness', f'select scraped_at from {table} order by scraped_at desc nulls last limit 1', table+'_freshness_idx')]:
            plan = db.execute('explain (analyze,buffers,format json) '+query).fetchone()[0][0]
            encoded = json.dumps(plan)
            assert expected in encoded, (table, name, plan)
            assert '"Node Type": "Sort"' not in encoded, (table, name, plan)
            report.append({'table':table, 'query':name, 'index':expected, 'execution_ms':plan['Execution Time']})
    # Reapplying the migration must be harmless.
    db.execute(Path('db/migrations/20261114_job_read_indexes.sql').read_text())
Path('proof').mkdir(exist_ok=True)
Path('proof/index-tests.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
