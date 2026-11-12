"""Public feeds linked by official team careers pages. No browser or authentication.

Dayforce uses its public anonymous CSRF endpoint, just like its careers frontend.
Missing arrays, changing totals, duplicate pages and incomplete pagination fail
the source, so a broken or loading page can never close existing jobs.
"""
import json,re
from urllib.parse import urlsplit,urljoin,parse_qs,urlencode
from bs4 import BeautifulSoup

def dayforce(source,client):
    url=source['url'];r=client.get(url);r.raise_for_status()
    p=urlsplit(r.url);parts=[x for x in p.path.split('/') if x]
    if len(parts)<3 or not re.fullmatch(r'[a-z]{2}-[A-Z]{2}',parts[0]):
        raise ValueError('Unrecognized Dayforce public board redirect')
    culture,tenant,board=parts[:3];base=f'https://{p.netloc}'
    token=client.get(base+'/api/auth/csrf');token.raise_for_status()
    csrf=token.json().get('csrfToken')
    if not csrf:raise ValueError('Missing public Dayforce CSRF nonce')
    jobs=[];seen=set();total=None
    for _ in range(60):
        body={'clientNamespace':tenant,'jobBoardCode':board,'cultureCode':culture,'paginationStart':len(jobs)}
        body.update(source.get('filters',{}))
        r=client.post(base+f'/api/geo/{tenant}/jobposting/search',json=body,
                      headers={'X-CSRF-TOKEN':csrf,'Origin':base,'Referer':url})
        r.raise_for_status();data=r.json()
        if not isinstance(data.get('jobPostings'),list) or 'maxCount' not in data:
            raise ValueError('Unrecognized Dayforce listing response')
        count=int(data['maxCount'])
        if total is not None and total!=count:raise ValueError('Dayforce total changed during pagination')
        total=count;batch=data['jobPostings']
        for j in batch:
            ident=j.get('jobPostingId')
            if not ident or ident in seen:raise ValueError('Missing/repeated Dayforce job')
            seen.add(ident)
            jobs.append(dict(title=j.get('jobTitle'),url=base+f'/{culture}/{tenant}/{board}/jobs/{ident}',
                location='; '.join(x.get('formattedAddress','') for x in (j.get('postingLocations') or [])),
                description=j.get('jobDescription'),posted_at=j.get('postingStartTimestampUTC')))
        if len(jobs)==total:return jobs
        if not batch or len(jobs)>total:raise ValueError('Incomplete Dayforce pagination')
    raise ValueError('Dayforce pagination cap reached')

def bamboohr(source,client):
    base=source['url'].rstrip('/');r=client.get(base+'/list');r.raise_for_status();data=r.json()
    if not isinstance(data.get('result'),list) or data.get('meta',{}).get('totalCount')!=len(data['result']):
        raise ValueError('Incomplete or unrecognized BambooHR list')
    jobs=[];seen=set()
    for j in data['result']:
        ident=j.get('id')
        if not ident or ident in seen:raise ValueError('Missing/repeated BambooHR job')
        seen.add(ident);loc=j.get('location') or {}
        jobs.append(dict(title=j.get('jobOpeningName'),url=base+'/'+str(ident),
            location=', '.join(str(loc[k]) for k in ('city','state') if loc.get(k))))
    return jobs

def lever(source,client):
    jobs=[];seen=set();board=source['board']
    for skip in range(0,3000,100):
        r=client.get(f'https://api.lever.co/v0/postings/{board}',params={'mode':'json','skip':skip,'limit':100})
        r.raise_for_status();data=r.json()
        if not isinstance(data,list):raise ValueError('Unrecognized Lever response')
        for j in data:
            ident=j.get('id')
            if not ident or ident in seen:raise ValueError('Missing/repeated Lever job')
            seen.add(ident)
            description=(j.get('description') or '')+'\n'+'\n'.join(x.get('content','') for x in j.get('lists',[]))+'\n'+(j.get('additional') or '')
            jobs.append(dict(title=j.get('text'),url=j.get('hostedUrl'),location=j.get('categories',{}).get('location'),description=description))
        if len(data)<100:return jobs
    raise ValueError('Lever pagination cap reached')

