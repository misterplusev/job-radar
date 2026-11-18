"""Employer job detail extraction. Bounded, cached, and independent of listing health."""
import json
import re
import time
from datetime import datetime, timezone, timedelta
from urllib.parse import urlsplit

from bs4 import BeautifulSoup

from live_refresh import BoundedSession
from providers.teamwork import UA
from publish_teams import _clean_text, _iso


def jsonld_job(page):
    soup = BeautifulSoup(page, 'html.parser')
    for script in soup.find_all('script', type='application/ld+json'):
        try:
            value = json.loads(script.get_text())
        except (ValueError, TypeError):
            continue
        queue = value if isinstance(value, list) else [value]
        for _ in range(100):
            if not queue:break
            item=queue.pop(0)
            if not isinstance(item, dict):
                continue
            if isinstance(item.get('@graph'), list):
                queue.extend(item['@graph'])
            if item.get('@type') == 'JobPosting' or 'JobPosting' in (item.get('@type') or []):
                return item
    return {}


def fetch_detail(row):
    with BoundedSession() as client:
        url = row['url']
        p = urlsplit(url)
        if p.netloc == 'www.teamworkonline.com':
            client.headers.update(UA)
        if p.hostname and p.hostname.endswith(('.myworkdayjobs.com', '.myworkdaysite.com')):
            parts = [s for s in p.path.split('/') if s]
            if parts and re.fullmatch(r'[a-z]{2}-[A-Z]{2}', parts[0]):
                parts = parts[1:]
            if parts and parts[-1] == 'apply':
                parts = parts[:-1]
            if p.hostname.endswith('.myworkdaysite.com') and parts[:1] == ['recruiting']:
                parts = parts[1:]
                tenant = parts.pop(0) if parts else ''
            else:
                tenant = p.hostname.split('.')[0]
            if not tenant or len(parts) < 3 or parts[1] != 'job':
                raise ValueError('unrecognized official Workday detail URL')
            endpoint = f'https://{p.hostname}/wday/cxs/{tenant}/' + '/'.join(parts)
            r = client.get(endpoint); r.raise_for_status()
            item = r.json().get('jobPostingInfo') or {}
            return {'description': _clean_text(item.get('jobDescription')), 'posted_at': _iso(item.get('startDate')), 'salary': None}
        r = client.get(url); r.raise_for_status()
        item = jsonld_job(r.text)
        if not item:
            raise ValueError('JobPosting structured data missing')
        salary = item.get('baseSalary')
        return {'description': _clean_text(item.get('description')), 'posted_at': _iso(item.get('datePosted')),
                'salary': json.dumps(salary, ensure_ascii=False) if salary else None}


def enrich(con, limit=250, seconds=900):
    con.row_factory = __import__('sqlite3').Row
    cols = {r[1] for r in con.execute('pragma table_info(team_jobs)')}
    for name in ('salary', 'detail_status', 'detail_checked_at'):
        if name not in cols:
            con.execute(f'alter table team_jobs add column {name} text')
    now = datetime.now(timezone.utc)
    # A denial stays visible. Give new and due jobs from other organizations a turn.
    cutoffs = tuple((now - interval).isoformat() for interval in
                    (timedelta(hours=12), timedelta(days=2), timedelta(days=7)))
    rows = con.execute('''select * from team_jobs where is_active=1
        and platform in ('teamworkonline','workday') and (detail_checked_at is null
        or (coalesce(detail_status,'') not in ('success','forbidden','rate_limited') and detail_checked_at<=?)
        or (detail_status in ('forbidden','rate_limited') and detail_checked_at<=?)
        or (detail_status='success' and detail_checked_at<=?))
        order by detail_checked_at is not null, detail_checked_at, first_seen_at desc limit ?''',
        (*cutoffs, min(2000, max(0, limit) * 4)))
    started = time.monotonic()
    counts = {'success':0, 'error':0, 'pending':0, 'deferred_this_run':0, 'error_reasons':{}, 'error_samples':[]}
    blocked_orgs, limited_hosts = set(), set()
    for record in rows.fetchall():
        if counts['success'] + counts['error'] >= limit or time.monotonic() - started > seconds:
            break
        row = dict(record)
        parts = urlsplit(row['url'])
        org = (parts.hostname, parts.path.rsplit('/', 1)[0])
        if parts.hostname in limited_hosts or org in blocked_orgs:
            counts['deferred_this_run'] += 1
            continue
        stamp = datetime.now(timezone.utc).isoformat()
        try:
            detail = fetch_detail(row)
            if len(detail['description'] or '') < 80:
                raise ValueError('incomplete description')
            con.execute('''update team_jobs set description=?,posted_at=coalesce(?,posted_at),
                salary=coalesce(?,salary),detail_status='success',detail_checked_at=? where id=?''',
                (detail['description'],detail['posted_at'],detail['salary'],stamp,row['id']))
            counts['success'] += 1
        except Exception as exc:
            # Preserve known details and active state on a detail-page failure.
            code = getattr(getattr(exc, 'response', None), 'status_code', None)
            status = 'error'
            if code == 403:
                status = 'forbidden'
                blocked_orgs.add(org)
            elif code == 429:
                status = 'rate_limited'
                limited_hosts.add(parts.hostname)
            reason = f'{parts.hostname} HTTP {code}' if code else type(exc).__name__
            counts['error_reasons'][reason] = counts['error_reasons'].get(reason, 0) + 1
            con.execute("update team_jobs set detail_status=?,detail_checked_at=? where id=?", (status,stamp,row['id']))
            counts['error'] += 1
            if len(counts['error_samples']) < 5:
                counts['error_samples'].append({'url':row['url'],'error':f'{type(exc).__name__}: {exc}'[:350]})
        con.commit()
    counts['pending'] = con.execute("select count(*) from team_jobs where is_active=1 and platform in ('teamworkonline','workday') and coalesce(detail_status,'')!='success'").fetchone()[0]
    return counts
