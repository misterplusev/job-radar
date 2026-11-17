# Recurring cloud staging: durable handoff

Updated 2026-11-17T02:07:43.779070+00:00. **BUILD COMPLETE; recurring operation verified.** The user authorized documenting and building an isolated recurring development environment. This work is deployed, not a proposal. The Workday repair itself is NOT proven or promoted.

## Read first

- `D:\abet_ops\jobs_scrapers\AGENTS.md`, `RUNBOOK.md`, `DOCUMENTATION_INDEX.md`.
- `2026-11-17 0150 Recurring Staging Operations.md`: accounts, exact source paths, workflow, storage schemas, schedule, budgets, endpoint authentication, diagnosis and rollback.
- `2026-11-17 0158 Staging Acceptance Evidence.md`: actual cloud runs, regression counts, source failures, redeploy/persistence and recurrence evidence.
- `2026-11-17 0155 Staging Source Inventory.md` and `source_inventory.json`: per-file physical/nonblank lines, hashes, absolute paths and static symbol locations.

## Deployed system

Live page: https://abet-jobs-staging.abetscrape.workers.dev/
JSON: https://abet-jobs-staging.abetscrape.workers.dev/status
Cloudflare account: `b6847328054eee51af12c25cf34a565a`; Worker `abet-jobs-staging`; SQLite-backed Durable Object `StagingControl`, binding `STAGING`, object `isolated-development-v1`.
Controller version `edf0ca19-1015-4cf6-9d90-705993bae74a`. Current harness branch `misterplusev/job-radar` / `codex/recurring-staging-20261117`; source revision `34670ee4687d8d6346c195d3c286e02a2312778a`. Its cloud test run 44000280990 passed fifteen controller and four HTTP guard tests.

GitHub-hosted Actions run the real pinned candidate regression tests and bounded live source probes. Sole staging clock is the Durable Object alarm. Robotics hourly :05; tech hourly :20; teams hourly :35; sportsbook every four hours at 00:50/04:50/08:50/12:50/16:50/20:50 UTC. Production stays at twelve hours. One active staging lease; normal 78/day, hard cap 96/day; private sportsbook 200 leases/month at four minutes, reserving at most 800 private Actions minutes/month for this workload. Public jobs have eight-minute ceilings. No local runtime or paid upgrade is required.

State is persistent but is NOT a full production PostgreSQL clone: run receipts, cooldowns, bounded job samples. Candidate tests exercise persistence/lifecycle/delivery behavior using cloud fixtures and mocked external services. Staging never receives production Supabase or Discord credentials. All six unsupported sportsbook transports remain explicitly unsupported, not passing. Registry: 66 robotics, 13 tech, 152 team routes for 124 organizations, 24 sportsbook/18 HTTP-supported. Two sources/public cycle, one/sportsbook; twelve requests/source, 105-second network budget/120-second process kill, 16 MiB response/24 MiB source threshold. Seven-day/max672 receipts and ten-job samples/source. Persistent backoff doubles 1–24 hours and respects longer Retry-After; 403 waits at least a day. No automatic promotion.

## Evidence and current findings

First automatic runs: robotics 43997984357 (112 tests), tech 43998255324 (89 with four expected skips), teams 43998385133 (74), sportsbook 43998642966 (15 + 17). All regression suites passed. Boston Dynamics, AMBSE and BetMGM still returned 429s. Houston Texans yielded four valid jobs. Initial Anthropic/Cloudflare/Stripe probes hit the original 4 MiB staging guard; it was raised to the current bounded allowance and tested, without rewriting those failures as successes.

Second automatic robotics run: https://github.com/misterplusev/job-radar/actions/runs/44000337581, slot 02:05 UTC. workday:rockwellautomation: failed, 0 jobs, 5 requests; greenhouse:stripe: passed, 791 jobs, 1 requests. This proves operation across another scheduled slot after redeployment without a manual start. Boston Dynamics cooldown was respected. `recurrence-proof.json` and `final-staging-state.json` contain details. Production health remains degraded for the preexisting failed sources, with database checks healthy; do not say all scrapers are fixed.

`persistence-proof.json` proves receipts, source states, counters and alarm survived a real controller redeploy. `deployment-parity-proof.json` proves production scheduler and HF versions unchanged and GitHub changes limited to docs/new staging workflows. `binding-cleanup-proof.json` confirms only STAGING/GITHUB_TOKEN/REPORT_TOKEN/CONTROL_TOKEN remain. Initial HF_READ_TOKEN/RUN_TOKEN were explicitly removed after noticing Cloudflare retained old secrets across uploads. No staging HF Space was created: creation returned402 requiring PRO. Historical Docker notes are marked accordingly; no active HTTP-server mode remains.

## Source and workflows

Pinned candidates: robotics/teams `ac5370eb792394cfc0dd289305bc104992479cd0`; tech `f631e0b6f165cf4764ab857f1b4164ec76f83dc8`; sportsbook `bcf53bb7c2371601e92f247ddf0aa36d3f9fecdc`. Never confuse these with a deployed production repair.

Dispatch-only workflow `.github/workflows/staging-recurring.yml`: main `job-radar` master; `job-radar-tech` master; private `sportsbook-jobs-dashboard` prod/sportsbook-jobs. Sportsbook additionally needs registration on default `main`. Workflow registration commits are in their receipt JSON. No GitHub cron was added. Harness files live under `runtime/staging/`; runner entrypoint `runner/ci_run.py`, execution library `server.py`, live provider child `live_probe.py`, request guard `network_guard.py`, regression isolation `isolation/sitecustomize.py`.

## Operator access and constraints

Cloud-only execution is mandatory. Do not launch local providers, tests, databases, browser sessions or subagents. Local source/static documentation and remote API administration are permitted. Use D: for user artifacts and E: for scratch. Never print credentials.

Remote-only helper `cloud_admin.py`: status/pause/enable/tick/worker-upload/github-secrets; obsolete-secret cleanup has an explicit staging-only command. `github_admin.py`: remote source/commit/run/log administration. `verify_deployments.py` and `inspect_cloud.py`: read-only cloud verification. `document_build.py`: static inventory/doc index generation. `prepare_documentation_commit.py` prepares documentation payloads. `check_documentation.py` checks known secret exclusion. Do not rerun historical build transforms or stale commit specs blindly; helpers check branch-head races.

Credential locations/names only: `E:\abet\.env` Cloudflare account/token; existing gh authentication; `D:\abet_ops\jobs_scrapers\private\recurring_staging.json` report/control tokens. GitHub secret `ABET_JOBS_STAGING_REPORT_TOKEN` on all three repositories. Cloudflare GITHUB_TOKEN uses existing authorized GitHub access; code restricts dispatch targets, but the credential itself is broader than this service. The user's machine is not required for scheduled operation.

Production scheduler version stays `2b3d123d-3f56-4532-a556-efa7495fea36`; production HF Space `abetco/sportsbook-jobs` stays `7026b4a72b90747c13d6b94f426044f8bdf40cf8`. Production UTC: robotics00:09/12:09; tech09:37/21:37; teams10:23/22:23; sportsbook11:00/23:00. Never reset production slots or create another production sender.

## Next work, separate from this completed build

Read subsequent staging receipts; diagnose actual Workday access failures and source-budget/transport limitations; prove fixes in cloud before promotion. Full source coverage, six unsupported sportsbook transports, full isolated PostgreSQL integration, account-wide current quotas and sustained reliability remain unproven. Do not convert passing fixture tests into a claim of live source recovery. Pause staging through its own /pause endpoint if requested; preserve its database and never pause production by mistake. The detailed rollback is in the operations guide.