def paylocity(source,client):
    r=client.get(source['url']);r.raise_for_status()
    match=re.search(r'window\.pageData\s*=\s*',r.text)
    if not match:raise ValueError('Missing Paylocity pageData')
    data=json.JSONDecoder().raw_decode(r.text[match.end():])[0]
    if not isinstance(data.get('Jobs'),list):raise ValueError('Missing Paylocity jobs array')
    jobs=[];seen=set()
    for j in data['Jobs']:
        ident=j.get('JobId')
        if not ident or ident in seen:raise ValueError('Missing/repeated Paylocity job')
        seen.add(ident)
        jobs.append(dict(title=j.get('JobTitle'),url=f'https://recruiting.paylocity.com/Recruiting/Jobs/Details/{ident}',
            location=j.get('LocationName'),description=j.get('Description'),posted_at=j.get('PublishedDate')))
    return jobs

def paycor(source,client):
    r=client.get(source['url'],headers={'User-Agent':'ABET-TeamsJobs/1.0 (+https://misterplusev.github.io/job-radar/)','Accept':'text/html,application/xhtml+xml'});r.raise_for_status()
    soup=BeautifulSoup(r.text,'html.parser')
    if not soup.find('form',action=re.compile('CareerHomeSearch')):raise ValueError('Missing Paycor search form')
    out={}
    for a in soup.find_all('a',href=re.compile('JobIntroduction.action')):
        u=urljoin(r.url,a['href']);q=parse_qs(urlsplit(u).query)
        if not q.get('id') or not q.get('clientId'):raise ValueError('Incomplete Paycor job URL')
        canonical=f'https://recruitingbypaycor.com/career/JobIntroduction.action?'+urlencode({'clientId':q['clientId'][0],'id':q['id'][0]})
        row=a.find_parent(class_=re.compile('GroupJobClass')) or a.find_parent('tr')
        loc=row.find(class_=re.compile('Location')) if row else None
        out[canonical]=dict(title=a.get_text(' ',strip=True),url=canonical,location=loc.get_text(' ',strip=True) if loc else None)
    if not out and not re.search('no (?:open |available |current )?(?:jobs|positions)|no openings',soup.get_text(' ',strip=True),re.I):
        raise ValueError('Paycor empty board not verified')
    return list(out.values())

def jazzhr(source,client):
    r=client.get(source['url']);r.raise_for_status();soup=BeautifulSoup(r.text,'html.parser')
    if not soup.select_one('#form_search_jobs'):raise ValueError('Missing JazzHR listing form')
    out={}
    for a in soup.select('a.job_title_link[href]'):
        u=urljoin(r.url,a['href']).split('?')[0];row=a.find_parent('tr')
        cells=row.find_all('td') if row else []
        out[u]=dict(title=a.get_text(' ',strip=True),url=u,location=cells[1].get_text(' ',strip=True) if len(cells)>1 else None)
    if not out and not re.search('no (?:open |available )?(?:jobs|positions)',soup.get_text(' ',strip=True),re.I):
        raise ValueError('JazzHR empty board not verified')
    if soup.find('a',string=re.compile(r'^Next',re.I)):raise ValueError('JazzHR pagination requires review')
    return list(out.values())

def tnse(source,client):
    r=client.get(source['url']);r.raise_for_status();soup=BeautifulSoup(r.text,'html.parser');out={}
    for a in soup.find_all('a',href=re.compile(r'entertimeonline\.com/ta/6146095\.careers\?ShowJob=')):
        q=parse_qs(urlsplit(a['href']).query);u='https://secure3.entertimeonline.com/ta/6146095.careers?'+urlencode({'ShowJob':q['ShowJob'][0]})
        out[u]=dict(title=a.get_text(' ',strip=True),url=u,location='Winnipeg, Manitoba')
    if not out:raise ValueError('True North job links missing; review official page')
    return list(out.values())

def clearcompany(source,client):
    r=client.get(source['url']);r.raise_for_status();soup=BeautifulSoup(r.text,'html.parser')
    script=soup.find('script',attrs={'data-site-id':True})
    if not script:raise ValueError('ClearCompany public site ID missing')
    site=script['data-site-id'];jobs=[];seen=set();total=None
    for page in range(50):
        r=client.get('https://careers-api.clearcompany.com/v1/'+site,params={'pageIndex':page,'pageSize':100});r.raise_for_status();d=r.json()
        if not isinstance(d.get('results'),list) or 'totalCount' not in d:raise ValueError('Missing ClearCompany results/count')
        count=int(d['totalCount'])
        if total is not None and count!=total:raise ValueError('ClearCompany total changed')
        total=count
        for j in d['results']:
            ident=j.get('id')
            if not ident or ident in seen:raise ValueError('Missing/repeated ClearCompany job')
            seen.add(ident);base=source['url'].split('?')[0]
            jobs.append(dict(title=j.get('positionTitle'),url=base+'?jobId='+ident,location=j.get('location'),
                             description=j.get('description'),posted_at=j.get('postedDate'),team=j.get('brandName') or source['team']))
        if len(jobs)==total:return jobs
        if not d['results'] or len(jobs)>total:raise ValueError('Incomplete ClearCompany pagination')
    raise ValueError('ClearCompany pagination cap')

