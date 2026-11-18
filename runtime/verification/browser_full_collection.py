"""Approval-gated one-browser, cloud-only full Workday listing verification.

Uses normal website pagination buttons; never solves a challenge or replays cookies.
No database or notification code. Does not claim complete job-detail enrichment.
"""
import datetime as dt,importlib.util,json,os,subprocess,time
from pathlib import Path
from urllib.parse import urlsplit

class IncompleteListing(RuntimeError):pass

class Listing:
    def __init__(self):self.total=None;self.rows=[];self.paths=set();self.pages=0;self.skipped=0
    @property
    def complete(self):return self.total is not None and len(self.rows)+self.skipped==self.total
    def accept(self,data,offset):
        if self.complete:raise IncompleteListing('Unexpected page after complete listing')
        if not isinstance(data,dict) or not isinstance(data.get('jobPostings'),list):raise IncompleteListing('Invalid listing shape')
        total=data.get('total');rows=data['jobPostings']
        if type(total) is not int or not 0<=total<=5000:raise IncompleteListing('Invalid or over-budget advertised total')
        if offset!=len(self.rows)+self.skipped:raise IncompleteListing('Unexpected page offset')
        if self.total is None:self.total=total
        elif total not in (0,self.total):raise IncompleteListing('Advertised total changed')
        if not rows and len(self.rows)+self.skipped<self.total:raise IncompleteListing('Empty page before advertised total')
        fresh=[];kept=[];bad=0
        for row in rows:
            if not isinstance(row,dict):raise IncompleteListing('Invalid posting')
            path=row.get('externalPath');title=row.get('title')
            # A posting the employer published without a title or job path is skipped and counted. It used to fail
            # its board, and one failed board fails the whole 19-board collection (run 44407253462: one Hard Rock row).
            if not isinstance(path,str) or not path.startswith('/job/') or not title:bad+=1;continue
            if path in self.paths or path in fresh:raise IncompleteListing('Repeated posting across pages')
            fresh.append(path);kept.append(row)
        if len(self.rows)+self.skipped+len(rows)>self.total:raise IncompleteListing('Rows exceed advertised total')
        if self.skipped+bad>max(3,self.total//50):raise IncompleteListing('Too many postings without a title or job path')
        self.paths.update(fresh);self.rows.extend(kept);self.skipped+=bad;self.pages+=1
        if self.pages>250:raise IncompleteListing('Page cap exceeded')

def challenged(text):
    text=text.lower()
    return ('security check' in text and 'enable javascript and cookies' in text) or any(s in text for s in ('verify you are human','request is being verified'))

def acceptance_ok(report,expected):
    return (len(report['sources'])==expected and all(s['complete'] for s in report['sources'])
            and report['cleanup']['passed'] and report['cleanup']['remaining_owned_processes']==0
            and report['browser_count']==1 and report['production_writes']==0 and report['discord_sends']==0)

def main():
    assert os.environ.get('CLOUD_BROWSER_FULL_COLLECTION_APPROVED')=='true','Separate explicit approval required; first compatibility session has ended'
    assert os.environ.get('GITHUB_ACTIONS')=='true' and os.name=='nt','GitHub-hosted Windows only'
    assert not any(os.environ.get(k) for k in ('SUPABASE_SERVICE_ROLE_KEY','DISCORD_WEBHOOK_JOBS'))
    import psutil
    from playwright.sync_api import sync_playwright
    root=Path(__file__).resolve().parent
    spec=importlib.util.spec_from_file_location('guard',root/'20261019_runaway_guard_v1_0_0.py')
    guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
    state=guard.guard_before_agent('workday-full-listing-verification')
    if not state['ok']:raise SystemExit(state['reason'])
    catalog=json.loads((root/'full-browser-catalog.json').read_text())
    assert len(catalog)==19
    out=Path('proof/workday-full-listings');out.mkdir(parents=True,exist_ok=True)
    started=time.monotonic();deadline=started+900;requests_count=[0];owned=[];browser=None;blocked=set()
    report={'at':dt.datetime.now(dt.timezone.utc).isoformat(),'scope':'Complete official listing identities; detail enrichment and production persistence NOT tested','browser_count':0,'production_writes':0,'discord_sends':0,'sources':[]}
    try:
        with sync_playwright() as p:
            before={proc.pid for proc in psutil.Process().children(recursive=True)}
            browser=p.chromium.launch(headless=True);report['browser_count']=1
            owned=[proc for proc in psutil.Process().children(recursive=True) if proc.pid not in before]
            context=browser.new_context();page=context.new_page()
            def route(r):
                requests_count[0]+=1
                if requests_count[0]>2000 or time.monotonic()>deadline:r.abort()
                else:r.continue_()
            page.route('**/*',route)
            for index,source in enumerate(catalog):
                item={**source,'complete':False};listing=Listing();responses=[];begin=time.monotonic();source_deadline=min(deadline,begin+180)
                if source['host'] in blocked:
                    item['error']='Host challenge observed earlier in this session; no repeat requests';report['sources'].append(item);continue
                endpoint=f"/wday/cxs/{source['tenant']}/{source['site']}/jobs"
                def capture(response):
                    if urlsplit(response.url).netloc==source['host'] and urlsplit(response.url).path==endpoint and response.request.method=='POST':
                        record={'status':response.status,'challenge':response.headers.get('cf-mitigated')=='challenge'}
                        try:record.update(data=response.json(),offset=response.request.post_data_json.get('offset'))
                        except Exception:record['error']='Non-JSON listing response'
                        responses.append(record)
                def next_response(cursor):
                    until=min(source_deadline,time.monotonic()+25)
                    while len(responses)<=cursor and time.monotonic()<until:
                        page.wait_for_timeout(200)
                        if challenged(page.locator('body').inner_text(timeout=3000)):
                            blocked.add(source['host']);raise IncompleteListing('Browser security challenge; no interaction or retry')
                    if len(responses)<=cursor:raise IncompleteListing('No native listing response before deadline')
                    record=responses[cursor]
                    if record['challenge']:blocked.add(source['host']);raise IncompleteListing('Native listing returned a security challenge')
                    if record['status']!=200 or record.get('error'):raise IncompleteListing(f"Native listing HTTP{record['status']} or invalid JSON")
                    return record
                page.on('response',capture)
                try:
                    if time.monotonic()>deadline or requests_count[0]>=2000:raise IncompleteListing('Global budget exhausted')
                    response=page.goto(source['url'],wait_until='domcontentloaded',timeout=35000)
                    item['page_status']=response.status if response else None
                    cursor=0
                    while True:
                        if time.monotonic()>=source_deadline:raise IncompleteListing('Source deadline exhausted')
                        record=next_response(cursor);listing.accept(record['data'],record['offset']);cursor+=1
                        if listing.complete:break
                        button=page.get_by_role('button',name='next',exact=True)
                        if not button.is_enabled():raise IncompleteListing('Next button disabled before full total')
                        button.click(timeout=10000)
                    item.update(complete=True,advertised_total=listing.total,collected=len(listing.rows),skipped_malformed=listing.skipped,pages=listing.pages)
                    (out/f'{index:02d}-jobs.json').write_text(json.dumps({'source':source,'advertised_total':listing.total,'skipped_malformed':listing.skipped,'jobs':listing.rows},indent=2),encoding='utf-8')
                except Exception as exc:item['error']=type(exc).__name__+': '+str(exc)[:400]
                finally:
                    page.remove_listener('response',capture)
                    item.update(seconds=round(time.monotonic()-begin,3),pages_observed=listing.pages,rows_observed=len(listing.rows))
                    try:page.screenshot(path=str(out/f'{index:02d}.png'),timeout=5000)
                    except Exception:pass
                    report['sources'].append(item)
                    (out/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
            context.close();browser.close();browser=None
    finally:
        if browser:
            try:browser.close()
            except Exception:pass
        for proc in reversed(owned):
            try:
                if proc.is_running():
                    subprocess.run(['taskkill','/PID',str(proc.pid),'/T','/F'],capture_output=True,creationflags=0x08000000,timeout=15)
            except psutil.Error:pass
        _,alive=psutil.wait_procs(owned,timeout=5)
        guard.cleanup_after_agent(state['t0'],'workday-full-listing-verification')
        report.update(requests=requests_count[0],seconds=round(time.monotonic()-started,3),cleanup={'remaining_owned_processes':len(alive),'passed':not alive})
        report['all_listings_complete']=len(report['sources'])==19 and all(s['complete'] for s in report['sources'])
        (out/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
        print(json.dumps(report,indent=2))
    if not acceptance_ok(report,19):raise SystemExit(1)

if __name__=='__main__':main()
