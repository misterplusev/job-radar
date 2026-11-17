import { CATALOG } from './catalog.mjs';
export const MODULES = {robotics:5,tech:20,sports_teams:35,sportsbook:50};
export const SHAS = {robotics:'ac5370eb792394cfc0dd289305bc104992479cd0',tech:'f631e0b6f165cf4764ab857f1b4164ec76f83dc8',sports_teams:'ac5370eb792394cfc0dd289305bc104992479cd0',sportsbook:'bcf53bb7c2371601e92f247ddf0aa36d3f9fecdc'};
export const PERIOD_HOURS={robotics:1,tech:1,sports_teams:1,sportsbook:4};
const TARGETS={robotics:['misterplusev/job-radar','master'],sports_teams:['misterplusev/job-radar','master'],tech:['misterplusev/job-radar-tech','master'],sportsbook:['misterplusev/sportsbook-jobs-dashboard','prod/sportsbook-jobs']};
const WORKFLOW='staging-recurring.yml';
const MIN_TESTS={robotics:100,tech:70,sports_teams:60,sportsbook:15};
const DAY=86400000,HOUR=3600000,MAX_RUNS=96,MAX_REPORT=98304;
const json=(x,status=200)=>Response.json(x,{status,headers:{'Cache-Control':'no-store'}});
const sourceKey=(m,id)=>`s:${m}:${id}`;
export function slotAt(now,minute,hours=1){const d=new Date(now);d.setUTCMinutes(minute,0,0);if(+d>now)d.setUTCHours(d.getUTCHours()-1);while(d.getUTCHours()%hours)d.setUTCHours(d.getUTCHours()-1);return d.toISOString();}
export function retryAt(source,previous,now){
 const failures=(previous?.failures||0)+1;
 let delay=Math.min(24,2**Math.min(failures-1,5))*HOUR;
 for(const event of source.http||[]){const raw=event.retry_after||'';const parsed=/^\d+$/.test(raw)?Number(raw)*1000:Date.parse(raw)-now;if(Number.isFinite(parsed))delay=Math.max(delay,parsed);if(event.status===403)delay=Math.max(delay,DAY);}
 return now+delay;
}
export function chooseSources(module,states,cursor,now){
 const eligible=CATALOG[module].filter(s=>s.supported&&(!states[sourceKey(module,s.id)]?.retry_at||states[sourceKey(module,s.id)].retry_at<=now));
 const priority=eligible.filter(s=>s.priority),normal=eligible.filter(s=>!s.priority);
 const chosen=[];
 if(priority.length)chosen.push(priority[cursor%priority.length].id);
 if(normal.length)chosen.push(normal[cursor%normal.length].id);
 if(chosen.length<2){const other=eligible.filter(s=>!chosen.includes(s.id));if(other.length)chosen.push(other[cursor%other.length].id);}
 return chosen;
}
export function normalizeReport(body,lease){
 if(body.module!==lease.module||body.slot!==lease.slot||body.lease_id!==lease.lease_id||body.source_sha!==SHAS[lease.module])throw Error('report identity/revision mismatch');
 if(body.production_writes!==0||body.discord_sends!==0)throw Error('isolation violation reported');
 const tests=(body.tests||[]).slice(0,3).map(t=>({passed:t.passed===true,tests:Number(t.tests)||0,returncode:t.returncode,tail:String(t.tail||'').slice(-1800)}));
 const testOK=tests.length>0&&tests.every(t=>t.passed)&&tests.reduce((n,t)=>n+t.tests,0)>=MIN_TESTS[lease.module];
 const seen=new Set();const sources=[];
 for(const s of body.sources||[]){
  if(!lease.source_ids.includes(s.source_id)||seen.has(s.source_id)||!Number.isInteger(s.requests)||s.requests<0||s.requests>12)throw Error('source identity/request budget mismatch');
  seen.add(s.source_id);
  sources.push({source_id:s.source_id,status:s.status,complete:s.complete===true,jobs_total:Math.min(Number(s.jobs_total)||0,100000),requests:s.requests,bytes:Number(s.bytes)||0,seconds:Number(s.seconds)||0,error:String(s.error||'').slice(-600),http:(s.http||[]).slice(-12).map(e=>({host:String(e.host||'').slice(0,160),path:String(e.path||'').slice(0,200),status:e.status,retry_after:String(e.retry_after||'').slice(0,100),cf_ray:String(e.cf_ray||'').slice(0,100),response_title:String(e.response_title||'').slice(0,180)})),sample:(s.sample||[]).slice(0,10).map(j=>({title:String(j.title||'').slice(0,160),url:String(j.url||'').slice(0,500),location:String(j.location||'').slice(0,120)}))});
 }
 const full=seen.size===lease.source_ids.length;
 const status=!testOK?'test_failed':!full?'incomplete':!sources.length?'cooldown':sources.every(s=>s.status==='passed'&&s.complete)?'passed':'degraded';
 return {lease_id:lease.lease_id,module:lease.module,slot:lease.slot,source_sha:body.source_sha,runner_build:String(body.runner_build||'').slice(0,100),github_run_url:String(body.github_run_url||'').slice(0,200),status,tests,sources,started_at:body.started_at,finished_at:body.finished_at,production_writes:0,discord_sends:0,scope:'bounded canaries; not a full production scrape'};
}

