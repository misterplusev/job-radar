"""Employer job detail extraction. Bounded, cached, and independent of listing health."""
import json
import re
import time
from datetime import datetime, timezone, timedelta
from urllib.parse import urlsplit

from bs4 import BeautifulSoup

from live_refresh import BoundedSession
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
        if 'myworkdayjobs.com' in p.netloc:
            parts = [s for s in p.path.split('/') if s]
            if re.fullmatch(r'[a-z]{2}-[A-Z]{2}', parts[0]):
                parts = parts[1:]
            if parts[-1] == 'apply':
                parts = parts[:-1]
            path = '/'.join(parts[1:])
            endpoint = f'https://{p.netloc}/wday/cxs/{p.netloc.split(".")[0]}/{parts[0]}/{path}'
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
    # Failed pages retry on the next bounded run, including after a network fix.
    retry_before = datetime.now(timezone.utc).isoformat()
    refresh_before = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    rows = [dict(r) for r in con.execute('''select * from team_jobs where is_active=1
        and (platform in ('teamworkonline','workday'))
        and (detail_checked_at is null or (detail_status!='success' and detail_checked_at<?)
             or (detail_status='success' and detail_checked_at<?))
        order by detail_checked_at is not null, first_seen_at desc limit ?''', (retry_before,refresh_before,limit))]
    start = time.monotonic(); counts = {'success':0, 'error':0, 'pending':0}
    for row in rows:
        if time.monotonic() - start > seconds:
            break
        stamp = datetime.now(timezone.utc).isoformat()
        try:
            detail = fetch_detail(row)
            if len(detail['description'] or '') < 80:
                raise ValueError('incomplete description')
            con.execute('''update team_jobs set description=?,posted_at=coalesce(?,posted_at),
                salary=coalesce(?,salary),detail_status='success',detail_checked_at=? where id=?''',
                (detail['description'],detail['posted_at'],detail['salary'],stamp,row['id']))
            counts['success'] += 1
        except Exception:
            # Preserve known details and active state on a detail-page failure.
            con.execute("update team_jobs set detail_status='error',detail_checked_at=? where id=?",(stamp,row['id']))
            counts['error'] += 1
        con.commit()
    counts['pending'] = con.execute("select count(*) from team_jobs where is_active=1 and platform in ('teamworkonline','workday') and coalesce(detail_status,'')!='success'").fetchone()[0]
    return counts
