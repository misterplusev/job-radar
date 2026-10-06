-- ============================================================
-- Job Radar (Robotics Jobs module) — INDEPENDENT schema
-- Mirrors the sportsbook jobs module exactly, robotics namespaced
-- so it never collides with public.jobs in the same project.
-- Applied by scripts/run_migration.py (Management API) and idempotent.
-- ============================================================

-- 1) Robotics jobs (sportsbook jobs shape: upsert on_conflict=company,url)
create table if not exists public.robotics_jobs (
  id              bigserial primary key,
  company         text not null,
  title           text not null,
  url             text not null,
  location        text,
  description     text,
  is_active       boolean not null default true,
  last_seen_at    timestamptz,
  scraped_at      timestamptz,
  ats             text,
  posted_at       text,
  closed_at       timestamptz,
  source_payload  jsonb,
  unique (company, url)
);

create index if not exists idx_robotics_jobs_company on public.robotics_jobs(company);
create index if not exists idx_robotics_jobs_url on public.robotics_jobs(url);
create index if not exists idx_robotics_jobs_is_active on public.robotics_jobs(is_active);
create index if not exists idx_robotics_jobs_posted_at on public.robotics_jobs(posted_at desc);

-- 2) Applications tracker (sportsbook applications shape)
create table if not exists public.robotics_applications (
  id          bigserial primary key,
  company     text not null,
  job_url     text not null,
  job_title   text,
  status      text not null default 'applied',  -- applied | interviewing | rejected | offer | archived
  applied_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now(),
  notes       text,
  unique (company, job_url)
);

create index if not exists idx_robotics_applications_company on public.robotics_applications(company);
create index if not exists idx_robotics_applications_applied_at on public.robotics_applications(applied_at desc);

create or replace function public.touch_robotics_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

drop trigger if exists trg_robotics_applications_touch on public.robotics_applications;
create trigger trg_robotics_applications_touch
before update on public.robotics_applications
for each row execute function public.touch_robotics_updated_at();

-- 3) Scrape-run telemetry (sportsbook job_scrape_runs shape)
create table if not exists public.robotics_job_scrape_runs (
  id             bigserial primary key,
  provider       text,
  status         text,
  job_count      int not null default 0,
  trigger_source text,
  error_summary  text,
  created_at     timestamptz not null default now()
);

create index if not exists idx_robotics_job_scrape_runs_provider on public.robotics_job_scrape_runs(provider);

-- 4) RLS: dashboard reads robotics_jobs + scrape runs live with the anon key
--    (exact sportsbook dashboard behavior); service key bypasses RLS.
alter table public.robotics_jobs enable row level security;
alter table public.robotics_job_scrape_runs enable row level security;
alter table public.robotics_applications enable row level security;

drop policy if exists "anon read robotics_jobs" on public.robotics_jobs;
create policy "anon read robotics_jobs"
  on public.robotics_jobs for select
  to anon
  using (true);

drop policy if exists "anon read robotics_job_scrape_runs" on public.robotics_job_scrape_runs;
create policy "anon read robotics_job_scrape_runs"
  on public.robotics_job_scrape_runs for select
  to anon
  using (true);

-- 5) Dashboard join view (sportsbook parity)
create or replace view public.robotics_jobs_with_applied as
select
  j.*,
  (a.id is not null) as is_applied,
  a.status as applied_status,
  a.applied_at as applied_at
from public.robotics_jobs j
left join public.robotics_applications a
  on a.company = j.company and a.job_url = j.url;
