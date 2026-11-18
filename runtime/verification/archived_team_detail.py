"""Inspect existing official board artifacts on the GitHub-hosted runner, without employer traffic."""
import hashlib
import io
import json
import os
import subprocess
from pathlib import Path
import tarfile
import zipfile

assert os.environ.get("GITHUB_ACTIONS") == "true"
inputs=json.loads(Path('runtime/verification/history-input.json').read_text())
targets={x['url']:x for x in inputs['targets']}
results=[]
candidates={}
for artifact in inputs['artifacts']:
    # Fetch the artifact through the repository's cloud CLI so authorization stays on GitHub's API.
    data=subprocess.check_output(['gh','api',f"repos/{os.environ['GITHUB_REPOSITORY']}/actions/artifacts/{artifact['id']}/zip"])
    with zipfile.ZipFile(io.BytesIO(data)) as outer:
        member=next(x for x in outer.infolist() if x.filename.endswith('.tar'))
        assert member.file_size<100_000_000
        with tarfile.open(fileobj=io.BytesIO(outer.read(member))) as tar:
            files=[x for x in tar.getmembers() if x.isfile() and x.name.rsplit('/',1)[-1]=='team_jobs.json']
            assert len(files)==1 and files[0].size<75_000_000
            payload=json.load(tar.extractfile(files[0]))
    rows=payload['jobs']
    read=qualifying=0
    for j in rows:
        t=targets.get(j.get('url'))
        if not t or t['title']!=j.get('title') or t['team']!=j.get('team'):
            continue
        read+=1
        body=(j.get('description') or '').strip()
        if len(body)<80 or j.get('detail_status')!='success' or not j.get('detail_checked_at') or body.endswith(('...','…')):
            continue
        qualifying+=1
        candidates.setdefault(t['url'],{'id':t['id'],'url':t['url'],'company':t['team'],'title':t['title'],
                'description':body,'sha256':hashlib.sha256(body.encode()).hexdigest(),
                'observed_at':j['detail_checked_at'],'artifact':artifact['id'],'module':'sports_teams'})
    results.append({'artifact':artifact,'jobs':len(rows),'verified_target_identities':read,'qualifying_bodies':qualifying})
out=Path('history-proof');out.mkdir()
(out/'history.json').write_text(json.dumps({'targets':len(targets),'artifacts':results,'recoverable':len(candidates)},indent=2)+'\n')
(out/'verified.json').write_text(json.dumps(list(candidates.values()),indent=2)+'\n')
print((out/'history.json').read_text())
