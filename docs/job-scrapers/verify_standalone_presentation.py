"""Read-only proof of shared standalone headers, cards and styles on production."""
from pathlib import Path
from datetime import datetime,timezone
from urllib.parse import urljoin
import requests,re,hashlib,json
ROOT=Path(__file__).resolve().parent
def digest(text):return hashlib.sha256(text.replace('\r\n','\n').encode()).hexdigest()
def main():
    session=requests.Session();report={'checked_at':datetime.now(timezone.utc).isoformat(),'browser_visual_check':False,'boards':[]}
    expected_css=digest((ROOT/'ui/standalone.css').read_text(encoding='utf-8'));expected_ui=digest((ROOT/'ui/standalone-ui.mjs').read_text(encoding='utf-8'))
    def get(url):
        r=session.get(url,timeout=30);r.raise_for_status();r.encoding='utf-8';return r
    for industry,url,title in [('robotics','https://misterplusev.github.io/robotics-jobradar-board/','Robotics Jobs'),('tech','https://misterplusev.github.io/jobradar-tech-board/','Tech Jobs'),('teams','https://misterplusev.github.io/job-radar/','Sports Teams Jobs')]:
        page=get(url);stylesheet=re.search(r'href="(standalone\.css[^"]*)"',page.text)
        assert stylesheet,(industry,'old page')
        css=get(urljoin(url,stylesheet[1]));ui=get(urljoin(url,'standalone-ui.mjs'))
        assert digest(css.text)==expected_css,(industry,'stale stylesheet');assert digest(ui.text)==expected_ui,(industry,'stale renderer')
        assert f'<h1>{title}</h1>' in page.text and 'class="abet-wordmark"' in page.text
        assert 'board-overview' in page.text and 'company-scroll' in page.text and '<table' not in page.text
        assert 'jobCardMarkup' in page.text and 'wireJobDetails' in page.text
        report['boards'].append({'id':industry,'url':url,'http':page.status_code,'shared_css_sha256':digest(css.text),'shared_renderer_sha256':digest(ui.text),'branded_header':True,'collapsible_overview':True,'cards':True})
    url='https://sportsbook-jobs-dashboard.vercel.app/';page=get(url)
    assert '<h1>Sportsbook Jobs</h1>' in page.text and 'abet-wordmark' in page.text and 'SB-JOBS' not in page.text,'Sportsbook old header'
    scripts=re.findall(r'<script[^>]+src="([^"]+)"',page.text)
    bundle='\n'.join(get(urljoin(url,src)).text for src in scripts if '/app/' in src)
    for token in ['company-scroll','board-overview','job-card-heading','job-details','Scroll companies right']:assert token in bundle,token
    styles=re.findall(r'<link[^>]+href="([^"]+\.css(?:\?[^"]*)?)"',page.text)
    style_text='\n'.join(get(urljoin(url,src)).text for src in styles)
    for token in ['.abet-wordmark','.job-card','.company-scroll','grid-template-rows:repeat(2,34px)','grid-auto-flow:column']:assert token in style_text,token
    report['boards'].append({'id':'sportsbook','url':url,'http':page.status_code,'branded_header':True,'collapsible_overview':True,'two_row_horizontal_companies':True,'cards':True,'css_urls':styles})
    (ROOT/'ui/presentation-live-proof.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
