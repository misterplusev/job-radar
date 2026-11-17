"""Cloud Actions staging execution library. No timer, HTTP server, database key or Discord webhook."""
import datetime as dt,hashlib,hmac,json,os,re,shutil,subprocess,sys,tempfile,threading,time
from pathlib import Path
import requests
ROOT=Path(__file__).resolve().parent
MANIFEST=json.loads((ROOT/'source_manifest.json').read_text())
CATALOG=json.loads((ROOT/'catalog.json').read_text())
LOCK=threading.Lock();STATE={'active':None,'completed':0,'latest':None,'report_error':None}

def now():return dt.datetime.now(dt.timezone.utc).isoformat()
def child_env(module,network_off=False):
    base=ROOT/'sources'/('robotics' if module=='sports_teams' else module)
    paths=[str(ROOT/'isolation'),str(ROOT),str(base)]
    if module=='sports_teams':paths.insert(0,str(base/'sports_teams'))
    if module=='sportsbook':paths.insert(0,str(base/'scripts'))
    # Explicit allowlist: children never inherit staging control/report/HF tokens.
    return {'PATH':os.environ.get('PATH','/usr/local/bin:/usr/bin:/bin'),'HOME':'/tmp','LANG':'C.UTF-8','PYTHONPATH':os.pathsep.join(paths),'PYTHONDONTWRITEBYTECODE':'1','PYTHONUNBUFFERED':'1','ABET_STAGING_CLOUD':'1','STAGING_TEST_NETWORK_OFF':'1' if network_off else '0','ABET_BASE_DIR':'/tmp/staging-diagnostics'}

def command(cmd,cwd,env,timeout):
    try:
        p=subprocess.run(cmd,cwd=cwd,env=env,capture_output=True,text=True,timeout=timeout)
        output=p.stdout+'\n'+p.stderr
        return {'passed':p.returncode==0,'returncode':p.returncode,'tests':sum(int(x) for x in re.findall(r'Ran (\d+) tests?',output)),'tail':output[-1800:]}
    except subprocess.TimeoutExpired:return {'passed':False,'returncode':124,'tests':0,'tail':'Hard cloud subprocess deadline exceeded'}

def execute(task):
    module=task['module'];base=ROOT/'sources'/('robotics' if module=='sports_teams' else module)
    report={'lease_id':task['lease_id'],'module':module,'slot':task['slot'],'source_sha':MANIFEST[module]['sha'],'runner_build':os.environ.get('STAGING_BUILD','unknown'),'github_run_url':'https://github.com/'+os.environ.get('GITHUB_REPOSITORY','')+'/actions/runs/'+os.environ.get('GITHUB_RUN_ID',''),'started_at':now(),'tests':[],'sources':[],'production_writes':0,'discord_sends':0}
    try:
        with tempfile.TemporaryDirectory(prefix='abet-staging-') as tmp:
            # Existing tests may write local cloud fixture files; source snapshots remain intact.
            work=Path(tmp)/'source';shutil.copytree(base,work)
            env=child_env(module,True)
            paths=[str(ROOT/'isolation'),str(ROOT),str(work)]
            if module=='sports_teams':paths.insert(0,str(work/'sports_teams'))
            if module=='sportsbook':paths.insert(0,str(work/'scripts'))
            env['PYTHONPATH']=os.pathsep.join(paths);env['ABET_BASE_DIR']=str(Path(tmp)/'fixture-data')
            testdir='sports_teams' if module=='sports_teams' else 'tests'
            pattern='test_workday*.py' if module=='sportsbook' else 'test_*.py'
            report['tests'].append(command([sys.executable,'-m','unittest','discover','-s',testdir,'-p',pattern,'-v'],work,env,90))
            if module=='sportsbook':report['tests'].append(command([sys.executable,'-m','unittest','discover','-s','tests','-p','test_hf_launcher_schedule_health.py','-v'],work,env,30))
            if all(t['passed'] for t in report['tests']):
                for sid in task['source_ids']:
                    output=Path(tmp)/'probe.json'
                    result=command([sys.executable,str(ROOT/'live_probe.py'),module,sid,task['lease_id'],str(output)],ROOT,child_env(module),120)
                    if output.exists():report['sources'].append(json.loads(output.read_text()));output.unlink()
                    else:report['sources'].append({'source_id':sid,'status':'failed','complete':False,'error':result['tail'][-600:],'requests':12 if result['returncode']==124 else 0,'sample':[]})
            report['status']='test_failed' if not all(t['passed'] for t in report['tests']) else 'cooldown' if not report['sources'] else 'passed' if all(s['status']=='passed' for s in report['sources']) else 'degraded'
    except Exception as exc:report.update(status='runner_error',error=type(exc).__name__+': '+str(exc)[:300])
    finally:
        report['finished_at']=now()
        # Persist at most one active report locally until the controller acknowledges it.
        STATE['latest']=report;STATE['completed']+=1
        for attempt in range(3):
            try:
                response=requests.post(os.environ['STAGING_REPORT_URL'],headers={'Authorization':'Bearer '+os.environ['STAGING_REPORT_TOKEN']},json=report,timeout=15)
                response.raise_for_status();STATE['report_error']=None;break
            except Exception as exc:
                STATE['report_error']=type(exc).__name__+': '+str(exc)[:160]
                if attempt<2:time.sleep(2**attempt)
        STATE['active']=None;LOCK.release()
