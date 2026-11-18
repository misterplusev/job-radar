"""Store the validated public listings as bounded, rolling GitHub release assets."""
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
from urllib.parse import quote
from datetime import datetime,timezone

import requests

REPO="misterplusev/job-radar"
TAG="abet-workday-listings-v1"
API="https://api.github.com/repos/"+REPO
NAME=re.compile(r"listings-([0-9]+)-([0-9]+)\.json\.gz")
def main():
    if os.environ.get("GITHUB_REPOSITORY")!=REPO or os.environ.get("GITHUB_REF_NAME")!="master" or os.environ.get("GITHUB_ACTIONS")!="true":
        raise RuntimeError("Release writes require the deployed cloud workflow")
    path=Path("proof/listings.json.gz"); body=path.read_bytes()
    payload=json.loads(gzip.decompress(body)); assert payload["schema"]==1 and 0<len(payload["boards"])<=19
    at=datetime.fromisoformat(payload["observed_at"])
    assert 0<=(datetime.now(timezone.utc)-at).total_seconds()<10800
    stamp=int(at.timestamp());run=int(os.environ["GITHUB_RUN_ID"])
    name=f"listings-{stamp}-{run}.json.gz"
    marker="Bounded public snapshots of official team and employer career pages. Managed by the ABET Workday collector."
    with requests.Session() as gh:
        gh.headers.update({"Authorization":"Bearer "+os.environ["GH_TOKEN"],"Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28"})
        def call(method,url,**options):
            reply=gh.request(method,url,timeout=(7,35),**options);reply.raise_for_status();return reply
        reply=gh.get(API+"/releases/tags/"+TAG,timeout=15)
        if reply.status_code==404:
            release=call("POST",API+"/releases",json={"tag_name":TAG,"target_commitish":os.environ["GITHUB_SHA"],
                "name":"Verified Workday career listings","body":marker,"prerelease":True,"make_latest":"false"}).json()
        else:
            reply.raise_for_status();release=reply.json()
        assert release["tag_name"]==TAG and release["body"]==marker and not release.get("immutable")
        assets=call("GET",API+f'/releases/{release["id"]}/assets',params={"per_page":100}).json()
        managed=[a for a in assets if NAME.fullmatch(a["name"]) and a["state"]=="uploaded"]
        if any(int(NAME.fullmatch(a["name"])[1])>stamp for a in managed):
            raise RuntimeError("A newer snapshot already exists")
        existing=next((a for a in managed if a["name"]==name),None)
        if not existing:
            url=f'https://uploads.github.com/repos/{REPO}/releases/{release["id"]}/assets'
            existing=call("POST",url,params={"name":name},headers={"Content-Type":"application/gzip"},data=body).json()
        assert existing["size"]==len(body) and existing["state"]=="uploaded"
        # Read back with public credentials just like the consumers; never forward the write token.
        response=requests.get(existing["browser_download_url"],timeout=35);response.raise_for_status()
        assert hashlib.sha256(response.content).digest()==hashlib.sha256(body).digest()
        ordered=sorted([a for a in managed if a["id"]!=existing["id"]],key=lambda a:tuple(map(int,NAME.fullmatch(a["name"]).groups())),reverse=True)
        for expired in ordered[2:]:
            call("DELETE",API+f'/releases/assets/{expired["id"]}')
        print(json.dumps({"observed_at":payload["observed_at"],"boards":len(payload["boards"]),
              "asset":existing["browser_download_url"],"bytes":len(body),"sha256":hashlib.sha256(body).hexdigest()}))
if __name__=="__main__":main()
