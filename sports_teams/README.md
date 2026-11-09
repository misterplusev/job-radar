# Sports teams jobs scraper

Production matches the robotics/tech jobs pipeline: GitHub Actions -> shared
Supabase database -> live searchable board and deduplicated Discord publisher.

- Repository: https://github.com/misterplusev/job-radar/tree/master/sports_teams
- Workflow: `.github/workflows/sports-teams.yml` in that repository.
- Schedule: hourly at minute 23 UTC; one run at a time, 45-minute timeout.
- Board: https://misterplusev.github.io/job-radar/
- Health: https://misterplusev.github.io/job-radar/health.json
- Storage: `team_jobs`, `team_job_observations`, `team_job_scrape_runs`,
  `team_job_notifications`, owner-scoped `team_applications`.

`python run.py ingest` uses Supabase when configured. `python run.py scrape all`
is the read-only source proof; `python run.py render` exports the active cache.
The scheduled workflow runs `pipeline_local.py --cloud` directly.
`pipeline_local.py` is the historical filename, not a local-only runtime.

Teamwork follows real pagination links and discovers NFL/NHL/MLB/NBA portals.
Workday, Greenhouse, ADP, UKG, the NBA frontend and official 49ers links are
supported. Failures preserve existing jobs; only verified complete observations
can retire missing jobs. First-seen dates are immutable across upserts/rebuilds.
Full details refresh in bounded batches (250 pages/run, 15-minute detail budget).
The health receipt exposes remaining details and every source failure.
Some Teamwork detail pages reject automated requests with HTTP 403; their
listings remain visible, prior descriptions are preserved, and failures are
reported without bypassing the site's restrictions.

Notifications remain parked (`NOTIFICATIONS_PAUSED: '1'` in the workflow) under
the pre-existing operator hold. Tests mock delivery; no messages were sent.
Normal delivery acknowledges only successful chunks; old unannounced listings
are not represented as newly posted. Existing delivery history is in Supabase.

Tests: `python -m unittest discover -p "test_*.py"` (33 regression checks).
`node test_worker.mjs` covers the retired relay experiment (7 safety checks).
The local operator helper `verify_deployment.py` checks board/database counts, duplicate URLs and
preservation of the original observation dates without modifying production.

Local operator deployment helper: `deploy_github.py`; secrets travel via GitHub secret stdin.
The shared database migration was applied in an isolated one-time workflow;
the original robotics and tech pipelines were not modified.
After production certification on 2026-11-09, the old Windows scrape/publish
tasks were exported to the local backup and disabled. GitHub Actions owns
the recurring schedule; do not re-enable the Windows tasks alongside it.

The Hugging Face/Cloudflare experiment is retired: HF could not reach Teamwork
or its relay reliably. The sportsbook launcher and Dockerfile were restored
byte-for-byte from the pre-change backup. Those experiment files remain here
for audit/rollback and are not the production sports teams scheduler.

Application marks on the board are private to the browser; they do not submit
applications. Authenticated database application records have owner-scoped RLS.
This does not replace the job search's Markdown application tracker.