export class StagingControl {
 constructor(ctx,env){this.ctx=ctx;this.env=env;}
 async config(){return await this.ctx.storage.get('control')||{enabled:false,modules:{},active:null,day:null,run_count:0};}
 async dispatch(lease){
  const [repo,ref]=TARGETS[lease.module];
  const r=await fetch(`https://api.github.com/repos/${repo}/actions/workflows/${WORKFLOW}/dispatches`,{method:'POST',headers:{Authorization:`Bearer ${this.env.GITHUB_TOKEN}`,Accept:'application/vnd.github+json','User-Agent':'ABET-Isolated-Staging','Content-Type':'application/json'},body:JSON.stringify({ref,inputs:{module:lease.module,slot:lease.slot,lease_id:lease.lease_id,source_sha:lease.source_sha}}),signal:AbortSignal.timeout(8000)});
  if(r.status!==204)throw Error(`Staging workflow dispatch HTTP ${r.status}`);
  return {started:true};
 }
 async accept(body,now=Date.now()){
  const existing=await this.ctx.storage.get('r:'+body.lease_id);if(existing)return {accepted:true,duplicate:true};
  const state=await this.config();if(!state.active||body.lease_id!==state.active.lease_id)throw Error('unknown or expired lease');
  const report=normalizeReport(body,state.active);report.recorded_at=new Date(now).toISOString();
  await this.ctx.storage.transaction(async tx=>{
   for(const source of report.sources){
    const key=sourceKey(report.module,source.source_id),prev=await tx.get(key);
    const passed=source.status==='passed'&&source.complete&&report.status!=='test_failed';
    await tx.put(key,{module:report.module,source_id:source.source_id,source_sha:report.source_sha,status:source.status,last_at:now,last_success:passed?now:prev?.last_success||null,failures:passed?0:(prev?.failures||0)+1,retry_at:passed?null:retryAt(source,prev,now),consecutive_passes:passed?(prev?.source_sha===report.source_sha?prev?.consecutive_passes||0:0)+1:0,jobs_total:source.jobs_total,sample:passed?source.sample:prev?.sample||[],sample_observed_at:passed?now:prev?.sample_observed_at||null,http:source.http.slice(-3),error:source.error});
   }
   state.modules[report.module]={...state.modules[report.module],status:report.status,last_run:now,last_report:report.lease_id,last_error:report.status==='passed'?null:report.sources.find(s=>s.error)?.error||report.tests.find(t=>!t.passed)?.tail?.slice(-300)||report.status};
   state.active=null;state.last_report=now;
   await tx.put('r:'+report.lease_id,report);await tx.put('latest:'+report.module,report);await tx.put('control',state);
  });
  const rows=await this.ctx.storage.list({prefix:'r:',limit:800});const sorted=[...rows].sort((a,b)=>Date.parse(b[1].recorded_at)-Date.parse(a[1].recorded_at));
  const remove=sorted.filter((x,i)=>i>=672||now-Date.parse(x[1].recorded_at)>7*DAY).map(x=>x[0]);if(remove.length)await this.ctx.storage.delete(remove);
  if(state.enabled)await this.ctx.storage.setAlarm(now+30000);
  return {accepted:true,status:report.status};
 }
 async tick(now=Date.now()){
  let state=await this.config();if(!state.enabled)return state;
  state.last_tick=now;
  const day=new Date(now).toISOString().slice(0,10);if(state.day!==day){state.day=day;state.run_count=0;}
  if(state.active){
   if(state.active&&now-state.active.created_at>12*60000){
    const lease=state.active;state.modules[lease.module]={...state.modules[lease.module],status:'runner_timeout',last_error:'No accepted result within twelve minutes; inspect staging Actions run',last_run:now};
    await this.ctx.storage.put('r:'+lease.lease_id,{...lease,status:'runner_timeout',recorded_at:new Date(now).toISOString()});state.active=null;
   }
  }
  if(!state.active&&state.run_count<MAX_RUNS){
   const sourceStates=Object.fromEntries(await this.ctx.storage.list({prefix:'s:',limit:400}));
   for(const [module,minute] of Object.entries(MODULES)){
    const slot=slotAt(now,minute,PERIOD_HOURS[module]),prior=state.modules[module]||{};if(prior.slot===slot)continue;
    const month=day.slice(0,7);if(state.private_month!==month){state.private_month=month;state.private_runs=0;}
    if(module==='sportsbook'&&state.private_runs>=200){state.modules[module]={...prior,status:'private_budget_hold',last_error:'800 reserved Actions minutes/month limit reached'};continue;}
    let source_ids=chooseSources(module,sourceStates,prior.cursor||0,now);
    if(module==='sportsbook')source_ids=[source_ids[(prior.cursor||0)%4===3&&source_ids.length>1?1:0]].filter(Boolean);
    const lease={lease_id:`${slot}:${module}`,slot,module,source_sha:SHAS[module],source_ids,created_at:now};
    state.modules[module]={...prior,slot,cursor:(prior.cursor||0)+1,status:'dispatched'};
    state.active=lease;state.run_count++;if(module==='sportsbook')state.private_runs++;await this.ctx.storage.put('control',state);
    try{const reply=await this.dispatch(lease);state.runner_error=reply.started?null:reply.reason||'runner did not start';}
    catch(e){state.runner_error=String(e.message).slice(0,200);}
    break;
   }
  }
  await this.ctx.storage.put('control',state);return state;
 }
 async health(){
  const now=Date.now(),state=await this.config(),sourceRows=Object.fromEntries(await this.ctx.storage.list({prefix:'s:',limit:400}));
  const modules={};
  for(const [m,minute] of Object.entries(MODULES)){
   const latest=await this.ctx.storage.get('latest:'+m);const sources=Object.values(sourceRows).filter(s=>s.module===m);
   modules[m]={...state.modules[m],every_minutes:PERIOD_HOURS[m]*60,minute_utc:minute,next_due_utc:new Date(Date.parse(slotAt(now,minute,PERIOD_HOURS[m]))+PERIOD_HOURS[m]*HOUR).toISOString(),source_sha:SHAS[m],registered_sources:CATALOG[m].length,sandbox_supported_sources:CATALOG[m].filter(s=>s.supported).length,observed_sources:sources.length,passing_sources:sources.filter(s=>s.status==='passed').length,cooling_sources:sources.filter(s=>s.retry_at>now).length,latest,source_status:sources.map(({sample,...s})=>s),promotion_eligible:CATALOG[m].every(c=>c.supported&&sourceRows[sourceKey(m,c.id)]?.source_sha===SHAS[m]&&sourceRows[sourceKey(m,c.id)]?.consecutive_passes>=3)};
  }
  const overdue=state.enabled?Object.entries(modules).filter(([m,v])=>!v.last_run||now-v.last_run>2*PERIOD_HOURS[m]*HOUR).map(([m])=>m):[];
  const heartbeat_stale=state.enabled&&(!state.last_tick||now-state.last_tick>10*60000);
  return {service:'abet-jobs-staging',environment:'isolated cloud development',...state,status:!state.enabled?'paused':heartbeat_stale?'scheduler_stale':overdue.length?'awaiting_or_overdue':Object.values(modules).every(m=>m.status==='passed')?'canaries_passed':'degraded',overdue,heartbeat_stale,modules,next_alarm:await this.ctx.storage.getAlarm(),limits:{runs_per_day:96,normal_scheduled_runs_per_day:78,private_runs_per_month:200,private_reserved_minutes_per_month:800,sources_per_run:2,sportsbook_sources_per_run:1,requests_per_source:12,seconds_per_source:120,report_retention_days:7,max_reports:672,sample_jobs_per_source:10},storage:'dedicated SQLite-backed Durable Object; no production Supabase',production_dispatch_capability:false,discord_sends:0};
 }
 async alarm(){
  await this.ctx.blockConcurrencyWhile(async()=>{const s=await this.config();if(!s.enabled)return;await this.ctx.storage.setAlarm(Date.now()+60000);try{await this.tick();}finally{const next=await this.config();if(next.enabled)await this.ctx.storage.setAlarm(Date.now()+(next.active?60000:Math.min(300000,Math.max(1000,Math.min(...Object.entries(MODULES).map(([m,minute])=>Date.parse(slotAt(Date.now(),minute,PERIOD_HOURS[m]))+PERIOD_HOURS[m]*HOUR-Date.now()))))))}});
 }
 async fetch(request){
  const path=new URL(request.url).pathname;
  if(path==='/status')return json(await this.health());
  if(path==='/lease')return json((await this.config()).active||{});
  return this.ctx.blockConcurrencyWhile(async()=>{
   if(path==='/report')return json(await this.accept(await request.json()));
   if(path==='/enable'||path==='/pause'){const s=await this.config();s.enabled=path==='/enable';s.changed_at=Date.now();await this.ctx.storage.put('control',s);if(s.enabled)await this.ctx.storage.setAlarm(Date.now()+1000);else await this.ctx.storage.deleteAlarm();return json({enabled:s.enabled});}
   if(path==='/tick')return json(await this.tick());
   return json({error:'not found'},404);
  });
 }
}
export default {
 async fetch(request,env){
  const path=new URL(request.url).pathname;
  if(request.method==='GET'&&path==='/')return new Response(PAGE,{headers:{'Content-Type':'text/html; charset=utf-8','Cache-Control':'public,max-age=60'}});
  const object=env.STAGING.get(env.STAGING.idFromName('isolated-development-v1'));
  if(request.method==='GET'&&path==='/status')return object.fetch('https://staging/status');
  if(request.method==='GET'&&path==='/lease'&&env.REPORT_TOKEN&&request.headers.get('Authorization')===`Bearer ${env.REPORT_TOKEN}`)return object.fetch('https://staging/lease');
  const expected=path==='/report'?env.REPORT_TOKEN:env.CONTROL_TOKEN;
  if(request.method!=='POST'||!['/report','/enable','/pause','/tick'].includes(path)||!expected||request.headers.get('Authorization')!==`Bearer ${expected}`)return json({error:'unauthorized'},403);
  const length=Number(request.headers.get('Content-Length')||0);if(length>MAX_REPORT)return json({error:'body too large'},413);
  const text=await request.text();if(text.length>MAX_REPORT)return json({error:'body too large'},413);
  try{return await object.fetch(new Request('https://staging'+path,{method:'POST',body:text||'{}',headers:{'Content-Type':'application/json'}}));}
  catch(error){return json({error:String(error.message).slice(0,160)},400);}
 }
};
const PAGE=`<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>ABET Jobs Staging</title><style>body{font:16px system-ui;background:#101820;color:#edf2f7;margin:32px;max-width:1200px}h1{color:#81e6d9}table{width:100%;border-collapse:collapse}td,th{padding:12px;text-align:left;border-bottom:1px solid #34495e}pre{white-space:pre-wrap;font-size:13px}a{color:#81e6d9}.card{padding:20px;background:#1b2936;margin:16px 0;border-radius:10px}</style><h1>ABET Jobs Staging</h1><p>Cloud validation: robotics, tech and teams hourly; sportsbook every four hours. No production database writes or Discord sends. A passing canary is not full-source acceptance.</p><div id="summary" class="card">Loading persistent staging receiptsâ€¦</div><table><thead><tr><th>Module</th><th>Latest cycle</th><th>Sources observed / registered</th><th>Next UTC run</th><th>Promotion ready</th></tr></thead><tbody id="rows"></tbody></table><div id="detail"></div><script>async function refresh(){try{const h=await(await fetch('/status')).json();document.getElementById('summary').textContent=(h.enabled?'Schedule enabled':'Schedule paused')+' Â· '+(h.run_count||0)+'/96 runs today Â· '+(h.active?'Running '+h.active.module:'Runner idle')+' Â· Persistent isolated SQLite storage';const rows=document.getElementById('rows'),details=document.getElementById('detail');rows.replaceChildren();details.replaceChildren();for(const [m,v]of Object.entries(h.modules)){const tr=document.createElement('tr');for(const x of [m,v.status||'Not run yet',v.observed_sources+' / '+v.registered_sources,v.next_due_utc,v.promotion_eligible?'Yes':'No']){const td=document.createElement('td');td.textContent=x;tr.append(td)}rows.append(tr);const box=document.createElement('details');box.className='card';const title=document.createElement('summary');title.textContent=m+' â€” tests, live sources, cooldowns and pinned revision';const pre=document.createElement('pre');pre.textContent=JSON.stringify(v,null,2);box.append(title,pre);details.append(box)}}catch(e){document.getElementById('summary').textContent='Status read failed: '+e.message}}refresh();setInterval(refresh,60000);</script>`;
