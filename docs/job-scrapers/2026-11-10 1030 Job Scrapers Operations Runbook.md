# Job scrapers operations — November 10, 2026

Start with [the architecture](2026-11-10%201030%20Job%20Scrapers%20Architecture.md). Owner: ABET / Chris. This runbook separates read-only diagnosis from actions that scrape, change production or send Discord messages. It does not install another schedule.

## Resume safely and establish the current truth

1. Read the local repository instructions and machine rules. Preserve uncommitted work. On the operator's Windows machine, `D:\abet_ops\STOP_ALL_AGENTS_MACHINE` is present as of this audit: start no agents or browsers and never edit the switch. Bounded HTTP inspection does not require a browser.
2. Read `scrapers.json`, the module README and live default/production branch. Record the deployed revision. A stale local checkout is not deployment evidence.
3. Run the bounded read-only verifier once, and open its JSON result. It uses existing `gh` authentication and public health GETs, with per-request deadlines. It never loads provider modules.

```powershell
& 'C:\Program Files\Python314\python.exe' -X utf8 'D:\abet_ops\jobs_scrapers\verify_scrapers.py' --out 'D:\abet_ops\jobs_scrapers\latest_verification.json'
```

`--strict` makes any warning a nonzero exit. Without it, zero means inspection completed, not that services are healthy. Authentication/API errors are recorded as inspection failures. The checker reads GitHub workflow state, the workflow file from the default branch, eight recent scheduled executions, sportsbook health/schedule and teams health/coverage. It flags observed intervals over two hours for modules configured hourly. This is a diagnostic threshold, not a promised SLA.

The audit receipt is a point-in-time snapshot. Keep dated receipts for changes instead of rewriting historical claims. Store no webhook URLs, access tokens, private applicant information or full environment dumps in receipts.

## Diagnose the right layer

| Symptom | Inspect first | What the evidence means |
|---|---|---|
| No run at the expected time | Workflow state, default-branch cron, `event=schedule` history; or sportsbook health's due slot | Missing trigger is a scheduling problem, not necessarily a provider failure |
| Run started but job count fell | Per-provider receipt, pagination/completeness, HTTP status and elapsed time | Error/blocked/timeout must not masquerade as a verified empty employer board |
| Database fresh but Discord quiet | New/eligible counts, pause flag, webhook destination metadata, delivery receipts | Zero new jobs may be normal; older modules can lose an alert after a successful database upsert |
| Teams has pending notifications | Eligibility, active state, posting/discovery dates, source observation and delivery budget | Pending is not automatically eligible; do not mass-release historical or unrelated jobs |
| Board old while scraper succeeded | Database last observation versus frontend deployment/artifact | The robotics/tech static board repository is separate from ingestion |
| Workflow red but some jobs posted | Manifest and final failure step | Teams deliberately exposes partial source failures after retaining useful results |
| Teams source works but official link unproved | Registry evidence and `career_link_verified` | Feed access alone does not establish the actual team's careers-page linkage |

Useful read-only GitHub commands (GitHub CLI must already be authenticated):

```powershell
gh workflow view pipeline.yml --repo misterplusev/job-radar --yaml
gh run list --repo misterplusev/job-radar --workflow pipeline.yml --event workflow_dispatch --limit 8
gh run list --repo misterplusev/job-radar-tech --workflow pipeline.yml --event workflow_dispatch --limit 8
gh run list --repo misterplusev/job-radar --workflow sports-teams.yml --limit 8
gh run view RUN_ID --repo misterplusev/job-radar --log-failed
gh api repos/misterplusev/sportsbook-jobs-dashboard/actions/workflows/scrape.yml
```

Replace `RUN_ID` with an observed numeric run ID. Review logs locally for secrets before quoting or publishing them. Robotics/tech use `workflow_dispatch` from the Cloudflare scheduler. Automatic run titles are `job-radar <UTC ISO slot>`; repair/manual titles must not be counted as cadence proof. Sports teams also uses Cloudflare dispatch, with titles `sports-teams <UTC ISO slot>`. Its scheduler health is separate from its published source/coverage receipt.

