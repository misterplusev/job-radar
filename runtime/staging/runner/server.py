"""Private HF cloud staging runner. No timer, boot run, database key or Discord webhook."""
import datetime as dt,hashlib,hmac,json,os,re,shutil,subprocess,sys,tempfile,threading,time
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
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
    report={'lease_id':task['lease_id'],'module':module,'slot':task['slot'],'source_sha':MANIFEST[module]['sha'],'runner_build':os.environ.get('STAGING_BUILD','unknown'),'started_at':now(),'tests':[],'sources':[],'production_writes':0,'discord_sends':0}
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
        try:
            response=requests.post(os.environ['STAGING_REPORT_URL'],headers={'Authorization':'Bearer '+os.environ['STAGING_REPORT_TOKEN']},json=report,timeout=20)
            response.raise_for_status();STATE['report_error']=None
        except Exception as exc:STATE['report_error']=type(exc).__name__+': '+str(exc)[:160]
        STATE['active']=None;LOCK.release()

class Handler(BaseHTTPRequestHandler):
    def reply(self,obj,status=200):
        data=json.dumps(obj).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
    def authorized(self):
        want=os.environ.get('STAGING_RUN_TOKEN','');got=self.headers.get('X-Run-Token','')
        return bool(want) and hmac.compare_digest(want,got)
    def do_GET(self):
        if self.path=='/health':return self.reply({'service':'abet-jobs-isolated-staging','build':os.environ.get('STAGING_BUILD'),'active':STATE['active'],'completed':STATE['completed'],'report_error':STATE['report_error'],'source_shas':{m:v['sha'] for m,v in MANIFEST.items()},'has_timer':False,'production_credentials_present':any(os.environ.get(k) for k in ('SUPABASE_URL','SUPABASE_SERVICE_ROLE_KEY','DISCORD_WEBHOOK_JOBS'))})
        if self.path=='/result' and self.authorized():return self.reply(STATE['latest'])
        self.reply({'error':'not found'},404)
    def do_POST(self):
        if self.path!='/run' or not self.authorized():return self.reply({'error':'unauthorized'},403)
        size=int(self.headers.get('Content-Length','0'))
        if not 0<size<8192:return self.reply({'error':'invalid size'},400)
        try:
            task=json.loads(self.rfile.read(size));module=task['module']
            assert module in CATALOG and task['source_sha']==MANIFEST[module]['sha']
            assert isinstance(task['source_ids'],list) and len(task['source_ids'])<=2
            allowed={s['id'] for s in CATALOG[module] if s['supported']}
            assert set(task['source_ids'])<=allowed
            assert 1<=len(task['lease_id'])<=120 and 1<=len(task['slot'])<=80
        except Exception:return self.reply({'error':'invalid task or source revision'},400)
        if STATE['latest'] and STATE['latest']['lease_id']==task['lease_id']:return self.reply({'started':False,'reason':'already completed'})
        if not LOCK.acquire(False):return self.reply({'started':False,'reason':'busy'},409)
        STATE['active']={'lease_id':task['lease_id'],'module':module,'started_at':now()}
        threading.Thread(target=execute,args=(task,),daemon=True).start();self.reply({'started':True},202)
    def log_message(self,*args):pass

if __name__=='__main__':
    if any(os.environ.get(k) for k in ('SUPABASE_URL','SUPABASE_SERVICE_ROLE_KEY','DISCORD_WEBHOOK_JOBS')):raise SystemExit('Production credentials forbidden in staging')
    # Every copied file must still match its pinned source manifest.
    for module,meta in MANIFEST.items():
        for path,digest in meta.get('file_sha256',{}).items():
            if hashlib.sha256((ROOT/'sources'/module/path).read_bytes()).hexdigest()!=digest:raise SystemExit('Pinned source mismatch '+module+'/'+path)
    ThreadingHTTPServer(('0.0.0.0',7860),Handler).serve_forever()
