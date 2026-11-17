# Temporary production cadence and cloud validation

On November 16 Pacific, the user authorized reducing production cadence while proposed repairs are tested in cloud development. Production collection is now scheduled twice daily per module, eight scheduled runs total instead of 24. The Workday retry proposal failed live-source acceptance and remains undeployed. Existing source failures remain visible; this release does not establish full source health.

## Schedule and deployment

| Module | Previous interval | New interval | New UTC slots | Next slot after cutover |
|---|---|---|---|---|
| Robotics | 4 hours | 12 hours | 00:09, 12:09 | November 17 12:09 |
| Tech | 4 hours | 12 hours | 09:37, 21:37 | November 17 09:37 |
| Sports teams | 4 hours | 12 hours | 10:23, 22:23 | November 17 10:23 |
| Sportsbook | 4 hours | 12 hours | 11:00, 23:00 | November 17 11:00 |

Offsets deliberately retain the last four-hour slots during this cutover. The scheduler was paused at 00:09:52 UTC and enabled at 00:27:44 UTC on November 17. The already-dispatched robotics run was allowed to finish. All four recorded slot IDs and dispatch-attempt counts survived; the automatic scheduler did not replay any completed slot. Its five-minute heartbeat and public database circuit breaker remain active. No additional clock, recurring test, sender or database was created.

| Component | Exact released source | Hosted deployment |
|---|---|---|
| Cloudflare scheduler | `misterplusev/job-radar`, commit `e3f71e8e4383a39061b107a411c7bb43c1938d96`, `runtime/cloudflare/worker.mjs` | `abet-jobs-scheduler`, version `2b3d123d-3f56-4532-a556-efa7495fea36` |
| Sportsbook launcher | `misterplusev/sportsbook-jobs-dashboard`, branch `prod/sportsbook-jobs`, commit `dd0e212208694beef464bdb1f3be22455b0fa744`, `runtime/huggingface/launcher.py` | `abetco/sportsbook-jobs`, commit `7026b4a72b90747c13d6b94f426044f8bdf40cf8`, root `launcher.py`; runtime SHA verified RUNNING |
| Sportsbook freshness watchdog | Same sportsbook source commit, `runtime/cloudflare/watchdog/src/index.js` | `abet-jobs-watchdog`, version `1e2b674c-a595-4ac7-bcec-435ac1f81646` |

The scheduler changes four `everyHours` values from 4 to 12 and uses offsets 0, 9, 10 and 11. It retains completed sportsbook `success`, `degraded` and `failed` records when a runtime rebuild forgets its local slot. Degraded/failed errors remain visible. Regression coverage includes that restart behavior and the actual cutover timestamps.

The launcher changes `SCHEDULE_EVERY_HOURS` to 12 and `SCHEDULE_HOUR_OFFSET_UTC` to 11, keeping its 30-minute grace. It removes the `RUN_ON_BOOT` scrape path, so an obsolete variable cannot bypass the sole scheduler. Its existing keepalive thread remains; it does not collect jobs.

The watchdog changes only its fallback `STALE_SECONDS` from 6 hours to 14 hours. Normal schedule-aware health uses the launcher. Its two-hour monitoring cron and all existing bindings are preserved. No credentials, schemas, tables, retention policies, job senders, scraper collection functions or dashboard code changed in this release.

## Cloud proof

