# ABET job scrapers: runbook

**This is the one current document.** Last verified November 13, 2026, 04:50 UTC. Every figure in it was measured; the source and time are given where it matters. Anything not measured says so. Everything else in this folder with a date in its name is history; where it disagrees with this file, this file is right.

Four scrapers (robotics, tech, sports teams, sportsbook) collect job postings, write them to one shared free database, post new jobs to one Discord channel each, and feed one standalone board each plus one tab each in `abet-dashboard`. Free tiers only: nothing here may depend on a paid plan.

## 1. The system at a glance

| | Robotics | Tech | Sports teams | Sportsbook |
|---|---|---|---|---|
| Source repository | `misterplusev/job-radar` (`master`) | `misterplusev/job-radar-tech` (`master`) | `misterplusev/job-radar` (`master`), folder `sports_teams/` | `misterplusev/sportsbook-jobs-dashboard` (`prod/sportsbook-jobs`), private |
| Runs on | GitHub Actions, `pipeline.yml` | GitHub Actions, `pipeline.yml` | GitHub Actions, `sports-teams.yml` | Hugging Face Space (private), `launcher.py` |
| Entry point | `run.py ingest` | `run.py ingest` | `sports_teams/pipeline_local.py --cloud`, then `publish_teams.py --post --limit 0` | `scripts/scrape.py` |
| Started by | the scheduler | the scheduler | the scheduler | the scheduler |
| UTC hours | 00 04 08 12 16 20, at :09 | 01 05 09 13 17 21, at :37 | 02 06 10 14 18 22, at :23 | 03 07 11 15 19 23, at :00 |
| Jobs table | `robotics_jobs` | `tech_jobs` | `team_jobs` | `jobs` |
| Run receipts table | `robotics_job_scrape_runs` | `tech_job_scrape_runs` | `team_job_scrape_runs` | `job_scrape_runs` |
| Discord delivery ledger | `robotics_job_notifications` (stores Discord message IDs) | `tech_job_notifications` (stores Discord message IDs) | `team_job_notifications` | none yet (see section 8) |
| Discord poster | `jobradar/publish.py` in the run | `jobradar/publish.py` in the run | `sports_teams/publish_teams.py` in the run | Cloudflare Worker `abet-jobs-watchdog`, every 2 hours |
| Standalone board | `misterplusev.github.io/robotics-jobradar-board/` | `misterplusev.github.io/jobradar-tech-board/` | `misterplusev.github.io/job-radar/` | `sportsbook-jobs-dashboard.vercel.app` |
| `abet-dashboard` tab | Robotics | Tech | Sports Teams | Sportsbook |

Shared pieces:

- **Database:** Supabase project `abet-app-core`, Free plan, smallest compute: 411 MB of memory (project metrics endpoint, November 12 08:30 UTC). All four scrapers, all four boards and all four dashboard tabs read and write it through its REST API.
- **Scheduler:** Cloudflare Worker `abet-jobs-scheduler`. Source: `runtime/cloudflare/worker.mjs` in `job-radar`. It is the only clock. No workflow has a cron line and the sportsbook launcher has no timer.
- **Boards and dashboard tabs** read the jobs tables directly from the browser with the public key. If the REST API is down, every board and tab is blank even though the pages load.

## 2. How a run flows

1. Every 5 minutes the scheduler wakes (`tick()` in `worker.mjs`).
2. It reads one row from the database through the REST API (`databaseCheck()`). If that fails, it starts nothing and marks every module `held_database_down`.
3. For each module whose slot is due and has not run: GitHub modules get a `workflow_dispatch` with the slot as input (the run is titled `<prefix> <slot>`); sportsbook gets `POST /api/run?slot=<slot>` on its Space. At most two attempts per slot, 15 minutes apart. A slot never runs twice.
4. The run fetches postings from employers, then writes to the database:
   - robotics and tech (`publish()` in `jobradar/publish.py`): new and changed postings are written in full; unchanged postings get a ten-column refresh (`TOUCH_COLUMNS`). Change is detected by a hash stored in `source_payload.content_hash_v2`.
   - sports teams (`sports_teams/cloud_storage.py`): downloads `team_jobs`, merges, uploads.
   - sportsbook (`publish_to_supabase()` in `scripts/scrape.py`): upserts collected postings and closes only postings that were still open and have disappeared.
