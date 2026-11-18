import json,os,sys
from pathlib import Path
import requests
from urllib.parse import urlsplit
sys.path.insert(0,str(Path("sports_teams").resolve()))
import enrichment
from jobradar.workday_snapshot import board
snap=board("my1060wd.wd5.myworkdayjobs.com","my1060wd","Chicago_Cubs_FO")
assert snap
out=[]
for job in snap[1]:
    url="https://my1060wd.wd5.myworkdayjobs.com/Chicago_Cubs_FO"+job["externalPath"]
    try:
        d=enrichment.fetch_detail({"url":url})
        out.append({"url":url,"description_chars":len(d["description"]),"date":d["posted_at"]})
    except requests.HTTPError as exc:
        if exc.response is not None and exc.response.status_code in (403, 429):
            out.append({"http":exc.response.status_code});break
        raise
Path("cubs-details.json").write_text(json.dumps(out,indent=2));print(out)
assert len(out)==len(snap[1]) and all(r.get("description_chars",0)>=80 for r in out)
