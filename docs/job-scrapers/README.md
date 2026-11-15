# ABET job scrapers — start here

**Current documentation index: [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md).** Read it with [RUNBOOK.md](RUNBOOK.md) and [AGENTS.md](AGENTS.md) before working on the system.

The four scrapers run in the cloud. One Cloudflare scheduler starts each every four hours on staggered hours. GitHub Actions runs robotics, tech, sports teams and the sportsbook delivery worker; Hugging Face runs the sportsbook scraper. One Supabase project holds the job data. Each module has exactly one Discord sender using the shared send implementation. The retired watchdog job announcer and independent Space timer must not be restored as extra senders/clocks.

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
