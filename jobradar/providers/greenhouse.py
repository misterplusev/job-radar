"""Greenhouse provider — uses the public boards API (no auth).

Endpoint: https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true
Covers a large share of tech companies and startups that host careers on Greenhouse.
"""
from __future__ import annotations

import html
import re
from typing import List

from bs4 import BeautifulSoup

from ..models import Job, clean_ws, now_iso
from .base import Provider, http_get

API = "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true"


def _strip_html(raw: str) -> str:
    if not raw:
        return ""
    text = BeautifulSoup(html.unescape(raw), "html.parser").get_text("\n", strip=True)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


class GreenhouseProvider(Provider):
    source = "greenhouse"

    def fetch(self, run_id: str) -> List[Job]:
        url = API.format(slug=self.slug)
        try:
            data = http_get(url).json()
        except Exception:
            return []  # unknown/closed board -> no jobs, don't crash the run
        company = _board_company(data, self.slug)
        jobs: List[Job] = []
        for j in data.get("jobs", []):
            title = clean_ws(j.get("title"))
            j_url = j.get("absolute_url") or ""
            if not title or not j_url:
                continue
            location = clean_ws((j.get("location") or {}).get("name"))
            desc = _strip_html(j.get("content") or "")
            jobs.append(Job(
                company=company,
                title=title,
                url=j_url,
                location=location or None,
                description=desc,
                description_raw=j.get("content") or "",
                description_clean=desc,
                source=self.source,
                provider_slug=self.slug,
                run_id=run_id,
                remote=("remote" in (location or "").lower()) or None,
                posted_at=j.get("updated_at") or j.get("first_published"),
                scraped_at=now_iso(),
            ))
        return jobs


def _board_company(data: dict, slug: str) -> str:
    name = (data.get("name") or "").strip()
    if name:
        return name
    return slug.replace("-", " ").title()
