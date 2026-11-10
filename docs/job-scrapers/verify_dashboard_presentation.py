"""Read-only proof of the production dashboard's four-module presentation version."""
from pathlib import Path
from urllib.parse import urljoin
from datetime import datetime,timezone
import json,re,subprocess,requests
ROOT=Path(__file__).resolve().parent
def main():
    base='https://abet-dashboard.vercel.app/';session=requests.Session()
    def get(url):
        r=session.get(url,timeout=30);r.raise_for_status();r.encoding='utf-8';return r
    receipt=json.loads((ROOT/'ui/dashboard-parity-publication.json').read_text(encoding='utf-8'))
    page=get(base);scripts=re.findall(r'<script[^>]+src="([^"]+)"',page.text);main=next(src for src in scripts if '/assets/main-' in src);bundle=get(urljoin(base,main)).text
    tokens=['2026-11-10.3','data-job-presentation','board-overview','company-scroll','job-card-heading','job-details','abet-wordmark']
    supporting=[];imports=sorted(set(re.findall(r'from\s*["\'](\./[^"\']+\.js)["\']',bundle)));assert len(imports)<60
    # Vite can place shared exports in a chunk named after another widget.
    # Follow actual static import edges, rather than assuming all jobs code is in main.
    for relative in imports:
        if all(token in bundle for token in tokens):break
        url=urljoin(urljoin(base,main),relative);assert url.startswith(base+'assets/')
        content=get(url).text;bundle+='\n'+content;supporting.append(url)
    for token in tokens:assert token in bundle,('Missing production UI token',token)
    assert 'className:"ijw-job"' not in bundle and 'className:"jbw-job-card"' not in bundle
    css_urls=re.findall(r'<link[^>]+href="([^"]+\.css)"',page.text);styles='\n'.join(get(urljoin(base,url)).text for url in css_urls)
    for selector in ['.jobs-board .job-card','.jobs-board .company-scroll','.jobs-board .abet-wordmark']:assert selector in styles,selector
    assert 'grid-template-rows:repeat(2,34px)' in styles
    proof=get(base+'jobs-standard-proof.json').json();preview=get(base+'jobs-standard-proof.html')
    assert len(proof['modules'])==4 and all(m['version']=='2026-11-10.3' for m in proof['modules'])
    assert proof['standaloneCssSha256']=='bc31b9f215462cbd17ccd6864b98d66b5d2959e7e3eeb08252f07dd0aeb473cb'
    assert 'not a screenshot of the production browser' in preview.text
    assert preview.text.count('class="proof-panel"')==4 and preview.text.count('class="job-card"')==8
    routes=[]
    for tab in ['jobs-browser','robotics-jobs','tech-jobs','teams-jobs']:
        assert tab in bundle;r=get(base+'?section=jobs&tab='+tab);routes.append({'url':r.url,'http':r.status_code})
    p=subprocess.run(['vercel.cmd','inspect',base,'--json'],capture_output=True,text=True,encoding='utf-8',timeout=40,check=True);deployment=json.loads(p.stdout)
    p=subprocess.run(['vercel.cmd','api','/v13/deployments/'+deployment['id'],'--raw'],capture_output=True,text=True,encoding='utf-8',timeout=40,check=True);meta=json.loads(p.stdout)
    assert meta['readyState']=='READY' and meta['gitSource']['sha']==receipt['commit'],('Wrong production revision',meta.get('gitSource'))
    result={'checked_at':datetime.now(timezone.utc).isoformat(),'browser_visual_check':False,'deployment':{'id':meta['id'],'state':meta['readyState'],'source_commit':meta['gitSource']['sha']},'version':'2026-11-10.3','bundle':urljoin(base,main),'supporting_chunks_inspected':supporting,'routes':routes,'shared_stylesheet_sha256':proof['standaloneCssSha256'],'shared_header_overview_card_in_live_bundle':True,'two_row_scroll_css_in_live_bundle':True,'interaction_proof':base+'jobs-standard-proof.json','preview':base+'jobs-standard-proof.html','preview_type':'Static rendering of actual components with sampled public records; not a browser screenshot'}
    (ROOT/'ui/dashboard-parity-live-proof.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
