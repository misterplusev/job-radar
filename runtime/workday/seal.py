"""Seal the complete, cleaned results of one guarded cloud browser run without contacting employers.

A posting the collector had to skip (the employer listed it without a title or job path) is carried over from the
previous published listing, so that no scraper closes a job the employer still lists:
- identified by its job path or its requisition fields: carried for as long as the board lists it;
- not identifiable: every job of that board that would otherwise leave the listing is held, for at most HOLD_DAYS.
"""
from datetime import datetime
import gzip
import json
import os
from pathlib import Path
import re
import sys
import urllib.request

KEYS=("title","externalPath","locationsText","postedOn","bulletFields")
HOLD_DAYS=7
RELEASE="https://api.github.com/repos/misterplusev/job-radar/releases/tags/abet-workday-listings-v1"
NAME=re.compile(r"listings-([0-9]+)-([0-9]+)\.json\.gz")


class PreviousListingUnavailable(RuntimeError):pass


def _usable(job):
    return (isinstance(job,dict) and isinstance(job.get("externalPath"),str) and job["externalPath"].startswith("/job/")
            and isinstance(job.get("title"),str) and bool(job["title"].strip()))


def carry_over(jobs, skipped_rows, skipped, previous_jobs, observed_at):
    """Return (jobs to add, counts) for one board. previous_jobs is that board in the previous listing ([] if none)."""
    present={j["externalPath"] for j in jobs}
    absent=[j for j in previous_jobs if _usable(j) and j["externalPath"] not in present]
    by_path={j["externalPath"]:j for j in absent}
    known={j["externalPath"] for j in previous_jobs if _usable(j)}
    rows=list(skipped_rows)+[{} for _ in range(skipped-len(skipped_rows))]
    added={};counts={"carried":0,"held":0,"new_unreadable":0,"unidentified":0}
    for row in rows:
        path=row.get("externalPath");match=by_path.get(path) if path else None
        if match is None and row.get("bulletFields"):
            same=[j for j in absent if j.get("bulletFields")==row["bulletFields"] and j["externalPath"] not in added]
            if len(same)==1:match=same[0]
        if match is not None and match["externalPath"] not in added:
            added[match["externalPath"]]={k:match[k] for k in KEYS if k in match};counts["carried"]+=1
        elif path and path not in known and path not in present:
            counts["new_unreadable"]+=1   # never stored by any scraper: nothing can be closed
        else:
            counts["unidentified"]+=1
    if counts["unidentified"]:
        now=datetime.fromisoformat(observed_at)
        for job in absent:
            if job["externalPath"] in added:continue
            since=job.get("held_since") or observed_at
            if (now-datetime.fromisoformat(since)).total_seconds()<HOLD_DAYS*86400:
                added[job["externalPath"]]={**{k:job[k] for k in KEYS if k in job},"held_since":since};counts["held"]+=1
    return list(added.values()),counts


