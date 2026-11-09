"""TeamWork Online: vertical page -> org slugs -> each org's own portal.

Why two hops: the vertical listing is server-rendered with a hard 48-card cap (every pagination
parameter returns the same 48), but every card's URL contains its organisation slug
(`/hockey-jobs/hockeyjobs/<org-slug>/<job-slug>-<id>`). Following those slugs gives each team's
own portal, which lists that team's postings rather than the league-wide first page.
"""
from __future__ import annotations

import html as html_mod
import re
from collections import Counter
from dataclasses import dataclass
from typing import Iterable

import requests

from providers.base import Job
from providers.teamwork import BASE, UA, CARD_RE, CATEGORY_RE, LOCATION_RE, _clean, scrape_org, TeamWorkOrg, pages

VERTICALS = {
    'NHL': 'https://www.teamworkonline.com/hockey-jobs/hockeyjobs',
    'NFL': 'https://www.teamworkonline.com/football-jobs/footballjobs',
    'MLB': 'https://www.teamworkonline.com/baseball-jobs/baseballjobs',
    'NBA': 'https://www.teamworkonline.com/basketball-jobs/nbateamjobs',
}
ORG_SLUG_RE = re.compile(r'^/([^/]+-jobs)/([^/]+)/([^/]+)/', re.I)


@dataclass
class DetectedOrg:
    league: str
    org_name: str
    slug: str
    vertical_path: str
    sampled_jobs: int


def _cards(page: str):
    for m in CARD_RE.finditer(page):
        href, title_html, tail = m.group(1), m.group(2), m.group(3)
        title = _clean(title_html)
        if not title:
            continue
        cat = CATEGORY_RE.search(tail)
        loc = LOCATION_RE.search(tail)
        yield {
            'href': href,
            'title': title,
            'org': _clean(cat.group(1)) if cat else '',
            'location': _clean(loc.group(1)) if loc else '',
        }


def discover(league: str, session=None, timeout: int = 45) -> list[DetectedOrg]:
    """Read the vertical page and return every organisation it exposes, with its slug."""
    url = VERTICALS[league]
    client = session or requests.Session()
    by_slug: dict[str, DetectedOrg] = {}
    names = Counter()
    page = '\n'.join(pages(url, client, timeout))
    for card in _cards(page):
        m = ORG_SLUG_RE.match(card['href'])
        if not m:
            continue
        vertical_path, _, slug = m.group(1), m.group(2), m.group(3)
        key = slug.lower()
        names[key] += 1
        if key not in by_slug:
            by_slug[key] = DetectedOrg(league=league, org_name=card['org'], slug=slug,
                                       vertical_path=f'{vertical_path}/{m.group(2)}', sampled_jobs=0)
    for key, org in by_slug.items():
        org.sampled_jobs = names[key]
    return sorted(by_slug.values(), key=lambda o: -o.sampled_jobs)


def scrape_all_orgs(orgs: Iterable[DetectedOrg], session=None, timeout: int = 45) -> list[Job]:
    client = session or requests.Session()
    out: list[Job] = []
    for org in orgs:
        tw = TeamWorkOrg(league=org.league, team=org.org_name or org.slug,
                         vertical_path=f'{org.vertical_path}/{org.slug}', org_id='')
        try:
            out.extend(scrape_org(tw, session=client, timeout=timeout))
        except Exception as exc:  # noqa: BLE001
            print(f'  [warn] {org.league} {org.slug}: {type(exc).__name__}: {exc}')
    return out