5. New postings are announced in Discord (see the table above) and recorded in the delivery ledger.
6. The scheduler records the result. `GET /health` on the scheduler shows every module's slot, status and last success.

## 3. Limits you must not cross

These are why the November 11–12 outage happened. `tests/test_guardrails.py` enforces the first five before every scrape.

| Rule | Why | Enforced by |
|---|---|---|
| One scheduler. No cron in any workflow, no timer in the launcher. | A second clock starts runs nobody can see or stagger. | `test_no_workflow_has_its_own_timer`; launcher test `test_launcher_has_no_timer_of_its_own` |
| No scraper more often than every 4 hours. | The database has 411 MB of memory. With three scrapers every hour its REST API was down November 11 21:18 to November 12 05:18 UTC and again November 12 15:09 to November 13 02:58 UTC. | `test_no_scraper_runs_more_often_than_every_four_hours` |
| No two scrapers in the same hour. | Two writers at once push the database into swap. | `test_no_two_scrapers_share_an_hour` |
| A scrape never applies schema or reloads the REST schema cache. Schema changes go through the manual `apply-schema.yml` only. | A schema reload on a busy small database left the REST API unable to load its schema. | `test_scrape_workflows_never_apply_schema` |
| Unchanged postings get the light refresh; at most 1,500 first-time rewrites per run; one copy of each description. | Under the old code each run rewrote in full every row it collected. Rows collected per run, from the November 13 run receipts: robotics 17,608, tech 3,766, sports teams 2,247 (written twice per run). The duplicate copies were 184 MB of the 282 MB of description text in `robotics_jobs`, 77 of 109 MB in `tech_jobs` and 47 of 72 MB in `jobs` (measured November 13 03:25 UTC). | `test_backfill_stays_small_and_descriptions_are_stored_once`, `tests/test_write_volume.py` |
| The scheduler checks the database before starting anything. | During the outage every slot was still dispatched into a database that could not answer. | `test_scheduler_checks_the_database_before_starting_runs`; `runtime/cloudflare/test_guardrails.mjs` |
| Database under 500 MB. | Free plan limit. | `verify_all.py` reports it as a problem when over |
| Do not add columns or tables that store the description again, and do not select `description` in list queries. | Size and the 5 GB monthly data-transfer limit. | Review |

Free-tier limits are from each provider's documentation, read November 12, 2026. "Our use" is measured unless it says otherwise:

| Account | Limit | Our use |
|---|---|---|
| Supabase database size | 500 MB | See `verify_all.py` |
| Supabase data transfer | 5 GB a month | **Not measured.** It is shown only on the Supabase organization Usage page; the API does not return it |
| Supabase compute | smallest size, shared CPU | 411 MB of memory (metrics endpoint, November 12 08:30 UTC); one scraper per hour |
| GitHub Actions | free on public repositories; 2,000 minutes a month on private ones | Three public workflows. Run times measured November 13: robotics 6 min 1 s and 2 min 59 s, tech 1 min 51 s, sports teams 4 min 35 s |
| Cloudflare Workers | 100,000 requests a day | One scheduler tick every 5 minutes (code). Daily request count not measured |
| Hugging Face Space | free CPU Space | Six scheduled runs a day. Run times measured November 13: 177 s, 189 s, 196 s, 179 s |
| Discord | enforced by HTTP 429 with `retry_after`, which every sender obeys | 5 jobs per message, 2.1 seconds between messages (code) |

## 4. How to check that everything works

One command, read-only, safe at any time:

```
python D:\abet_ops\jobs_scrapers\tools\verify_all.py --save
```

It checks database health, the scheduler, each table with the exact query the dashboard tab sends, each standalone board and its data request, data freshness, the latest run receipts, the Discord delivery ledgers and database size. It ends with **All checks passed** or a numbered list of problems.

Places to look by hand:

| What | Where |
|---|---|
| Is the database up | Supabase dashboard, project `abet-app-core`. Table Editor shows every table live. |
| Scheduler state | `https://abet-jobs-scheduler.abetscrape.workers.dev/health` (HTTP 200 = healthy, 503 = something listed under `overdue`) |
| Robotics and teams runs | `github.com/misterplusev/job-radar/actions` |
| Tech runs | `github.com/misterplusev/job-radar-tech/actions` |
| Sportsbook runs | the Space's `/api/health` (private; `tools/deploy_space.py health`) |
| What reached Discord | `robotics_job_notifications`, `tech_job_notifications` (state, `delivered_at`, `discord_message_id`), `team_job_notifications` |

