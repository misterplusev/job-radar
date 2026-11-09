-- Independent namespace; public read-only jobs/health, service-only writes.
create table if not exists public.team_jobs (
 id bigserial primary key, league text not null, team text not null, company text not null,
 title text not null, url text not null unique, location text, description text,
 platform text, ats text, posted_at text, first_seen_at timestamptz not null default now(),
 last_seen_at timestamptz, scraped_at timestamptz, is_active boolean not null default true,
 closed_at timestamptz, logo_url text, source_id text, salary text, detail_status text,
 detail_checked_at timestamptz
);
create index if not exists team_jobs_active_idx on public.team_jobs(is_active);
create index if not exists team_jobs_first_idx on public.team_jobs(first_seen_at desc);
create or replace function public.team_keep_first_seen() returns trigger language plpgsql as $$
begin new.first_seen_at=old.first_seen_at; return new; end; $$;
drop trigger if exists team_keep_first_seen on public.team_jobs;
create trigger team_keep_first_seen before update on public.team_jobs for each row execute function public.team_keep_first_seen();
create table if not exists public.team_job_observations (
 id bigserial primary key, source_id text not null, url text not null,
 is_active boolean not null, observed_at timestamptz, unique(source_id,url)
);
create table if not exists public.team_job_scrape_runs (
 id bigserial primary key,run_id uuid not null,provider text not null,source text,
 platform text,status text not null,job_count integer not null default 0,duration_ms integer,
 error_summary text,trigger_source text,created_at timestamptz not null default now(),unique(run_id,provider)
);
create index if not exists team_job_runs_date_idx on public.team_job_scrape_runs(created_at desc);
create table if not exists public.team_job_notifications (
 id bigserial primary key,url text not null unique,status text not null,
 delivered_at timestamptz
);
create table if not exists public.team_applications (
 id bigserial primary key,user_id uuid not null default auth.uid() references auth.users(id),
 company text not null,job_url text not null,job_title text,status text not null default 'applied',
 applied_at timestamptz not null default now(),updated_at timestamptz not null default now(),notes text,
 unique(user_id,company,job_url)
);
alter table public.team_jobs enable row level security;
alter table public.team_job_observations enable row level security;
alter table public.team_job_scrape_runs enable row level security;
alter table public.team_job_notifications enable row level security;
alter table public.team_applications enable row level security;
drop policy if exists team_jobs_read on public.team_jobs;
create policy team_jobs_read on public.team_jobs for select to anon,authenticated using(true);
drop policy if exists team_runs_read on public.team_job_scrape_runs;
create policy team_runs_read on public.team_job_scrape_runs for select to anon,authenticated using(true);
drop policy if exists team_applications_owner on public.team_applications;
create policy team_applications_owner on public.team_applications for all to authenticated using(user_id=auth.uid()) with check(user_id=auth.uid());
grant select on public.team_jobs,public.team_job_scrape_runs to anon,authenticated;
grant all on public.team_jobs,public.team_job_scrape_runs,public.team_job_observations,public.team_job_notifications,public.team_applications to service_role;
grant select,insert,update,delete on public.team_applications to authenticated;
grant usage,select on sequence public.team_applications_id_seq to authenticated;
grant usage,select on all sequences in schema public to service_role;
create or replace view public.team_jobs_with_applied with (security_invoker=true) as
 select j.*,a.id is not null as is_applied,a.status as applied_status,a.applied_at
 from public.team_jobs j left join public.team_applications a on a.job_url=j.url and a.company=j.company and a.user_id=auth.uid();
grant select on public.team_jobs_with_applied to authenticated;
notify pgrst, 'reload schema';
