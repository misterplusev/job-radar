"""NBA — careers.nba.com (Phenom People in front of Workday).

Verified 2026-11-07:
    POST https://careers.nba.com/widgets
      payload pageName=search-results, ddoKey=refineSearch, size=20, from=0
      -> {"refineSearch": {"totalHits": 54, "hits": 20, "data": {"jobs": [...]}}}
    job fields: title, applyUrl (nba.wd108.myworkdayjobs.com/nbacareers/...), location,
                postedDate, dateCreated, category, descriptionTeaser, jobId

Phenom returns 20 per page; `from` paginates to totalHits. The apply URL is Workday, which is
the NBA's actual ATS — so this is first-party data surfaced through the careers-site widget.
"""
from __future__ import annotations

import json
from typing import Optional

import requests

from providers.base import Job

ENDPOINT = 'https://careers.nba.com/widgets'
PAGE_SIZE = 20
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125.0 Safari/537.36',
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Origin': 'https://careers.nba.com',
    'Referer': 'https://careers.nba.com/search-results',
}


def payload(start: int = 0, size: int = PAGE_SIZE, keywords: str = '') -> dict:
    return {
        'lang': 'en_us', 'deviceType': 'desktop', 'country': 'us', 'pageName': 'search-results',
        'ddoKey': 'refineSearch', 'sortBy': 'Most relevant', 'subsearch': '',
        'from': start, 'jobs': True, 'counts': True,
        'all_fields': ['category', 'country', 'state', 'city', 'type'],
        'size': size, 'clearAll': False, 'jdsource': 'facets', 'isSliderEnable': False,
        'pageId': 'page19', 'siteType': 'external', 'keywords': keywords, 'global': True,
        'selected_fields': {}, 'locationData': {},
    }


def scrape(session: Optional[requests.Session] = None, timeout: int = 45) -> list[Job]:
    client = session or requests.Session()
    jobs: list[Job] = []
    seen = set()
    start = 0
    total = None
    for _ in range(100):
        resp = client.post(ENDPOINT, data=json.dumps(payload(start)), headers=HEADERS, timeout=timeout)
        resp.raise_for_status()
        block = (resp.json() or {}).get('refineSearch') or {}
        if 'totalHits' not in block or not isinstance((block.get('data') or {}).get('jobs'), list):
            raise ValueError('Unrecognized NBA jobs response')
        if total is None:
            total = int(block.get('totalHits') or 0)
        batch = ((block.get('data') or {}).get('jobs')) or []
        if not batch:
            if total and start < total: raise ValueError('Incomplete NBA pagination')
            break
        for item in batch:
            url = (item.get('applyUrl') or '').strip()
            title = (item.get('title') or '').strip()
            if not title or not url or url in seen:
                continue
            seen.add(url)
            jobs.append(Job(
                league='NBA',
                team='NBA League Office',
                title=title,
                url=url,
                location=(item.get('location') or '').strip() or None,
                description_clean=(item.get('descriptionTeaser') or '').strip(),
                posted_at=item.get('postedDate') or item.get('dateCreated'),
                platform='workday',
            ))
        start += PAGE_SIZE
        if total and start >= total:
            break
        if len(batch) < PAGE_SIZE:
            if total and start < total: raise ValueError('Incomplete NBA page')
            break
    else:
        raise ValueError('NBA pagination limit reached')
    return jobs
