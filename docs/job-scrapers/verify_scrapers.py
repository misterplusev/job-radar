"""Read-only, bounded architecture/cadence inspection. No scraper imports or writes to services.

Uses existing `gh` authentication plus public health endpoints. Writes only the
requested local JSON receipt. Never dispatches jobs, sends Discord, reads secrets,
applies SQL, or launches agents/browsers. Owner: ABET jobs documentation.
"""
import argparse,base64,json,re,shutil,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError

ROOT=Path(__file__).resolve().parent

def gh_json(exe,endpoint):
    p=subprocess.run([exe,'api',endpoint],capture_output=True,text=True,encoding='utf-8',timeout=35)
    if p.returncode:raise RuntimeError('GitHub read failed; verify gh authentication/repository access')
    return json.loads(p.stdout)

def public_json(url):
    try:
        with urlopen(Request(url,headers={'User-Agent':'ABET-Jobs-Documentation-Audit/1.0'}),timeout=30) as r:
            return json.load(r)
    except HTTPError as e:
        if e.code == 503:return json.load(e)
        raise

def inspect(registry,exe):
    report={'checked_at':datetime.now(timezone.utc).isoformat(),'read_only':True,'modules':[]}
    for m in registry['modules']:
        r={'id':m['id'],'runtime':m['runtime'],'warnings':[]}
        try:
            wf=gh_json(exe,f"repos/{m['repo']}/actions/workflows/{m['workflow']}")
            r['workflow_state']=wf['state']
            if wf['state']!=m['expected_workflow_state']:r['warnings'].append('workflow_state_drift')
            # Actions executes schedules on the repository DEFAULT branch.
            repo=gh_json(exe,f"repos/{m['repo']}")
            r['default_branch']=repo['default_branch'];r['repository_private']=repo['private']
            f=gh_json(exe,f"repos/{m['repo']}/contents/.github/workflows/{m['workflow']}?ref={repo['default_branch']}")
            source=base64.b64decode(f['content']).decode('utf-8')
            r['workflow_blob_sha']=f['sha'];r['configured_crons']=re.findall(r'cron:\s*[\"\x27]([^\"\x27]+)',source)
            if r['configured_crons']!=m['expected_crons']:r['warnings'].append('cron_drift')
            cloud_scheduler=m.get('scheduler',{}).get('type')=='cloudflare-durable-object-alarm'
            event='workflow_dispatch' if cloud_scheduler else 'schedule'
            runs=gh_json(exe,f"repos/{m['repo']}/actions/workflows/{m['workflow']}/runs?branch={repo['default_branch']}&event={event}&per_page=30")['workflow_runs']
            if cloud_scheduler:
                prefix=m['scheduler'].get('run_name_prefix','job-radar')
                runs=[x for x in runs if re.match('^'+re.escape(prefix)+r' \d{4}-\d{2}-\d{2}T',x.get('display_title',''))][:8]
                r['scheduler']=m['scheduler']
            else:runs=runs[:8]
            r['recent_scheduled_runs']=[{k:x.get(k) for k in ('id','created_at','updated_at','status','conclusion','html_url')} for x in runs]
            dates=[datetime.fromisoformat(x['created_at'].replace('Z','+00:00')) for x in runs]
            r['observed_start_gaps_hours']=[round((a-b).total_seconds()/3600,2) for a,b in zip(dates,dates[1:])]
            if m['runtime']=='github-actions':
                if not dates:r['warnings'].append('no_scheduled_run_evidence')
                elif (datetime.now(timezone.utc)-dates[0]).total_seconds()>7200:r['warnings'].append('last_scheduled_start_over_two_hours_ago')
                if any(x>2 for x in r['observed_start_gaps_hours']):r['warnings'].append('observed_gaps_exceed_hourly_configuration')
        except Exception as e:r['warnings'].append(f'workflow_inspection_failed: {type(e).__name__}: {e}')
        if m.get('health'):
            try:
                h=public_json(m['health']);r['health']={k:h.get(k) for k in ('status','healthy','checked_at','last_run_end','last_scrape_at','next_run_utc','scrape_running','schedule','notifications_paused','delivery_status','providers_expected_count','providers_success_count','providers_empty','providers_error','providers_timeout') if k in h}
                if m.get('scheduler',{}).get('type')=='cloudflare-durable-object-alarm':
                    scheduler_url=m['scheduler'].get('health_url',m['health'])
                    sh=h if scheduler_url==m['health'] else public_json(scheduler_url)
                    relevant=[x for x in sh.get('overdue',[]) if x.startswith(m['id']) or x=='scheduler heartbeat']
                    r['scheduler_health']={'paused':sh.get('paused'),'last_scheduler_tick':sh.get('last_scheduler_tick'),
                                          'module':sh.get('modules',{}).get(m['id']),'overdue':relevant}
                    if sh.get('paused'):r['warnings'].append('scheduler_paused')
                    if relevant:r['warnings'].append('scheduler_overdue')
                if h.get('latest_manifest'):
                    manifest=h['latest_manifest']
                    r['operational_status']=manifest.get('runtime_status',manifest.get('overall_status'))
                    r['career_link_audit_status']=manifest.get('career_link_audit_status')
                if 'modules' not in h and h.get('status') not in ('healthy',None):r['warnings'].append('live_health_'+str(h.get('status')))
                if m.get('schedule'):
                    for k,v in m['schedule'].items():
                        if h.get('schedule',{}).get(k)!=v:r['warnings'].append('runtime_schedule_drift:'+k)
                if m.get('coverage'):
                    c=public_json(m['coverage']);r['coverage_summary']=c['summary']
                    r['unproven_career_links']=[t['team'] for t in c['teams'] if not t.get('career_link_verified')]
            except Exception as e:r['warnings'].append(f'health_inspection_failed: {type(e).__name__}')
        report['modules'].append(r)
    report['warning_count']=sum(len(m['warnings']) for m in report['modules'])
    return report

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=ROOT/'latest_verification.json');p.add_argument('--strict',action='store_true');a=p.parse_args()
    exe=shutil.which('gh')
    if not exe and Path(r'C:\Program Files\GitHub CLI\gh.exe').exists():exe=r'C:\Program Files\GitHub CLI\gh.exe'
    if not exe:raise SystemExit('GitHub CLI is required; authenticate with gh before running this read-only verifier.')
    result=inspect(json.loads((ROOT/'scrapers.json').read_text(encoding='utf-8')),exe)
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    for m in result['modules']:print(m['id'],json.dumps({'crons':m.get('configured_crons'),'workflow_state':m.get('workflow_state'),'warnings':m['warnings']}))
    print('Receipt:',a.out.resolve())
    return 1 if a.strict and result['warning_count'] else 0

if __name__=='__main__':raise SystemExit(main())
