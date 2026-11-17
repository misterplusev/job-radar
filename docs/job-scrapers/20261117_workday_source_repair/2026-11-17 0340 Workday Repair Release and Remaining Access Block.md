# Workday repair release and remaining access block

Observed November 17, 2026 UTC (November 16 Pacific). This document supersedes the earlier unpromoted-candidate wording for the code changes identified below. It does **not** establish complete source recovery.

## Result

Request handling and data-integrity repairs were cloud-tested and released to all four scrapers. Explicit security challenges stop immediately, ordinary transient failures retain bounded retries, incomplete Workday results remain failures, and useful HTTP diagnostics are retained. The blocked career sources still need an accessible, authorized retrieval method. They are not counted as recovered.

Production remains cloud-only at twelve-hour intervals. No collection schedule, database schema, credentials, Discord sender, notification cursor, or historical jobs were changed in this repair. There was no manual production scrape or test Discord message. The separate staging controller is enabled and continues bounded tests without production database or Discord credentials.

## Exact diagnosis and evidence

- [Cloud diagnostic 44007603631](https://github.com/misterplusev/job-radar/actions/runs/44007603631): public Workday GETs returned HTTP429 with `CF-Mitigated: challenge` and text `Security Check Enable JavaScript and cookies to continue`. Boston Dynamics and AMBSE were among the requested sites. The BetMGM GET in that particular diagnostic used `/External`, so it must not be presented as a test of the canonical `/BetMGM` listing API.
- [Cloud diagnostic 44008297230](https://github.com/misterplusev/job-radar/actions/runs/44008297230): Hard Rock and Betway public career GETs also returned explicit challenges. Boston Dynamics' own corporate careers URL returned HTTP200 containing JavaScript verification, not a job list.
- Earlier sportsbook staging run43998642966 reached the canonical BetMGM listing endpoint: 429,429,200, then four successful detail GETs, followed by persistent429 on another detail. Access failures are intermittent and path-specific; not every request or site is permanently inaccessible.
- Existing diagnostic excerpts took only the first4KiB of HTML, predominantly SVG markup. The error text was omitted. The repair inspects a bounded64KiB prefix, removes SVG/script/style markup, redacts clientIP/secrets, and records the challenge header, CF-Ray, HTTP status, method, host, path, pagination offset and retry decision.
- Sportsbook previously caught a failed detail request and continued. Returning that partial list as a complete source could make the persistence layer close still-open postings. The repair fails the incomplete source and returns no partial collection from it.
- Production scheduler database check was OK at03:35UTC. The observed failures do not establish a Supabase quota outage or a Cloudflare credential problem. The Cloudflare challenge belongs to the employer's career site, not our scheduler account.

## Released revisions

| Component | Before | Tested/released revision |
|---|---|---|
| Robotics and sports teams, `misterplusev/job-radar`, `master` | `cd91cba32f19262ecf28bbab69ea473d13e5ef4e` | `a47faad85f70bf3ea57c853973c1b4ad6bd768e5` |
| Tech, `misterplusev/job-radar-tech`, `master` | `b1bae9fd0b8f652ec289086c1d3277f1593fe9c4` | `3d5c1e89ecded51fff43dcaca253d65e08b47f98` |
| Sportsbook, private `misterplusev/sportsbook-jobs-dashboard`, `prod/sportsbook-jobs` | `008bfd4f0df76f1c1c96c75f31f0c3c0744747c0` | `03e7f50efd72f94e70f131197d031bce52231320` |
| Existing HF Space `abetco/sportsbook-jobs` | `7026b4a72b90747c13d6b94f426044f8bdf40cf8` | `e43043fa23fc741eaaf71a902150f64dfab6f550` |
| Staging controller `abet-jobs-staging` | Worker version `edf0ca19-1015-4cf6-9d90-705993bae74a` | Worker version `a5fe8270-44eb-46c4-a734-a5fc1a04d3c1`; source `91af158bab61db76797db53eefdd185857da84ad` |

GitHub production branches were advanced without force to the exact passing release commits at03:38UTC. HF received exactly six runtime files at03:39UTC; all six remote file hashes matched. The launcher, Dockerfile, scheduler, sender and secrets were untouched. At03:40UTC the HF API reported the new revision RUNNING on cpu-basic; the runtime had zero boot scrapes, was idle, and still advertised the12-hour schedule. The scheduler database check was OK. The exact receipt is `post-release-verification.json`.

Restart limitation: HF's local manifest is ephemeral. Its runtime health therefore became `unknown`, with no local last-run timestamp, until the next scheduled scrape; this is not a passing scraper result. The durable scheduler preserved the previous completed degraded slot and did not replay it. Production collection with the new code is pending the normal schedule. Restoring health from a durable receipt after restart remains a separate unresolved limitation; no synthetic run was used to disguise it.

## Scripts and line-level changes

All paths in this table are repository-relative. Complete reviewed copies reside under this package's `release/main/`, `release/tech/` and `release/sportsbook/` directories. The corresponding `main-production-repair.diff`, `tech-production-repair.diff` and `sportsbook-production-repair.diff` contain the full exact unified diffs, including tests and workflows. `*-rollback-manifest.json` inventories every changed file with before/after SHA256, existence and before-image path.

| Script | Exact change |
|---|---|
| Main/tech `jobradar/workday_http.py`; sportsbook `scripts/lib/workday_http.py` | Identical new helper. Line32 defines `WorkdayChallenge`; line84 cleans bounded evidence; line163 starts request policy; line217 records `cf_mitigated`; line227 stops an explicit challenge after one response. Lines245 onward enforce exhaustion/deadline decisions. Ordinary retry maximum5, waits5/10/20/40seconds plus jitter, longer Retry-After respected, total source deadline preserved. Only approved read-only Workday GET/HEAD/listingPOST paths accepted. No automatic redirect, proxy, CAPTCHA or challenge solving. |
| Main/tech `jobradar/providers/workday.py:38` | Listing reads use the shared helper; existing pagination/completeness protections retained. |
| Main/tech `jobradar/fetch_worker.py:22` | Pass remaining source budget to provider subprocess. Line31 forwards structured Workday evidence even when a later retry succeeds. |
| Main `sports_teams/live_refresh.py:48` | `BoundedSession` sends read-only Workday listingPOSTs through the same policy; ordinary unrelatedPOSTs are not retried by that policy. Connect/read timeout tuple remains within total deadline. |
| Main/tech `.github/workflows/pipeline.yml:69` | Include bounded Workday JSONL artifacts, seven-day retention. |
| Main `.github/workflows/sports-teams.yml:99` | Include teams Workday JSONL artifacts, seven-day retention. |
| SB `scripts/providers/betmgm.py:47` and `:112` | Shared helper, complete listing validation, fail source on detail failure instead of skipping. |
| SB `scripts/providers/betway.py:30` and `:88` | Same request and completeness policy. |
| SB `scripts/providers/hardrock.py:100` and `:187` | Same request and completeness policy; existing corporate-role filter retained. |
| SB `scripts/provider_runner.py:56` | Carry the existing absolute task deadline into Workday requests, reserving a small reporting margin. |
| SB `scripts/scrape.py:745` | Add bounded HTTP diagnostic summary to existing manifest. No database schema change. |
| All three `.github/workflows/workday-retry-review.yml` | Manual cloud regression only, no cron, browser or production secrets. Network guard enabled during tests. |
| All three `runtime/verification/isolation/sitecustomize.py` | Disables external sockets only when explicitly enabled by regression environment. Not in production scraper PYTHONPATH. |

Diagnostics on cloud disk: `data/runtime/workday-http/*.jsonl`, or the sports-teams working directory equivalent. At most48 files, seven days,256KiB/file. Detailed attempts are not stored as new database rows. The sportsbook manifest keeps the last32 interesting HTTP events. Process-local host cooldown is24hours for an explicit challenge; a new production subprocess does not persist that cooldown. Staging additionally persists source cooldowns in its own Durable Object and waits at least24hours (or longer Retry-After) before probing a challenged source again.

## Cloud validation

| Scope | Actual result | Evidence |
|---|---|---|
| Exact production-base robotics/teams patch | 114 root tests +74 teams tests passed | [44011285475](https://github.com/misterplusev/job-radar/actions/runs/44011285475) |
| Exact production-base tech patch | 91 discovered,87 passed,4 existing scheduler-only skips | [44011289470](https://github.com/misterplusev/job-radar-tech/actions/runs/44011289470) |
| Exact production-base sportsbook patch | 17 Workday +17 launcher +10 outbox +10 provider compatibility tests passed | [44011293196](https://github.com/misterplusev/sportsbook-jobs-dashboard/actions/runs/44011293196) |
| Staging controller and guard | Passing cloud validation before deployment | [44010003987](https://github.com/misterplusev/job-radar/actions/runs/44010003987) |
| Actual new handling on live source | Rockwell explicit challenge:1 request, blocked_access, no retry. Stripe:791jobs,1 successful request.114 regression tests passed. Productionwrites0, Discordsends0. | [44010386131](https://github.com/misterplusev/job-radar/actions/runs/44010386131) |

Totals for release regressions:329 passed and4 explicit skips across333 discovered tests. These tests cover retry recovery, numeric/date Retry-After, deadlines, challenge handling, incomplete pagination, failed-detail rejection, persistence protections and outbox behavior. They are not proof all employers were collected. The historic standalone Rebet regression file was not part of this scoped release suite; no claim of an entirely green legacy sportsbook test suite is made.

The staging sports-teams run at03:35UTC also recorded a one-request Mariners challenge while its other source passed. See the saved staging status receipt for source-level evidence. Current status: https://abet-jobs-staging.abetscrape.workers.dev/ . The controller reports degraded honestly and has no automatic promotion.

## Remaining access work and safety hold

An ordinary one-session GitHub-hosted browser compatibility check is prepared at `cloud_browser_probe.py`. It uses no production credentials, does not solve or bypass any challenge, and closes/kills only its own browser processes in `finally`. The original machine guard and snapshot scripts are included unchanged. Workflow input defaultsfalse. This browser test has NOT run.

`D:\abet_ops\STOP_ALL_AGENTS_MACHINE` exists. Rule2 of `D:\abet_ops\20261019_AGENT_RUNAWAY_AND_MEMORY_SAFETY_RULES_v1_0_0.md` says "while it exists, start NO agent and NO browser anywhere." A specific exception for one bounded cloud test was requested; the reply is still pending. No stop file, guard, watchdog or user browser was modified. Continue only after explicit exception. An approved compatibility test is not authorization for recurring browser scraping.

If ordinary supported browser access succeeds, review its complete-source output and resource cost before proposing a collection adapter. If it remains challenged, obtain an employer-supported feed/access route. Do not bypass restrictions, repeatedly probe known blocked hosts, remove sources from coverage, or reuse search-indexed jobs as fresh listings. Boston Dynamics' indexed corporate page contains jobs, but the raw cloud response has not proven a usable live feed.

## Rollback

1. Read current repository heads and inspect intervening changes. Do not reset an entire branch. The exact old source is in `rollback/main/`, `rollback/tech/`, `rollback/sportsbook/`. Each `*-rollback-manifest.json` distinguishes replaced files from newly added files.
2. Create a new reverse commit restoring only these files, deleting only files marked `existed:false` if they have not since been adopted by another change. Verify the current target file equals this release before overwriting it. Preserve unrelated subsequent changes. Run the existing cloud regression workflow on the reversal before promotion.
3. For the HF Space use `huggingface-before-repair.json` and `rollback/huggingface/`. Restore the five previous runtime files and remove the newly added `scripts/lib/workday_http.py` together in one parent-checked HF commit, only when no production scrape is running. Keep launcher, secrets, cadence, sender and manifest history intact. Verify every uploaded byte and the running Space revision/health. No boot scrape should occur.
4. For staging, source revision34670ee4687d8d6346c195d3c286e02a2312778a / old Worker versionedf0ca19-1015-4cf6-9d90-705993bae74a is the prior controller. Preserve Durable Object state, leases, slot receipts and cooldowns; never clear them to force a passing result. The deployment receipt before this repair is `staging-before-repair-deployment.json`.
5. Rollback changes no database schema and deletes no job or notification history. Reverting sportsbook restores its prior skipped-detail weakness; assess that explicitly before choosing a rollback.

## Package inventory and resumption

This package is `D:\abet_ops\jobs_scrapers\20261117_workday_source_repair`.

- `2026-11-17 0305 Repair Handoff.md`: chronological checkpoints, pending permission and next steps.
- `release/`: exact released source; `rollback/`: prior source before-images.
- `*-production-repair.diff`: exact before/after code, tests and workflow diffs.
- `*-production-repair-spec.json`, `*-rollback-manifest.json`, `*-production-repair-commit.json`: paths, hashes, branch preconditions and promotion receipts.
- `huggingface-before-repair.json`, `huggingface-repair-deployment.json`: old runtime health/source, scoped deployment and byte verification.
- `diagnosis-44007603631/`, `diagnosis-44008297230/`: cloud response evidence.
- `run-440112*.log`: full release cloud-test logs.
- `prepare_release_review.py`, `prepare_release_branch.py`, `backup_release.py`: source-only preparation and remote backups.
- `promote_tested_release.py`: guarded non-forced promotion to an already passing exact commit; not a general scraper runner.
- `deploy_sportsbook_repair.py`: scoped existing-Space source upload; no local scraper execution.
- `github_admin.py`: remote source and Actions administration only.

The adjacent recurring-staging package contains controller/source inventory, budget schema, source snapshots and operator helpers. `RUNBOOK.md` and `DOCUMENTATION_INDEX.md` point here. Credentials are referenced by their existing locations and names only; no credential values belong in this package or its cloud documentation.
