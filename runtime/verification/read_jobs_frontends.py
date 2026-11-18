"""Read through the production public role, inspect the independent employer index and staging status."""
import base64,json,re
from urllib.request import Request,urlopen
from urllib.parse import urlencode
from pathlib import Path

def read(url,headers=None):
    req=Request(url,headers={'User-Agent':'ABET-Jobs/1.0 (+https://abet-dashboard.vercel.app)',**(headers or {})})
    with urlopen(req,timeout=18) as res:
        return res.status,res.read(18000000)
def main():
    probe={}
    boards={'robotics':('https://misterplusev.github.io/robotics-jobradar-board/','robotics_jobs','robotics-jobs'),
            'tech':('https://misterplusev.github.io/jobradar-tech-board/','tech_jobs','tech-jobs'),
            'sports_teams':('https://misterplusev.github.io/job-radar/','team_jobs','teams-jobs'),
            'sportsbook':('https://sportsbook-jobs-dashboard.vercel.app/','jobs','jobs-browser')}
    page=read(boards['robotics'][0])[1].decode()
    url,key=re.search(r'SB_URL="([^"]+)",\s*SB_ANON="([^"]+)"',page).groups()
    assert url=='https://alxgteasytezekyunyjk.supabase.co'
    payload=key.split('.')[1]
    assert json.loads(base64.urlsafe_b64decode(payload+'='*(-len(payload)%4)))['role']=='anon'
    headers={'apikey':key,'Authorization':'Bearer '+key}
    probe['public_module_reads']={}
    for name,(standalone,table,tab) in boards.items():
        route='https://abet-dashboard.vercel.app/?'+urlencode({'section':'jobs','tab':tab})
        params=urlencode({'select':'id,title,url','is_active':'eq.true','order':'id.desc','limit':1})
        code,body=read(url+'/rest/v1/'+table+'?'+params,headers)
        rows=json.loads(body)
        assert code==200 and len(rows)==1 and rows[0]['title'] and rows[0]['url'].startswith('https://')
        probe['public_module_reads'][name]={'standalone':standalone,'standalone_http':read(standalone)[0],
            'dashboard':route,'dashboard_http':read(route)[0],'table':table,'database_public_role':'anon','database_http':code,
            'active_row':rows[0]}
    index='https://careers.hardrock.com/graphql/execute.json/shrss/getAllJobDetailsList'
    try:
        code,body=read(index)
        items=json.loads(body)['data']['jobsList']['items']
        exact=[r for r in items if str(r.get('jobPortalUrl') or '').endswith('_R17674')]
        probe['hard_rock_employer_index']={'http':code,'total':len(items),'matching_records':len(exact),'employer_url':index,
            'fields':sorted(exact[0]) if exact else [],'field_sizes':{k:len(str(v)) for k,v in (exact[0] if exact else {}).items()}}
    except Exception as exc:
        probe['hard_rock_employer_index']={'error':type(exc).__name__,'http':getattr(exc,'code',None)}
    try:
        _,body=read('https://abet-jobs-staging.abetscrape.workers.dev/status')
        st=json.loads(body)
        probe['staging']={k:st.get(k) for k in ('service','environment','status','enabled','next_alarm','last_tick','production_dispatch_enabled','discord_sends','limits')}
        probe['staging']['modules']={k:{f:v.get(f) for f in ('status','last_dispatch','last_result','sha','next_due','interval_hours') if f in v} for k,v in st.get('modules',{}).items() if isinstance(v,dict)}
    except Exception as exc:
        probe['staging']={'error':type(exc).__name__,'http':getattr(exc,'code',None)}
    print(json.dumps(probe,indent=2))
    Path('http-acceptance.json').write_text(json.dumps(probe,indent=2))
if __name__=='__main__':main()
