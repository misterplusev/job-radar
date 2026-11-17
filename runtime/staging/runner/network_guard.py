"""Hard request/body/deadline guard for reviewed read-only career requests."""
import time,re,json,hashlib
from urllib.parse import urlsplit
import requests

class BudgetExceeded(RuntimeError):pass

class NetworkBudget:
    def __init__(self, allowed_hosts, max_requests=12, seconds=105):
        self.allowed=set(allowed_hosts);self.limit=max_requests;self.deadline=time.monotonic()+seconds
        self.events=[];self.bytes=0;self.count=0;self.original=None;self.violation=None

    def validate(self, method, url):
        p=urlsplit(url)
        if p.scheme!='https' or p.username or p.password or p.port not in (None,443):raise BudgetExceeded('Only public HTTPS career reads allowed')
        host=(p.hostname or '').lower()
        if host not in self.allowed:raise BudgetExceeded('Unreviewed host blocked: '+host)
        if method not in ('GET','HEAD') and not (method=='POST' and re.fullmatch(r'/wday/cxs/[^/]+/[^/]+/jobs/?',p.path)):
            raise BudgetExceeded('Non-career-read method blocked')
        if self.count>=self.limit or time.monotonic()>=self.deadline:raise BudgetExceeded('Request/deadline budget exhausted')
        return p

    def install(self):
        self.original=requests.Session.send
        budget=self
        def guarded(session, request, **kw):
            try:p=budget.validate(request.method,request.url)
            except BudgetExceeded as exc:budget.violation=str(exc);raise
            budget.count+=1
            remaining=max(.1,budget.deadline-time.monotonic())
            kw['timeout']=(min(8,remaining),min(12,remaining));kw['stream']=True
            began=time.monotonic();event={'host':p.hostname,'path':p.path,'method':request.method,'attempt':budget.count}
            try:
                # Redirects are recursively sent through this same guard by Requests.
                response=budget.original(session,request,**kw)
                if not response._content_consumed:
                    chunks=[];size=0
                    for part in response.iter_content(65536):
                        size+=len(part);budget.bytes+=len(part)
                        if size>4*1024*1024 or budget.bytes>8*1024*1024 or time.monotonic()>budget.deadline:
                            response.close();raise BudgetExceeded('Response byte/deadline budget exhausted')
                        chunks.append(part)
                    response._content=b''.join(chunks);response._content_consumed=True
                event.update(status=response.status_code,bytes=len(response.content),retry_after=response.headers.get('Retry-After','')[:100],cf_ray=response.headers.get('CF-Ray','')[:100],server=response.headers.get('Server','')[:80],body_prefix_sha256=hashlib.sha256(response.content[:4096]).hexdigest())
                if response.status_code>=400:
                    title=re.search(r'<title[^>]*>(.*?)</title>',response.text[:65536],re.I|re.S)
                    event['response_title']=re.sub(r'\s+',' ',title.group(1))[:180] if title else ''
                return response
            except Exception as exc:
                if isinstance(exc,BudgetExceeded):budget.violation=str(exc)
                event['error']=type(exc).__name__+': '+str(exc)[:160];raise
            finally:
                event['elapsed_ms']=round((time.monotonic()-began)*1000);budget.events.append(event)
        requests.Session.send=guarded
        return self

    def close(self):
        if self.original:requests.Session.send=self.original
