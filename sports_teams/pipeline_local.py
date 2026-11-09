#!/usr/bin/env python3
"""Live HTTP sources -> SQLite tracking -> local board and dashboard feed.

Why: announcements and the board must answer "is this a NEW job or one we already track?".
Supabase has no team_jobs table yet (service key missing), so this keeps the same contract in a
local SQLite file. When the key lands, `db/schema_team_jobs.sql` replaces this with no field changes.

    python pipeline_local.py            # refresh supported live sources -> db -> board + feed
    python pipeline_local.py --stats    # just print the state

Table mirrors public.team_jobs:  unique(team, url), first_seen_at, last_seen_at, is_active, logo_url.
"""
from __future__ import annotations

import argparse
import os
import uuid
import json
import re
import sqlite3
import sys
import unicodedata
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROOFS = Path(r'D:\abet_ops\proofs')
DB = ROOT / 'data' / 'team_jobs.db'
BOARD = ROOT / 'board'
DASH_FEED = Path(r'D:\abet_ops\abet-dashboard\public\data\team_jobs.json')
NEW_WINDOW_HOURS = 48

import importlib.util
spec = importlib.util.spec_from_file_location('pt', ROOT / 'publish_teams.py')
pt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pt)

SCHEMA = """
create table if not exists team_jobs (
    id integer primary key autoincrement,
    league text not null,
    team text not null,
    title text not null,
    url text not null,
    location text,
    description text,
    platform text,
    posted_at text,
    first_seen_at text not null,
    last_seen_at text,
    is_active integer not null default 1,
    closed_at text,
    logo_url text,
    unique(team, url)
);
create index if not exists team_jobs_league on team_jobs(league);
create index if not exists team_jobs_first_seen on team_jobs(first_seen_at);
create table if not exists team_job_scrape_runs (
    id integer primary key autoincrement,
    source text not null,
    platform text,
    status text not null,
    job_count integer not null default 0,
    duration_ms integer,
    error_summary text,
    created_at text not null
);
"""


def now():
    return datetime.now(timezone.utc).isoformat()


def connect():
    DB.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB)
    con.executescript(SCHEMA)
    return con


def ingest(con, rows, record_runs=True):
    new = updated = 0
    for r in rows:
        if not r.get('platform'):
            portal = (r.get('portal') or '') + ' ' + (r.get('url') or '')
            for host in ('teamworkonline', 'myworkdayjobs', 'greenhouse', 'lever',
                         'ultipro', 'adp', 'dayforce'):
                if host in portal:
                    r['platform'] = 'workday' if host == 'myworkdayjobs' else host
                    break
        team_display = pt._display_team(r)
        league = (r.get('league') or '').upper()
        url = r.get('url')
        if not url:
            continue
        title = pt._clean_text(r.get('title'))[:500]
        loc = pt._clean_text(r.get('location'))[:300]
        desc = pt._clean_text(r.get('description'))[:50000]
        posted = pt._iso(r.get('posted_at'))
        logo = pt.logo_for(r)
        cur = con.execute('select id, first_seen_at from team_jobs where url=? order by id limit 1', (url,))
        hit = cur.fetchone()
        if hit:
            con.execute('''update team_jobs set league=?, title=?, location=?, description=case when length(?)>length(coalesce(description,'')) or length(?)>length(coalesce(description,'')) then ? else description end,
                           platform=?, posted_at=coalesce(?,posted_at), last_seen_at=?, is_active=1, closed_at=null,
                           logo_url=? where id=?''',
                        (league, title, loc, desc, desc, desc, r.get('platform'), posted, r.get('scraped_at') or now(), logo, hit[0]))
            updated += 1
        else:
            con.execute('''insert into team_jobs (league, team, title, url, location, description,
                           platform, posted_at, first_seen_at, last_seen_at, is_active, logo_url)
                           values (?,?,?,?,?,?,?,?,?,?,1,?)''',
                        (league, team_display, title, url, loc, desc, r.get('platform'),
                         posted, now(), r.get('scraped_at') or now(), logo))
            new += 1
        if record_runs:
            con.execute('''insert into team_job_scrape_runs (source, platform, status, job_count, created_at)
                           values (?,?,?,?,?)''',
                        (f"{league}:{team_display}", r.get('platform'), 'legacy_import', 1, now()))
    con.commit()
    return new, updated


def deactivate_missing(con, live_urls):
    if not live_urls:
        return 0
    marks = ','.join('?' * len(live_urls))
    cur = con.execute(f'update team_jobs set is_active=0, closed_at=? '
                      f'where is_active=1 and url not in ({marks})', (now(), *live_urls))
    con.commit()
    return cur.rowcount


