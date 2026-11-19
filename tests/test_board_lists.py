"""Robotics companies are scraped by this repository, tech companies by job-radar-tech. No company in both.

Until 2026-11-19 nine tech companies were in this list as well. Their jobs were stored in robotics_jobs and in
tech_jobs (2,445 jobs in both tables) and none of them was ever announced in the robotics channel.
"""
import json
import unittest
from pathlib import Path

from jobradar.relevance import STRICT_TITLE_ONLY_COMPANIES

ROOT = Path(__file__).resolve().parents[1]
# The tech scraper's companies (job-radar-tech/config/targets.json, 2026-11-19).
TECH_COMPANIES = {"cloudflare", "stripe", "databricks", "coinbase", "mongodb", "figma", "airbnb", "robinhood", "twilio",
                  "vercel", "instacart", "gusto", "dropbox", "anthropic", "ramp", "openai"}


def slugs():
    targets = json.loads((ROOT / "config" / "targets.json").read_text(encoding="utf-8"))
    found = []
    for source in ("greenhouse", "lever", "ashby", "workday"):
        for entry in targets.get(source, []):
            found.append((entry.get("slug") if isinstance(entry, dict) else entry).lower())
    return found


class BoardLists(unittest.TestCase):
    def test_no_tech_company_is_in_the_robotics_list(self):
        self.assertEqual(sorted(set(slugs()) & (TECH_COMPANIES | set(STRICT_TITLE_ONLY_COMPANIES))), [])

    def test_no_company_is_listed_twice(self):
        listed = slugs()
        self.assertEqual(sorted(s for s in set(listed) if listed.count(s) > 1), [])


if __name__ == "__main__":
    unittest.main()
