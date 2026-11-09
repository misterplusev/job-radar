"""Bounded live refresh for the existing scheduled sports-team pipeline.

Owner: sports-team jobs pipeline. HTTP only; no browsers, agents or notifications.
Successful sources replace only their own observations. Failed sources retain jobs
and their previous last_seen_at. Empty/unrecognized responses never close jobs.
"""
from __future__ import annotations

import json
import os
import re
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from datetime import datetime, timezone
from urllib.parse import urlsplit, parse_qs

import requests

from providers import nba, nfl, teamwork, teamwork_vertical, adp, ultipro

MAX_WORKERS = 3
MAX_REQUESTS = 80
SOURCE_SECONDS = 240
SOURCE_ALIASES = {
    'football-jobs/la-rams-careers/la-rams-micro':
        'football-jobs/la-rams-careers/los-angeles-rams',
}


class BoundedSession(requests.Session):
    _teamwork_lock = threading.Lock()
    _teamwork_last_request = 0.0
    def __init__(self):
        super().__init__()
        self.started = time.monotonic()
        self.calls = 0

    def request(self, method, url, **kwargs):
        # Retry read-only requests, with the same total source budget and pacing.
        retryable = method.upper() in ('GET', 'HEAD')
        for attempt in range(3):
            delay = 2 ** attempt
            try:
                response = self._request_once(method, url, **kwargs)
            except (requests.Timeout, requests.ConnectionError):
                if not retryable or attempt == 2:
                    raise
            else:
                if not retryable or response.status_code not in (429, 500, 502, 503, 504) or attempt == 2:
                    return response
                try:
                    delay = max(delay, min(30, int(response.headers.get('Retry-After', delay))))
                except (TypeError, ValueError):
                    pass
            time.sleep(delay)

    def _request_once(self, method, url, **kwargs):
        self.calls += 1
        remaining = SOURCE_SECONDS - (time.monotonic() - self.started)
        if self.calls > MAX_REQUESTS or remaining <= 0:
            raise TimeoutError('source request/time budget exceeded')
        if 'teamworkonline.com' in urlsplit(url).netloc:
            # One host-wide request every two seconds across all workers.
            with self._teamwork_lock:
                wait = 2.0 - (time.monotonic() - type(self)._teamwork_last_request)
                if wait > 0:
                    time.sleep(wait)
                type(self)._teamwork_last_request = time.monotonic()
        remaining = SOURCE_SECONDS - (time.monotonic() - self.started)
        if remaining <= 0:
            raise TimeoutError('source request/time budget exceeded')
        kwargs['timeout'] = min(float(kwargs.get('timeout', 25)), 25, remaining)
        relay=os.environ.get('TEAMS_SOURCE_RELAY_URL')
        if relay and method.upper()=='GET' and urlsplit(url).netloc=='www.teamworkonline.com':
            original=requests.Request('GET',url,params=kwargs.pop('params',None)).prepare().url
            kwargs['params']={'url':original}
            kwargs['headers']={'Authorization':'Bearer '+os.environ['DISCORD_RELAY_TOKEN']}
            response=super().request(method,relay,**kwargs)
            if response.headers.get('X-Source-URL'):response.url=response.headers['X-Source-URL']
            return response
        return super().request(method, url, **kwargs)


def source_from_row(row):
    url = row.get('url') or row.get('careers_url') or ''
    p = urlsplit(url)
    parts = [x for x in p.path.split('/') if x]
    team, league = row.get('team', ''), row.get('league', '')
    base = {'team': team, 'league': league}
    if 'teamworkonline.com' in p.netloc and len(parts) >= 3:
        path = '/'.join(parts[:3])
        path = SOURCE_ALIASES.get(path,path)
        return dict(base, kind='teamworkonline', key='tw:' + path, path=path)
    if 'greenhouse.io' in p.netloc and parts:
        board = parts[0]
        return dict(base, kind='greenhouse', key='gh:' + board, board=board)
    if 'myworkdayjobs.com' in p.netloc and parts:
        site = parts[1] if re.fullmatch(r'[a-z]{2}-[A-Z]{2}', parts[0]) and len(parts) > 1 else parts[0]
        if site.lower() == 'job':
            return None  # Old snapshots omitted the Workday site; use registry below.
        tenant = p.netloc.split('.')[0]
        return dict(base, kind='workday', key='wd:' + p.netloc + '/' + site,
                    host=p.netloc, tenant=tenant, site=site)
    if 'ultipro.com' in p.netloc and len(parts) >= 3 and parts[1] == 'JobBoard':
        return dict(base, kind='ultipro', key='ukg:' + p.netloc + '/' + '/'.join(parts[:3]),
                    host=p.netloc, company_id=parts[0], board_guid=parts[2])
    if 'adp.com' in p.netloc:
        cid = parse_qs(p.query).get('cid', [''])[0]
        if cid:
            return dict(base, kind='adp', key='adp:' + cid, cid=cid)
    return None


