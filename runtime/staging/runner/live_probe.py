"""One pinned provider in a cloud subprocess. No production persistence/sender calls."""
import sys,os,json,time,importlib,dataclasses
from pathlib import Path
from urllib.parse import urlsplit
from network_guard import NetworkBudget,BudgetExceeded
ROOT=Path(__file__).resolve().parent

def hosts_for(source):
    kind=source['kind'];spec=source['spec']
    common={'boards-api.greenhouse.io','api.lever.co','api.ashbyhq.com','www.amazon.jobs'}
    if kind=='workday':
        if 'host' in spec:return {spec['host']}
        return {spec['slug']+'.'+{'bostondynamics':'wd1','autostore':'wd3','rockwellautomation':'wd1'}[spec['slug']]+'.myworkdayjobs.com'}
    if kind=='sportsbook':
        return set(spec.get('hosts',[]))|{'boards-api.greenhouse.io','api.lever.co','api.ashbyhq.com'}
    for key in ('url','host'):
        if spec.get(key):common.add(urlsplit(spec[key]).hostname if key=='url' else spec[key])
    if kind=='teamworkonline':common.add('www.teamworkonline.com')
    if kind=='ultipro':common.update({spec.get('host')})
    if kind=='adp':common.update({'workforcenow.adp.com'})
    if kind=='lever':common.add('jobs.lever.co')
    return {x for x in common if x}

def run(module,source,run_id):
    base=ROOT/'sources'/('robotics' if module=='sports_teams' else module)
    if module=='sports_teams':sys.path[:0]=[str(base/'sports_teams'),str(base)]
    elif module=='sportsbook':sys.path.insert(0,str(base/'scripts'))
    else:sys.path.insert(0,str(base))
    os.chdir(base/'sports_teams' if module=='sports_teams' else base)
    guard=NetworkBudget(hosts_for(source)).install();start=time.monotonic()
    result={'source_id':source['id'],'kind':source['kind'],'status':'failed','complete':False,'jobs_total':0,'sample':[]}
    try:
        if module=='sports_teams':
            import live_refresh
            live_refresh.SOURCE_SECONDS=105;live_refresh.MAX_REQUESTS=12
            got=live_refresh.fetch_source(source['spec'])
            if got['status']!='success':raise RuntimeError(got.get('error','source failed'))
            jobs=got['rows']
        elif module=='sportsbook':
            from lib.workday_http import source_budget
            spec=source['spec'];cls=getattr(importlib.import_module('providers.'+spec['module']),spec['class'])
            with source_budget(start+105):jobs=cls().scrape()
        else:
            from jobradar.providers import build_providers
            from jobradar.workday_http import source_budget
            provider=build_providers({source['kind']:[source['spec']]})[0]
            with source_budget(start+105):jobs=provider.fetch(run_id)
        if guard.violation:raise BudgetExceeded(guard.violation)
        last_http={(e['host'],e['path'],e['method']):e for e in guard.events}
        if any(e.get('status',200)>=400 or e.get('error') for e in last_http.values()):raise ValueError('Provider returned after an unrecovered HTTP failure; observation incomplete')
        rows=[j if isinstance(j,dict) else dataclasses.asdict(j) for j in jobs]
        urls=[j.get('url') for j in rows]
        if any(not j.get('title') or not j.get('url') for j in rows) or len(set(urls))!=len(urls):raise ValueError('Incomplete or duplicate job identity')
        result.update(status='passed' if rows else 'empty',complete=True,jobs_total=len(rows),sample=[{'title':str(j['title'])[:180],'url':str(j['url'])[:600],'location':str(j.get('location') or '')[:160]} for j in rows[:25]])
    except Exception as exc:
        challenged=any(e.get('cf_mitigated')=='challenge' for e in guard.events) or 'WorkdayChallenge' in (type(exc).__name__+': '+str(exc))
        result.update(status='blocked_access' if challenged else 'budget_exhausted' if isinstance(exc,BudgetExceeded) else 'failed',error=(type(exc).__name__+': '+str(exc))[-600:])
    finally:
        guard.close();result.update(requests=guard.count,bytes=guard.bytes,seconds=round(time.monotonic()-start,3),http=guard.events[-12:])
    return result

if __name__=='__main__':
    if os.environ.get('ABET_STAGING_CLOUD')!='1':raise SystemExit('Cloud staging only')
    module,source_id,run_id,out=sys.argv[1:]
    source=next(x for x in json.loads((ROOT/'catalog.json').read_text())[module] if x['id']==source_id)
    if not source['supported']:raise SystemExit('Source transport not approved for this sandbox')
    Path(out).write_text(json.dumps(run(module,source,run_id)),encoding='utf-8')
