"""One-off validation: run the relevance gate over REAL board titles.

No writes, no Discord, no Supabase. Read-only probe of the public Greenhouse
boards-api so the gate is measured against actual postings rather than fixtures.
"""
import sys
import json
import html
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import requests
from bs4 import BeautifulSoup

from jobradar import relevance

BOARDS = [
    # (slug, expected_bucket)
    ("anthropic", "noise"), ("stripe", "noise"), ("coinbase", "noise"),
    ("figma", "noise"), ("airbnb", "noise"), ("robinhood", "noise"),
    ("databricks", "noise"),
    ("waymo", "keep"), ("figureai", "keep"), ("apptronik", "keep"),
    ("locusrobotics", "keep"), ("agilityrobotics", "keep"),
]


def strip_html(raw):
    if not raw:
        return ""
    return BeautifulSoup(html.unescape(raw), "html.parser").get_text(" ", strip=True)


def main():
    tally = {("noise", "keep"): 0, ("noise", "drop"): 0,
             ("keep", "keep"): 0, ("keep", "drop"): 0}
    leaks, misses = [], []

    for slug, bucket in BOARDS:
        url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true"
        try:
            jobs = requests.get(url, timeout=60).json().get("jobs", [])
        except Exception as e:  # noqa: BLE001
            print(f"  !! {slug}: {e}")
            continue

        kept = 0
        for j in jobs:
            title = re.sub(r"\s+", " ", (j.get("title") or "")).strip()
            if not title:
                continue
            desc = strip_html(j.get("content") or "")
            got = "keep" if relevance.is_relevant(title, desc, (j.get("company_name") or slug)) else "drop"
            tally[(bucket, got)] += 1
            kept += got == "keep"
            if bucket == "noise" and got == "keep":
                leaks.append(f"{slug}: {title}")
            if bucket == "keep" and got == "drop":
                misses.append(f"{slug}: {title}")

        total = len(jobs)
        print(f"  {slug:20s} {bucket:5s}  {total:5d} jobs -> {kept:4d} announced "
              f"({100.0 * kept / total if total else 0:.1f}%)")

    print("\n=== TALLY ===")
    for k, v in sorted(tally.items()):
        print(f"  expected={k[0]:5s} got={k[1]:5s}  {v}")

    noise_total = tally[("noise", "keep")] + tally[("noise", "drop")]
    keep_total = tally[("keep", "keep")] + tally[("keep", "drop")]
    print(f"\nnoise boards: {tally[('noise','keep')]}/{noise_total} leaked "
          f"({100.0 * tally[('noise','keep')] / max(noise_total,1):.2f}%)")
    print(f"robotics boards: {tally[('keep','keep')]}/{keep_total} kept "
          f"({100.0 * tally[('keep','keep')] / max(keep_total,1):.2f}%)")

    print(f"\n=== LEAKS (noise announced) — first 30 of {len(leaks)} ===")
    for x in leaks[:30]:
        print("  +", x)
    print(f"\n=== MISSES (robotics suppressed) — first 30 of {len(misses)} ===")
    for x in misses[:30]:
        print("  -", x)

    Path("relevance_validation.json").write_text(
        json.dumps({"tally": {f"{k[0]}|{k[1]}": v for k, v in tally.items()},
                    "leaks": leaks, "misses": misses}, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()