| Check | Result | Evidence |
|---|---|---|
| Cadence, slot deduplication, restart behavior, database breaker and delivery regression | 37 tests passed | [Scheduler cloud run](https://github.com/misterplusev/job-radar/actions/runs/43986301680) |
| Launcher cadence, freshness, authorization, no boot scrape | 17 tests passed | [Sportsbook cadence cloud run](https://github.com/misterplusev/sportsbook-jobs-dashboard/actions/runs/43986671578) |
| Watchdog health and notification regression with fake HTTP | All checks passed | Same sportsbook cadence run |
| Workday candidate, robotics root suite | 112 tests passed | [Robotics and teams development run](https://github.com/misterplusev/job-radar/actions/runs/43987203375) |
| Workday candidate, teams suite | 74 tests passed | Same robotics and teams development run |
| Workday candidate, tech root suite | 89 tests run, four scheduler-only tests skipped | [Tech development run](https://github.com/misterplusev/job-radar-tech/actions/runs/43987212695) |
| Workday candidate, sportsbook mocked retry/integrity tests | 15 tests passed | [Sportsbook development run](https://github.com/misterplusev/sportsbook-jobs-dashboard/actions/runs/43987221641) |
| Three real robotics Workday source reads | Failed: all three returned HTTP 429 after five attempts | Robotics and teams development run, `workday-development-proof` artifact |
| Three real sportsbook Workday source reads | Failed: BetMGM and Betway exhausted five attempts; Hard Rock Bet hit HTTP 429 and exhausted its source budget during a detail request | Sportsbook development run, `workday-development-proof` artifact |

Development used GitHub-hosted Linux runners, separate `codex/workday-validation-20261117` branches and read-only repository permissions. No production database or Discord credentials were passed to these workflows. The real-source probes only read career data; they import no production persistence or sender entrypoints. No local scraper, provider, database, browser or runtime test was launched.

The robotics probes received Cloudflare-served HTML 429 responses without `Retry-After`, including at offset 0, despite the longer waits. This proves the longer-backoff candidate did not restore access from that runner. It does not prove whether the upstream rule is IP reputation, another protection rule, or a conventional rate threshold. These failures happened without any Supabase request. More retries alone are not an accepted repair.

## Production verification and usage boundary

The sportsbook runtime rebuild correctly started no scrape automatically. Because its ephemeral runtime receipt was cleared, one recorded on-demand cloud verification was started at 00:28:24 UTC using the unchanged production scraper. It finished at 00:31:04 UTC in 156.9 seconds, published 676 jobs, and reported database persistence success. Coverage remained 19 successful providers, two empty providers and three errors: degraded. Its next scheduled run is November 17 11:00 UTC and its schedule health no longer reports a missed slot. This one-time validation is additional to the eight scheduled daily runs.

The existing single sportsbook sender was invoked once to drain the verification run's queue: [delivery run 43988650446](https://github.com/misterplusev/job-radar/actions/runs/43988650446) passed. At 00:32 UTC the ledger contained three pending and 40 delivered rows; at 00:34 UTC it contained 43 delivered rows and no pending rows. No synthetic Discord messages or second sender were used. This verifies the normal sender's completion and persisted acknowledgements; no separate Discord message-content readback was performed in this cadence release.

The scheduler is enabled and database checks answer successfully. Existing robotics, teams and sportsbook source failures are still reported. The latest tech production execution remains successful. This is a verified cadence change, not a claim that all source failures are fixed or that reliability has been established permanently.

At 00:25 UTC the database measured 287,386,771 bytes, about 287.4 decimal MB (274.1 MiB), against the documented 500 MB free-plan limit. Storage is not reclaimed by reducing cadence. Monthly data transfer has not been measured. Browser/dashboard reads, monitoring polls, other projects, bounded dispatch retries and operator verification runs remain additional consumers. Eight scheduled runs instead of 24 is a 66.7% reduction in scheduled collection runs, not a measured 66.7% reduction in every account's usage.

## Promotion gate and rollback

Keep the Workday changes on development branches. Before promotion, require deterministic tests, complete live collection from affected canonical career sources in the intended cloud runtime, source completeness/closure protection, bounded request count and duration, and sufficient sanitized diagnostic receipts. After a candidate passes, release one affected module at a time, verify its existing persistence and delivery path, then observe normal scheduled execution. Do not promote a retry candidate just because mocked tests pass, and do not hide failed providers to turn health green.

Cadence rollback is a coordinated operation: pause dispatch while allowing any active run to finish; restore/test matching scheduler and launcher cadence; review computed due slots against persisted receipts before enabling; verify the freshness thresholds match. A naive interval/offset change can replay older slots or start several overdue modules together. Do not clear Durable Object state, reset ledgers or delete histories. Preserve the no-boot-scrape and completed-degraded-slot safeguards unless a separately tested rollback requires otherwise.

Historical rollback references: scheduler before version `b019279e-a0d2-4a91-9e45-d61d69deb6fa`; sportsbook Space before commit `0541980aca0771d1554107050df4fc70a3543faf`; watchdog before version `2959c528-108b-4380-acec-52d2ad0f07d9`. These are evidence/recovery references, not instructions to blindly restore all three: the old launcher permits boot scrapes, and the old scheduler can replay degraded slots after a rebuild. An emergency cadence rollback must coordinate those behaviors and the health thresholds.

## Operator evidence and source inventory

Private evidence directory: `D:\abet_ops\jobs_scrapers\20261117_cadence_and_cloud_validation`. It contains exact before/after source copies, production/development Git receipts, deployment receipts, cloud logs and downloaded diagnostic artifacts. Credential values are excluded. Existing credential locations remain in the private operator appendix.

`cadence_file_inventory.json` records every changed production source/test file's hash, line count, changed hunks and Python AST definitions or JavaScript declaration scan. `job-radar-cadence.patch` and `sportsbook-jobs-dashboard-cadence.patch` contain the exact changes. Cloud workflows remain on development branches only; no test cron was added. Existing whole-system inventories retain their snapshot dates and are not presented as automatically current.
