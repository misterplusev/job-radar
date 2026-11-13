## Production reliability update — November 10, 2026

Cloudflare Durable Object alarms in `abet-jobs-scheduler` own dispatch for all four
job scrapers, each every 4 hours on its own UTC hour: robotics 00/04/08/12/16/20 at :09,
tech 01/05/… at :37, sports teams 02/06/… at :23, sportsbook 03/07/… at :00
(`runtime/cloudflare/worker.mjs` `MODULES`). GitHub Actions executes the first three and
a Hugging Face Space executes sportsbook; none has a timer of its own.
the old GitHub cron is removed to avoid two scheduler owners. The scheduler is
activated only after release verification. Health: https://abet-jobs-scheduler.abetscrape.workers.dev/health

Providers execute in bounded subprocesses and incomplete HTTP/pagination results
raise errors. Cleanup uses request-size-bounded batches and confirmed update counts.
Partial source runs preserve existing active jobs and produce a degraded manifest.
Notifications use an RLS-protected persistent queue; delivery is acknowledged after
Discord returns a message ID. Existing listings are not mass-replayed. Delivery is
at-least-once if acceptance succeeds but the acknowledgement is lost.

Run receipts are uploaded as `job-radar-receipt`, including
`data/runtime/latest_manifest.json`. Inspect provider completeness and delivery
totals, not just the workflow icon. The scheduler source and pause/rollback runbook
live in `misterplusev/job-radar/runtime/cloudflare` and its shared scraper docs.

# Robotics Job Radar

Production: employer careers / official ATS sources -> Python ingestion -> Supabase -> searchable board and Discord job alerts.

**Start here:** [shared architecture, operations and new-industry build guide](https://github.com/misterplusev/job-radar/tree/master/docs/job-scrapers). Verified November 10, 2026. Machine inventory and a read-only schedule/health checker are included there.

## Current production

- Repository default branch: `master`; workflow `.github/workflows/pipeline.yml`.
- Schedule: every 4 hours at :09 on UTC hours 00, 04, 08, 12, 16, 20, dispatched by the Cloudflare scheduler. No GitHub cron.
- Entry point: `python run.py ingest`; then `python run.py render --out out/dashboard.html` uploads a workflow artifact.
- Targets: `config/targets.json`; providers in `jobradar/providers/` include Greenhouse, Lever, Ashby, Amazon and Workday.
- Tables: `robotics_jobs`, `robotics_job_scrape_runs`, `robotics_applications`; view `robotics_jobs_with_applied` in the shared Supabase project.
- Board: [Robotics jobs](https://misterplusev.github.io/robotics-jobradar-board/). Its static frontend is a separate board repository; rendering the workflow artifact does not redeploy it.
- Secrets: `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `DISCORD_WEBHOOK_JOBS`; schema step uses `SUPABASE_ACCESS_TOKEN` and `SUPABASE_PROJECT_REF`.

Robotics relevance filtering applies to notifications; collected employer jobs remain searchable. New-job alerts use database URL deduplication. This module does not have the teams module's durable notification queue; an alert failure after a successful upsert may not retry on the next run. See the shared architecture for actual pacing and recovery limitations.

## Working on the code

Read the workflow, current provider source, module schema and applicable local instructions before running commands. `run.py ingest` can write production and send alerts when secrets are present; it is not a read-only inspection. `db/apply_schema.py` applies SQL. Preserve local uncommitted work.

Optional scoring, LLM judging and resume/cover-letter generation code remains in this repository. Those commands are separate from the scheduled ingestion workflow and are not automatically run in production. A generated document or board checkbox is not an application submission.

This repository is public. Keep credentials, personal skills matrices, resumes and private application records out of new commits and public artifacts. Never put service-role keys in a frontend. Preserve employer evidence and immutable discovery dates.

The separate [sports teams module](sports_teams/README.md) shares this repository but has its own workflow, table namespace, publisher and board.
