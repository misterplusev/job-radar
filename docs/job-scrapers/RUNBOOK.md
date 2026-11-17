# ABET job scrapers: runbook

## Browser compatibility evidence — November 17, 2026, 13:48 Pacific

The operator-approved single cloud browser session completed and closed cleanly: Boston Dynamics and BetMGM Workday both returned actual listing JSON and visible jobs (85 and23 advertised; first20 of each observed). This is first-page compatibility proof, not a complete scrape. An HTTP-only comparison still received explicit security challenges on seven Workday public pages. No production protocol change was deployed from those results.

A full-pagination candidate covering all19 configured Workday boards is prepared; its nine cloud safety fixtures passed, and its browser job was skipped. The first one-test exception is consumed. Another browser launch remains disabled pending an explicit extension under the existing stop rule. [Evidence, scripts, limits and remaining work](20261117_workday_source_repair/2026-11-17%201400%20Browser%20Evidence%20and%20Full%20Listing%20Candidate.md).

## Workday failure-handling repair — November 17, 2026, 03:39 UTC

The tested request-handling and data-integrity repair is released: main/teams `a47faad85f70bf3ea57c853973c1b4ad6bd768e5`, tech `3d5c1e89ecded51fff43dcaca253d65e08b47f98`, sportsbook `03e7f50efd72f94e70f131197d031bce52231320`, existing sportsbook HF Space `e43043fa23fc741eaaf71a902150f64dfab6f550`. Explicit upstream security challenges stop after one response; ordinary transient failures retain bounded retry/backoff and Retry-After handling. Incomplete sportsbook Workday details/pagination now fail the source instead of publishing a partial result. Structured redacted diagnostics are retained in bounded cloud files. Production cadence, database schema and one-sender design are unchanged.

**Full source recovery is NOT proven.** Actual Workday responses contain `CF-Mitigated: challenge` and a security-check page. The new live staging run proves one-request challenge handling and a successful unaffected source, not restored Workday access. Production remains every twelve hours and staging remains isolated. Release cloud suites: 329 passed, four explicitly skipped. The initial approved browser compatibility test has now completed as described above; it is not authorization for additional or recurring browser sessions.

[Exact scripts, full diffs, cloud runs, deployed versions, remaining access block and rollback](20261117_workday_source_repair/2026-11-17%200340%20Workday%20Repair%20Release%20and%20Remaining%20Access%20Block.md). This entry supersedes older statements that the entire Workday candidate is still unpromoted; it does not supersede their evidence that source access failed.

## Recurring isolated staging — November 17, 2026 UTC