def build_sources(pt):
    sources = {}
    # Versioned registry makes the cloud runtime independent of old proof files.
    registry = pt.ROOT / 'sources.json'
    if registry.exists():
        sources.update({s['key']: s for s in json.loads(registry.read_text(encoding='utf-8'))})
    def add(row):
        source = source_from_row(row)
        if source and source.get('league') in ('NFL', 'NBA', 'MLB', 'NHL'):
            sources.setdefault(source['key'], source)
    for row in pt.load_rows():
        add(dict(row, team=pt._display_team(row)))
    for row in json.loads((pt.ROOT / 'teams.json').read_text(encoding='utf-8'))['teams']:
        add(row)
    for club in json.loads((pt.ROOT / 'mlb_clubs.json').read_text(encoding='utf-8')):
        wd = club.get('workday')
        if wd and wd[0] != 'asmglobal':
            tenant, pod, site = wd
            add({'league': 'MLB', 'team': pt._display_team({'league': 'MLB', 'team': club['club_slug']}),
                 'url': f'https://{tenant}.{pod}.myworkdayjobs.com/{site}'})
    # NBA's careers frontend is the validated source, not an inferred Workday list.
    for key in list(sources):
        if key.startswith('wd:nba.'):
            del sources[key]
    sources['nba:league'] = {'kind': 'nba', 'key': 'nba:league', 'league': 'NBA', 'team': 'NBA League Office'}
    for retired in ('tw:football-jobs/minnesota-vikings-jobs/vikings','tw:football-jobs/49ers/san-francisco-49ers',
                    'tw:football-jobs/la-rams-careers/la-rams-micro'):
        sources.pop(retired,None)
    return sources


def fetch_source(source):
    start = time.monotonic()
    try:
        with BoundedSession() as client:
            kind = source['kind']
            if kind == 'teamworkonline':
                jobs = teamwork.scrape_org(teamwork.TeamWorkOrg(source['league'], source['team'], source['path'], source.get('org_id','')), session=client)
            elif kind == 'nba':
                jobs = nba.scrape(session=client)
            elif kind == 'ultipro':
                jobs = ultipro.scrape(source['league'], source['team'], source['company_id'], source['board_guid'], host=source['host'], session=client)
            elif kind == 'adp':
                jobs = adp.scrape(source['league'], source['team'], source['cid'], session=client)
            elif kind == 'official_links':
                from bs4 import BeautifulSoup
                response=client.get(source['url']);response.raise_for_status()
                soup=BeautifulSoup(response.text,'html.parser')
                jobs=[]
                for link in soup.find_all('a',href=True):
                    if urlsplit(link['href']).netloc=='career4.successfactors.com' and 'jobId=' in link['href']:
                        jobs.append(dict(title=link.get_text(' ',strip=True),url=link['href'],platform='successfactors'))
                if not jobs:raise ValueError('Official careers page has no recognized job links')
            elif kind == 'greenhouse':
                response = client.get(f'https://boards-api.greenhouse.io/v1/boards/{source["board"]}/jobs', params={'content': 'true'})
                response.raise_for_status()
                data = response.json()
                if not isinstance(data.get('jobs'), list):
                    raise ValueError('missing Greenhouse jobs array')
                jobs = [dict(title=j.get('title'), url=j.get('absolute_url'), location=(j.get('location') or {}).get('name'),
                             description=j.get('content'), posted_at=j.get('first_published')) for j in data['jobs']]
            elif kind == 'workday':
                jobs, seen = [], set()
                for offset in range(0, 1000, 20):
                    response = client.post(f'https://{source["host"]}/wday/cxs/{source["tenant"]}/{source["site"]}/jobs',
                                           json={'appliedFacets': {}, 'limit': 20, 'offset': offset, 'searchText': ''})
                    response.raise_for_status()
                    data = response.json()
                    if not isinstance(data.get('jobPostings'), list):
                        raise ValueError('missing Workday jobPostings array')
                    batch = data['jobPostings']
                    for j in batch:
                        path = j.get('externalPath')
                        if not path or path in seen:
                            raise ValueError('missing or repeated Workday job path')
                        seen.add(path)
                        jobs.append(dict(title=j.get('title'), url=f'https://{source["host"]}/{source["site"]}{path}', location=j.get('locationsText')))
                    if offset + len(batch) >= int(data.get('total', 0)):
                        break
                    if not batch:
                        raise ValueError('incomplete Workday pagination')
                else:
                    raise ValueError('Workday pagination cap reached')
            else:
                raise ValueError('unsupported provider')
        observed_at = datetime.now(timezone.utc).isoformat()
        rows = []
        for job in jobs:
            row = dict(job) if isinstance(job, dict) else asdict(job)
            if not row.get('title') or not row.get('url'):
                raise ValueError('source returned a job without title or URL')
            team=row.get('team') or source['team']
            league=row.get('league') or source['league']
            if source['kind']=='teamworkonline':
                import publish_teams as labels
                for key,meta in labels.LOGO_MAP.items():
                    if labels._norm(team) in (labels._norm(key.partition(':')[2]),labels._norm(meta.get('espn_name'))):
                        league=key.partition(':')[0];break
            row.update(league=league, team=team, platform=row.get('platform') or source['kind'], source_id=source['key'], scraped_at=observed_at)
            row['description'] = row.get('description') or row.get('description_clean') or ''
            rows.append(row)
        return {'source': source, 'rows': rows, 'status': 'success',
                'observed_at': observed_at, 'duration_ms': int((time.monotonic() - start) * 1000), 'error': None}
    except Exception as exc:
        return {'source': source, 'rows': [], 'status': 'error', 'observed_at': datetime.now(timezone.utc).isoformat(),
                'duration_ms': int((time.monotonic() - start) * 1000), 'error': f'{type(exc).__name__}: {exc}'[:500]}


