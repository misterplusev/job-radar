"""Bounded cloud-only read diagnostics for public Workday career endpoints. No persistence/sender imports."""
import datetime as dt,hashlib,html,json,os,re,time
from pathlib import Path
from urllib.parse import urlsplit
import requests
assert os.environ.get('GITHUB_ACTIONS')=='true','Cloud execution required'
assert not any(os.environ.get(k) for k in ('SUPABASE_SERVICE_ROLE_KEY','DISCORD_WEBHOOK_JOBS'))
SOURCES=[
 ('hardrock','seminolehardrock.wd503.myworkdayjobs.com','seminolehardrock','seminolehardrockcareers'),
 ('betway','myhcm.wd3.myworkdayjobs.com','myhcm','Betway'),
]
OUT=Path('proof/workday-diagnosis');OUT.mkdir(parents=True,exist_ok=True)
REPORT={'at':dt.datetime.now(dt.timezone.utc).isoformat(),'run_url':f"https://github.com/{os.environ['GITHUB_REPOSITORY']}/actions/runs/{os.environ['GITHUB_RUN_ID']}",'sources':[],'production_writes':0,'discord_sends':0}
def normalized(raw):
    text=re.sub(r'(?is)<(script|style|svg)\b.*?</\1>',' ',raw)
    text=re.sub(r'<[^>]+>',' ',text)
    return re.sub(r'\s+',' ',html.unescape(text)).strip()[:8000]
def fetch(session,label,method,url,**kw):
    assert url.startswith('https://') and (urlsplit(url).hostname.endswith('.myworkdayjobs.com') or urlsplit(url).hostname=='bostondynamics.com')
    start=time.monotonic();r=session.request(method,url,timeout=(8,20),allow_redirects=False,stream=True,**kw)
    body=b''
    for chunk in r.iter_content(65536):
        body+=chunk
        if len(body)>1024*1024:break
    r.close();text=body.decode('utf-8','replace')
    record={'label':label,'method':method,'url':url,'status':r.status_code,'seconds':round(time.monotonic()-start,3),'headers':{k:r.headers.get(k) for k in ('Content-Type','Retry-After','Server','CF-Ray','Location','Date','CF-Mitigated')},'bytes_read':len(body),'sha256':hashlib.sha256(body).hexdigest(),'readable_text':normalized(text),'cookie_names':list(session.cookies.keys())}
    try:
        data=json.loads(text);record['json_keys']=list(data) if isinstance(data,dict) else type(data).__name__
        if isinstance(data,dict):record.update(total=data.get('total'),job_count=len(data.get('jobPostings',[])))
    except ValueError:pass
    # Only public career HTML/JSON; no request cookies or credential values are logged.
    (OUT/(label+'.txt')).write_text(text,encoding='utf-8')
    return record
for module,host,tenant,site in SOURCES:
    origin='https://'+host;page=origin+'/en-US/'+site;endpoint=origin+f'/wday/cxs/{tenant}/{site}/jobs'
    source={'module':module,'host':host,'events':[]}
    try:
        session=requests.Session();session.headers.update({'User-Agent':'ABET-Jobs-Source-Validation/1.0','Accept':'text/html,application/json'})
        home=fetch(session,module+'-career','GET',page);source['events'].append(home)
        if home['status'] in (403,429) or home['headers'].get('CF-Mitigated')=='challenge':
            source['stopped']='Public career page rejected access; no further requests to this host'
        elif home['status']==200:
            time.sleep(2)
            headers={'Accept':'application/json','Content-Type':'application/json','Origin':origin,'Referer':page}
            csrf=session.cookies.get('CALYPSO_CSRF_TOKEN')
            if csrf:headers['X-Calypso-CSRF-Token']=csrf
            result=fetch(session,module+'-jobs','POST',endpoint,headers=headers,json={'appliedFacets':{},'limit':20,'offset':0,'searchText':''})
            source['events'].append(result)
    except Exception as exc:source['error']=type(exc).__name__+': '+str(exc)[:400]
    REPORT['sources'].append(source)
try:
    session=requests.Session();session.headers['User-Agent']='ABET-Jobs-Source-Validation/1.0'
    REPORT['boston_official_page']=fetch(session,'boston-official','GET','https://bostondynamics.com/careers/')
except Exception as exc:REPORT['boston_official_error']=str(exc)[:400]
(OUT/'report.json').write_text(json.dumps(REPORT,indent=2),encoding='utf-8')
print(json.dumps(REPORT,indent=2))
