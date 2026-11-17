# ABET job scrapers — start here

Latest release: [November 17 Workday handling repair and remaining access block](20261117_workday_source_repair/2026-11-17%200340%20Workday%20Repair%20Release%20and%20Remaining%20Access%20Block.md). The request-handling, diagnostics and incomplete-source fixes are deployed after329 passing cloud regression tests (four explicit skips). Complete Workday access is still unresolved. Exact code diffs, source inventory, tests, deployment receipts and rollback are in that package; do not interpret the release as all-source recovery.

## Recurring isolated staging — November 17, 2026 UTC

A separate cloud staging controller is now enabled: [live status](https://abet-jobs-staging.abetscrape.workers.dev/). Robotics, tech and sports teams validate hourly; sportsbook every four hours, capped at 800 reserved private Actions minutes/month. It runs pinned candidate regression suites and bounded rotating live canaries, keeps its own SQLite-backed Durable Object state, and has no production database or Discord credentials. This is not a full Supabase clone or an all-source scrape every hour. Production remains every twelve hours.

[Staging operations, schema, source paths, budgets and rollback](20261117_recurring_cloud_staging/2026-11-17%200150%20Recurring%20Staging%20Operations.md); [build handoff](20261117_recurring_cloud_staging/2026-11-17%200113%20Staging%20Build%20Handoff.md). Current Workday access failures remain visible; the scoped handling repair above is released. One production clock and one isolated staging clock serve different environments; never let staging dispatch production pipelines.

**Current documentation index: [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md).** Read it with [RUNBOOK.md](RUNBOOK.md) and [AGENTS.md](AGENTS.md) before working on the system.

The four scrapers run in the cloud. One Cloudflare scheduler starts each every twelve hours temporarily on staggered hours. GitHub Actions runs robotics, tech, sports teams and the sportsbook delivery worker; Hugging Face runs the sportsbook scraper. One Supabase project holds the job data. Each module has exactly one Discord sender using the shared send implementation. The retired watchdog job announcer and independent Space timer must not be restored as extra senders/clocks.

Current cadence and original development release gate: [2026-11-17 0029 Temporary Cadence and Cloud Validation.md](2026-11-17%200029%20Temporary%20Cadence%20and%20Cloud%20Validation.md). The later scoped handling release above supersedes its unpromoted-code status; Workday source-access failures remain unresolved.

| Need | Document |
|---|---|
| Current architecture, schedules, operations and failure recovery | [RUNBOOK.md](RUNBOOK.md) |
| Documentation scope, coverage, gaps and maintenance rules | [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) |
| Latest deployed repairs, cloud proof, eight screenshots and rollback | [November 14 release proof](2026-11-14%20Recovery%20Proof.md) |
| Fresh file inventory, line counts, hashes and function locations | [November 14 source inventory](20261114_documentation_audit/source_inventory/README.md) |
| Fresh database structures, policies, grants, indexes and functions | [November 14 public database dictionary](20261114_documentation_audit/DATABASE.md) |
| Accounts and credential locations/names | Private operator copy: `D:\abet_ops\jobs_scrapers\OPERATOR_APPENDIX.md`; no credential values in public documentation |
| Database consumers, retention and old telemetry | Consumer audit (operator copy: `20261113_database_consumers_audit/REVIEW.txt`), metrics origin/removal (operator copy: `20261113_1900_storage_and_limits/ABET_METRICS_ORIGIN.md`) |
| Prior file inventories and generated reference | [Historical inventory](inventory/README.md), local `SYSTEM_REFERENCE.md` dated November 13; not current deployment instructions |

The source and schema inventories have explicit coverage limits. Function locations are not a complete behavioral specification; current Git branches do not by themselves prove deployed-bundle parity; there is no enforced cross-service documentation drift check yet. These gaps are listed in the documentation index.

The November 10 new-industry build guide and all older review/draft packages are historical. Use the current cloud-only runtime, cadence and sender rules when reusing their code. The November 13 shared-engine local candidate is undeployed and is not a production dependency.

Version-controlled documentation lives in [job-radar/docs/job-scrapers](https://github.com/misterplusev/job-radar/tree/master/docs/job-scrapers). Private account details and raw operator evidence live under `D:\abet_ops\jobs_scrapers`. Keep the public and private copies aligned without publishing credentials, resumes or application records.