def applicantpro(source,client):
    r=client.get(source['url']);r.raise_for_status()
    match=re.search(r'domainId\s*:\s*(\d+)',r.text)
    if not match:raise ValueError('ApplicantPro public domainId missing')
    p=urlsplit(r.url);base=f'https://{p.netloc}'
    r=client.get(base+'/core/jobs/'+match[1],params={'getParams':json.dumps({'isInternal':0})});r.raise_for_status();data=r.json()
    d=data.get('data',{})
    if data.get('success') is not True or not isinstance(d.get('jobs'),list) or int(d.get('jobCount',-1))!=len(d['jobs']):
        raise ValueError('Incomplete ApplicantPro job list')
    jobs=[];seen=set()
    for j in d['jobs']:
        u=j.get('jobUrl')
        if not u or u in seen:raise ValueError('Missing/repeated ApplicantPro job URL')
        seen.add(u);jobs.append(dict(title=j.get('title'),url=u,location=j.get('jobLocation'),posted_at=j.get('startDateRef')))
    return jobs

def icims(source,client):
    url=source['url'];jobs=[];seen=set();pages=set()
    for _ in range(50):
        r=client.get(url,params={'in_iframe':'1'});r.raise_for_status();soup=BeautifulSoup(r.text,'html.parser')
        if r.url in pages:raise ValueError('Repeated iCIMS page')
        pages.add(r.url)
        table=soup.select_one('.iCIMS_JobsTable')
        if not table:
            if 'There are currently no job openings' in soup.get_text(' ',strip=True) and not jobs:return []
            raise ValueError('Missing iCIMS jobs table')
        for card in table.select('.iCIMS_JobCardItem'):
            a=card.select_one('.title a[href]');title=card.select_one('h3');loc=card.select_one('.header.left')
            if not a or not title:raise ValueError('Incomplete iCIMS job card')
            u=urljoin(r.url,a['href']).split('?')[0]
            if u in seen:raise ValueError('Repeated iCIMS job')
            seen.add(u);jobs.append(dict(title=title.get_text(' ',strip=True),url=u,location=loc.get_text(' ',strip=True).replace('Job Locations','').strip() if loc else None))
        nextlink=soup.find('a',attrs={'title':re.compile('Next',re.I)}) or soup.find('a',attrs={'aria-label':re.compile('Next',re.I)})
        if not nextlink:return jobs
        url=urljoin(r.url,nextlink['href'])
    raise ValueError('iCIMS pagination cap')

def msg(source,client):
    r=client.get(source['url']);r.raise_for_status();soup=BeautifulSoup(r.text,'html.parser');jobs={}
    for card in soup.select('.job-entry'):
        a=card.find('a',href=re.compile('gh_jid='))
        if not a:raise ValueError('MSG job link missing')
        title=a.get_text(' ',strip=True)
        if title.lower() in ('join our network','join our talent community'):continue
        q=parse_qs(urlsplit(a['href']).query);p=urlsplit(a['href']);u=f'https://{p.netloc}{p.path}?gh_jid='+q['gh_jid'][0]
        jobs[u]=dict(title=title,url=u,description=card.get_text(' ',strip=True))
    if not jobs and not soup.select('.job-entry'):raise ValueError('MSG rendered jobs missing; loading state is not empty')
    if soup.find('a',class_=re.compile('next')):raise ValueError('MSG pagination requires review')
    return list(jobs.values())

