-- Job Radar — Postgres/Supabase schema. Apply once in the Supabase SQL editor.
-- The local SQLite backend creates equivalent tables in code.

create table if not exists public.jobs (
  id                bigserial primary key,
  company           text not null,
  title             text not null,
  url               text not null unique,
  location          text,
  description        text,
  description_raw    text,
  description_clean  text,
  source            text,          -- e.g. greenhouse, lever, indeed
  provider_slug     text,          -- company slug within a source
  run_id            text,
  salary            text,
  remote            boolean,
  posted_at         timestamptz,
  is_active         boolean not null default true,
  scraped_at        timestamptz not null default now()
);
create index if not exists idx_jobs_company on public.jobs(company);
create index if not exists idx_jobs_scraped_at on public.jobs(scraped_at desc);

create table if not exists public.job_scores (
  id                bigserial primary key,
  job_id            bigint not null references public.jobs(id) on delete cascade,
  fit_score         int not null,
  archetype         text,
  matched_strengths jsonb,
  gaps              jsonb,
  lead_with         text,
  rationale         text,
  model             text not null,          -- 'heuristic' or the claude model id
  scored_at         timestamptz not null default now(),
  alerted           boolean not null default false,
  unique(job_id, model)
);
create index if not exists idx_job_scores_fit on public.job_scores(fit_score desc);

create table if not exists public.applications (
  id           bigserial primary key,
  company      text not null,
  job_url      text not null,
  job_title    text,
  status       text not null default 'draft',   -- draft|applied|interviewing|rejected|offer|archived
  fit_score    int,
  resume_path  text,
  cover_path   text,
  applied_at   timestamptz,
  updated_at   timestamptz not null default now(),
  notes        text,
  unique(company, job_url)
);

create table if not exists public.scrape_runs (
  id            bigserial primary key,
  run_id        text not null,
  source        text,
  provider_slug text,
  status        text not null,         -- success|error|publish_failed
  job_count     int not null default 0,
  error_summary text,
  started_at    timestamptz,
  finished_at   timestamptz not null default now()
);
