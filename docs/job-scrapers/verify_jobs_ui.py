"""Read-only deployed jobs UI contract verification. No browser or application writes."""
from pathlib import Path
from datetime import datetime,timezone
from urllib.parse import urljoin
import hashlib,re,json,requests
ROOT=Path(__file__).resolve().parent
def main():
    session=requests.Session();report={'checked_at':datetime.now(timezone.utc).isoformat(),'browser_visual_check':False,'standalone':[],'dashboard':{}}
    canonical=(ROOT/'ui/job-board-core.mjs').read_text(encoding='utf-8')
    expected=hashlib.sha256(canonical.encode()).hexdigest()
    for label,url in [('robotics','https://misterplusev.github.io/robotics-jobradar-board/'),('tech','https://misterplusev.github.io/jobradar-tech-board/'),('teams','https://misterplusev.github.io/job-radar/')]:
        page=session.get(url,timeout=30);page.raise_for_status();core=session.get(urljoin(url,'job-board-core.mjs'),timeout=30);core.raise_for_status();core.encoding='utf-8'
        observed=hashlib.sha256(core.text.replace('\r\n','\n').encode()).hexdigest();assert observed==expected,(label,'stale shared core')
        page.encoding='utf-8';assert 'Include international &amp; unspecified locations' in page.text;assert 'Newest posted first' in page.text;assert 'abet-chip-flip' in page.text;assert 'value="all">All' in page.text
        assert ('value="1" selected' in page.text) if label!='teams' else ('<option value="active">Active only</option>' in page.text)
        report['standalone'].append({'id':label,'url':url,'http':page.status_code,'core_sha256':observed,'controls':True,'chip':True,'core_mime':core.headers.get('Content-Type')})
    root='https://sportsbook-jobs-dashboard.vercel.app/';page=session.get(root,timeout=30);page.raise_for_status()
    scripts=re.findall(r'<script[^>]+src="([^"]+)"',page.text);app=[]
    for src in scripts:
        if '/app/' in src:
            response=session.get(urljoin(root,src),timeout=30);response.raise_for_status();app.append(response.text)
    bundle='\n'.join(app);assert 'Include international' in bundle,'Sportsbook old deployment';assert 'Date not provided' in bundle;assert 'abet-chip-flip' in bundle
    report['standalone'].append({'id':'sportsbook','url':root,'http':page.status_code,'bundle_contract':True,'chip':True})
    root='https://abet-dashboard.vercel.app/';page=session.get(root,timeout=30);page.raise_for_status()
    scripts=re.findall(r'<script[^>]+src="([^"]+)"',page.text);src=next(x for x in scripts if '/assets/main-' in x);response=session.get(urljoin(root,src),timeout=30);response.raise_for_status();bundle=response.text
    assert 'Include international' in bundle and 'Date not provided' in bundle,'Dashboard old deployment'
    assert 'ijw-logo' in bundle and 'ijw-toggles' in bundle and 'All matches' in bundle
    for tab in ['jobs-browser','robotics-jobs','tech-jobs','teams-jobs']:
        assert tab in bundle
        check=session.get(root+'?section=jobs&tab='+tab,timeout=30);check.raise_for_status()
    report['dashboard']={'url':root+'?section=jobs&tab=robotics-jobs','http':page.status_code,'bundle':src,'four_routes':True,'logo_renderer':True,'filter_contract':True}
    for url in ['https://misterplusev.github.io/robotics-jobradar-board/logos/zoox.png','https://misterplusev.github.io/robotics-jobradar-board/logos/nuro.png','https://misterplusev.github.io/jobradar-tech-board/logos/openai.png','https://a.espncdn.com/i/teamlogos/mlb/500/nym.png']:
        image=session.get(url,timeout=20);image.raise_for_status();assert image.headers.get('Content-Type','').startswith('image/')
    report['representative_logos_http']=200
    path=ROOT/'ui/live-ui-verification.json';path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
