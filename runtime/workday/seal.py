"""Seal the complete, cleaned results of one guarded cloud browser run without contacting employers."""
from datetime import datetime
import gzip
import json
from pathlib import Path
import sys


def seal(source, catalog):
    report=json.loads((source/"report.json").read_text(encoding="utf-8"))
    known=json.loads(catalog.read_text(encoding="utf-8"))
    assert len(known)==len(report["sources"])==19 and report["all_listings_complete"]
    assert report["cleanup"]=={"remaining_owned_processes":0,"passed":True} and report["browser_count"]==1
    assert report["production_writes"]==report["discord_sends"]==0
    boards={}
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
        boards[key]={"total":len(urls),"jobs":[{k:j[k] for k in ("title","externalPath","locationsText","postedOn","bulletFields") if k in j} for j in data["jobs"]]}
    assert datetime.fromisoformat(report["at"]).tzinfo
    return {"schema":1,"observed_at":report["at"],"boards":boards}
if __name__=="__main__":
    data=seal(Path(sys.argv[1]),Path(sys.argv[2]))
    out=Path(sys.argv[3]);out.parent.mkdir(exist_ok=True,parents=True)
    out.write_bytes(gzip.compress(json.dumps(data,separators=(",",":"),ensure_ascii=False).encode(),mtime=0))
    print("Verified",len(data["boards"]),"boards and",sum(x["total"] for x in data["boards"].values()),"listings")
