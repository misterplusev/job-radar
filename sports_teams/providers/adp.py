"""ADP Workforce Now public career-center API.

Verified 2026-11-08 with the Rays and White Sox:
    GET https://workforcenow.adp.com/mascsr/default/careercenter/public/events/staffing/v1/
        job-requisitions?cid=<clientId>&ccId=19000101_000001&lang=en_US&$top=50
      -> {"jobRequisitions":[...], "meta":{"totalNumber": N}}
    Cubs cid returns totalNumber 0 (genuinely no openings).

Job link shape: the career-center page with the requisition id appended, which is what the
club's own "View job" button opens.
"""
from __future__ import annotations

from typing import Optional

import requests

from providers.base import Job

BASE = ('https://workforcenow.adp.com/mascsr/default/careercenter/public/events/staffing/v1/'
        'job-requisitions')
PORTAL = ('https://workforcenow.adp.com/mascsr/default/mdf/recruitment/recruitment.html'
          '?cid={cid}&ccId={ccid}&lang=en_US&jobId={job}')
UA = {'User-Agent': 'ABET-TeamsJobs/1.0 (+https://abet-dashboard.vercel.app)',
      'Accept': 'application/json'}


def _loc(item: dict) -> Optional[str]:
    locs = item.get('locations') or []
    names = []
    for l in locs:
        if isinstance(l, dict):
            name = l.get('name') or l.get('locationName') or ''
            if name:
                names.append(name)
    return ', '.join(sorted(set(names))) or None


def scrape(league: str, team: str, cid: str, session: Optional[requests.Session] = None,
           timeout: int = 45, page_size: int = 50, ccid: str = '19000101_000001') -> list[Job]:
    client = session or requests.Session()
    out: list[Job] = []
    start = 1
    total = None
    seen = set()
    for _ in range(100):
        # This public endpoint uses one-based $skip (meta.startSequence), not
        # $startSequence; the latter is ignored and repeats page one.
        url = f'{BASE}?cid={cid}&ccId={ccid}&lang=en_US&$top={page_size}&$skip={start}'
        resp = client.get(url, headers=UA, timeout=timeout)
        resp.raise_for_status()
        data = resp.json() or {}
        if not isinstance(data.get('jobRequisitions'),list) or 'totalNumber' not in (data.get('meta') or {}):
            raise ValueError('Unrecognized ADP jobs response')
        reqs = data.get('jobRequisitions') or []
        meta = data.get('meta') or {}
        count=int(meta['totalNumber'])
        if total is not None and count!=total:raise ValueError('ADP total changed during pagination')
        total=count
        for r in reqs:
            rid = r.get('requisitionId') or r.get('clientRequisitionID') or ''
            title = (r.get('requisitionTitle') or '').strip()
            if not title or not rid or rid in seen:
                raise ValueError('Missing/repeated ADP requisition or title')
            seen.add(rid)
            out.append(Job(
                league=league,
                team=team,
                title=title,
                url=PORTAL.format(cid=cid, ccid=ccid, job=rid),
                location=_loc(r),
                description_clean=(r.get('requisitionDescription') or ''),
                posted_at=r.get('postDate') or r.get('requisitionOpenDate'),
                platform='adp',
            ))
        # Some centers cap $top below the requested page size. Advance by the
        # received count, otherwise the Bucks feed silently skips requisitions.
        start += len(reqs)
        if not reqs and len(out)<total:raise ValueError('Incomplete ADP pagination')
        if not reqs or start > total:
            if len(out)!=total:raise ValueError('Incomplete ADP result count')
            break
    else:raise ValueError('ADP pagination limit reached')
    return out
