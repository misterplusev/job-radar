"""Bounded HTTP/data/CORS deployment proof. No browser, messages or writes to services."""
import base64,json,re,subprocess
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urljoin
import requests

ROOT=Path(__file__).resolve().parent
def main():
 session=requests.Session();report={'checked_at':datetime.now(timezone.utc).isoformat(),'browser_visual_check':False,'read_only':True,'standalone':[],'dashboard':[]}
 root='https://abet-dashboard.vercel.app/'
 page=session.get(root,timeout=30);page.raise_for_status()
 assets=re.findall(r'<script[^>]+src="([^"]+)"',page.text);assert assets
 script_url=urljoin(root,assets[0]);script=session.get(script_url,timeout=30);script.raise_for_status();text=script.text
 token=None
 for candidate in re.findall(r'eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+',text):
  body=candidate.split('.')[1];claims=json.loads(base64.urlsafe_b64decode(body+'='*(-len(body)%4)))
  if claims.get('ref')=='alxgteasytezekyunyjk' and claims.get('role')=='anon':token=candidate;break
 assert token,'No app-core public read key found in deployed jobs bundle'
 headers={'apikey':token,'Authorization':'Bearer '+token,'Prefer':'count=exact','Origin':root.rstrip('/')}
 for id,tab,table,standalone in [('sportsbook','jobs-browser','jobs','https://sportsbook-jobs-dashboard.vercel.app/'),('robotics','robotics-jobs','robotics_jobs','https://misterplusev.github.io/robotics-jobradar-board/'),('tech','tech-jobs','tech_jobs','https://misterplusev.github.io/jobradar-tech-board/'),('teams','teams-jobs','team_jobs','https://misterplusev.github.io/job-radar/')]:
  assert tab in text and table in text,(id,'route/table absent from deployed bundle')
  route=root+'?section=jobs&tab='+tab;resp=session.get(route,timeout=30);resp.raise_for_status()
  endpoint='https://alxgteasytezekyunyjk.supabase.co/rest/v1/'+table
  data=session.get(endpoint,headers=headers,params={'select':'id,title,url','is_active':'eq.true','limit':1},timeout=30);data.raise_for_status();assert data.json()
  preflight=session.options(endpoint,headers={'Origin':root.rstrip('/'),'Access-Control-Request-Method':'GET','Access-Control-Request-Headers':'apikey,authorization,prefer'},timeout=30);preflight.raise_for_status()
  allow=preflight.headers.get('Access-Control-Allow-Origin');assert allow in ['*',root.rstrip('/')]
  report['dashboard'].append({'id':id,'url':route,'http':resp.status_code,'table':table,'database_http':data.status_code,'active_jobs':int(data.headers['Content-Range'].split('/')[1]),'cors':allow,'bundle_contains_route':True})
  web=session.get(standalone,timeout=30);web.raise_for_status();entry={'id':id,'url':standalone,'http':web.status_code}
  if id in ['robotics','tech']:
   u=re.search(r'SB_URL\s*=\s*"([^"]+)"',web.text)[1];k=re.search(r'SB_ANON\s*=\s*"([^"]+)"',web.text)[1]
   r=session.get(u+'/rest/v1/'+table,headers={'apikey':k,'Authorization':'Bearer '+k},params={'select':'company,title,url,location,ats,posted_at,is_active,scraped_at','order':'posted_at.desc.nullslast,scraped_at.desc','limit':1},timeout=30);r.raise_for_status();assert r.json();entry['embedded_config_data_http']=r.status_code
  elif id=='teams':
   r=session.get(urljoin(standalone,'team_jobs.json'),timeout=30);r.raise_for_status();feed=r.json();assert feed.get('jobs');entry.update(feed_http=r.status_code,feed_jobs=len(feed['jobs']),feed_declared_count=feed.get('count'))
  else:
   paths=re.findall(r'<script[^>]+src="([^"]+)"',web.text);assert len(paths)<50
   found=False
   for path in paths:
    if '/app/' not in path:continue
    r=session.get(urljoin(standalone,path),timeout=30);r.raise_for_status()
    if 'alxgteasytezekyunyjk' in r.text:found=True
   entry['app_core_project_in_frontend_bundle']=found
  report['standalone'].append(entry)
 inspect=subprocess.run(['vercel.cmd','inspect',root,'--json'],capture_output=True,text=True,encoding='utf-8',timeout=40,check=True)
 deployment_id=json.loads(inspect.stdout)['id']
 metadata=subprocess.run(['vercel.cmd','api','/v13/deployments/'+deployment_id,'--raw'],capture_output=True,text=True,encoding='utf-8',timeout=40,check=True)
 deployed=json.loads(metadata.stdout);assert deployed['readyState']=='READY'
 report['deployment']={'id':deployment_id,'state':deployed['readyState'],'source_commit':deployed.get('gitSource',{}).get('sha'),'bundle_url':script_url}
 out=ROOT/'audit_20261110/public_pages_verified.json';out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
