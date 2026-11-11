"""TeamWork Online organisation portal provider.

Verified against the NHL league office page 2026-11-07:
    https://www.teamworkonline.com/hockey-jobs/hockeyjobs/nhl-league-office
      ?employment_opportunity_search%5Borganization_id%5D=28289

The page is server-rendered with a stable card structure:
    <h3 class="organization-portal__job-title"><a href="…/slug-2197013">Title </a></h3>
    <p class="organization-portal__job-category">National Hockey League (NHL)</p>
    <p class="organization-portal__job-location">Toronto, ON, Canada · Hybrid</p>
    <span class="organization-portal__job__career-level">Entry Level</span>

Adding an employer is one TeamWorkOrg row (vertical, org_slug, org_id). The org id is the
`organization_id` query parameter the employer's own "View jobs" link uses — that is the
first-party route, no aggregator in between.
"""
from __future__ import annotations

import html as html_mod
import re
from urllib.parse import urljoin, urlsplit
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import Iterable

import requests

from providers.base import Job

BASE = "https://www.teamworkonline.com"
UA = {"User-Agent": "ABET-TeamsJobs/1.0 (+https://abet-dashboard.vercel.app)",
      "Accept": "text/html,application/xhtml+xml"}

CARD_RE = re.compile(
    r'organization-portal__job-title[^>]*>\s*<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>'
    r'(.*?)'
    r'(?=organization-portal__job-title|$)', re.S)
CATEGORY_RE = re.compile(r'organization-portal__job-category">(.*?)</p>', re.S)
LOCATION_RE = re.compile(r'organization-portal__job-location">(.*?)</p>', re.S)
LEVEL_RE = re.compile(r'organization-portal__job__career-level">(.*?)</span>', re.S)
TAG_RE = re.compile(r"<[^>]+>")


@dataclass(frozen=True)
class TeamWorkOrg:
    league: str
    team: str
    vertical_path: str      # e.g. "hockey-jobs/hockeyjobs/nhl-league-office"
    org_id: str             # e.g. "28289"


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", html_mod.unescape(TAG_RE.sub("", value or ""))).strip()


def org_url(org: TeamWorkOrg) -> str:
    url = f"{BASE}/{org.vertical_path}"
    return url + f"?employment_opportunity_search%5Borganization_id%5D={org.org_id}" if org.org_id else url


def pages(url, client, timeout, expected_org_id=''):
    """Follow the site's real next links; never silently accept a truncated board."""
    seen = set()
    for _ in range(60):
        if url in seen:
            raise ValueError('repeated Teamwork pagination URL')
        seen.add(url)
        response = client.get(url, headers=UA, timeout=timeout)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        if expected_org_id:
            selected = soup.select('select[name="employment_opportunity_search[organization_id]"] option[selected]')
            if len(selected) != 1 or selected[0].get('value') != str(expected_org_id):
                raise ValueError('Teamwork response did not confirm the requested organization filter')
        if not soup.select('.organization-portal__job-title') and not soup.select('select[name="employment_opportunity_search[organization_id]"]'):
            raise ValueError('unrecognized Teamwork portal response')
        yield response.text
        link = soup.find('a', rel='next')
        if not link:
            return
        next_url = urljoin(response.url, link.get('href', ''))
        if urlsplit(next_url).netloc != urlsplit(BASE).netloc:
            raise ValueError('off-site Teamwork pagination link')
        url = next_url
    raise ValueError('Teamwork pagination cap reached')


def scrape_org(org: TeamWorkOrg, session=None, timeout: int = 45) -> list[Job]:
    client = session or requests.Session()
    page = '\n'.join(pages(org_url(org), client, timeout, org.org_id))
    jobs: list[Job] = []
    seen = set()
    for m in CARD_RE.finditer(page):
        href, title_html, tail = m.group(1), m.group(2), m.group(3)
        title = _clean(title_html)
        if not title or href in seen:
            continue
        seen.add(href)
        loc = LOCATION_RE.search(tail)
        cat = CATEGORY_RE.search(tail)
        lvl = LEVEL_RE.search(tail)
        location = _clean(loc.group(1)) if loc else None
        if lvl:
            level = _clean(lvl.group(1))
            if level and location:
                location = f"{location} · {level}"
        jobs.append(Job(
            league=org.league,
            team=_clean(cat.group(1)) if cat and _clean(cat.group(1)) else org.team,
            title=title,
            url=BASE + href if href.startswith("/") else href,
            location=location,
            description_clean=_clean(cat.group(1)) if cat else "",
            platform="teamworkonline",
        ))
    return jobs


def scrape_many(orgs: Iterable[TeamWorkOrg]) -> list[Job]:
    out: list[Job] = []
    session = requests.Session()
    for org in orgs:
        out.extend(scrape_org(org, session=session))
    return out