def collect(pt):
    sources = build_sources(pt)
    discovery = []
    for league in ('NFL', 'NHL', 'MLB', 'NBA'):
        try:
            with BoundedSession() as client:
                orgs = teamwork_vertical.discover(league, session=client)
            for org in orgs:
                if any(x in org.slug.lower() for x in ('necbl', 'riddell', 'sports-info', 'camelback')):
                    continue
                path = f'{org.vertical_path}/{org.slug}'
                key = 'tw:' + path
                sources.setdefault(key, dict(key=key, kind='teamworkonline', path=path, league=league, team=org.org_name))
            discovery.append({'league': league, 'sources': len(orgs), 'status': 'success'})
            print(f'[DISCOVERY] {league}: {len(orgs)} organizations',flush=True)
        except Exception as exc:
            discovery.append({'league': league, 'status': 'error', 'error': type(exc).__name__})
            print(f'[DISCOVERY] {league}: {type(exc).__name__}',flush=True)
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        results=[]
        futures=[pool.submit(fetch_source,s) for s in sources.values()]
        for future in as_completed(futures):
            result=future.result();results.append(result)
            print(f'[SOURCE] {result["source"]["key"]}: {result["status"]} {len(result["rows"])} jobs',flush=True)
    return results, discovery


def apply_results(con, results, pipeline):
    con.execute('create table if not exists team_job_observations (source_id text not null,url text not null,is_active integer not null default 1,observed_at text,primary key(source_id,url))')
    columns = {r[1] for r in con.execute('pragma table_info(team_jobs)')}
    if 'source_id' not in columns:
        con.execute('alter table team_jobs add column source_id text')
    # Attach old observations to their actual source without refreshing timestamps.
    for row in con.execute('select id,team,league,url from team_jobs').fetchall():
        source = source_from_row(dict(zip(('id','team','league','url'), row)))
        if source:
            key = 'nba:league' if source['key'].startswith('wd:nba.') else source['key']
            con.execute('update team_jobs set source_id=? where id=?', (key, row[0]))
            con.execute('insert or ignore into team_job_observations(source_id,url,is_active) values(?,?,1)', (key,row[3]))
    new = updated = closed = 0
    for result in results:
        source, status = result['source'], result['status']
        if status == 'success':
            n, u = pipeline.ingest(con, result['rows'], record_runs=False)
            new += n; updated += u
            urls = {r['url'] for r in result['rows']}
            for old,new_path in SOURCE_ALIASES.items():
                if source['key']=='tw:'+new_path:
                    con.execute('delete from team_job_observations where source_id=?',('tw:'+old,))
            con.execute('update team_job_observations set is_active=0,observed_at=? where source_id=?', (result['observed_at'], source['key']))
            for url in urls:
                con.execute('update team_jobs set source_id=? where url=?', (source['key'], url))
                con.execute('insert into team_job_observations(source_id,url,is_active,observed_at) values(?,?,1,?) on conflict(source_id,url) do update set is_active=1,observed_at=excluded.observed_at', (source['key'],url,result['observed_at']))
        con.execute('insert into team_job_scrape_runs(source,platform,status,job_count,duration_ms,error_summary,created_at) values(?,?,?,?,?,?,?)',
                    (source['key'], source['kind'], status, len(result['rows']), result['duration_ms'], result['error'], result['observed_at']))
    # A cross-listed job closes only when all its known sources report it absent.
    cur = con.execute('''update team_jobs set is_active=0,closed_at=? where is_active=1
                         and exists (select 1 from team_job_observations o where o.url=team_jobs.url)
                         and not exists (select 1 from team_job_observations o where o.url=team_jobs.url and o.is_active=1)''', (pipeline.now(),))
    closed = cur.rowcount
    con.commit()
    return new, updated, closed