def seal(source, catalog, previous=None):
    """previous: the previous sealed listing (dict), {} when none was ever published, or a callable returning one.
    It is only required when a board skipped a posting; a callable is always called so the path stays exercised."""
    report=json.loads((source/"report.json").read_text(encoding="utf-8"))
    known=json.loads(catalog.read_text(encoding="utf-8"))
    assert len(known)==len(report["sources"])==19 and report["all_listings_complete"]
    assert report["cleanup"]=={"remaining_owned_processes":0,"passed":True} and report["browser_count"]==1
    assert report["production_writes"]==report["discord_sends"]==0
    assert datetime.fromisoformat(report["at"]).tzinfo
    problem=None
    if callable(previous):
        try:previous=previous()
        except PreviousListingUnavailable as exc:previous=None;problem=str(exc)
    boards={};totals={"carried":0,"held":0,"new_unreadable":0,"unidentified":0}
    for i,expected in enumerate(known):
        receipt=report["sources"][i]
        data=json.loads((source/f"{i:02d}-jobs.json").read_text(encoding="utf-8"))
        assert data["source"]==expected and receipt["id"]==expected["id"] and receipt["complete"]
        # Postings the employer published without a title or job path are skipped by the collector and counted.
        skipped=receipt.get("skipped_malformed",0)
        assert skipped==data.get("skipped_malformed",0) and 0<=skipped<=max(3,receipt["advertised_total"]//50)
        assert receipt["advertised_total"]==data["advertised_total"]==receipt["collected"]+skipped
        assert receipt["collected"]==len(data["jobs"])
        urls={j["externalPath"] for j in data["jobs"]}
        assert len(urls)==len(data["jobs"]) and all(p.startswith("/job/") for p in urls)
        key="/".join(expected[k] for k in ("host","tenant","site"))
        if key in boards:raise ValueError("duplicate board")
        jobs=[{k:j[k] for k in KEYS if k in j} for j in data["jobs"]]
        board={"total":len(jobs),"jobs":jobs}
        if skipped:
            if previous is None:
                raise PreviousListingUnavailable(f"{key} skipped {skipped} posting(s) and the previous listing could not be read"
                                                 f" ({problem or 'none given'}); nothing is published, so no scraper closes a job on this listing")
            rows=data.get("skipped") or []
            assert isinstance(rows,list) and len(rows)<=skipped and all(isinstance(r,dict) for r in rows)
            extra,counts=carry_over(jobs,rows,skipped,((previous.get("boards") or {}).get(key) or {}).get("jobs") or [],report["at"])
            jobs.extend(extra)
            assert len({j["externalPath"] for j in jobs})==len(jobs)
            board={"total":len(jobs),"jobs":jobs,"skipped":skipped,**counts}
            for name in totals:totals[name]+=counts[name]
            print(f"[WORKDAY_SEAL] {key}: {skipped} posting(s) skipped by the collector: {counts}",flush=True)
        boards[key]=board
    result={"schema":1,"observed_at":report["at"],"boards":boards}
    if isinstance(previous,dict) and previous.get("observed_at"):result["previous_observed_at"]=previous["observed_at"]
    print(f"[WORKDAY_SEAL] previous listing: {(previous or {}).get('observed_at') or problem or 'none published yet'}; totals {totals}",flush=True)
    return result


def previous_from_release():
    """The newest published listing, read the way the scrapers read it. {} when none was ever published."""
    try:
        headers={"Accept":"application/vnd.github+json","User-Agent":"abet-workday-seal"}
        if os.environ.get("GH_TOKEN"):headers["Authorization"]="Bearer "+os.environ["GH_TOKEN"]
        with urllib.request.urlopen(urllib.request.Request(RELEASE,headers=headers),timeout=20) as reply:
            release=json.load(reply)
        assets=[a for a in release.get("assets",[]) if a.get("state")=="uploaded" and NAME.fullmatch(a.get("name",""))]
        if not assets:return {}
        latest=max(assets,key=lambda a:tuple(map(int,NAME.fullmatch(a["name"]).groups())))
        request=urllib.request.Request(latest["browser_download_url"],headers={"User-Agent":"abet-workday-seal"})
        with urllib.request.urlopen(request,timeout=30) as reply:
            raw=reply.read(3_000_001)
        if len(raw)>3_000_000:raise ValueError("previous listing is over budget")
        data=json.loads(gzip.decompress(raw))
        if not isinstance(data,dict) or data.get("schema")!=1 or not isinstance(data.get("boards"),dict):raise ValueError("unexpected shape")
        return data
    except Exception as exc:
        if getattr(exc,"code",None)==404:return {}
        raise PreviousListingUnavailable(f"{type(exc).__name__}: {str(exc)[:160]}") from exc


if __name__=="__main__":
    previous=previous_from_release
    if len(sys.argv)>4:
        previous=json.loads(gzip.decompress(Path(sys.argv[4]).read_bytes()))
    data=seal(Path(sys.argv[1]),Path(sys.argv[2]),previous)
    out=Path(sys.argv[3]);out.parent.mkdir(exist_ok=True,parents=True)
    out.write_bytes(gzip.compress(json.dumps(data,separators=(",",":"),ensure_ascii=False).encode(),mtime=0))
    print("Verified",len(data["boards"]),"boards and",sum(x["total"] for x in data["boards"].values()),"listings")
