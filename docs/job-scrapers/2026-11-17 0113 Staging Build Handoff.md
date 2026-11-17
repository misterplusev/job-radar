# Recurring cloud staging build handoff

Status: BUILDING. The user explicitly authorized documenting and building the recurring isolated development environment on November 16 Pacific / November 17 UTC. Continue this task after compaction; do not stop after creating branches or one-time tests.

## Required outcome

- Four scraper modules represented in cloud staging, using pinned development copies of their real collection code.
- Repeated scheduled validation more frequent than the temporary 12-hour production cadence.
- Persistent isolated staging state and evidence, plus meaningful persistence/completeness/delivery-simulation checks. No production database writes or real Discord messages from staging.
- Strict request, runtime, storage and retention budgets. Repeated upstream 429s must back off, not create a request storm.
- Live visible status with per-module results, tested SHA, next scheduled run, request counts, source errors and promotion eligibility. A failed/deferred source must not become green.
- Actual cloud run receipts proving the first staging cycle. Document everything needed to operate, pause, resume, reproduce and remove staging without touching production.
- No automatic promotion. Keep the proposed Workday fix undeployed until actual acceptance passes.

## Starting facts

Production is enabled at 12-hour intervals: robotics 00:09/12:09 UTC; tech 09:37/21:37; teams 10:23/22:23; sportsbook 11:00/23:00. Scheduler Worker `abet-jobs-scheduler` is in Cloudflare account `b6847328054eee51af12c25cf34a565a`. Do not alter this cadence or clear its Durable Object state.

Main repository `misterplusev/job-radar` production master was `c85eebe093b34ad3225e7b194ce94efedf2c67ef`. Tech production master `4a97502b24ccb74ee70584f0d74f6f2c6aa1c7cf`. Sportsbook private repository `misterplusev/sportsbook-jobs-dashboard`, production branch `prod/sportsbook-jobs`, source `dd0e212208694beef464bdb1f3be22455b0fa744`; deployed private HF Space `abetco/sportsbook-jobs` `7026b4a72b90747c13d6b94f426044f8bdf40cf8`.

Development branch `codex/workday-validation-20261117` exists in all three repositories (main contains robotics and teams). Last candidate SHAs: main `ac5370eb792394cfc0dd289305bc104992479cd0`; tech `f631e0b6f165cf4764ab857f1b4164ec76f83dc8`; sportsbook `bcf53bb7c2371601e92f247ddf0aa36d3f9fecdc`.

Existing development workflows run only on push/manual dispatch. They are NOT recurring staging. Main mocked suites passed 112 root + 74 teams tests, tech 89 with four expected skips, sportsbook 15. Live robotics sources Boston Dynamics, AutoStore, Rockwell Automation still returned 429 after five attempts. Sportsbook BetMGM/Betway exhausted retries; Hard Rock detail requests exhausted the source budget. Do not call these fixes proven.

## Operating restrictions and access

Cloud-only runtime execution. Local source/document inspection, static generation and remote API administration are allowed; no local scraper/provider/database/browser/test execution. Do not spawn subagents or browser sessions. User files stay on D:, scratch E:. Do not print credentials.

Read `D:\abet_ops\jobs_scrapers\AGENTS.md`, `RUNBOOK.md`, and the newest dated handoff. Existing API-only administration helper: `D:\abet_ops\jobs_scrapers\20261117_cadence_and_cloud_validation\github_admin.py`. The GitHub connector reads public source but mutation returns 403 and private reads return 404; existing `gh` authentication can administer the repositories. Use safe structured API payloads and branch-head checks.

Cloudflare scheduler account credentials: variable names CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN in `E:\abet\.env`. HF existing authorized token: HF_TOKEN_ABETCO in that file. Production Supabase registry: `E:\abet\.env.account-registry.local`; staging must not receive these credentials. Private production scheduler control token location: `D:\abet_ops\jobs_scrapers\private\jobs_scheduler.json`; do not reuse as a staging ingest token.

## Implementation direction and checkpoint

Initial inspection completed at 01:13 UTC. No staging resources created or deployed yet. Evaluate a dedicated cloud staging control/storage worker with persistent bounded state, a scheduler that can dispatch only reviewed development workflows, and separate cloud test runners. Keep production credentials, dispatch targets and database completely out of staging. Prefer existing free accounts; verify supported storage/runtime limits before provisioning. Any scheduler added for staging must have zero production dispatch capability and must be documented as a separate environment, not a second production clock.

Next: inspect relevant real providers and cloud storage options; pin the concrete design and budgets here; implement and execute cloud-only tests; provision isolated staging; run and verify the first real cycle; update this handoff with deployed identifiers, evidence and remaining issues. Save a checkpoint before any compaction or long runtime wait.
