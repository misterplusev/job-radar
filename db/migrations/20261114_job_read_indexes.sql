-- One-time additive maintenance. Never run from a scrape or reload REST schema.
-- The old posted_at DESC indexes use NULLS FIRST and cannot satisfy these reads.
-- A short lock timeout prevents waiting behind a writer. No history is modified.
SET lock_timeout = '2s';
SET statement_timeout = '30s';
CREATE INDEX IF NOT EXISTS robotics_jobs_active_newest_idx ON public.robotics_jobs (posted_at DESC NULLS LAST, id DESC) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS tech_jobs_active_newest_idx ON public.tech_jobs (posted_at DESC NULLS LAST, id DESC) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS team_jobs_active_newest_idx ON public.team_jobs (posted_at DESC NULLS LAST, id DESC) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS jobs_active_newest_idx ON public.jobs (posted_at DESC NULLS LAST, id DESC) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS robotics_jobs_freshness_idx ON public.robotics_jobs (scraped_at DESC NULLS LAST);
CREATE INDEX IF NOT EXISTS tech_jobs_freshness_idx ON public.tech_jobs (scraped_at DESC NULLS LAST);
CREATE INDEX IF NOT EXISTS team_jobs_freshness_idx ON public.team_jobs (scraped_at DESC NULLS LAST);
CREATE INDEX IF NOT EXISTS jobs_freshness_idx ON public.jobs (scraped_at DESC NULLS LAST);