def snapshot(con):
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=NEW_WINDOW_HOURS)).isoformat()
    con.row_factory = sqlite3.Row
    rows = con.execute('select * from team_jobs where is_active=1').fetchall()
    jobs = []
    for raw in rows:
        row = dict(raw)
        row.update(company=row['team'], ats=row['platform'], logo=row['logo_url'],
                   new=bool(row['first_seen_at'] and row['first_seen_at'] >= cutoff))
        jobs.append(row)
    return jobs


def write_outputs(jobs):
    by_league = Counter(j['league'] or 'UNKNOWN' for j in jobs)
    by_platform = Counter(j['platform'] or 'unknown' for j in jobs)
    payload = {
        'schema': 'abet.teams.board.v1',
        'generated_at': now(),
        'count': len(jobs),
        'new_count': sum(1 for j in jobs if j['new']),
        'by_league': dict(by_league),
        'by_platform': dict(by_platform),
        'jobs': sorted(jobs, key=lambda j: (j['league'], j['team'], j['title'])),
    }
    BOARD.mkdir(exist_ok=True)
    encoded=json.dumps(payload,indent=1)
    temp=BOARD/'team_jobs.tmp';temp.write_text(encoded,encoding='utf-8');temp.replace(BOARD/'team_jobs.json')
    if DASH_FEED.parent.exists():
        temp=DASH_FEED.with_suffix('.tmp');temp.write_text(encoded,encoding='utf-8');temp.replace(DASH_FEED)
    return payload


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--stats', action='store_true')
    ap.add_argument('--backfill-first-seen', action='store_true')
    ap.add_argument('--cloud', action='store_true')
    ap.add_argument('--detail-limit', type=int, default=250)
    ap.add_argument('--trigger', default='manual')
    args = ap.parse_args()
    con = connect()
    cloud = None
    if args.cloud:
        from cloud_storage import CloudStorage
        cloud = CloudStorage()
        print('Restored cloud observations:', cloud.restore(con), flush=True)
        write_outputs(snapshot(con))
    if args.stats:
        total = con.execute('select count(*) from team_jobs').fetchone()[0]
        active = con.execute('select count(*) from team_jobs where is_active=1').fetchone()[0]
        print(f'db={DB}\nrows={total} active={active}')
        return 0

    if args.backfill_first_seen:
        ap.error('first_seen_at is an observation time and must not be overwritten with posted_at')

    # This bounded HTTP/data pipeline starts no agents or browsers. The existing
    # machine stop switch continues to govern agents/browsers and publishing.
    import live_refresh
    results, discovery = live_refresh.collect(pt)
    new, updated, closed = live_refresh.apply_results(con, results, sys.modules[__name__])
    run_id=str(uuid.uuid4())
    if cloud:
        print('Persisted listings:',cloud.persist(con,results,run_id,args.trigger),flush=True)
    write_outputs(snapshot(con))
    print('[DETAILS] Starting cached description enrichment',flush=True)
    import enrichment
    details = enrichment.enrich(con, limit=args.detail_limit)
    if cloud:
        print('Persisted cloud rows:', cloud.persist(con,results,run_id,args.trigger), flush=True)
    audit = {'checked_at': now(), 'discovery': discovery, 'details':details,
             'sources': [{k: v for k, v in r.items() if k != 'rows'} | {'job_count': len(r['rows'])} for r in results]}
    audit_path = ROOT / 'data' / 'latest_refresh_audit.json'
    audit_path.write_text(json.dumps(audit, indent=2), encoding='utf-8')
    jobs = snapshot(con)
    payload = write_outputs(jobs)
    failed = sum(r['status'] != 'success' for r in results)
    manifest = {'schema':'abet.jobs.scrape-manifest.v1','generated_at':now(),
        'overall_status':'degraded' if failed or any(r['status']!='success' for r in discovery) else 'healthy',
        'providers':audit['sources'],'discovery':discovery,'details':details,
        'totals':{'providers':len(results),'successful':len(results)-failed,'failed':failed,'active_jobs':len(jobs),'new':new,'updated':updated,'closed':closed},
        'persistence':'supabase' if cloud else 'sqlite','trigger':args.trigger}
    manifest_path=ROOT/'data/runtime/latest_scrape_manifest.json'
    manifest_path.parent.mkdir(parents=True,exist_ok=True)
    temp=manifest_path.with_suffix('.tmp');temp.write_text(json.dumps(manifest,indent=2),encoding='utf-8');temp.replace(manifest_path)
    print(f'live sources={len(results)} -> new={new} updated={updated} deactivated={closed}')
    print(f'db rows active={len(jobs)} new(<= {NEW_WINDOW_HOURS}h)={payload["new_count"]}')
    print('by league:', payload['by_league'])
    print('by platform:', payload['by_platform'])
    return 0 if any(r['status']=='success' for r in results) else 1


if __name__ == '__main__':
    raise SystemExit(main())
