"""Approval-gated, one-browser cloud compatibility check. No challenge solving, login, write or publishing."""
import importlib.util,json,os,time
from pathlib import Path
import psutil
from playwright.sync_api import sync_playwright
assert os.environ.get('GITHUB_ACTIONS')=='true' and os.name=='nt','GitHub-hosted Windows only'
assert os.environ.get('CLOUD_BROWSER_APPROVED')=='true','Explicit operator exception required'
assert not any(os.environ.get(k) for k in ('SUPABASE_SERVICE_ROLE_KEY','DISCORD_WEBHOOK_JOBS'))
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('runaway_guard',ROOT/'20261019_runaway_guard_v1_0_0.py')
guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
g=guard.guard_before_agent('workday-cloud-compatibility-once')
if not g['ok']:raise SystemExit(g['reason'])
out=Path('proof/cloud-browser');out.mkdir(parents=True,exist_ok=True)
urls=[('boston-official','https://bostondynamics.com/careers/'),('boston-workday','https://bostondynamics.wd1.myworkdayjobs.com/en-US/Boston_Dynamics'),('betmgm','https://betmgminc.wd5.myworkdayjobs.com/en-US/BetMGM')]
proof={'run_url':f"https://github.com/{os.environ['GITHUB_REPOSITORY']}/actions/runs/{os.environ['GITHUB_RUN_ID']}",'browser_count':0,'pages':[],'production_writes':0,'discord_sends':0}
owned=[];browser=None
try:
    with sync_playwright() as p:
        before={x.pid for x in psutil.Process().children(recursive=True)}
        browser=p.chromium.launch(headless=True)
        proof['browser_count']=1
        owned=[x for x in psutil.Process().children(recursive=True) if x.pid not in before]
        context=browser.new_context();page=context.new_page()
        for name,url in urls:
            item={'name':name,'url':url};count=[0];responses=[]
            def route(r):
                count[0]+=1
                if count[0]>180:r.abort()
                else:r.continue_()
            def capture(response):
                if '/wday/cxs/' in response.url and response.url.endswith('/jobs'):
                    rec={'url':response.url,'status':response.status,'cf_mitigated':response.headers.get('cf-mitigated')}
                    if response.ok:
                        try:
                            data=response.json();rec.update(total=data.get('total'),jobs=len(data.get('jobPostings',[])))
                            rec['request_payload']=response.request.post_data_json
                            body=json.dumps(data,ensure_ascii=False)
                            if len(body.encode('utf-8'))<=1024*1024:
                                (out/(name+'-listing-'+str(len(responses))+'.json')).write_text(body,encoding='utf-8')
                        except Exception:pass
                    responses.append(rec)
            page.route('**/*',route);page.on('response',capture)
            try:
                response=page.goto(url,wait_until='domcontentloaded',timeout=35000)
                page.wait_for_timeout(5000)
                text=page.locator('body').inner_text(timeout=10000)
                item.update(status=response.status if response else None,final_url=page.url,title=page.title(),requests=count[0],text=text[:8000],listing_responses=responses)
                item['challenge_present']=any(t in text.lower() for t in ('security check','enable javascript and cookies','request is being verified','verify you are human'))
                page.screenshot(path=str(out/(name+'.png')),full_page=False)
                (out/(name+'.html')).write_text(page.content(),encoding='utf-8')
                # A challenge is recorded and left untouched. No clicks, scripts or token replay.
            except Exception as exc:item['error']=type(exc).__name__+': '+str(exc)[:400]
            finally:
                page.unroute('**/*',route);page.remove_listener('response',capture)
            proof['pages'].append(item)
        context.close();browser.close();browser=None
finally:
    if browser:
        try:browser.close()
        except Exception:pass
    for proc in reversed(owned):
        try:
            if proc.is_running():proc.kill()
        except psutil.Error:pass
    _,alive=psutil.wait_procs(owned,timeout=5)
    proof['cleanup']={'owned_processes':len(owned),'remaining_owned_processes':len(alive),'passed':not alive}
    guard.cleanup_after_agent(g['t0'],'workday-cloud-compatibility-once')
    (out/'report.json').write_text(json.dumps(proof,indent=2),encoding='utf-8')
print(json.dumps(proof,indent=2))
