"""Sports-teams jobs scraper — base contract.

Standalone from the sportsbook/robotics stacks: teams are not employers in the same sense
(they are franchises, and most post through a league platform or TeamWork Online), so this
tree keeps its own Job contract and registry.

Platforms found by live probing 2026-11-07:
  NFL  -> Greenhouse board `nflcareers` (44 postings verified)
  NHL  -> TeamWork Online organisation portal, org_id 28289 (job cards verified in HTML)
  MLB  -> mlb.com/careers is Next.js client-side; postings are NOT in __NEXT_DATA__ (needs its API)
  NBA  -> careers.nba.com runs on Phenom People (widget API, not yet mapped)
  Per-team pages (all four leagues) are JS-rendered and expose no static job links.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class Job:
    league: str
    team: str
    title: str
    url: str
    location: Optional[str]
    description_raw: str = ""
    description_clean: str = ""
    posted_at: Optional[str] = None
    platform: str = ""
    is_active: bool = True