def bkse(source,client):
    r=client.get(source['url']);r.raise_for_status();soup=BeautifulSoup(r.text,'html.parser')
    for script in soup.find_all('script'):
        raw=script.get_text();start=raw.find('self.__next_f.push(')
        if start<0:continue
        try:payload=json.JSONDecoder().raw_decode(raw[start+len('self.__next_f.push('):])[0]
        except ValueError:continue
        if not isinstance(payload,list) or len(payload)<2 or not isinstance(payload[1],str):continue
        text=payload[1];match=re.search(r'"jobs"\s*:\s*',text)
        if not match:continue
        groups=json.JSONDecoder().raw_decode(text[match.end():])[0]
        if not isinstance(groups,dict):raise ValueError('Unrecognized BKSE job groups')
        out={}
        for department,rows in groups.items():
            if not isinstance(rows,list):raise ValueError('Unrecognized BKSE department jobs')
            for j in rows:
                if not j.get('id') or not j.get('url') or j['id'] in out:raise ValueError('Missing/repeated BKSE job')
                p=urlsplit(j['url']);u=f'https://{p.netloc}{p.path}?gh_jid='+str(j['id'])
                out[j['id']]=dict(title=j.get('title'),url=u,location=j.get('location'),description=j.get('description'),team='Brooklyn Sports & Entertainment')
        return list(out.values())
    raise ValueError('BKSE server-rendered job data missing')

def _hireology_detail(client,url):
    """Description, employer date and pay from the job page's JobPosting data. Best effort."""
    try:
        r=client.get(url);r.raise_for_status()
        for script in BeautifulSoup(r.text,'html.parser').find_all('script',type='application/ld+json'):
            try:item=json.loads(script.get_text())
            except (ValueError,TypeError):continue
            if isinstance(item,dict) and item.get('@type')=='JobPosting':
                pay=item.get('baseSalary')
                return dict(description=item.get('description'),posted_at=item.get('datePosted'),
                            salary=json.dumps(pay,ensure_ascii=False) if pay else None)
    except Exception:
        pass
    return {}

def _hireology_rendered(page,client):
    """Server-rendered careers page (2026-11): job cards plus an explicit result count.

    The page announces "N jobs found" in an <output> element beside the results; the
    cards must match that number exactly, so a paginated, truncated or still-loading
    page fails the source instead of closing jobs. Job URLs keep the stored identity
    https://careers.hireology.com/<org>/<id>/description.
    """
    soup=BeautifulSoup(page,'html.parser')
    results=soup.select_one('[data-qa-id="jobs-results"]')
    counts=[re.fullmatch(r'(\d+)\s+jobs?\s+found',o.get_text(' ',strip=True)) for o in soup.find_all('output')]
    counts=[c for c in counts if c]
    if results is None or results.get('aria-busy')=='true' or len(counts)!=1:
        raise ValueError('Hireology public configuration missing')
    m=counts[0]
    total=int(m.group(1));jobs=[];seen=set()
    for card in soup.select('[data-qa-id="job-card"]'):
        link=card.select_one('a[data-qa-id="job-card-title"]')
        p=urlsplit(link.get('href') or '') if link else None
        ident=re.fullmatch(r'/[^/]+/(\d+)/description',p.path) if p else None
        if not ident or p.netloc!='careers.hireology.com' or ident.group(1) in seen:
            raise ValueError('Missing/repeated Hireology job')
        seen.add(ident.group(1))
        where=card.select_one('[data-qa-id="job-card-location"]')
        jobs.append(dict(title=link.get_text(' ',strip=True),url=f'https://careers.hireology.com{p.path}',
                         location=where.get_text(' ',strip=True) if where else None,description=None,salary=None))
    if len(jobs)!=total:raise ValueError('Incomplete Hireology pagination')
    for job in jobs[:60]:
        job.update({k:v for k,v in _hireology_detail(client,job['url']).items() if v})
    return jobs

def hireology(source,client):
    r=client.get(source['url']);r.raise_for_status();m=re.search(r'var startingData\s*=\s*',r.text)
    if not m:return _hireology_rendered(r.text,client)
    config=json.JSONDecoder().raw_decode(r.text[m.end():])[0]
    if config.get('apiUrl')!='https://api.hireology.com/v2':raise ValueError('Unexpected Hireology API host')
    headers={'Authorization':'Bearer '+config['apiToken']};jobs=[];seen=set();total=None
    for page in range(1,51):
        r=client.get(config['apiUrl']+'/public/careers/'+config['careersPath'],params={'page':page,'page_size':100},headers=headers)
        r.raise_for_status();d=r.json()
        if not isinstance(d.get('data'),list) or 'count' not in d:raise ValueError('Unrecognized Hireology public jobs')
        count=int(d['count'])
        if total is not None and total!=count:raise ValueError('Hireology total changed')
        total=count
        for j in d['data']:
            ident=j.get('id')
            if not ident or ident in seen:raise ValueError('Missing/repeated Hireology job')
            seen.add(ident);jobs.append(dict(title=j.get('name'),url=j.get('career_site_url'),description=j.get('job_description'),
                location='; '.join(', '.join(x.get(k,'') for k in ('city','state')) for x in j.get('locations',[])),
                salary=json.dumps(j['compensation']) if j.get('compensation') else None))
        if len(jobs)==total:return jobs
        if not d['data'] or len(jobs)>total:raise ValueError('Incomplete Hireology pagination')
    raise ValueError('Hireology pagination cap')

