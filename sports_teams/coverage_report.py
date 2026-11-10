"""Report each team's official route and current run, without equating discovery with proof."""
import json,html
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent

def build(results):
    checks={r['source']['key']:r for r in results};teams=[]
    for team in json.loads((ROOT/'official_careers_registry.json').read_text(encoding='utf-8')):
        routes=[];urls=set()
        for key in team['source_keys']:
            r=checks.get(key,{})
            count=len(r['rows']) if 'rows' in r else r.get('job_count')
            urls.update(j['url'] for j in r.get('rows',[]) if r.get('status')=='success')
            routes.append({'source_key':key,'status':r.get('status','not_checked'),
                           'job_count':count,'checked_at':r.get('observed_at'),'error':r.get('error')})
        good=sum(r['status']=='success' for r in routes)
        status='verified' if routes and good==len(routes) else 'partial' if good else 'unverified'
        teams.append(dict(team,verification_status=status,live_checks=routes,unique_jobs_in_checked_sources=len(urls)))
    summary={'teams':len(teams),'with_verified_source':sum(any(x['status']=='success' for x in t['live_checks']) for t in teams),
             'all_configured_routes_verified':sum(t['verification_status']=='verified' for t in teams),
             'partial':sum(t['verification_status']=='partial' for t in teams),'unverified':sum(t['verification_status']=='unverified' for t in teams)}
    return {'generated_at':datetime.now(timezone.utc).isoformat(),'summary':summary,'teams':teams,
            'scope':'124 NFL, NBA, MLB and NHL teams. Shared ownership boards may include affiliated businesses. A verified source means its live listing fetched completely; it does not claim every linked vendor or alternate career page works.',
            'proof_note':'Official league directories and team pages were checked individually. Some NBA team pages block HTTP; for those, the branded employer ATS and matching public job links establish the route. Discovery evidence is retained in the local official_audit directory.'}

def write(report,directory):
    directory=Path(directory);directory.mkdir(exist_ok=True,parents=True)
    (directory/'coverage.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    e=html.escape;rows=[]
    for t in report['teams']:
        boards=list(dict.fromkeys(x['board_url'] for x in t['routes'] if x.get('source_key')))
        links='<br>'.join('<a href="'+e(u,quote=True)+'">'+e(u)+'</a>' for u in boards)
        checks='<br>'.join(e(x['source_key'])+': '+e(x['status'])+' ('+str(x.get('job_count'))+' jobs)'+(' — '+e(x['error']) if x.get('error') else '') for x in t['live_checks'])
        rows.append('<tr><td>'+e(t['league'])+'</td><td><a href="'+e(t['official_entry_url'],quote=True)+'">'+e(t['team'])+'</a></td><td>'+e(t['verification_status'])+'</td><td>'+links+'</td><td>'+checks+'</td></tr>')
    text='<!doctype html><html><meta charset="utf-8"><title>Sports team career coverage</title><style>body{font:15px system-ui;margin:2rem;color:#152238}table{border-collapse:collapse;width:100%}td,th{padding:12px;border:1px solid #ccd5df;text-align:left;vertical-align:top;overflow-wrap:anywhere}td:nth-child(4){max-width:350px}input{padding:10px;width:300px}a{color:#1260a8}</style><h1>Sports team career coverage</h1><p>'+e(report['generated_at'])+'</p><p>'+e(str(report['summary']))+'</p><p>'+e(report['scope'])+'</p><p>'+e(report['proof_note'])+'</p><input id="filter" placeholder="Filter by team, league, or status"><p><a href="coverage.json">Full JSON evidence</a> · <a href="index.html">Job board</a></p><table><thead><tr><th>League</th><th>Official team entry</th><th>Status</th><th>Employer boards</th><th>Live checks</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table><script>document.getElementById("filter").oninput=e=>{for(const r of document.querySelectorAll("tbody tr"))r.hidden=!r.textContent.toLowerCase().includes(e.target.value.toLowerCase())}</script></html>'
    (directory/'coverage.html').write_text(text,encoding='utf-8')

if __name__=='__main__':
    results=[json.loads(p.read_text(encoding='utf-8')) for p in (ROOT/'data/official_audit/source_checks').glob('*.json')]
    report=build(results);write(report,ROOT/'data/official_audit');print(json.dumps(report['summary']))
