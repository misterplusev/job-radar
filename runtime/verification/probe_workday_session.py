"""Cloud-only, ordinary HTTP session compatibility check. No browser or challenge solving."""
import datetime as dt,json,os,time
from pathlib import Path
import requests
assert os.environ.get('GITHUB_ACTIONS')=='true','Run only in the cloud workflow'
assert not any(os.environ.get(k) for k in ('SUPABASE_SERVICE_ROLE_KEY','DISCORD_WEBHOOK_JOBS'))
SOURCES=[
 ('Boston Dynamics','bostondynamics.wd1.myworkdayjobs.com','bostondynamics','Boston_Dynamics'),
 ('AutoStore','autostore.wd3.myworkdayjobs.com','autostore','autostore'),
 ('Rockwell Automation','rockwellautomation.wd1.myworkdayjobs.com','rockwellautomation','External_Rockwell_Automation'),
 ('BetMGM','betmgminc.wd5.myworkdayjobs.com','betmgminc','BetMGM'),
 ('Betway','myhcm.wd3.myworkdayjobs.com','myhcm','Betway'),
 ('Hard Rock Bet','seminolehardrock.wd503.myworkdayjobs.com','seminolehardrock','seminolehardrockcareers'),
 ('AMB Sports and Entertainment','ambgroup.wd1.myworkdayjobs.com','ambgroup','AMBSE'),
]
# Existing production UA, unchanged. This isolates ordinary session/page initialization.
UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122 Safari/537.36'
def summary(r):
 text=r.text[:65536].lower()
 challenge=r.headers.get('CF-Mitigated','').lower()=='challenge' or ('security check' in text and 'enable javascript and cookies' in text)
 return {'status':r.status_code,'content_type':r.headers.get('Content-Type'),'cf_mitigated':r.headers.get('CF-Mitigated'),'cf_ray':r.headers.get('CF-Ray'),'challenge':challenge}
report={'at':dt.datetime.now(dt.timezone.utc).isoformat(),'browser_sessions':0,'production_writes':0,'discord_sends':0,'sources':[]}
for company,host,tenant,site in SOURCES:
 item={'company':company,'host':host,'requests':0,'complete':False};started=time.monotonic()
 try:
  with requests.Session() as session:
   session.headers.update({'User-Agent':UA})
   url=f'https://{host}/en-US/{site}'
   r=session.get(url,timeout=(10,20),allow_redirects=False);item['requests']+=1;item['public_page']=summary(r)
   if item['public_page']['challenge'] or r.status_code!=200:
    item['result']='public_page_unavailable';continue
   item['cookie_names']=sorted(set(session.cookies.keys()))
   r=session.post(f'https://{host}/wday/cxs/{tenant}/{site}/jobs',json={'appliedFacets':{},'limit':20,'offset':0,'searchText':''},headers={'Accept':'application/json','Content-Type':'application/json','Referer':url},timeout=(10,20),allow_redirects=False)
   item['requests']+=1;item['listing']=summary(r)
   if item['listing']['challenge'] or r.status_code!=200:
    item['result']='listing_unavailable';continue
   data=r.json();rows=data.get('jobPostings');total=data.get('total')
   assert isinstance(rows,list) and isinstance(total,int),'Invalid listing payload'
   item.update(result='listing_loaded',advertised_total=total,first_page_count=len(rows),complete=len(rows)==total,sample=[{'title':j.get('title'),'path':j.get('externalPath')} for j in rows[:3]])
 except Exception as exc:item.update(result='error',error=type(exc).__name__+': '+str(exc)[:300])
 finally:item['seconds']=round(time.monotonic()-started,3);report['sources'].append(item)
out=Path('proof/session-http');out.mkdir(parents=True,exist_ok=True)
(out/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