def paycom(source,client):
    r=client.get(source['url']);r.raise_for_status();m=re.search(r'var configsFromHost\s*=\s*',r.text)
    if not m:raise ValueError('Paycom public portal configuration missing')
    config=json.JSONDecoder().raw_decode(r.text[m.end():])[0];lib=json.loads(config['libConfig'])
    base=lib['atsPortalMantleServiceUrl']
    if base!='https://portal-applicant-tracking.us-cent.paycomonline.net/':raise ValueError('Unexpected Paycom public service host')
    # Anonymous session issued in the public board HTML; no account sign-in.
    headers={'Authorization':config['sessionJWT'],'Locale':'en-US','Portal-Host-Referrer':r.url}
    filters={k:[] for k in ('workEnvironments','positionTypes','educationLevels','categories','travelTypes','shiftTypes','otherFilters')}
    filters.update(distanceFrom=0,keywordSearchText='',location='',sortOption='')
    jobs=[];seen=set();total=None
    for _ in range(50):
        r=client.post(base+'api/ats/job-posting-previews/search',json={'skip':len(jobs),'take':100,'filtersForQuery':filters},headers=headers)
        r.raise_for_status();d=r.json()
        if not isinstance(d.get('jobPostingPreviews'),list) or 'jobPostingPreviewsCount' not in d:raise ValueError('Unrecognized Paycom listings')
        count=int(d['jobPostingPreviewsCount'])
        if total is not None and count!=total:raise ValueError('Paycom total changed')
        total=count
        for j in d['jobPostingPreviews']:
            ident=j.get('jobId')
            if not ident or ident in seen:raise ValueError('Missing/repeated Paycom job')
            seen.add(ident);jobs.append(dict(title=j.get('jobTitle'),url='https://www.paycomonline.net/v4/ats/web.php/portal/'+source['board']+'/jobs/'+str(ident),
                location=j.get('locations'),description=j.get('description'),posted_at=j.get('postedOn')))
        if len(jobs)==total:return jobs
        if not d['jobPostingPreviews'] or len(jobs)>total:raise ValueError('Incomplete Paycom pagination')
    raise ValueError('Paycom pagination cap')

def hirebridge(source,client):
    jobs=[];seen=set()
    for start in range(1,5001,100):
        r=client.get('https://hbapi.hirebridge.com/careercenter/v2/GetJobListings',
            params={'cid':source['cid'],'language':'en','startrow':start,'endrow':start+99});r.raise_for_status()
        d=r.json();d=json.loads(d) if isinstance(d,str) else d
        if not isinstance(d,list):raise ValueError('Unrecognized Hirebridge public list')
        for j in d:
            ident=j.get('joblistid')
            if not ident or ident in seen:raise ValueError('Missing/repeated Hirebridge job')
            seen.add(ident);team=j.get('busunitname') or j.get('companyname') or source['team']
            jobs.append(dict(title=j.get('jobtitle'),url=f'https://recruit.hirebridge.com/v3/CareerCenter/v2/details.aspx?cid={source["cid"]}&jid={ident}',
                location=j.get('locations'),description=(j.get('jobintro') or '')+(j.get('jobdesc') or ''),
                team=team,league='NHL' if 'Devils' in team else source['league']))
        if len(d)<100:return jobs
    raise ValueError('Hirebridge pagination cap')