Reading the scheduler's statuses: `success`, `in_progress`, `awaiting_run` (asked, not yet visible), `deferred_running` (an earlier run is still going), `held_database_down` (circuit breaker), `failure`/`cancelled`/`degraded`/`failed` (the run ended badly; the next slot tries again), `error` (the scheduler could not reach GitHub or the Space).

Things that look wrong but are not:

- `team_job_notifications` has 773 `pending` rows (November 13 04:34 UTC). Sports teams only announces postings that are recent; older ones stay `pending` and are never sent.
- A sports-teams run is marked failed if any single team source fails, even though everything else was saved and announced. Check the run log for `[SOURCE] ... fail`.
- After a failed slot the scheduler keeps showing that failure until the module's next slot, even if someone ran it successfully by hand in between. `last_success` is the field to trust.

## 5. Operating it

All commands are in `D:\abet_ops\jobs_scrapers\tools\` and read credentials from the local credential files; none prints a secret.

| Task | Command |
|---|---|
| Pause every scraper | `python jobs_ops.py sched pause` |
| Resume | `python jobs_ops.py sched enable` |
| Scheduler state | `python jobs_ops.py sched health` |
| Database health | `python jobs_ops.py supa health` |
| Restart the database (free; on November 13 the restart was requested at 02:52:44 UTC and all services were healthy at 02:58:11) | `python jobs_ops.py supa restart`, or Supabase dashboard → Project Settings → General → Restart project |
| Run one GitHub scraper now | `gh workflow run pipeline.yml -R misterplusev/job-radar --ref master -f scheduler_slot=manual-<time> -f trigger_source=operator` (tech: `-R misterplusev/job-radar-tech`; teams: `sports-teams.yml`) |
| Read-only SQL | `python jobs_ops.py sql "select ..."` |
| Back up a table to D: | `python backup_table.py <table> <folder>` |
| Deploy the scheduler | `python deploy_worker.py before`, then `python deploy_worker.py upload <worker.mjs from the commit> <commit>` |
| Deploy to the sportsbook Space | `python deploy_space.py before`, then `python deploy_space.py upload "<message>" <local file>=<path in Space>` |

Rules for changes:

1. Change code in the repository, run the tests, commit, push. Robotics, tech and teams run from `master` on their next slot; nothing else to deploy.
2. The scheduler and the Space do not deploy from a push. Deploy them from the exact committed file with the commands above; both commands verify the deployed file matches.
3. To change the schedule, edit `MODULES` in `worker.mjs` **and** `SCHEDULE_EVERY_HOURS` / `SCHEDULE_HOUR_OFFSET_UTC` in the sportsbook `launcher.py` (it only describes the cadence for its health report). Run `node --test runtime/cloudflare/test_scheduler.mjs runtime/cloudflare/test_guardrails.mjs` and `python -m unittest discover -s tests`. Section 3 still applies.
4. Deploying the Space restarts it, and it scrapes once on start (`RUN_ON_BOOT=1`). Deploy it when no other scraper is running.
5. Never run a manual scrape while another scraper is running. Check the scheduler first.

Scheduler settings (Cloudflare Worker secrets): `GITHUB_TOKEN`, `CONTROL_TOKEN` (for pause/enable/tick), `SPORTSBOOK_SPACE_URL`, `SPACE_READ_TOKEN`, `SPACE_RUN_TOKEN` (equals the Space's `RUN_TOKEN`), `SUPABASE_URL`, `SUPABASE_ANON_KEY` (the public key; turns the circuit breaker on), `ALERT_WEBHOOK` (optional Discord webhook; when set, one message after 15 minutes of bad health, a reminder every 6 hours, one on recovery).

## 6. When something is wrong

| Symptom | Likely cause | Do this |
|---|---|---|
| Boards and dashboard tabs are empty; pages load | REST API down | `jobs_ops.py supa health`. If `rest` or `db` is unhealthy for more than 15 minutes: `sched pause`, `supa restart`, wait for all three services healthy, `sched enable`. |
| Scheduler shows `held_database_down` | Circuit breaker; same as above | Same as above. Runs resume by themselves when the database answers. |
| One module `failure` once | An employer site or a transient error | Nothing; the next slot retries. Read the run log if it repeats. |
| One module failing every slot | A source parser broke or a secret expired | Read the run log (`[SOURCE]`, `[PUBLISH]`, `[DISCORD]` lines). Fix in the repository. |
| Scheduler `error: Space 401/403/404` | The Space is private and the read token or run token is wrong | Reset `SPACE_READ_TOKEN` / `SPACE_RUN_TOKEN` on the Worker and `RUN_TOKEN` on the Space. |
| Scheduler `scheduler heartbeat` overdue | The Worker's alarm stopped | `sched enable` re-arms it. |
| Jobs are saved but nothing reaches Discord | Webhook secret missing or rotated | Robotics/tech/teams: the workflow's Discord secret. Sportsbook: the `abet-jobs-watchdog` Worker. |
| Database over 500 MB | Something is storing more than it should | `verify_all.py` lists the largest tables. |

Do **not** respond to a slow database by retrying runs or raising the cadence. Pause first.

## 7. What happened on November 11–12, 2026

| UTC | Event |
|---|---|
| Nov 10 and before | GitHub run history shows robotics, tech and teams completing between 3 and 5 runs a day under hourly cron lines; sportsbook was scheduled 8 times a day. |
| Nov 11 05:17 | Commit `94ec045` moved dispatch to the Cloudflare scheduler **every hour** for robotics and tech (teams from 08:00), kept a schema-apply step in every run, and every run rewrote in full every row it collected (per run on November 13: robotics 17,608, tech 3,766, sports teams 2,247 written twice). |
| Nov 11 15:23 | First failed run. 21:18: the REST API could no longer load its schema; everything returned 503/504. |
| Nov 12 05:18 | Recovered on its own; failed again from 15:09. |
| Nov 12 19:34–19:50 | Seven fixes deployed (3-hour stagger, light writes, no per-run schema step, Padres parser, sportsbook active-only deactivation). The database was already down, so none could be proven. |
| Nov 13 02:52 | Scheduler paused, database restarted. 02:58: healthy. |
| Nov 13 02:59–03:36 | All four scrapers run and succeed. One scheduler for all four at a 4-hour cadence deployed, with the database circuit breaker. Duplicate description copies removed: database 1,296 MB → 909 MB. |

Root cause: three scrapers were put on a true hourly clock against a free database that until then had received 3 to 5 runs a day from each. Nothing limited cadence, nothing checked the database before starting runs, nothing alerted, and sportsbook kept a separate clock. Section 3 is the fix for each of those.

## 8. Known gaps

- **Sportsbook Discord posting is not on the standard path.** New sportsbook jobs are announced by a separate Cloudflare Worker (`abet-jobs-watchdog`, source in `runtime/cloudflare/watchdog/` of the sportsbook repository) in a different Cloudflare account, because the Hugging Face Space cannot reach Discord. By its source that Worker keeps a KV cursor (`last_notified_first_seen_at`, the last job it announced) but no per-job delivery record and no Discord message IDs; its deployed code and current behaviour have not been observed. The changes that move sportsbook onto the common sender are prepared and tested but not deployed: see `20261112_2100_common_sender_review\REVIEW.md` in the operator folder. They need access to that Cloudflare account so the old announcer can be switched off first; otherwise jobs would be announced twice. Table `sportsbook_job_notifications` exists and has 0 rows (November 13 04:35 UTC).
- **Three write implementations.** Robotics and tech share one design in two copies; teams and sportsbook each have their own. Scheduling, cadence, guardrails and health are now common. Merging the write and Discord code into one core is still to do.
- **Sports teams rewrites its whole table twice per run** (2,247 rows on November 13 03:03 UTC). Its run took 4 min 35 s with the database healthy throughout.
- **The sportsbook board downloads every description of every sportsbook job on each visit.** It should request descriptions on demand.
- **Four sportsbook tests fail** (`test_rebet_*`), and did before these changes. They reach the live Rebet page.
- **The scheduler's Space read token** is the existing Hugging Face token. A read-only token for just that Space would be tighter.
- The sportsbook Space's `BUNDLE_MANIFEST.json` no longer matches the deployed files; the Git commit named in each Space commit message is the source of truth.
