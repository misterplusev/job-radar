import concurrent.futures, hashlib, json, re
from pathlib import Path
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
out=Path('evidence');out.mkdir(exist_ok=True)
pages=['https://www.nba.com/bulls/career-opportunities','https://www.nba.com/bucks/careers','https://www.nba.com/clippers/company/careers/openpositions']
records=[];assets=['https://cdn.nba.com/teams/static/bulls/_next/static/chunks/pages/career-opportunities-1eeef2215a6ed800.js', 'https://cdn.nba.com/teams/static/bucks/assets/index-B9HvEVuZ.js', 'https://cdn.nba.com/teams/static/clippers/_next/static/chunks/2m27mebpj0xw0.js', 'https://cdn.nba.com/teams/static/clippers/_next/static/chunks/20l7s7qbalw2j.js', 'https://cdn.nba.com/teams/static/clippers/_next/static/chunks/1yjkekt6b324r.js', 'https://cdn.nba.com/teams/static/clippers/_next/static/chunks/32m24o3-idw3a.js', 'https://cdn.nba.com/teams/static/clippers/_next/static/chunks/186-up04u1hcl.js', 'https://cdn.nba.com/teams/static/clippers/_next/static/chunks/2pnxd893a1zw5.js', 'https://cdn.nba.com/teams/static/clippers/_next/static/chunks/0puvfeo3vnuln.js', 'https://cdn.nba.com/teams/static/clippers/_next/static/chunks/turbopack-1salptro4bqoj.js', 'https://cdn.nba.com/teams/static/clippers/_next/static/chunks/04_yucvjrx8jh.js', 'https://cdn.nba.com/teams/static/clippers/_next/static/DTOq7MteAu1OVCQVIw7ih/_buildManifest.js', 'https://cdn.nba.com/teams/static/clippers/_next/static/DTOq7MteAu1OVCQVIw7ih/_ssgManifest.js', 'https://cdn.nba.com/teams/static/clippers/_next/static/DTOq7MteAu1OVCQVIw7ih/_clientMiddlewareManifest.js']
def fetch(url):
    record={'url':url}
    try:
        r=requests.get(url,timeout=20);record.update(status=r.status_code,final_url=r.url)
        if len(r.content)>12000000:raise ValueError('asset size budget exceeded')
        name=hashlib.sha256(url.encode()).hexdigest()[:20]+'.txt'
        (out/name).write_text(r.text,encoding='utf8');record['file']=name
        record['matches']=[r.text[max(0,m.start()-120):m.end()+250] for m in re.finditer(r'paylocity|greenhouse|workforcenow|035c77cb|chibullsdigital[^" ]*|jobRequisitions',r.text,re.I)][:20]
        return record,r.text
    except Exception as exc:record['error']=str(exc)[:200];return record,''
for url in pages:
    record,body=fetch(url);records.append(record)
    soup=BeautifulSoup(body,'html.parser')
    for s in soup.find_all('script',src=True):
        u=urljoin(url,s['src'])
        if 'cdn.nba.com/' in u and (('bulls' in u and ('career-opportunities' in u or '/_app-' in u)) or ('bucks' in u and '/assets/index-' in u) or 'clippers' in u):assets.append(u)
assert len(set(assets))<=40
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
    for record,_ in pool.map(fetch,sorted(set(assets))):records.append(record)
(out/'index.json').write_text(json.dumps(records,indent=2),encoding='utf8')
print(json.dumps([{'url':r['url'],'status':r.get('status'),'match_count':len(r.get('matches',[]))} for r in records]))
