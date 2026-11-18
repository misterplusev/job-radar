"""Download one verified release asset with this hosted runner's read-only GitHub token."""
from datetime import datetime,timezone
import hashlib
import json,os,re,sys
from pathlib import Path
import requests

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from jobradar.workday_snapshot import RELEASE_URL, _unpack

def main():
    assert os.environ.get("GITHUB_ACTIONS")=="true"
    token=os.environ["GH_TOKEN"]
    headers={"Authorization":"Bearer "+token,"Accept":"application/vnd.github+json"}
    reply=requests.get(RELEASE_URL,headers=headers,timeout=(5,15))
    reply.raise_for_status()
    assets=[a for a in reply.json()["assets"] if a.get("state")=="uploaded" and
            re.fullmatch(r"listings-[0-9]+-[0-9]+\.json\.gz",a["name"]) and 0<a["size"]<=3000000]
    asset=max(assets,key=lambda a:tuple(map(int,re.findall(r"\d+",a["name"]))))
    endpoint=f'https://api.github.com/repos/misterplusev/job-radar/releases/assets/{int(asset["id"])}'
    # requests strips Authorization when following an off-host redirect.
    data=requests.get(endpoint,headers={**headers,"Accept":"application/octet-stream"},timeout=(5,30))
    data.raise_for_status()
    raw=data.content
    assert len(raw)==asset["size"] and asset.get("digest")=="sha256:"+hashlib.sha256(raw).hexdigest()
    bundle=_unpack(raw);at=datetime.fromisoformat(bundle["observed_at"])
    age=(datetime.now(timezone.utc)-at).total_seconds()
    if age < -60 or age >10800:
        print(f"Latest verified catalog is {age/3600:.1f} hours old; direct collection will run.")
        if os.environ.get("REQUIRE_FRESH_WORKDAY")=="1":raise ValueError("expected fresh snapshot")
        return
    assert bundle["schema"]==1 and len(bundle["boards"])==19
    path=Path(os.environ["RUNNER_TEMP"])/"verified-workday-catalog.json.gz"
    tmp=path.with_suffix(".tmp");tmp.write_bytes(raw);tmp.replace(path)
    with open(os.environ["GITHUB_ENV"],"a",encoding="utf-8") as out:print("WORKDAY_LISTINGS_FILE="+str(path),file=out)
    print(f'Verified Workday asset {asset["id"]}, {len(bundle["boards"])} boards, observed {at.isoformat()}, {len(raw)} bytes')
if __name__=="__main__":main()
