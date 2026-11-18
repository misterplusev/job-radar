"""Bounded diagnostics from an already-received public detail page. Performs no network I/O."""
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit

from bs4 import BeautifulSoup
from teamwork_detail import detail, job_id, words


def record_missing(row, response, clean):
    directory = os.environ.get('TEAMWORK_DETAIL_EVIDENCE_DIR')
    if not directory or response.status_code != 200 or response.headers.get('cf-mitigated', '').lower() == 'challenge':
        return
    expected = job_id(row['url'])
    title = row.get('title') or ''
    if not expected or not title or job_id(response.url) != expected or len(response.content) > 1_000_000:
        return
    out = Path(directory)
    out.mkdir(parents=True, exist_ok=True)
    target = out / (expected + '.json')
    if target.exists() or sum(1 for _ in out.glob('*.json')) >= 8:
        return
    soup = BeautifulSoup(response.text, 'html.parser')
    if not any(words(h.get_text(' ', strip=True)) == words(title) for h in soup.find_all('h1')):
        return
    canonical = soup.find('link', rel='canonical')
    if canonical and canonical.get('href') and job_id(urljoin(response.url, canonical['href'])) != expected:
        return
    apply_links = set()
    for link in soup.find_all('a', href=True):
        label = words(' '.join((link.get_text(' ', strip=True), link.get('aria-label') or '', link.get('title') or '')))
        if 'apply' not in label.split():
            continue
        parsed = urlsplit(urljoin(response.url, link['href']))
        host = parsed.hostname or ''
        if parsed.scheme == 'https' and host.endswith(('.myworkdayjobs.com','.myworkdaysite.com')) and 'job' in parsed.path.split('/'):
            apply_links.add(urlunsplit(('https',host,parsed.path,'','')))
    record = {'job_id':expected,'url':row['url'],'title':title,'team':row.get('team'),'http':200,
              'observed_at':datetime.now(timezone.utc).isoformat(),'official_apply_links':sorted(apply_links)[:6],
              'source_sha256':hashlib.sha256(response.content).hexdigest()}
    try:
        body = detail(response.text, row['url'], response.url, title, clean)['description']
    except ValueError as exc:
        record['observation'] = str(exc)
    else:
        record['candidate_chars'] = len(body)
        record['candidate_sha256'] = hashlib.sha256(body.encode()).hexdigest()
        if len(body.encode()) <= 16_000:
            record['candidate_description'] = body
    # No scripts, forms, cookies, request headers or HTML dump enter the artifact.
    tmp = target.with_suffix('.tmp')
    tmp.write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    tmp.replace(target)
