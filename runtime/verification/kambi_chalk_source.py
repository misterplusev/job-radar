import json
from pathlib import Path
from urllib.parse import urljoin,urlsplit
from xml.etree import ElementTree as ET
from collections import Counter
import requests
from bs4 import BeautifulSoup
out={}
base='https://kambi.teamtailor.com/jobs'
http=requests.Session();http.headers.update({'User-Agent':'ABET-Jobs/1.0 (+https://abet-dashboard.vercel.app)'})
res=http.get(base,timeout=15);doc=BeautifulSoup(res.content,'html.parser')
out['board']={'http':res.status_code,'final':res.url,'rss':[(q.get('type'),urljoin(res.url,q.get('href',''))) for q in doc.select('link[rel~=alternate]') if 'rss' in q.get('type','')],
              'roles':{},'pagination':[(a.get('href'),a.get_text(' ',strip=True)) for a in doc.select('a[rel=next],.pagination a,[class*=pagination] a')][:8]}
for a in doc.select('a[href]'):
    u=urljoin(res.url,a['href']);part=urlsplit(u)
    if part.hostname=='kambi.teamtailor.com' and part.path.startswith('/jobs/') and part.path[6:7].isdigit() and not part.path.endswith('/applications/new'):
        out['board']['roles'][u]=a.get_text(' ',strip=True)[:140]
if out['board']['roles']:
    url=next(iter(out['board']['roles']));resp=http.get(url,timeout=15);d=BeautifulSoup(resp.content,'html.parser')
    ld=[json.loads(x.string) for x in d.select('script[type="application/ld+json"]') if x.string]
    for obj in ld:
        if isinstance(obj,dict) and obj.get('@type')=='JobPosting':
            out['sample']={'http':resp.status_code,'url':url,'keys':list(obj),'title':obj.get('title'),'location':obj.get('jobLocation'),'published':obj.get('datePosted'),'org':obj.get('hiringOrganization'),'description_size':len(obj.get('description',''))}
for mime,feed in out['board']['rss']:
    resp=http.get(feed,timeout=15);root=ET.fromstring(resp.content)
    rows=root.findall('./channel/item')
    out['feed']={'http':resp.status_code,'url':feed,'count':len(rows),'ids':{str(q.findtext('link')):q.findtext('title') for q in rows},'sample':{c.tag:(c.text or '')[:150] for c in list(rows[0])} if rows else {}}
print(json.dumps(out,indent=2))
Path('employer-source-shapes.json').write_text(json.dumps(out,indent=2))
