# Sports teams jobs scraper

**Shared documentation:** [architecture, operations and new-industry build guide](https://github.com/misterplusev/job-radar/tree/master/docs/job-scrapers). Verified November 10, 2026; includes a machine inventory and read-only checker. The November 11 repair moved dispatch to the shared Cloudflare alarm scheduler; see the shared repair receipt for observed runs and remaining coverage gaps.

Production matches the robotics/tech jobs pipeline: GitHub Actions -> shared
Supabase database -> live searchable board and deduplicated Discord publisher.

- Repository: https://github.com/misterplusev/job-radar/tree/master/sports_teams
- Workflow: `.github/workflows/sports-teams.yml` in that repository.
- Schedule: Cloudflare Durable Object alarms, hourly at minute 23 UTC; GitHub Actions executes one run at a time with a 45-minute timeout. No GitHub cron remains.
- Board: https://misterplusev.github.io/job-radar/
- Health: https://misterplusev.github.io/job-radar/health.json
- Team-by-team coverage: https://misterplusev.github.io/job-radar/coverage.html
- Storage: `team_jobs`, `team_job_observations`, `team_job_scrape_runs`,
  `team_job_notifications`, owner-scoped `team_applications`.

`python run.py ingest` uses Supabase when configured. `python run.py scrape all`
is the read-only source proof; `python run.py render` exports the active cache.
The scheduled workflow runs `pipeline_local.py --cloud` directly.
`pipeline_local.py` is the historical filename, not a local-only runtime.

Production uses only the 124-team organization registry. Teamwork follows real
pagination on those exact employer boards; broad league discovery and old job
URLs cannot add production sources.
Workday, Greenhouse, ADP, UKG, the NBA frontend and official 49ers links are
supported, alongside Dayforce, Paycor, Paylocity, Paycom, BambooHR, Lever,
Jobvite, ClearCompany, ApplicantPro, Hireology, Hirebridge, iCIMS and official
team-specific listing pages. Failures preserve existing jobs; only verified complete observations
can retire missing jobs. First-seen dates are immutable across upserts/rebuilds.
Full details refresh in bounded batches (250 pages/run, 15-minute detail budget).
The health receipt exposes remaining details and every source failure.
Some Teamwork detail pages reject automated requests with HTTP 403; their
listings remain visible, prior descriptions are preserved, and failures are
reported without bypassing the site's restrictions.

Normal individual alerts are enabled. Scrapes queue URLs new to the database,
matching the other jobs scrapers. Successful chunks are acknowledged immediately;
failed chunks remain pending. Existing delivery history is preserved in Supabase.
The explicit recovery option can recover missed individual alerts from paused
scrapes, restricted to jobs observed on the configured organization sources.

The official registry contains all 124 NFL/NBA/MLB/NHL teams. Coverage is computed
from the current run, not the number of sources. A successful source does not
imply every alternate link works; blocked and missing routes remain visible.
Shared ownership boards retain the actual parent business name.

Normal publishing uses `--limit 0`: all eligible new jobs, five embeds per message,
with rate-limit pacing and a 10-minute delivery budget. Each successful chunk is
acknowledged immediately; unsent jobs remain queued. There is no summary or
20-job cap. Employer posting dates remain distinct from discovery dates.

Tests: `python -m unittest discover -p "test_*.py"`.
`node test_worker.mjs` covers the retired relay experiment (7 safety checks).
The local operator helper `verify_deployment.py` checks board/database counts, duplicate URLs and
preservation of the original observation dates without modifying production.

Local operator deployment helper: `deploy_github.py`; secrets travel via GitHub secret stdin.
The shared database migration was applied in an isolated one-time workflow;
the original robotics and tech pipelines were not modified.
After production certification on 2026-11-09, the old Windows scrape/publish
tasks were exported to the local backup and disabled. Cloudflare alarms own
the recurring schedule; do not re-enable the Windows tasks alongside it.

The Hugging Face/Cloudflare experiment is retired: HF could not reach Teamwork
or its relay reliably. The sportsbook launcher and Dockerfile were restored
byte-for-byte from the pre-change backup. Those experiment files remain here
for audit/rollback and are not the production sports teams scheduler.

Application marks on the board are private to the browser; they do not submit
applications. Authenticated database application records have owner-scoped RLS.
This does not replace the job search's Markdown application tracker.

Current proof (November 11): 152/152 source checks and 124/124 official career-route links proved. Bulls, Clippers and Bucks were verified through their rendered official pages, with exact configured-employer matching. Composite health is healthy. All eight standalone/dashboard views passed real browser checks. See [the public screenshots and receipts](https://misterplusev.github.io/job-radar/verification-20261111/) and the shared complete verification report; this is dated evidence, not a future uptime guarantee.
