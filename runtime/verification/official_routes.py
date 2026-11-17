"""Inspect employer-published links. Do not request restricted Workday hosts."""
import json
import re
from pathlib import Path
from urllib.parse import urlsplit,urljoin
from bs4 import BeautifulSoup
import requests

sites={}
for team in json.loads(Path("sports_teams/official_careers_registry.json").read_text()):
    routes=[r for r in team["routes"] if str(r.get("source_key","")).startswith("wd:")]
    if not routes: continue
    for p in {team["official_entry_url"]}|{r.get("official_page") for r in routes}:
        if p: sites.setdefault(p,[]).append(team["team"])
for page,org in [
    ("https://www.betmgminc.com/careers/","BetMGM"),
    ("https://supergroup.com/careers/search-jobs/betway-global-careers/","Betway"),
    ("https://www.rockwellautomation.com/en-us/careers.html","Rockwell Automation"),
    ("https://www.autostoresystem.com/careers","AutoStore"),
    ("https://bostondynamics.com/careers/","Boston Dynamics")]:
    sites.setdefault(page,[]).append(org)
blocked=set()
results=[]
with requests.Session() as s:
    s.headers["User-Agent"]="ABET employer career link review/1.0"
    for page,orgs in sorted(sites.items()):
        host=(urlsplit(page).hostname or "").lower()
        entry={"organizations":orgs,"entry":page}
        results.append(entry)
        if host.endswith(("myworkdayjobs.com","myworkdaysite.com")) or host in blocked:
            entry["result"]="restricted upstream, no request"; continue
        try:
            response=s.get(page,timeout=(4,8),allow_redirects=False)
            entry["http"]=response.status_code
            if response.status_code in (401,403,429) or response.headers.get("CF-Mitigated")=="challenge":
                blocked.add(host);entry["result"]="restricted, host stopped";continue
            if response.is_redirect:
                entry["official_redirect"]=urljoin(page,response.headers["Location"]);continue
            response.raise_for_status()
            soup=BeautifulSoup(response.content,"html.parser")
            found={}
            for tag in soup.select("a[href],iframe[src],link[type*=rss],link[type*=atom],[data-api-url]"):
                path=tag.get("data-api-url") or tag.get("href") or tag.get("src")
                if not path or path.startswith(("#","mailto:","tel:","javascript:")):continue
                link=urljoin(page,path)
                if urlsplit(link).scheme!="https":continue
                label=" ".join(tag.stripped_strings)[:95]
                if tag.has_attr("data-api-url") or re.search(r"workday|teamworkonline|careers?|job[s /-]|open position|search opening|join our team|/recruit|opening[s ]",link+" "+label,re.I):
                    found[link]=label or tag.name
            entry["career_links"]=[{"url":u,"label":l} for u,l in found.items()][:60]
            entry["job_posting_markup"]=bool(soup.find("script",type="application/ld+json",string=re.compile(r'"JobPosting"')))
        except requests.RequestException as exc:
            entry["error"]=type(exc).__name__
        print(", ".join(orgs),entry.get("http"),len(entry.get("career_links",[])),entry.get("result",""))
Path("official-routes.json").write_text(json.dumps(results,indent=2))
