"""Workday cxs API provider (direct career-portal JSON, no auth).

Discovered tenant/site combos (verified 2026-10-09):
  bostondynamics      -> bostondynamics.wd1.myworkdayjobs.com  / Boston_Dynamics
  autostore           -> autostore.wd3.myworkdayjobs.com       / autostore
  rockwellautomation  -> rockwellautomation.wd1.myworkdayjobs.com / External_Rockwell_Automation

The per-job detail endpoint is disabled (HTTP 400) on these instances, so
list-only fields are used: title, location, url (no descriptions).
"""
import re
import requests
import sys
import time
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from .base import Provider
from ..models import Job, clean_ws
from ..workday_http import WorkdayHTTP

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122 Safari/537.36",
    "Content-Type": "application/json",
    "Accept": "application/json",
}

_BOARDS = {
    "bostondynamics": ("bostondynamics.wd1.myworkdayjobs.com", "Boston_Dynamics"),
    "autostore": ("autostore.wd3.myworkdayjobs.com", "autostore"),
    "rockwellautomation": ("rockwellautomation.wd1.myworkdayjobs.com", "External_Rockwell_Automation"),
}

_BOARD_NAMES = {
    "bostondynamics": "Boston Dynamics",
    "autostore": "AutoStore",
    "rockwellautomation": "Rockwell Automation",
}

def posted_from_relative(text, observed_at) -> Optional[str]:
    """Workday shows only "Posted Today", "Posted Yesterday" or "Posted N Days Ago". Turn that into a date,
    counted back from the time the listing was read. "Posted 30+ Days Ago" has no exact date and returns
    None. Without a posted date a new job is never sent to Discord. The publisher keeps the first date it
    stored for a Workday job, so reading the same listing on another day cannot move the date."""
    words = " ".join(str(text or "").lower().split())
    if not words or "+" in words:
        return None
    if "today" in words:
        days = 0
    elif "yesterday" in words:
        days = 1
    else:
        match = re.search(r"(\d+)\s+days?\s+ago", words)
        if not match:
            return None
        days = int(match.group(1))
    try:
        seen = datetime.fromisoformat(str(observed_at).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        seen = datetime.now(timezone.utc)
    if seen.tzinfo is None:
        seen = seen.replace(tzinfo=timezone.utc)
    return (seen.astimezone(timezone.utc) - timedelta(days=days)).date().isoformat()


def _new_client(source):
    return WorkdayHTTP(lambda method, url, **kw: requests.post(url, **kw), source=source)


def _fetch_page(url, payload, client=None):
    client = client or _new_client("workday")
    return client.request("POST", url, headers=_HEADERS, json=payload).json()


class WorkdayProvider(Provider):
    source = "workday"

    def __init__(self, slug: str):
        super().__init__(slug)

    def fetch(self, run_id: str) -> List[Job]:
        board = _BOARDS.get(self.slug)
        if not board:
            raise ValueError("Unknown Workday board")
        host, site = board
        company = _BOARD_NAMES.get(self.slug, self.slug.replace("-", " ").title())
        from ..workday_snapshot import board as snapshot_board
        snapshot = snapshot_board(host, self.slug, site)
        if snapshot is not None:
            observed_at, rows = snapshot
            return [Job(company=company, title=clean_ws(row["title"]),
                        url=f"https://{host}/{site}" + row["externalPath"],
                        location=clean_ws(row.get("locationsText")) or None, source=self.source,
                        provider_slug=self.slug, run_id=run_id, scraped_at=observed_at,
                        posted_at=posted_from_relative(row.get("postedOn"), observed_at)) for row in rows]
        jobs: List[Job] = []
        seen = set()
        offset = 0
        expected_total = None
        client = _new_client(f"workday:{self.slug}")
        for _page in range(50):
            data = _fetch_page(
                f"https://{host}/wday/cxs/{self.slug}/{site}/jobs",
                {"limit": 20, "offset": offset, "searchText": ""},
                client=client,
            )
            if not isinstance(data, dict) or not isinstance(data.get("jobPostings"), list) or "total" not in data:
                raise ValueError("Workday returned an invalid result page")
            # Workday commonly returns total=0 on every page after page one.
            # Retain the initial advertised total instead of ending at page two.
            if expected_total is None:
                expected_total = int(data["total"])
            else:
                expected_total = max(expected_total, int(data["total"]))
            fresh = [jp for jp in (data.get("jobPostings") or [])
                     if jp.get("externalPath") not in seen]
            if not fresh:
                if offset < expected_total:
                    raise ValueError("Workday pagination ended before the advertised total")
                break
            for jp in fresh:
                title = clean_ws(jp.get("title"))
                external = (jp.get("externalPath") or "").strip()
                if not title or not external:
                    raise ValueError("Workday posting missing title or URL")
                seen.add(external)
                url = external if external.startswith("http") else f"https://{host}/{site}{external}"
                jobs.append(Job(
                    company=company,
                    title=title,
                    url=url,
                    location=clean_ws(jp.get("locationsText")) or None,
                    source=self.source,
                    provider_slug=self.slug,
                    run_id=run_id,
                    is_active=True,
                    posted_at=posted_from_relative(jp.get("postedOn"), datetime.now(timezone.utc).isoformat()),
                ))
            offset += len(data["jobPostings"])
            if offset >= expected_total:
                break
        else:
            raise RuntimeError("Workday pagination safety limit reached; incomplete observation")
        return jobs
