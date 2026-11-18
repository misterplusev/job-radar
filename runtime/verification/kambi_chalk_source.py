import json,re
from urllib.parse import urljoin,urlsplit
from pathlib import Path
import requests
from bs4 import BeautifulSoup
out={}
def soup(url):
    resp=requests.get(url,timeout=18,headers={'User-Agent':'ABET-Jobs/1.0 (+https://abet-dashboard.vercel.app)'});return resp,BeautifulSoup(resp.content,'html.parser')
url='https://www.kambi.com/working-at-kambi/open-positions/'
res,doc=soup(url)
links=[(a.get('href',''),a.get_text(' ',strip=True),a) for a in doc.select('main a[href],#content a[href]')]
if not links:links=[(a.get('href',''),a.get_text(' ',strip=True),a) for a in doc.select('a[href]')]
details=[(u,t,a) for u,t,a in links if urlsplit(u).path.startswith('/working-at-kambi/open-positions/') and len(urlsplit(u).path.strip('/').split('/'))>2 and 'kc_' not in u]
unique=list(dict.fromkeys(u for u,t,a in details))
def tags(el):return [(x.name,x.get('class'),x.get('id')) for x in list(el.parents)[:7] if x.name]
out['kambi']={'http':res.status_code,'url':res.url,'title':doc.title.get_text(strip=True),'links':unique,'first_card':str(details[0][2].parent.parent.parent)[:3200] if details else None,'context':tags(details[0][2]) if details else None,
  'archive_signals':[(t.name,t.get('class'),t.get('id'),{k:v for k,v in t.attrs.items() if k.startswith('data-')}) for t in doc.select('[class*=pagination],[class*=load-more],[data-total],[data-page],[class*=vacancies]')][:24],
  'pagination':[(a.get('href'),a.get_text(' ',strip=True)) for a in doc.select('a[rel=next],.page-numbers,.pagination a')],
  'linked_apis':[(l.get('rel'),l.get('href')) for l in doc.select('link[rel]') if 'api' in str(l.get('rel')) or 'json' in str(l.get('type'))]}
if unique:
    rs,d=soup(urljoin(res.url,unique[0]))
    out['detail']={'http':rs.status_code,'canonical':[(l.get('rel'),l.get('href')) for l in d.select('link[rel=canonical]')],'h1':[(q.get_text(' ',strip=True),tags(q)) for q in d.select('h1')][:2],
       'jsonld':[(str(q.string or q.get_text())[:900]) for q in d.select('script[type="application/ld+json"]')][:3],
       'body_candidates':[(q.name,q.get('class'),len(q.get_text(' ',strip=True))) for q in d.select('main,article,[class*=vacan],[class*=job-],[class*=entry-content]') if len(q.get_text(' ',strip=True))>100][:30],
       'apply':[(a.get('href'),a.get_text(' ',strip=True)) for a in d.select('a[href]') if 'apply' in a.get_text(' ',strip=True).lower()][:6]}
chalk='https://api.ashbyhq.com/posting-api/job-board/chalkboard';resp=requests.get(chalk,timeout=18)
out['chalk_ats']={'http':resp.status_code,'json_keys':list(resp.json())[:12],'jobs':len(resp.json()['jobs']) if isinstance(resp.json().get('jobs'),list) else None}
for site in ['https://chalkboard.io','https://jobs.ashbyhq.com/chalkboard']:
    try:
        resp,d=soup(site);out[site]={'http':resp.status_code,'url':resp.url,'title':d.title.get_text(strip=True) if d.title else '', 'career_links':[(a.get('href'),a.get_text(' ',strip=True)) for a in d.select('a[href]') if re.search('careers|jobs.ashby|join our team',str(a),re.I)][:7]}
    except Exception as exc:out[site]={'error':type(exc).__name__}
print(json.dumps(out,indent=2))
Path('employer-source-shapes.json').write_text(json.dumps(out,indent=2))
