# Sportsbook delivery correction and recovery evidence

Recorded November 11, 2026, 02:25 Pacific. This supersedes earlier claims that sportsbook had no persistent notification recovery. It does not claim that the deployed watchdog source has been inspected.

## Corrected finding

Sportsbook is delivering real job alerts. The user supplied a November 10, 6:10 p.m. Pacific Discord receipt containing Hard Rock Bet's Salesforce Solution Architect and Novig's Head of Product Marketing. The two-embed message format and master-list logos match the versioned watchdog formatter. This is user-provided delivery evidence; no independent message-ID readback was available for that message.

The previous diagnosis examined the Hugging Face scraper's direct notifier and incorrectly generalized its lack of a durable queue to the entire system. The versioned Cloudflare watchdog also publishes jobs and already retains a persistent KV delivery cursor. The Cloudflare management API returning HTTP 403 concerns the inspector's access; it does not demonstrate failure of the running Worker or its Discord webhook. The request for access was for deployed-source inspection, not to restore a proven outage.

## What the existing code actually does

Reference: private repository `misterplusev/sportsbook-jobs-dashboard`, branch `prod/sportsbook-jobs`, revision `f055bd71fc2e38631eebc052d00e381ca37b98ae`, `runtime/cloudflare/watchdog/src/index.js`, lines 274–317.

- `runCron` calls both the health check and `announceNewJobs`.
- `announceNewJobs` reads KV key `last_notified_first_seen_at`, queries newer active jobs and sends at most ten embeds.
- It advances that cursor only after Discord accepts the message. A failed send retains the cursor so the next invocation can retry.
- An absent cursor seeds to the latest discovery timestamp without dumping historical jobs.

An offline test of the unchanged reference source forced a send failure, then success, then another invocation. The failed send preserved the cursor; the next attempt delivered both jobs; the third attempt delivered none. No network requests or Discord messages were made by this test. [Test receipt](20261111_sportsbook_recovery/existing_watchdog_recovery_test.json).

A separate eleven-job fixture with identical discovery timestamps reproduces a narrower defect: the first ten are delivered, then `first_seen_at=gt.<timestamp>` skips the eleventh. This is a repository-code defect, not evidence that a real production job was missed. The public `/version` behavior differs from the versioned implementation, so repository/deployment parity cannot be assumed. No timestamp-cursor repair has been deployed.

## Current live evidence

[Read-only runtime inspection](20261111_sportsbook_recovery/current_runtime_health.json), 02:20 Pacific: all four modules healthy, zero warnings. Robotics completed its 02:09 slot; tech completed its 01:37 slot; teams completed its 01:23 slot. Sportsbook completed its previous scheduled scrape at November 10, 17:04 Pacific, with no provider errors/timeouts; its next normal slot was November 11, 03:00 Pacific. Twenty-three sources returned jobs; Chalkboard returned an empty result. The source counts do not themselves prove Discord delivery.

Earlier Discord evidence remains valid: robotics and tech production webhooks passed existing-message readback; teams' destination and acknowledged delivery records agreed. Sportsbook now has the user's actual message receipt in addition to healthy runtime and valid operator-store webhook metadata. The prior [Discord wiring audit](2026-11-11%200145%20Discord%20Wiring%20Verification%20and%20Documentation%20Status.md) preserves those dates and evidence types. All 124 teams and all eight browser views were verified in the earlier complete coverage report; they were not rechecked by browser in this task.

## Exactly what changed

**Production publisher unchanged.** No sportsbook source or secret was deployed or replaced, no publisher was disabled, and no schedule, KV cursor, job/application row or delivery acknowledgement was altered. No Discord test or job message was sent by this task. [Fresh revision and empty-table receipt](20261111_sportsbook_recovery/correction_state.json) confirms the production branch remains `f055bd71fc2e38631eebc052d00e381ca37b98ae` and the Space remains `95db2a29832416e9fc86df276b5e7fce7de88314`.

**One preparatory database change was applied.** An empty `sportsbook_job_notifications` table and its helper functions were added before the broader diagnosis was corrected. No production code consumes it, no backlog was inserted, and a later exact-count read confirmed zero rows. The complete [DDL](20261111_sportsbook_recovery/applied_outbox_schema.sql) and [migration receipt](20261111_sportsbook_recovery/schema_receipt/migration-receipt.json) document it. Five rollback-only database tests passed. [Schema workflow](https://github.com/misterplusev/job-radar/actions/runs/42999809617).

**Replacement code is local and deferred.** `D:\abet_ops\jobs_scrapers\20261111_sportsbook_recovery\source` contains an outbox candidate touching the scraper, launcher, bundle builder, watchdog, SQL and tests. Its Python suite passed 48 tests; this validates the candidate, not its necessity or a deployed replacement. The candidate watchdog removes the older announcer; it must not be deployed without inspecting the actual Worker and deciding whether the narrower cursor fix is sufficient. The [staged-file inventory](20261111_sportsbook_recovery/staged_files.json) identifies hashes and line counts. Existing unrelated changes in `D:\abet\sportsbook-jobs-runtime` were preserved.

**Documentation corrected.** The entry point, architecture, operations runbook, earlier audit and database dictionary now distinguish the HF sender, watchdog recovery, observed delivery and undeployed preparation. Historical receipts remain intact. Production scraper workflows were not changed by the documentation commit.

## Remaining inspection requirement

Both available management credentials returned HTTP 403 for source/settings/schedules in the sportsbook Worker's Cloudflare account. [Sanitized result](20261111_sportsbook_recovery/watchdog_before/receipt.json); [GET-only audit workflow](https://github.com/misterplusev/sportsbook-jobs-dashboard/actions/runs/43000565540). Workflow success means the inspection ran, not that the account allowed it.

To finish deployed-code verification, an existing credential authorized for that Worker's account is needed. Read the live source, bindings, schedule and cursor before deciding on a minimal repair or any publisher cutover. Preserve delivery state and test timestamp ties, failed sends and repeat invocations. Until that access exists, the correct status is: **live delivery confirmed; ordinary recovery verified in versioned code; deployed-source parity and the timestamp edge case remain open.** The original request for fully verified recovery is therefore not complete. Do not infer an outage or request credential changes merely to make working notifications resume.
