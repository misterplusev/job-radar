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


def shown_under(pt, r):
    """(team, league, logo, company, teams) for one scraped row.

    Many clubs do not run their own careers site: their owner does ("Groupe CH" for the Montreal Canadiens,
    "Maple Leaf Sports & Entertainment" for the Maple Leafs and the Raptors). The site names the owner, the
    board has no logo for an owner, and the club itself showed 0 jobs (541 of 1,422 active jobs on 2026-11-19).
    When the name the site gives is not a club we know, the job is shown under the club(s) the registry lists
    that careers site for. `company` keeps the name the site gives. `teams` is filled only when the site
    belongs to more than one club: the job is stored once and shown under each of them.
    """
    team, league, logo = pt._display_team(r), (r.get('league') or '').upper(), pt.logo_for(r)
    company, teams = team, None
    if logo is not None:
        return team, league, logo, company, teams

    def club(league_name, name):
        shown = pt._display_team({'league': league_name, 'team': name})
        return {'league': (league_name or '').upper(), 'team': shown, 'logo': pt.logo_for({'league': league_name, 'team': shown})}
    registered = [club(c.get('league'), c.get('team')) for c in (r.get('registered_teams') or [])]
    # A name such as "New Jersey Devils & Prudential Center" or "Miami Dolphins & Hard Rock Stadium" names a club
    # in full. That club is the employer even on another club's careers site (the Devils on the 76ers' owner's
    # site), unless it is one of several clubs the site is registered for (then the job belongs to all of them).
    wanted = pt._norm(team)
    named = [club(key.partition(':')[0], key.partition(':')[2]) for key in pt.LOGO_MAP
             if len(pt._norm(key.partition(':')[2])) >= 8 and pt._norm(key.partition(':')[2]) in wanted]
    registered_names = {c['team'] for c in registered}
    clubs = named if named and not (len(registered) > 1 and {c['team'] for c in named} <= registered_names) else registered
    clubs = [c for c in clubs if c['logo']]
    if clubs:
        team, league, logo = clubs[0]['team'], clubs[0]['league'], clubs[0]['logo']
        teams = clubs if len(clubs) > 1 else None
    return team, league, logo, company, teams


def rename_stored_owner_rows(con, pt, sources):
    """Apply the naming rule to stored jobs that no run re-reads; returns the number of rows changed.

    ingest() names a job when a source lists it. A closed job is never listed again, and a job whose source
    failed in this run is not listed either, so both kept the owner's name and no logo (420 closed and 6 open
    rows after the first run of the rule on 2026-11-19), and the board showed a team button for each owner.
    """
    columns = {c[1] for c in con.execute('pragma table_info(team_jobs)')}
    for name in ('company', 'teams', 'source_id'):
        if name not in columns:
            con.execute(f'alter table team_jobs add column {name} text')
    changed = 0
    for row_id, league, team, company, source_id in con.execute(
            "select id, league, team, coalesce(company, team), source_id from team_jobs where logo_url is null or logo_url=''").fetchall():
        source = sources.get(source_id)
        if not source:
            continue
        shown, shown_league, logo, owner, teams = shown_under(
            pt, {'league': league, 'team': company, 'registered_teams': source.get('registered_teams') or []})
        if logo and shown != team:
            con.execute('update team_jobs set team=?, league=?, logo_url=?, company=?, teams=? where id=?',
                        (shown, shown_league, logo, owner, json.dumps(teams) if teams else None, row_id))
            changed += 1
    con.commit()
    return changed


