"""NFL — league-office jobs straight from the NFL's own Greenhouse board.

Verified 2026-11-07: boards-api.greenhouse.io/v1/boards/nflcareers/jobs -> 44 postings,
first "Administrative Assistant". The Greenhouse board API is the backend the NFL careers
page renders, i.e. first-party.
"""
from __future__ import annotations

import html as html_mod
import re

import requests

from providers.base import Job

BOARD_TOKEN = "nflcareers"
LIST_URL = f"https://boards-api.greenhouse.io/v1/boards/{BOARD_TOKEN}/jobs"
DETAIL_URL = f"https://boards-api.greenhouse.io/v1/boards/{BOARD_TOKEN}/jobs/{{id}}"
UA = {"User-Agent": "ABET-TeamsJobs/1.0 (+https://abet-dashboard.vercel.app)"}


def _text(value: str) -> str:
    return re.sub(r"\s+", " ", html_mod.unescape(re.sub(r"<[^>]+>", " ", value or ""))).strip()


def scrape(session=None, with_descriptions: bool = False, timeout: int = 45) -> list[Job]:
    client = session or requests.Session()
    resp = client.get(LIST_URL, params={"content": "true"}, headers=UA, timeout=timeout)
    resp.raise_for_status()
    jobs: list[Job] = []
    for item in resp.json().get("jobs", []):
        loc = item.get("location") or {}
        jobs.append(Job(
            league="NFL",
            team="NFL League Office",
            title=(item.get("title") or "").strip(),
            url=item.get("absolute_url") or "",
            location=(loc.get("name") or None) if isinstance(loc, dict) else None,
            description_raw=item.get("content") or "",
            description_clean=_text(item.get("content") or ""),
            posted_at=(item.get("updated_at") or item.get("first_published") or None),
            platform="greenhouse",
        ))
    return jobs
