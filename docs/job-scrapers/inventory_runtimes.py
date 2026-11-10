"""Finite GET-only HF/Cloudflare metadata inventory; no runtime triggers or secret output."""
import email.policy,json,sys
from email.parser import BytesParser
from pathlib import Path
from urllib.parse import quote
import requests
from generate_inventory import ROOT,OUT,details,eligible,write,category
sys.path.insert(0,r'D:\abet_ops\sports_teams')
from deploy_cloud import envfile

def main():
 sources=json.loads(OUT.joinpath('source_inventory.json').read_text(encoding='utf-8'))['sources']
 sources=[s for s in sources if s['id'] not in {'sportsbook-deployed-space','sportsbook-watchdog'}]
 cfg=envfile(r'E:\abet\.env');session=requests.Session()
 hfheaders={'Authorization':'Bearer '+cfg['HF_TOKEN_ABETCO']}
 def get(url,headers):
  r=session.get(url,headers=headers,timeout=35);r.raise_for_status();return r
 info=get('https://huggingface.co/api/spaces/abetco/sportsbook-jobs',hfheaders).json();sha=info['sha']
 entries=get(f'https://huggingface.co/api/spaces/abetco/sportsbook-jobs/tree/{sha}?recursive=true',hfheaders).json()
 assert len(entries)<1000,'HF inventory pagination must be implemented if this grows'
 rows=[]
 for entry in entries:
  if entry['type']!='file':continue
  path=entry['path'];row={'source':'sportsbook-deployed-space','revision':sha,'path':path,'bytes':entry.get('size',0),'lines':None,'category':category(path),'url':f'https://huggingface.co/spaces/abetco/sportsbook-jobs/blob/{sha}/{quote(path)}'}
  if eligible(path,row['bytes']):details(row,get(f'https://huggingface.co/spaces/abetco/sportsbook-jobs/raw/{sha}/{quote(path)}',hfheaders).content)
  else:row['count_note']='Binary/generated/private artifact; metadata only'
  rows.append(row)
 sources.append({'id':'sportsbook-deployed-space','repo':'Hugging Face abetco/sportsbook-jobs','revision':sha,'files':rows})
 # Preserve the successful Space audit even if watchdog permissions differ.
 write(sources)
 print('Deployed Space:',len(rows),'files',flush=True)
 headers={'Authorization':'Bearer '+cfg['CLOUDFLARE_API_TOKEN']};account=cfg['CLOUDFLARE_ACCOUNT_ID'];base=f'https://api.cloudflare.com/client/v4/accounts/{account}/workers/scripts/abet-jobs-watchdog'
 try:r=get(base,headers)
 except requests.HTTPError as error:
  sources.append({'id':'sportsbook-watchdog','repo':'Cloudflare worker abet-jobs-watchdog','revision':'deployed source not accessible with current token','files':[],
   'inspection_status':f'HTTP {error.response.status_code}; public health is separately reachable',
   'versioned_source':'misterplusev/sportsbook-jobs-dashboard prod/sportsbook-jobs runtime/cloudflare/watchdog/',
   'configured_cron':'0 */2 * * *','limitation':'Cannot certify deployed code matches repository code or inspect deployed bindings/schedule with current credentials.'})
  write(sources);print('Watchdog source access unavailable; explicit gap saved, versioned source remains inventoried.',flush=True);return
 if 'multipart' in r.headers.get('Content-Type',''):
  message=BytesParser(policy=email.policy.default).parsebytes(('Content-Type: '+r.headers['Content-Type']+'\r\nMIME-Version: 1.0\r\n\r\n').encode()+r.content)
  files=[(p.get_filename() or p.get_param('name',header='content-disposition') or 'worker.js',p.get_payload(decode=True)) for p in message.iter_parts()]
 else:files=[('worker.js',r.content)]
 rows=[]
 for name,raw in files:
  if raw is None:continue
  row={'source':'sportsbook-watchdog','path':name,'bytes':len(raw),'revision':r.headers.get('ETag','deployed GET snapshot'),'lines':None,'category':'health/watchdog runtime'};details(row,raw);rows.append(row)
 schedules=get(base+'/schedules',headers).json().get('result')
 settings=get(base+'/settings',headers).json().get('result',{})
 bindings=[{'name':b.get('name'),'type':b.get('type')} for b in settings.get('bindings',[])]
 sources.append({'id':'sportsbook-watchdog','repo':'Cloudflare worker abet-jobs-watchdog','revision':r.headers.get('ETag','deployed GET snapshot'),'schedules':schedules,'binding_names_only':bindings,'files':rows})
 write(sources)
 print('Watchdog:',len(rows),'files; binding values omitted',flush=True)

if __name__=='__main__':main()