def ingest(con, rows, record_runs=True):
    new = updated = 0
    columns = {c[1] for c in con.execute('pragma table_info(team_jobs)')}
    for name in ('company', 'teams'):
        if name not in columns:
            con.execute(f'alter table team_jobs add column {name} text')
    for r in rows:
        if not r.get('platform'):
            portal = (r.get('portal') or '') + ' ' + (r.get('url') or '')
            for host in ('teamworkonline', 'myworkdayjobs', 'greenhouse', 'lever',
                         'ultipro', 'adp', 'dayforce'):
                if host in portal:
                    r['platform'] = 'workday' if host == 'myworkdayjobs' else host
                    break
        team_display, league, logo, company, teams = shown_under(pt, r)
        teams_json = json.dumps(teams) if teams else None
        url = r.get('url')
        if not url:
            continue
        title = pt._clean_text(r.get('title'))[:500]
        loc = pt._clean_text(r.get('location'))[:300]
        desc = pt._clean_text(r.get('description'))[:50000]
        platform = r.get('platform')
        if platform == 'teamworkonline' and desc.casefold() in (
            team_display.casefold(), pt._clean_text(r.get('team')).casefold()
        ):
            desc = ''
        posted = pt._iso(r.get('posted_at'))
        cur = con.execute('''select id, platform='teamworkonline' and length(trim(description))>0
                       and lower(trim(description))=lower(trim(team)) as stored_team_label
                       from team_jobs where url=? order by id limit 1''', (url,))
        hit = cur.fetchone()
        if hit:
            replace_description = (platform in ('greenhouse','adp') and len(desc)>=80) or (
                platform == 'teamworkonline' and hit[1]
            )
            con.execute('''update team_jobs set league=?, team=?, title=?, location=?, description=case when length(?)>length(coalesce(description,'')) or ? then ? else description end,
                           platform=?, posted_at=coalesce(?,posted_at), last_seen_at=?, is_active=1, closed_at=null,
                           logo_url=?, company=?, teams=? where id=?''',
                        (league, team_display, title, loc, desc, replace_description, desc, r.get('platform'), posted, r.get('scraped_at') or now(), logo, company, teams_json, hit[0]))
            updated += 1
        else:
            con.execute('''insert into team_jobs (league, team, title, url, location, description,
                           platform, posted_at, first_seen_at, last_seen_at, is_active, logo_url, company, teams)
                           values (?,?,?,?,?,?,?,?,?,?,1,?,?,?)''',
                        (league, team_display, title, url, loc, desc, r.get('platform'),
                         posted, now(), r.get('scraped_at') or now(), logo, company, teams_json))
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
    ap.add_argument('--recover-pending', action='store_true',help='Recover missed individual alerts from earlier paused scrapes')
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
    prior_urls={r[0] for r in con.execute('select url from team_jobs')}
    results, discovery = live_refresh.collect(pt)
    new, updated, closed = live_refresh.apply_results(con, results, sys.modules[__name__],
                                                    live_refresh.retired_replacements(pt),
                                                    registered_sources=set(live_refresh.build_sources(pt)))
    renamed = rename_stored_owner_rows(con, pt, live_refresh.build_sources(pt))
    if renamed:
        print(f'[NAMES] {renamed} stored jobs moved from an owner name to their team', flush=True)
    new_urls={r[0] for r in con.execute('select url from team_jobs')}-prior_urls
    if args.recover_pending:
        # Only jobs actually observed on the current organization sources.
        recovered={j['url'] for r in results if r['status']=='success' for j in r['rows']}
        state=pt.load_state()
        new_urls|=recovered-set(state.get('seen',[]))
        print('Recovered previously unannounced organization jobs:',len(new_urls),flush=True)
    # Queue only URLs new to the database, as in the other job scrapers.
    # Persist the queue before the listings so an interrupted write can retry.
    if cloud:
        cloud.queue_notifications(new_urls)
    else:
        state=pt.load_state()
        state['pending']=sorted((set(state.get('pending',[]))|new_urls)-set(state.get('seen',[])))
        pt.save_state(state)
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
    import coverage_report
    coverage=coverage_report.build(results)
    coverage_report.write(coverage,BOARD)
    runtime_healthy=not failed and coverage['summary']['with_verified_source']==124 and all(r['status']=='success' for r in discovery)
    coverage_verified=coverage['summary']['official_career_links_verified']==124
    manifest = {'schema':'abet.jobs.scrape-manifest.v1','generated_at':now(),
        'overall_status':'healthy' if runtime_healthy and coverage_verified else 'degraded',
        'runtime_status':'healthy' if runtime_healthy else 'degraded',
        'career_link_audit_status':'verified' if coverage_verified else 'partial',
        'team_coverage':coverage['summary'],
        'providers':audit['sources'],'discovery':discovery,'details':details,
        'totals':{'providers':len(results),'successful':len(results)-failed,'failed':failed,'active_jobs':len(jobs),'new':new,'updated':updated,'closed':closed},
        'persistence':'supabase' if cloud else 'sqlite','trigger':args.trigger,
        'scheduler_slot':os.environ.get('JOBRADAR_SCHEDULER_SLOT',''),
        'github_run_id':os.environ.get('GITHUB_RUN_ID','')}
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
