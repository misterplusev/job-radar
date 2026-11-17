"""Cloud Actions entrypoint. Execute the active staging lease against an exact checkout."""
import json,os,sys,subprocess
from pathlib import Path
import requests
ROOT=Path(__file__).resolve().parent
if os.environ.get('GITHUB_ACTIONS')!='true':raise SystemExit('GitHub-hosted cloud execution only')
required=('STAGING_REPORT_TOKEN','STAGING_REPORT_URL','STAGING_CONTROL_URL','STAGING_LEASE_ID','STAGING_MODULE','STAGING_SOURCE_DIR')
if any(not os.environ.get(k) for k in required):raise SystemExit('Missing staging input')
if any(os.environ.get(k) for k in ('SUPABASE_URL','SUPABASE_SERVICE_ROLE_KEY','DISCORD_WEBHOOK_JOBS')):raise SystemExit('Production credentials forbidden')
headers={'Authorization':'Bearer '+os.environ['STAGING_REPORT_TOKEN']}
r=requests.get(os.environ['STAGING_CONTROL_URL']+'/lease',headers=headers,timeout=20);r.raise_for_status();task=r.json()
if task.get('lease_id')!=os.environ['STAGING_LEASE_ID'] or task.get('module')!=os.environ['STAGING_MODULE']:raise SystemExit('Lease not active for this job')
source=Path(os.environ['STAGING_SOURCE_DIR']).resolve()
sha=subprocess.run(['git','rev-parse','HEAD'],cwd=source,check=True,capture_output=True,text=True).stdout.strip()
if sha!=task['source_sha']:raise SystemExit('Candidate checkout does not match pinned lease SHA')
module=task['module'];folder='robotics' if module=='sports_teams' else module
(ROOT/'sources').mkdir(exist_ok=True);(ROOT/'sources'/folder).symlink_to(source,target_is_directory=True)
(ROOT/'source_manifest.json').write_text(json.dumps({module:{'sha':sha}}))
catalog=ROOT.parent/'catalog.json'
if not (ROOT/'catalog.json').exists():(ROOT/'catalog.json').write_bytes(catalog.read_bytes())
import server
server.LOCK.acquire();server.STATE['active']={'lease_id':task['lease_id'],'module':module}
server.execute(task)
report=server.STATE['latest'];report['github_run_url']='https://github.com/'+os.environ['GITHUB_REPOSITORY']+'/actions/runs/'+os.environ['GITHUB_RUN_ID']
out=Path(os.environ.get('RUNNER_TEMP','/tmp'))/'staging-result.json';out.write_text(json.dumps(report,indent=2));print(json.dumps({k:report.get(k) for k in ('module','status','source_sha','started_at','finished_at','github_run_url')}))
if server.STATE['report_error']:raise SystemExit('Result reporting failed: '+server.STATE['report_error'])
raise SystemExit(0 if report['status']=='passed' else 1)
