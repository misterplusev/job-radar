"""UltiPro / UKG public job board API.

Verified 2026-11-08 against the Houston Astros:
    POST https://recruiting2.ultipro.com/HOU1000/JobBoard/<boardGuid>/JobBoardView/LoadSearchResults
      {"opportunitySearch": {"Top": 100, "Skip": 0, "QueryString": "", "OrderBy": [], "Filters": []}}
      -> {"opportunities": [{"Id","Title","PostedDate","Locations":[{"LocalizedName"}],
                             "BriefDescription","RequisitionNumber","JobCategoryName"}],
          "totalCount": 24}

Portal identifiers come from each club's own careers page (see mlb_clubs.json), so the mapping
is first-party rather than guessed.
"""
from __future__ import annotations

from typing import Optional

import requests

from providers.base import Job

UA = {'User-Agent': 'ABET-TeamsJobs/1.0 (+https://abet-dashboard.vercel.app)',
      'Accept': 'application/json', 'Content-Type': 'application/json'}


def scrape(league: str, team: str, company_id: str, board_guid: str,
           session: Optional[requests.Session] = None, timeout: int = 45,
           host: str = 'recruiting2.ultipro.com', page_size: int = 100) -> list[Job]:
    client = session or requests.Session()
    url = f'https://{host}/{company_id}/JobBoard/{board_guid}/JobBoardView/LoadSearchResults'
    out: list[Job] = []
    skip = 0
    total = None
    for _ in range(100):
        body = {'opportunitySearch': {'Top': page_size, 'Skip': skip, 'QueryString': '',
                                      'OrderBy': [], 'Filters': []}}
        resp = client.post(url, json=body, headers=UA, timeout=timeout)
        resp.raise_for_status()
        data = resp.json() or {}
        if not isinstance(data.get('opportunities'),list) or 'totalCount' not in data:
            raise ValueError('Unrecognized UKG jobs response')
        opps = data.get('opportunities') or []
        if total is None:
            total = int(data.get('totalCount') or 0)
        for o in opps:
            locs = o.get('Locations') or []
            loc = ', '.join({l.get('LocalizedName', '') for l in locs if isinstance(l, dict) and l.get('LocalizedName')})
            out.append(Job(
                league=league,
                team=team,
                title=(o.get('Title') or '').strip(),
                url=(f'https://{host}/{company_id}/JobBoard/{board_guid}/OpportunityDetail'
                     f'?opportunityId={o.get("Id")}'),
                location=loc or None,
                description_clean=(o.get('BriefDescription') or '').strip(),
                posted_at=o.get('PostedDate'),
                platform='ultipro',
            ))
        skip += page_size
        if not opps and len(out)<total:raise ValueError('Incomplete UKG pagination')
        if not opps or skip >= total:
            break
    else:raise ValueError('UKG pagination limit reached')
    return out
