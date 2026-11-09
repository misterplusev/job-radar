"""Cloud scheduler and read-only board, patterned on the sportsbook HF runtime.

Owner: ABET sports teams jobs. One subprocess, 45-minute deadline, 3 HTTP workers.
SCRAPER_PAUSED or data/STOP_SCRAPER parks scraping; notifications have a separate
guard. No browser or AI-agent processes are used. No scheduler runs on Windows.
"""
import hmac
import json
import os
import subprocess
import sys
import threading
import time
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
ET = ZoneInfo('America/New_York')
HOURS = (6,8,10,12,14,16,18,20)
LOCK = threading.Lock()
SHUTDOWN = threading.Event()
STATE = {'last_run_end':None,'last_run_start':None,'last_run_rc':None,'last_run_trigger':None}


def now(): return datetime.now(timezone.utc).isoformat()


def schedule(stamp=None):
    current=(stamp or datetime.now(timezone.utc)).astimezone(ET)
    slots=[(current+timedelta(days=d)).replace(hour=h,minute=0,second=0,microsecond=0) for d in (-1,0,1) for h in HOURS]
    before=max(s for s in slots if s<=current);after=min(s for s in slots if s>current)
    return {'timezone':'America/New_York','weekday_hours_et':list(HOURS),'weekend_hours_et':list(HOURS),
            'previous_due_utc':before.astimezone(timezone.utc).isoformat(),'next_due_utc':after.astimezone(timezone.utc).isoformat()}


def read_json(path, fallback):
    try:return json.loads(path.read_text(encoding='utf-8'))
    except (OSError,ValueError):return fallback


def health():
    manifest=read_json(ROOT/'data/runtime/latest_scrape_manifest.json',{})
    sched=schedule();status=manifest.get('overall_status','unknown')
    if STATE['last_run_rc'] not in (None,0):status='failed'
    if LOCK.locked():status='running'
    last=STATE['last_run_end']
    age=(datetime.now(timezone.utc)-datetime.fromisoformat(last)).total_seconds() if last else None
    due=datetime.fromisoformat(sched['previous_due_utc'])
    missed=not LOCK.locked() and datetime.now(timezone.utc)>due+timedelta(minutes=30) and (not last or datetime.fromisoformat(last)<due)
    if missed and status=='healthy':status='degraded'
    return {'service':'abet-sports-teams-jobs','runtime':'huggingface-space','status':status,
            **STATE,'scrape_running':LOCK.locked(),'last_run_age_seconds':age,'schedule':dict(sched,missed=missed),
            'notifications_paused':os.environ.get('NOTIFICATIONS_PAUSED','1')!='0',
            'latest_manifest':manifest}


def run(trigger):
    if os.environ.get('SCRAPER_PAUSED')=='1' or (ROOT/'data/STOP_SCRAPER').exists():return
    if not LOCK.acquire(False):return
    try:
        STATE.update(last_run_start=now(),last_run_trigger=trigger)
        logdir=ROOT/'data/logs';logdir.mkdir(parents=True,exist_ok=True)
        with (logdir/'latest.log').open('w',encoding='utf-8') as log:
            completed=subprocess.run([sys.executable,'-u',str(ROOT/'pipeline_local.py'),'--cloud','--trigger',trigger],
                                     cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=45*60)
        STATE['last_run_rc']=completed.returncode
        if completed.returncode==0 and os.environ.get('NOTIFICATIONS_PAUSED','1')=='0':
            subprocess.run([sys.executable,str(ROOT/'publish_teams.py'),'--post','--limit','100'],cwd=ROOT,timeout=600,check=True)
    except Exception as exc:
        STATE['last_run_rc']=1
        STATE['last_error']=type(exc).__name__
    finally:
        STATE['last_run_end']=now()
        (ROOT/'data/runtime').mkdir(parents=True,exist_ok=True)
        (ROOT/'data/runtime/launcher_state.json').write_text(json.dumps(STATE),encoding='utf-8')
        LOCK.release()
        print(json.dumps({'event':'completed',**STATE}),flush=True)


def scheduler():
    fired=set()
    while not SHUTDOWN.wait(30):
        current=datetime.now(ET)
        slot=current.strftime('%Y-%m-%d:%H')
        if current.hour in HOURS and slot not in fired:
            fired={slot}
            run('schedule')


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path=self.path.split('?')[0]
        if path=='/api/log':
            wanted=os.environ.get('RUN_TOKEN','')
            if not wanted or not hmac.compare_digest(self.headers.get('X-Run-Token',''),wanted):self.send_error(403);return
            log=ROOT/'data/logs/latest.log'
            body=('\n'.join(log.read_text(encoding='utf-8',errors='replace').splitlines()[-80:]) if log.exists() else '').encode();kind='text/plain'
        elif path=='/api/health':
            body=json.dumps(health()).encode();kind='application/json'
        elif path in ('/','/index.html','/team_jobs.json'):
            file=ROOT/'board'/('team_jobs.json' if path.endswith('.json') else 'live.html')
            if not file.exists():self.send_error(503);return
            body=file.read_bytes();kind='application/json' if file.suffix=='.json' else 'text/html; charset=utf-8'
        else:self.send_error(404);return
        self.send_response(200);self.send_header('Content-Type',kind);self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)

    def do_POST(self):
        wanted=os.environ.get('RUN_TOKEN','')
        if self.path!='/api/run' or not wanted or not hmac.compare_digest(self.headers.get('X-Run-Token',''),wanted):self.send_error(403);return
        if LOCK.locked():self.send_error(409);return
        threading.Thread(target=run,args=('manual',),daemon=True).start()
        self.send_response(202);self.end_headers()

    def log_message(self,*args):pass


if __name__=='__main__':
    if os.name=='nt':raise SystemExit('Cloud runtime only; use the bounded pipeline CLI locally')
    STATE.update(read_json(ROOT/'data/runtime/launcher_state.json',{}))
    threading.Thread(target=scheduler,daemon=True).start()
    if os.environ.get('RUN_ON_BOOT','1')=='1':threading.Thread(target=run,args=('boot',),daemon=True).start()
    print('Sports teams HTTP starting on '+os.environ.get('PORT','7861'),flush=True)
    try:ThreadingHTTPServer(('0.0.0.0',int(os.environ.get('PORT','7861'))),Handler).serve_forever()
    finally:SHUTDOWN.set()
