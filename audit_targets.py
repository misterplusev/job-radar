"""One-off audit: are the robots actually the right robots?

Probes every slug in config/targets.json and prints sample titles so a board
pointing at the wrong company (e.g. greenhouse `figure` = the mortgage lender,
not Figure AI) is visible instead of silently scraping noise.

Read-only. No writes, no Discord, no Supabase.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import requests

from config import settings

SAMPLES = 3


def gh(slug):
    r = requests.get(f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs",
                     timeout=45)
    if r.status_code != 200:
        return None, r.status_code
    jobs = r.json().get("jobs", [])
    titles = [re.sub(r"\s+", " ", (j.get("title") or "")).strip() for j in jobs]
    titles = [t for t in titles if t]
    company = (jobs[0].get("company_name") if jobs else None)
    return {"n": len(jobs), "company": company, "titles": titles[:SAMPLES]}, 200


def lever(slug):
    r = requests.get(f"https://api.lever.co/v0/postings/{slug}?mode=json", timeout=45)
    if r.status_code != 200:
        return None, r.status_code
    jobs = r.json()
    titles = [re.sub(r"\s+", " ", (j.get("text") or "")).strip() for j in jobs]
    titles = [t for t in titles if t]
    return {"n": len(jobs), "company": None, "titles": titles[:SAMPLES]}, 200


def ashby(slug):
    r = requests.get(f"https://api.ashbyhq.com/posting-api/job-board/{slug}", timeout=45)
    if r.status_code != 200:
        return None, r.status_code
    jobs = r.json().get("jobs", [])
    titles = [re.sub(r"\s+", " ", (j.get("title") or "")).strip() for j in jobs]
    titles = [t for t in titles if t]
    return {"n": len(jobs), "company": None, "titles": titles[:SAMPLES]}, 200


PROBES = {"greenhouse": gh, "lever": lever, "ashby": ashby}

# Signals that a board is the wrong industry.
SUSPECT = re.compile(
    r"counsel|attorney|accounting|treasury|underwriter|mortgage|lending|"
    r"loan|insurance|claims adjuster|real estate|retail|store|cashier|"
    r"nurse|clinical|teacher|barista|driver|warehouse|customer success",
    re.I,
)


def main():
    targets = settings.load_targets()
    report = {}

    for source, probe in PROBES.items():
        slugs = targets.get(source) or []
        if not slugs:
            continue
        print(f"\n=== {source} ===")
        for slug in slugs:
            try:
                data, code = probe(slug)
            except Exception as e:  # noqa: BLE001
                print(f"  {slug:26s} ERROR {e}")
                continue
            if data is None:
                print(f"  {slug:26s} HTTP {code}  (dead or wrong slug)")
                report[slug] = {"source": source, "status": code}
                continue
            flag = ""
            if data["n"] == 0:
                flag = "  <-- EMPTY"
            hits = [t for t in data["titles"] if SUSPECT.search(t)]
            if hits:
                flag = "  <-- NON-ROBOTICS SAMPLES"
            co = f" [{data['company']}]" if data.get("company") else ""
            print(f"  {slug:26s} {data['n']:5d}{co}{flag}")
            for t in data["titles"]:
                print(f"        - {t[:88]}")
            report[slug] = {"source": source, "n": data["n"],
                            "company": data.get("company"),
                            "samples": data["titles"], "suspect": hits}

    for key, probe in (("indeed_queries", lambda s: None), ("amazon", lambda s: None),
                       ("workday", lambda s: None)):
        for slug in (targets.get(key) or []):
            label = slug.get("q") if isinstance(slug, dict) else slug
            print(f"  [{key}] {label}  (not probed here)")

    Path("targets_audit.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("\n[saved] targets_audit.json")


if __name__ == "__main__":
    main()