For sportsbook, use the [public watchdog health](https://abet-jobs-watchdog.abetco.workers.dev/jobs-health). Inspect `schedule.missed`, previous/next due slots, `last_run_end`, expected provider count, errors, timeouts and the underlying manifest. A quiet overnight period is expected. `next_run_utc` and related fields may contain an explicit non-UTC offset in the sanitized response; parse the ISO timestamp instead of trusting the field name. The private Space's `/api/health` and source require existing Hugging Face access. `/api/run` is a mutating authenticated trigger, not a health check.

For teams, inspect [health](https://misterplusev.github.io/job-radar/health.json) and [coverage](https://misterplusev.github.io/job-radar/coverage.html), and the workflow artifact `sports-teams-scrape-receipt`. Health includes the manifest, notification pause state and delivery result. A database count alone cannot establish that all sources worked.

## Commands that change state

These are operating entry points, **not read-only checks**:

- Robotics/tech: `python run.py ingest` writes jobs and can send alerts; `python db/apply_schema.py` executes SQL; `python run.py render --out out/dashboard.html` writes an artifact.
- Teams: `python pipeline_local.py --cloud` scrapes and writes shared Supabase; `python publish_teams.py --post --limit 0` sends individual Discord alerts; `--recover-pending` is an explicit recovery action, not normal ingestion.
- Sportsbook: `python scripts/scrape.py` writes jobs and can notify; an authenticated Space run request starts that worker. Do not enable the legacy GitHub schedule as a fallback while the Space scheduler is active.
- `gh workflow run ...` starts a real workflow, including its migrations and publishers. Inspect inputs and environment before dispatch.

Normal operation already has its configured scheduler. Do not create Windows tasks, agent loops or duplicate cloud crons to compensate for a single failure. Diagnose and change the existing owner when authorized. No live scraper was dispatched by the documentation audit.

## Deployment and rollback

### Robotics and tech

Source of deployment is the module's GitHub default branch `master`; workflow versions and secrets belong to that repository. Cloudflare Durable Object alarms own robotics/tech scheduling. Inspect https://abet-jobs-scheduler.abetscrape.workers.dev/health first. Implement and review the narrow change, run focused provider/publisher tests with mocked HTTP and temporary storage, and inspect the exact diff. Apply reviewed additive schema migrations before code that requires them. Never deploy uncommitted local provider changes merely because they are present. Publisher changes depend on the additive `db/schema_notifications.sql`, applied by the existing schema runner. Provider HTTP failures must raise; Workday reports total=0 after its first page, so retain the first-page total. `jobradar/fetch_worker.py` enforces a real subprocess deadline. For a production change, observe the next authorized execution through source receipts, database updates, delivery results and the board. Roll back the specific source change using a reviewable revert; do not erase job history or first-seen timestamps or notification acknowledgements. Before any rollback that restores GitHub cron, pause the Cloudflare scheduler so there is only one owner. Pause uses authenticated POST `/pause`; enable uses `/enable`. The encrypted control token is stored in the operator secret store, never in public documentation. No cron slots are used by the Durable Object alarm scheduler.

The independently hosted static boards live in `robotics-jobradar-board` / `jobradar-tech-board`, branch `main`. A frontend-only change belongs there. Uploading `out/dashboard.html` as an Actions artifact does not deploy those sites.

### Sports teams

The production directory is `sports_teams/` in `misterplusev/job-radar`, with its own workflow and Pages deployment. Local `D:\abet_ops\sports_teams` is an operator staging directory, not a separate Git repository. Its `deploy_github.py` helper copies runtime files and can configure secrets; it is **not** a harmless docs synchronizer. For documentation edits, commit only the documentation paths. For runtime changes, review the helper's allowlist and generated tree before using it.

Sports teams now shares the alarm scheduler at :23 UTC. Its workflow checks `runtime_status` for source execution and retains a separate `career_link_audit_status`; composite `overall_status` remains degraded until that audit is complete. Review both, not only the workflow conclusion.

Run `python -m unittest discover -p 'test_*.py'` in the module for source/delivery regression coverage. Review migration effects and preserve `team_job_notifications`, observations, URL aliases and immutable discovery dates. A rollback must retain delivery acknowledgements or it can repeat old alerts. Keep the retired local/Hugging Face/Cloudflare schedulers disabled. The November 10 recovery is already complete; replaying it is unnecessary.

### Sportsbook

The Space scraper and Cloudflare watchdog are separate notification-capable components. In versioned watchdog source, `runCron` checks health and calls `announceNewJobs`; it is not merely a health monitor. That announcer uses KV key `last_notified_first_seen_at`, preserves it on failed Discord acceptance and advances only after success. The user supplied a live delivery receipt on November 11. A null Space `discord_notify_ok` does not establish that no watchdog message was sent.

A Cloudflare management API HTTP 403 means the inspecting credential cannot read/edit that deployment; it does not mean the Worker cannot post to Discord. Obtain deployed source, bindings, current cursor and the actual publishing route before changing publisher ownership. Preserve KV and delivery history, inspect timestamp-tie handling, and test failure/retry/duplicate behavior offline. Do not call `/announce` as a health probe: the repository route sends messages. Do not switch to the staged SQL outbox simply because it exists. The current outbox is empty and has no production consumer.

Read production source on `prod/sportsbook-jobs`. `scripts/build_hf_runtime_bundle.py` creates an allowlisted Hugging Face runtime with a hash manifest; inspect its current `--help` and source. Use its verification mode before preparing a deployment. **Its build operation removes the chosen output directory**: validate the resolved absolute output is a dedicated scratch bundle directory before building. Do not point it at a checkout, drive root or user document folder.

The Space's `main` revision is the deployed source of truth; its root launcher is produced from `runtime/huggingface/launcher.py`. Record the pre-change Space revision and bundle manifest. Deploy only the reviewed allowlisted bundle with existing authenticated access; keep all credential values in Space secrets. Inspect build status and then the provider manifest, due-slot status and delivery result. Roll back to the captured Space source revision without resetting Supabase job/application history. The Vercel frontend and Cloudflare watchdog are separate deployments; do not redeploy either merely to change a provider.

This guide does not embed token-bearing deploy commands. GitHub CLI, Hugging Face and Cloudflare access must come from the operator's existing authenticated tools/secret stores. Missing access is a real prerequisite, not something to guess or bypass.

## After every meaningful change

Update `scrapers.json`, the affected module README and this architecture package in the same change as runtime/configuration edits. Record: source revision, scheduler owner, changed paths, tests, live receipt, remaining failures, rollback revision and whether any alerts were sent. Verify that a second unchanged observation does not redeliver acknowledged jobs. Test notification failures with mocks, not real Discord spam. Keep the application tracker separate; job discovery is not an application event.

Do not write “all working” from only an exit code or a populated table. Report configured cadence and observed cadence separately, and distinguish a successful primary feed from complete organization-source evidence.
