"""Core data model: the Job contract shared by every provider and the storage layer."""
from __future__ import annotations

import re
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Optional


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def clean_ws(s: Optional[str]) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())


def _norm_key(s: Optional[str]) -> str:
    return re.sub(r"[^a-z0-9]+", "", (s or "").lower())


@dataclass
class Job:
    company: str
    title: str
    url: str
    location: Optional[str] = None
    description: str = ""
    description_raw: str = ""
    description_clean: str = ""
    source: str = ""            # greenhouse | lever | ashby | workday | indeed | ...
    provider_slug: str = ""     # company slug within the source
    run_id: str = ""
    salary: Optional[str] = None
    remote: Optional[bool] = None
    posted_at: Optional[str] = None
    is_active: bool = True
    scraped_at: str = field(default_factory=now_iso)

    def dedup_key(self) -> str:
        """Same posting seen via different sources collapses on this key."""
        return "|".join((_norm_key(self.company), _norm_key(self.title), _norm_key(self.location)))

    def to_row(self) -> dict:
        return asdict(self)


# columns that exist on the jobs table (the write surface)
JOB_COLUMNS = [
    "company", "title", "url", "location", "description", "description_raw",
    "description_clean", "source", "provider_slug", "run_id", "salary",
    "remote", "posted_at", "is_active", "scraped_at",
]