def aeg_kings(source,client):
    url=source['url'];out={};seenpages=set()
    for _ in range(50):
        r=client.get(url);r.raise_for_status();soup=BeautifulSoup(r.text,'html.parser')
        if r.url in seenpages:raise ValueError('Repeated AEG page')
        seenpages.add(r.url)
        for a in soup.find_all('a',href=re.compile(r'/careers/jobs/KINGS[^/]+/')):
            u=urljoin(r.url,a['href']);out[u]=dict(title=a.get_text(' ',strip=True),url=u)
        nxt=soup.select_one('.pager__item--next a[href]')
        if not nxt:
            if not out:raise ValueError('AEG Kings listing not recognized or empty; needs review')
            return list(out.values())
        url=urljoin(r.url,nxt['href'])
    raise ValueError('AEG pagination cap')

def jobvite(source,client):
    r=client.get(source['url']);r.raise_for_status();soup=BeautifulSoup(r.text,'html.parser');out={}
    for a in soup.select('.jv-job-list-name a[href]'):
        row=a.find_parent('tr');loc=row.select_one('.jv-job-list-location') if row else None
        u=urljoin(r.url,a['href'])
        if u in out:raise ValueError('Repeated Jobvite job')
        out[u]=dict(title=a.get_text(' ',strip=True),url=u,location=loc.get_text(' ',strip=True) if loc else None)
    if soup.select_one('.jv-pagination a') or soup.find('a',string=re.compile(r'^Next',re.I)):
        raise ValueError('Jobvite pagination requires review')
    if not out and not re.search('no (?:open |available )?(?:jobs|positions)',soup.get_text(' ',strip=True),re.I):
        raise ValueError('Jobvite empty board not verified')
    return list(out.values())

def bruins(source,client):
    r=client.get(source['url']);r.raise_for_status();soup=BeautifulSoup(r.text,'html.parser')
    marker=soup.select_one('.title-capt')
    if not marker or marker.get_text(strip=True)!='Boston Bruins':raise ValueError('Bruins title filter changed')
    m=re.search(r'var cws_opts\s*=\s*',r.text)
    if not m:raise ValueError('Bruins public search configuration missing')
    config=json.JSONDecoder().raw_decode(r.text[m.end():])[0]
    if config['api']!='https://jobsapi-google.m-cloud.io/api/':raise ValueError('Unexpected Bruins search API')
    filters=re.search(r'filters:\s*\["ats_portalid:([^"]+)"\]',r.text)
    if not filters:raise ValueError('Bruins external portal filter missing')
    portals=filters[1].split('~')
    if any('internal' in x.lower() for x in portals):raise ValueError('Refusing internal hiring portal')
    facet='('+' OR '.join('ats_portalid='+json.dumps(x) for x in portals)+')'
    out=[];seen=set();total=None;offset=0
    for _ in range(30):
        r=client.get(config['api']+'job/search',params={'companyName':config['org'],'pageSize':100,'offset':offset,
                       'query':'"Boston Bruins"','customAttributeFilter':facet})
        r.raise_for_status();d=r.json()
        if not isinstance(d.get('searchResults'),list) or 'totalHits' not in d:raise ValueError('Bruins result/count missing')
        count=int(d['totalHits'])
        if total is not None and count!=total:raise ValueError('Bruins total changed')
        total=count
        for item in d['searchResults']:
            j=item['job'];ident=j.get('id')
            if not ident or ident in seen:raise ValueError('Repeated/missing Bruins search job')
            seen.add(ident)
            # Same title filter as the official Bruins landing page, plus its
            # explicit external-portal allowlist. Venue concession roles excluded.
            if j.get('ats_portalid') not in portals:raise ValueError('Bruins API ignored portal filter')
            if 'boston bruins' not in j.get('title','').lower():continue
            out.append(dict(title=j['title'],url=j['url'],location=', '.join(j.get(k,'') for k in ('primary_city','primary_state')),
                            description=j.get('description'),posted_at=j.get('open_date')))
        offset=len(seen)
        if offset==total:return out
        if not d['searchResults'] or offset>total:raise ValueError('Incomplete Bruins pagination')
    raise ValueError('Bruins pagination cap')

SCRAPERS={'bruins':bruins,'jobvite':jobvite,'dayforce':dayforce,'bamboohr':bamboohr,'lever':lever,'paylocity':paylocity,
          'paycor':paycor,'jazzhr':jazzhr,'tnse':tnse,'clearcompany':clearcompany,
          'applicantpro':applicantpro,'icims':icims,'msg':msg,'bkse':bkse,
          'hireology':hireology,'paycom':paycom,'hirebridge':hirebridge,'aeg_kings':aeg_kings}
