"""Read one ordinary employer-published posting per affected host, without a browser."""
import gzip,json
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit
import requests
from bs4 import BeautifulSoup
payload=json.loads(gzip.decompress(Path("input/listings.json.gz").read_bytes()))
report=[]
for key,board in payload["boards"].items():
    host,tenant,site=key.split("/")
    if site not in {"BetMGM","Betway","seminolehardrockcareers","MLSE","Detroit-Tigers","Chicago_Cubs_FO"} or not board["jobs"]:continue
    # Select one genuine vacancy from that employer. Do not retry rejected requests.
    job=board["jobs"][0];url=f"https://{host}/en-US/{site}"+job["externalPath"]
    r=requests.get(url,headers={"User-Agent":"ABET-Jobs/1.0 (+https://abet-dashboard.vercel.app)"},timeout=(5,15),allow_redirects=False)
    rec={"site":site,"url":url,"http":r.status_code,"challenge":r.headers.get("CF-Mitigated")=="challenge","bytes":len(r.content)}
    if r.status_code==200 and not rec["challenge"]:
        soup=BeautifulSoup(r.content,"html.parser")
        rec["title_tag"]=soup.title.get_text(strip=True)[:120] if soup.title else None
        for elem in soup.select('script[type="application/ld+json"]'):
            try: items=json.loads(elem.string or elem.get_text())
            except ValueError:continue
            for item in items if isinstance(items,list) else [items]:
                if isinstance(item,dict) and item.get("@type")=="JobPosting":
                    desc=BeautifulSoup(item.get("description") or "","html.parser").get_text(" ",strip=True)
                    rec.update(title=item.get("title"),description_chars=len(desc),sample=desc[:75],date=item.get("datePosted"))
    report.append(rec)
print(json.dumps(report,indent=2));Path("detail-evidence.json").write_text(json.dumps(report,indent=2))
