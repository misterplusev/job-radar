"""Lever provider — public postings API (no auth).

Endpoint: https://api.lever.co/v0/postings/{slug}?mode=json
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from ..models import Job, clean_ws, now_iso
from .base import Provider, http_get
from .names import board_company

API = "https://api.lever.co/v0/postings/{slug}?mode=json"


class LeverProvider(Provider):
    source = "lever"

    def __init__(self, slug: str, content: bool = True):
        super().__init__(slug)
        self.content = content

    def fetch(self, run_id: str) -> List[Job]:
        data = http_get(API.format(slug=self.slug)).json()
        if not isinstance(data, list):
            raise ValueError("Lever returned an invalid posting list")
        company = board_company(self.slug)
        jobs: List[Job] = []
        for p in data:
            title = clean_ws(p.get("text"))
            url = p.get("hostedUrl") or p.get("applyUrl") or ""
            if not title or not url:
                raise ValueError("Posting missing title or URL; observation is incomplete")
            loc = clean_ws((p.get("categories") or {}).get("location"))
            if self.content:
                desc = clean_ws(p.get("descriptionPlain") or p.get("description"))
                raw = p.get("description") or ""
            else:
                desc, raw = "", ""
            jobs.append(Job(company=company, title=title, url=url, location=loc or None,
                            description=desc, description_raw=raw,
                            description_clean=desc, source=self.source, provider_slug=self.slug,
                            run_id=run_id, remote=("remote" in (loc or "").lower()) or None,
                            posted_at=posted_from_ms(p.get("createdAt")),
                            scraped_at=now_iso()))
        return jobs


def posted_from_ms(value) -> Optional[str]:
    """Lever gives the posting's creation time in milliseconds. Without a posted date a new job is
    never sent to Discord (the publisher only announces jobs posted in the last 14 days)."""
    try:
        return datetime.fromtimestamp(int(value) / 1000, tz=timezone.utc).isoformat(timespec="seconds")
    except (TypeError, ValueError, OverflowError, OSError):
        return None