A separate cloud staging controller is now enabled: [live status](https://abet-jobs-staging.abetscrape.workers.dev/). Robotics, tech and sports teams validate hourly; sportsbook every four hours, capped at 800 reserved private Actions minutes/month. It runs pinned candidate regression suites and bounded rotating live canaries, keeps its own SQLite-backed Durable Object state, and has no production database or Discord credentials. This is not a full Supabase clone or an all-source scrape every hour. Production remains every twelve hours.

[Staging operations, schema, source paths, budgets and rollback](20261117_recurring_cloud_staging/2026-11-17%200150%20Recurring%20Staging%20Operations.md); [build handoff](20261117_recurring_cloud_staging/2026-11-17%200113%20Staging%20Build%20Handoff.md). Current Workday access failures remain visible; the scoped handling repair above is released. One production clock and one isolated staging clock serve different environments; never let staging dispatch production pipelines.

## Temporary lower cadence from November 17 2026 UTC

Production now runs each scraper every 12 hours: eight scheduled collection runs per day instead of 24 (66.7% fewer). The Cloudflare Durable Object remains the only scheduler. UTC slots: robotics 00:09/12:09; tech 09:37/21:37; sports teams 10:23/22:23; sportsbook 11:00/23:00. The offsets preserve the last pre-change receipts and avoid replaying older slots during the cutover.

The sportsbook launcher reports the same 12-hour schedule with its existing 30-minute grace. It no longer starts a scrape on boot, even if an obsolete RUN_ON_BOOT variable is set. The scheduler preserves completed degraded/failed sportsbook slots across runtime restarts; they are not silently retried. The watchdog keeps its two-hour health-check timer and existing error reporting; its fallback stale threshold is 14 hours. This health-check timer is not a collection schedule.

The initial longer-backoff-only proposal failed its live-source probes and was not promoted at that checkpoint. The later 03:39 UTC release above adds explicit challenge handling, completeness protection and usable diagnostics, proven by scoped cloud regression tests and a live one-request challenge receipt. Source access remains unresolved. Passing retry simulations is not proof of restored source access. All runtime verification executes in the cloud; development workflows receive no production database or Discord credentials.

This reduces scheduled scrape load, not all account consumption. Public board/dashboard reads, monitoring traffic and other projects remain. Supabase monthly transfer is not measured, so this change does not guarantee every free-tier limit. The database measured 287,386,771 bytes at November 17 00:25 UTC. Current provider failures must remain visible.

Exact versions, cloud proof, release scope and rollback: [2026-11-17 0029 Temporary Cadence and Cloud Validation.md](2026-11-17%200029%20Temporary%20Cadence%20and%20Cloud%20Validation.md).


**This is the current operating document.** Cadence updated November 17, 2026 UTC (November 16 Pacific). Earlier recovery measurements below retain their observation dates. Measurements below retain their own observation dates; the November 14 recovery release has a separate linked evidence record. Older dated reports describe historical state and do not override this runbook.

Documentation audit, November 14 Pacific: [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) records current coverage, authoritative sources and remaining gaps. The [fresh source inventory](20261114_documentation_audit/source_inventory/README.md) and [fresh public database dictionary](20261114_documentation_audit/DATABASE.md) supersede the old November 10–13 inventories for their stated scopes. The old generated system reference is historical, not a current operating instruction.

Four scrapers (robotics, tech, sports teams, sportsbook) collect job postings, write them to one shared free database, post new jobs to one Discord channel each, and feed one standalone board each plus one tab each in `abet-dashboard`. Free tiers only: nothing here may depend on a paid plan.

**User requirement reaffirmed November 13, 2026: CLOUD ONLY.** Scrapers, runtime tests, test databases, schedules, persistence, and delivery must execute on cloud infrastructure. The user's machine must have no operational or recovery dependency. Local source inspection and read-only remote API administration are not runtime execution. Do not run local scraper/provider workers or a local PostgreSQL test harness, and do not present local tests as cloud verification. See `AGENTS.md`. The November 13 local shared-engine candidate is undeployed and does not establish production health.

## 1. The system at a glance

### November 14 recovery release

Workday page recovery is now on production `master`: robotics/teams repository `63c9ab92f96dab48592eba2463f13db60f2e2a5d`, tech repository `4a97502b24ccb74ee70584f0d74f6f2c6aa1c7cf`. Workday retries transient transport/429/selected 5xx/non-JSON responses at most three times, with bounded waits and the existing hard process deadline. A failed later page still fails the source; no partial result is treated as complete.

Eight additive read indexes were applied at 00:23 UTC. All eight production plans used their intended indexes without a Sort node; all four public active/newest queries returned rows. The measured robotics active/newest execution changed from 1,500.503 ms to 67.153 ms, and freshness from 82.364 ms to 5.119 ms. This is measured improvement, not a latency guarantee or proof of the sole historic timeout cause. Database size was 276,589,715 bytes; the new indexes total 2,301,952 bytes.

[Main cloud acceptance](https://github.com/misterplusev/job-radar/actions/runs/43658002855) passed 101 root tests, 72 sports-team tests, eight isolated PostgreSQL plan checks, three live Workday probes and all eight real hosted job views. [Tech acceptance](https://github.com/misterplusev/job-radar-tech/actions/runs/43657285357) completed 78 tests with four scheduler-only tests skipped. Actual Discord message readbacks passed for all four channels; no synthetic messages were sent. Browser evidence confirms working job data and filters, not that every employer has a working logo.

Release evidence, rollback and observation criteria: [November 14 recovery proof](2026-11-14%20Recovery%20Proof.md). Sustained seven-day acceptance is **pending**, not established by one passing run. Full release-verification scrapes use the existing cloud pipelines sequentially; they do not add a clock, sender, timer or cadence change.

Released production runs passed: [robotics 66/66 sources](https://github.com/misterplusev/job-radar/actions/runs/43658612837), [tech 13/13 sources](https://github.com/misterplusev/job-radar-tech/actions/runs/43658969565). Latest regular teams run 43647808774 had 152/152 listing-source routes and 124/124 team/official-career mappings verified. It also had **33 optional detail-enrichment HTTP 403 failures**; source success is not proof that every description was fetched. The scheduler at 00:40 UTC was healthy/unpaused with database OK and no overdue slots. Observation interval: November 15 00:40 to November 22 00:40 UTC; seven-day verdict remains pending.

| | Robotics | Tech | Sports teams | Sportsbook |
|---|---|---|---|---|
| Source repository | `misterplusev/job-radar` (`master`) | `misterplusev/job-radar-tech` (`master`) | `misterplusev/job-radar` (`master`), folder `sports_teams/` | `misterplusev/sportsbook-jobs-dashboard` (`prod/sportsbook-jobs`), private |
| Runs on | GitHub Actions, `pipeline.yml` | GitHub Actions, `pipeline.yml` | GitHub Actions, `sports-teams.yml` | Hugging Face Space (private), `launcher.py` |
| Entry point | `run.py ingest` | `run.py ingest` | `sports_teams/pipeline_local.py --cloud`, then `publish_teams.py --post --limit 0` | `scripts/scrape.py` |
| Started by | the scheduler | the scheduler | the scheduler | the scheduler |
| UTC hours | 00 12, at :09 | 09 21, at :37 | 10 22, at :23 | 11 23, at :00 |
| Jobs table | `robotics_jobs` | `tech_jobs` | `team_jobs` | `jobs` |
| Run receipts table | `robotics_job_scrape_runs` | `tech_job_scrape_runs` | `team_job_scrape_runs` | `job_scrape_runs` |
| Discord delivery ledger | `robotics_job_notifications` (Discord message ID per job) | `tech_job_notifications` (message ID per job) | `team_job_notifications` (message ID per job from November 13, 2026) | `sportsbook_job_notifications` (message ID, channel ID and webhook ID per job) |
| Discord sender (exactly one per module) | `jobradar/publish.py` in the run | the same file (identical copy) in the run | `sports_teams/publish_teams.py` in the run, sending through `send_discord_message()` in `jobradar/publish.py` | workflow `sportsbook-deliver.yml` in `job-radar` (`run.py deliver`, the same `jobradar/publish.py`), started by the scheduler after each sportsbook slot |
| Standalone board | `misterplusev.github.io/robotics-jobradar-board/` | `misterplusev.github.io/jobradar-tech-board/` | `misterplusev.github.io/job-radar/` | `sportsbook-jobs-dashboard.vercel.app` |
| `abet-dashboard` tab | Robotics | Tech | Sports Teams | Sportsbook |

Shared pieces:

- **Database:** Supabase project `abet-app-core`, Free plan, smallest compute: 411 MB of memory (project metrics endpoint, November 12 08:30 UTC). All four scrapers, all four boards and all four dashboard tabs read and write it through its REST API.
- **Scheduler:** Cloudflare Worker `abet-jobs-scheduler`. Source: `runtime/cloudflare/worker.mjs` in `job-radar`. It is the only production clock; the isolated staging controller cannot dispatch production pipelines. No workflow has a cron line and the sportsbook launcher has no timer.
- **Boards and dashboard tabs** read the jobs tables directly from the browser with the public key. If the REST API is down, every board and tab is blank even though the pages load.

## 2. How a run flows

1. Every 5 minutes the scheduler wakes (`tick()` in `worker.mjs`).
2. It reads one row from the database through the REST API (`databaseCheck()`). If that fails, it starts nothing and marks every module `held_database_down`.
3. For each module whose slot is due and has not run: GitHub modules get a `workflow_dispatch` with the slot as input (the run is titled `<prefix> <slot>`); sportsbook gets `POST /api/run?slot=<slot>` on its Space. At most two attempts per slot, 15 minutes apart. A slot never runs twice.
4. The run fetches postings from employers, then writes to the database:
   - robotics and tech (`publish()` in `jobradar/publish.py`): new and changed postings are written in full; unchanged postings get a ten-column refresh (`TOUCH_COLUMNS`). Change is detected by a hash stored in `source_payload.content_hash_v2`.
   - sports teams (`sports_teams/cloud_storage.py`): downloads `team_jobs`, merges, uploads.
   - sportsbook (`publish_to_supabase()` in `scripts/scrape.py`): upserts collected postings and closes only postings that were still open and have disappeared.
5. New postings are announced in Discord and recorded in the delivery ledger (section 2a).
6. The scheduler records the result. `GET /health` on the scheduler shows every module's slot, status and last success.

## 2a. Discord delivery: one system

Deployed November 13, 2026 (cutover 08:11:57–08:12:45 UTC).

- **One sender file.** `jobradar/publish.py` delivers for robotics, tech and sportsbook; the module is chosen with `JOBRADAR_MODULE`. The file is byte-identical in `misterplusev/job-radar` and `misterplusev/job-radar-tech`, and `tests/test_guardrails.py` in each pins its SHA-256, so a change to one copy stops every scrape until both match.
- **One send function.** `send_discord_message()` in that file is the only code that posts a job message. It requests `?wait=true`, waits out HTTP 429 using Discord's `retry_after`, makes at most 8 attempts, and raises unless Discord returns a message ID. Sports teams calls the same function from `sports_teams/publish_teams.py`.
- **One ledger contract.** A job gets a row before it is sent; the row is marked delivered only with the message ID Discord returned. Delivery is at-least-once: if a run dies between Discord accepting a message and the acknowledgement, the next run sends that message again.
- **Sportsbook.** Its scraper runs on a Hugging Face Space that cannot reach Discord. With Space variable `SPORTSBOOK_OUTBOX=1` the scraper writes one `pending` row per new job to `sportsbook_job_notifications` before saving the job, and never posts itself. The scheduler starts `sportsbook-deliver` once per finished sportsbook slot when its secret `SPORTSBOOK_DELIVERY` is `on`. Every new job is announced; there is no posting-age filter, matching the sender it replaced.
- **What each module still decides for itself:** which postings qualify (robotics and tech: dated within 14 days, robotics also its relevance filter; sports teams: its own recency rule in `publish_teams.py`, with its own ledger table shape), and the message wording.
- **The old sportsbook sender is removed.** Cloudflare Worker `abet-jobs-watchdog` (account `ac1a814d…`) no longer contains `announceNewJobs`; it keeps its health check, health alert, `/jobs-health` and relay. Its KV key `last_notified_first_seen_at` is left as the record of the last job it announced: `2026-11-13T03:18:31.445267+00:00`.
- **Never run two senders for one module.** To go back to the old sportsbook sender, follow the rollback in `20261112_2100_common_sender_review\REVIEW.md` section 6: switches off first, cursor handled, then the old Worker version (`dcf53ae2-24fc-4ad1-b08a-f7c6f6f5d3b5`).

## 3. Limits you must not cross

These are why the November 11–12 outage happened. `tests/test_guardrails.py` enforces the first five before every scrape.

| Rule | Why | Enforced by |
|---|---|---|
| One production scheduler. No cron in any workflow, no timer in the launcher. | A second clock starts runs nobody can see or stagger. | `test_no_workflow_has_its_own_timer`; launcher test `test_launcher_has_no_timer_of_its_own` |
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
| Hugging Face Space | free CPU Space | Two scheduled runs a day from November 17 UTC. Run times measured November 13: 177 s, 189 s, 196 s, 179 s |
| Discord | enforced by HTTP 429 with `retry_after`, which every sender obeys | 5 jobs per message, 2.1 seconds between messages (code) |

## 4. How to check that everything works

Run acceptance checks on the existing GitHub-hosted workflows, or inspect their latest results. These are manually dispatched checks with no cron and no new sender:

```
gh workflow run recovery-proof.yml -R misterplusev/job-radar --ref master
gh workflow run recovery-proof.yml -R misterplusev/job-radar-tech --ref master
```

The main workflow checks recovery behavior, isolated cloud PostgreSQL plans, three actual Workday sources, actual Discord messages, and the eight live board/dashboard views. Tech has its own regression and Discord readback workflow. Download `cloud-recovery-proof` artifacts for the JSON receipts and actual screenshots. They read production but do not publish jobs or send test messages. Run the main browser workflow once at a time; it closes its single browser in `finally` and has a 35-minute job ceiling.

These checks do not by themselves prove every employer was scraped on the latest production run. Also inspect the actual pipeline manifests/source receipts, Supabase run and delivery rows, scheduler health and database size. The old local `tools/verify_all.py` is a historical read-only audit utility with incomplete sportsbook ledger coverage; it is not the cloud acceptance command and must not be presented as full cloud verification.

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
- On November 13 at 06:27:43 UTC the scheduler reported `healthy` with all four modules having completed a scheduler-started run on the 4-hour cadence.
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
| Sportsbook sender switches | `python sportsbook_switches.py status`; `outbox on|off`; `delivery on|off` |
| Read the sportsbook Worker (code, timer, KV) | `python abetco_worker_read.py <receipts folder>` |
| Deploy or roll back the sportsbook Worker | `python deploy_watchdog.py before|upload|rollback …` |

Rules for changes:

1. Change code in the repository, run the tests, commit, push. Robotics, tech and teams run from `master` on their next slot; nothing else to deploy.
2. The scheduler and the Space do not deploy from a push. Deploy them from the exact committed file with the commands above; both commands verify the deployed file matches.
3. To change the schedule, edit `MODULES` in `worker.mjs` **and** `SCHEDULE_EVERY_HOURS` / `SCHEDULE_HOUR_OFFSET_UTC` in the sportsbook `launcher.py` (it only describes the cadence for its health report). Execute the scheduler Node tests and Python regression suite in GitHub-hosted CI, never locally. Section 3 still applies.
4. Deploying the Space restarts it. Since November 17, the launcher does **not** scrape on boot, even if an obsolete `RUN_ON_BOOT=1` variable exists. Deploy only when no production scraper is running; verify the running revision, cadence and health after restart. The next collection is started by the existing scheduler.
5. Never run a manual scrape while another scraper is running. Check the scheduler first.

Scheduler settings (Cloudflare Worker secrets): `GITHUB_TOKEN`, `CONTROL_TOKEN` (for pause/enable/tick), `SPORTSBOOK_SPACE_URL`, `SPACE_READ_TOKEN`, `SPACE_RUN_TOKEN` (equals the Space's `RUN_TOKEN`), `SUPABASE_URL`, `SUPABASE_ANON_KEY` (the public key; turns the circuit breaker on), `SPORTSBOOK_DELIVERY` (`on` starts the sportsbook delivery workflow after each sportsbook slot), `ALERT_WEBHOOK` (optional Discord webhook; when set, one message after 15 minutes of bad health, a reminder every 6 hours, one on recovery).

## 6. When something is wrong

| Symptom | Likely cause | Do this |
|---|---|---|
| Boards and dashboard tabs are empty; pages load | REST API down | `jobs_ops.py supa health`. If `rest` or `db` is unhealthy for more than 15 minutes: `sched pause`, `supa restart`, wait for all three services healthy, `sched enable`. |
| Scheduler shows `held_database_down` | Circuit breaker; same as above | Same as above. Runs resume by themselves when the database answers. |
| One module `failure` once | An employer site or a transient error | Nothing; the next slot retries. Read the run log if it repeats. |
| One module failing every slot | A source parser broke or a secret expired | Read the run log (`[SOURCE]`, `[PUBLISH]`, `[DISCORD]` lines). Fix in the repository. |
| Scheduler `error: Space 401/403/404` | The Space is private and the read token or run token is wrong | Reset `SPACE_READ_TOKEN` / `SPACE_RUN_TOKEN` on the Worker and `RUN_TOKEN` on the Space. |
| Scheduler `scheduler heartbeat` overdue | The Worker's alarm stopped | `sched enable` re-arms it. |
| Jobs are saved but nothing reaches Discord | Check eligible pending rows, sender run and webhook before assuming a credential issue | Robotics/tech/teams: their workflow and Discord secret. Sportsbook: `sportsbook-deliver.yml` in `job-radar`, its Discord secret and `sportsbook_job_notifications`; the watchdog is no longer a job sender. |
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
| Nov 13 02:59–03:36 | All four scrapers run and succeed. One scheduler for all four at a 4-hour cadence deployed, with the database circuit breaker. Duplicate description copies removed: database 1,296 MB → 909 MB at 03:39 UTC. |
| Nov 13 07:34 | Database 979,971,219 bytes: `abet_metrics` 727,007,232, `jobs_backup_20261007` 44,613,632, the four job tables 176,488,448 together. The job tables have grown since the 03:39 reading. |
| Nov 13 20:08 | `abet_metrics` emptied on the operator's instruction after the D: copy was matched against every live row. Database 994,929,811 -> 267,955,347 bytes. It was old monitoring data written by the Worker `abet-metrics-collector` until July 14, 2026; nothing read or wrote it. `jobs_backup_20261007` (44,613,632 bytes) remains. |

What the evidence shows:

- From November 11 the scheduler started robotics, tech and sports teams every hour. GitHub run history shows 3 to 5 completed runs a day for each before that.
- Logged row upserts by the robotics and tech production steps: 77,466 on November 10 and 312,957 on November 11 (robotics 66,261 → 249,184; tech 11,205 → 63,773). The schema-application step started 7 times on November 10 and 45 times on November 11. Counted from 59 workflow log archives; one tech run had no archive. Source: `D:\abet_ops\jobs_scrapers\20261112_usage_audit\historical_upsert_audit.json`.
- The database logs then show statement timeouts, the REST API unable to load its schema, and heavy swapping.
- The fixes deployed on November 12 at 19:34–19:50 UTC did not bring the database back; it answered again only after the scheduler was paused and the project restarted at 02:52 UTC on November 13. Subsequent initial recovery runs succeeded. November 14 then had two robotics Workday failures and intermittent query timeouts; the release note above records the targeted correction and current evidence.

What is not established: which single operation started the failure, and how much each one contributed. Read-only mode was never on (checked November 13 07:34 UTC) and the monthly data-transfer figure has not been measured, so "the free allowance ran out and Supabase shut it off" is **not** the diagnosis.

At the time nothing limited cadence, nothing checked the database before starting runs, nothing alerted, and sportsbook kept a separate clock. Section 3 addresses each of those.

## 8. Known gaps

- **Sports teams keeps its own queue and ledger shape.** It sends through the shared function and records message IDs, but which postings qualify is decided in `publish_teams.py` and its ledger is `team_job_notifications (url, status, delivered_at, discord_message_id)`, not the `(company, job_url, payload, state)` shape of the other three.
- **Two copies of the sender file.** Robotics and tech are separate repositories; the copies are held identical by the hash test, not by being one file.
- **Sports teams rewrites its whole table twice per run** (2,247 rows on November 13 03:03 UTC). Its run took 4 min 35 s with the database healthy throughout.
- **The sportsbook board downloads every description of every sportsbook job on each visit.** It should request descriptions on demand.
- **Four sportsbook tests fail** (`test_rebet_*`), and did before these changes. They reach the live Rebet page.
- **The scheduler's Space read token** is the existing Hugging Face token. A read-only token for just that Space would be tighter.
- The sportsbook Space's `BUNDLE_MANIFEST.json` no longer matches the deployed files; the Git commit named in each Space commit message is the source of truth.
