"""One-off atomic URL repair. Preserves original job IDs, first-seen and delivery history.

Runs only in the existing GitHub secrets environment. A service-only database
backup is committed in the same transaction before any duplicate is merged.
"""
import json,os
from pathlib import Path
import requests

SQL=r'''
begin;
lock table public.team_jobs,public.team_job_observations,public.team_job_notifications,public.team_applications in share row exclusive mode;
create table if not exists public.team_workday_repair_backup (
 id bigserial primary key, captured_at timestamptz default now(), table_name text not null, payload jsonb not null
);
alter table public.team_workday_repair_backup enable row level security;
revoke all on public.team_workday_repair_backup from anon,authenticated;
grant all on public.team_workday_repair_backup to service_role;
create table if not exists public.team_job_url_aliases (
 id bigserial primary key, old_url text not null unique, canonical_url text not null,
 original_job_id bigint not null, repaired_at timestamptz not null default now()
);
alter table public.team_job_url_aliases enable row level security;
grant select on public.team_job_url_aliases to anon,authenticated;
grant all on public.team_job_url_aliases to service_role;
drop policy if exists team_aliases_read on public.team_job_url_aliases;
create policy team_aliases_read on public.team_job_url_aliases for select to anon,authenticated using(true);
do $repair$
declare m jsonb; oldjob public.team_jobs%rowtype; newjob public.team_jobs%rowtype;
begin
 for m in select value from jsonb_array_elements(__PLAN__::jsonb) loop
  select * into oldjob from public.team_jobs where url=m->>'old_url';
  if not found then
   if exists(select 1 from public.team_job_url_aliases where old_url=m->>'old_url' and canonical_url=m->>'canonical_url') then continue; end if;
   raise exception 'Expected legacy job missing: %',m->>'old_id';
  end if;
  if oldjob.id!=(m->>'old_id')::bigint or oldjob.first_seen_at!=(m->>'first_seen_at')::timestamptz then
   raise exception 'Legacy identity changed: %',oldjob.id;
  end if;
  select * into newjob from public.team_jobs where url=m->>'canonical_url';
  if newjob.id is not null and newjob.first_seen_at<oldjob.first_seen_at then raise exception 'Canonical row is older'; end if;
  insert into public.team_workday_repair_backup(table_name,payload)
   select 'team_jobs',to_jsonb(j) from public.team_jobs j where url in (m->>'old_url',m->>'canonical_url');
  insert into public.team_workday_repair_backup(table_name,payload)
   select 'team_job_observations',to_jsonb(j) from public.team_job_observations j where url in (m->>'old_url',m->>'canonical_url');
  insert into public.team_workday_repair_backup(table_name,payload)
   select 'team_job_notifications',to_jsonb(j) from public.team_job_notifications j where url in (m->>'old_url',m->>'canonical_url');
  insert into public.team_workday_repair_backup(table_name,payload)
   select 'team_applications',to_jsonb(j) from public.team_applications j where job_url in (m->>'old_url',m->>'canonical_url');
  if exists(select 1 from public.team_applications a join public.team_applications b on a.user_id=b.user_id and a.company=b.company
    where a.job_url=m->>'old_url' and b.job_url=m->>'canonical_url') then raise exception 'Application merge requires review'; end if;
  update public.team_applications set job_url=m->>'canonical_url' where job_url=m->>'old_url';
  insert into public.team_job_observations(source_id,url,is_active,observed_at)
   select source_id,m->>'canonical_url',is_active,observed_at from public.team_job_observations where url=m->>'old_url'
   on conflict(source_id,url) do update set observed_at=greatest(team_job_observations.observed_at,excluded.observed_at);
  delete from public.team_job_observations where url=m->>'old_url';
  insert into public.team_job_observations(source_id,url,is_active,observed_at)
   values(m->>'source_id',m->>'canonical_url',coalesce(newjob.is_active,oldjob.is_active),coalesce(newjob.last_seen_at,oldjob.last_seen_at))
   on conflict(source_id,url) do nothing;
  insert into public.team_job_notifications(url,status,delivered_at)
   select m->>'canonical_url',status,delivered_at from public.team_job_notifications where url=m->>'old_url'
   on conflict(url) do update set status=case when team_job_notifications.status='delivered' or excluded.status='delivered' then 'delivered' else team_job_notifications.status end,
    delivered_at=least(team_job_notifications.delivered_at,excluded.delivered_at);
  delete from public.team_job_notifications where url=m->>'old_url';
  if newjob.id is not null then delete from public.team_jobs where id=newjob.id; end if;
  update public.team_jobs set url=m->>'canonical_url',source_id=m->>'source_id',posted_at=m->>'posted_at',
    title=coalesce(newjob.title,oldjob.title),location=coalesce(newjob.location,oldjob.location),
    description=coalesce(newjob.description,oldjob.description),salary=coalesce(newjob.salary,oldjob.salary),
    last_seen_at=coalesce(newjob.last_seen_at,oldjob.last_seen_at),scraped_at=coalesce(newjob.scraped_at,oldjob.scraped_at),
    is_active=coalesce(newjob.is_active,oldjob.is_active),closed_at=coalesce(newjob.closed_at,oldjob.closed_at),
    detail_status=coalesce(newjob.detail_status,oldjob.detail_status),detail_checked_at=coalesce(newjob.detail_checked_at,oldjob.detail_checked_at)
   where id=oldjob.id;
  insert into public.team_job_url_aliases(old_url,canonical_url,original_job_id) values(m->>'old_url',m->>'canonical_url',oldjob.id);
 end loop;
 if exists(select 1 from public.team_jobs where url ~ '^https://[^/]+\.myworkdayjobs\.com/job/') then raise exception 'Malformed Workday URLs remain'; end if;
end $repair$;
alter table public.team_jobs drop constraint if exists team_workday_site_required;
alter table public.team_jobs add constraint team_workday_site_required check(url !~ '^https://[^/]+\.myworkdayjobs\.com/job/');
notify pgrst,'reload schema';
commit;
'''

def main():
    project=os.environ['SUPABASE_PROJECT_REF'];assert project=='alxgteasytezekyunyjk'
    plan=json.loads(Path('workday_repair_plan.json').read_text())
    assert len(plan)==47 and len({r['old_url'] for r in plan})==47
    query=SQL.replace('__PLAN__',"'"+json.dumps(plan).replace("'","''")+"'")
    r=requests.post(f'https://api.supabase.com/v1/projects/{project}/database/query',
        headers={'Authorization':'Bearer '+os.environ['SUPABASE_ACCESS_TOKEN']},json={'query':query},timeout=90)
    if not r.ok:raise RuntimeError(f'Atomic repair failed HTTP {r.status_code}: {r.text[:1200]}')
    print('Atomic Workday repair committed: 47 aliases; original IDs and first-seen preserved.')

if __name__=='__main__':main()
