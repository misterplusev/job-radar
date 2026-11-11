# Tech and robotics production repair

Owner: ABET / Chris. Production work authorized by the operator after reviewing the exact code changes. This record supersedes the earlier diagnosis and review-only status for the deployed changes below. Sportsbook and sports teams were not migrated by this repair.

## Deployed source and runtime

| Component | Production source / evidence |
|---|---|
| Robotics initial reliability release | `misterplusev/job-radar` commit `94ec045d12fe333754efc4873f3f519753353265` |
| Robotics corrected Workday pagination | `01857d4c7b65a4ba4ac21680ab293d9038b71044` |
| Scheduler source and health contract | `misterplusev/job-radar` commit `d2fe9f99e319f5eba4bf0e19060a9e36e8fec47a`, `runtime/cloudflare/worker.mjs` |
| Tech reliability release / correction | `b92b2208882bc7d4b667efcef5aaadc4317200f2` / `832df2cd1f8d82d4b87b7699a1ae61237ac7ba56` |
| Final credential-safe diagnostic receipts | Robotics `3b4bdecd6d9487ef61a8cc100472b568290724cd`; tech `409457726fa8a9cc1ef04ec1d45bd696444bb038` |
| Live scheduler | [abet-jobs-scheduler health](https://abet-jobs-scheduler.abetscrape.workers.dev/health) |

The dirty Windows checkouts were preserved. Releases were staged from pinned production source, tested, then fast-forwarded with an explicit changed-file allowlist. No unrelated provider targets, resumes, applications, dashboard modules, sports-team runtime, sportsbook runtime, machine stop switches, or watchdog tasks were changed.

## What changed

- `jobradar/publish.py`: cleanup queries are quoted and bounded below 6 KB; update counts come from returned row IDs; exhausted persistence retries raise; telemetry checks HTTP status; partial runs suppress cleanup; verified empty sources can retire their old rows. Reactivated rows clear an old `closed_at` value.
- `db/schema_notifications.sql` and `db/apply_schema.py`: additive namespaced notification queues, RLS enabled, no anonymous grants, and no historical notification backfill. The live catalog confirms both queue tables exist.
- Publisher notification handling: pending intent is persisted before job upsert; delivery verifies the job was saved and remains active; Discord message IDs precede chunk acknowledgements. Retry exhaustion keeps work pending. Both modules use five embeds, 2.1-second pacing and bounded rate-limit retries.
- `jobradar/providers/{greenhouse,lever,ashby,amazon,workday}.py`: HTTP and malformed-response failures no longer masquerade as empty successful sources; paginated failures are explicit. Amazon follows the full query pagination instead of silently truncating at five pages and uses each configured query once.
- `jobradar/fetch_worker.py`: each provider runs in a bounded subprocess, with a real kill deadline and a 512 MiB Linux memory limit. Provider subprocesses receive no Supabase or Discord environment secrets.
- `run.py`: per-provider completeness and timing, truthful overall status, publication/delivery totals, dispatch slot and run ID are written to `data/runtime/latest_manifest.json`.
- `jobradar/diagnostics.py`: redact credential values and Discord webhook URLs before error text enters public manifests or failure alerts. The final diagnostic-only change passed the full local test suites; the live scrape receipts below precede this final redaction change.
- `.github/workflows/pipeline.yml`: tests run before migration/ingestion; run receipts upload even on failure; only explicit dispatch remains. Cloudflare owns the schedule.

Existing date/relevance eligibility rules remain in place. The queues repair delivery reliability; they do not reinterpret unknown posting dates or turn the industry feeds into personalized job matches.

## Scheduling and controls

Cloudflare Durable Object alarms dispatch robotics hourly at **:09 UTC** and tech at **:37 UTC**. The alarm also wakes at five-minute boundaries to observe execution and detect problems. The next wake is exposed as `next_alarm_at` in public health. No process on the Windows computer is required.

The account's existing five cron slots were full. The attempted new cron allocation was rejected by Cloudflare; no existing cron or service was removed, and no paid-plan upgrade was made. The deployed solution uses Durable Object alarms and **zero Cloudflare Cron Triggers**. GitHub's old robotics/tech cron declarations are removed, so there is one scheduling owner.

The scheduler serializes state changes, records each UTC slot, checks exact run titles before dispatch, defers while another production run is active, and bounds retries. Only `master` runs inform its health; one-off audit branches cannot falsely establish scraper health. It exposes stale execution or scheduler heartbeat as degraded health.

Public read-only endpoint: `GET /health`. Authenticated operator controls: `POST /pause`, `POST /enable`, and `POST /tick`. Pause deletes the pending alarm; enable arms it. Control and GitHub credentials are encrypted Worker secrets; the operator's private credential file is excluded from source control and the public inventory. Manual `/tick` is not evidence that an alarm fired.

## Live validation

Tech verification [42964823857](https://github.com/misterplusev/job-radar-tech/actions/runs/42964823857): healthy manifest; **13/13 providers**, 3,750 jobs upserted, 14 deactivated, seven newly eligible candidates and seven confirmed deliveries.

Robotics verification [42965402777](https://github.com/misterplusev/job-radar/actions/runs/42965402777): healthy manifest; **66/66 providers**, 17,682 provider results, 17,604 distinct company/URL rows upserted, 3,009 deactivated in this run, 24 newly eligible candidates and 24 confirmed deliveries.

The original diagnostic set contained 3,136 active rows whose cleanup had failed. A fresh database comparison found **3,035 now inactive**, **101 still active and observed again in the corrected complete scrape**, and **zero still active without a refreshed observation**. The 101 verified current listings were retained rather than blindly marking every old candidate closed. This comparison includes valid cleanup completed before the first verification run was stopped, so it need not equal the corrected run's deactivation count.

The first robotics verification run was deliberately cancelled when the new completeness check exposed an incorrect interpretation of Workday totals. Workday returns its total on page one and frequently returns zero on subsequent pages despite continuing to return jobs. The correction retains the first-page total. Direct read-only verification retrieved 89 Boston Dynamics, 35 AutoStore, and 446 Rockwell Automation jobs. Active counts were checked after cancellation, before resuming. The affected Workday records had not been wrongly retired.

The scheduler was enabled at **2026-11-11 05:31:57 UTC**. Its alarm fired independently at **05:31:58 UTC** and dispatched the current due slots. The scheduler state records `dispatch_origin=alarm`; both automatic runs appeared with the expected slot titles:

- Robotics [42966372146](https://github.com/misterplusev/job-radar/actions/runs/42966372146), slot `2026-11-11T05:09:00.000Z`.
- Tech [42966375401](https://github.com/misterplusev/job-radar-tech/actions/runs/42966375401), slot `2026-11-11T04:37:00.000Z`.

Both initial automatic runs completed successfully. Robotics finished at **05:40:01 UTC**, with 66/66 complete sources and 17,604 distinct rows upserted. Tech finished at **05:34:04 UTC**, with 13/13 complete sources and 3,750 rows upserted. Both reported zero deactivations, zero new notification candidates and zero deliveries on the repeat, confirming no replay of the previously acknowledged alerts in these runs.

The next regular tech alarm fired at **05:37:00 UTC** and started [run 42966927497](https://github.com/misterplusev/job-radar-tech/actions/runs/42966927497). Its manifest is healthy, with 13/13 complete sources, 3,750 rows upserted and zero duplicate deliveries. This establishes both activation catch-up and a subsequent clock-scheduled dispatch. The initial catch-up slots reflect activation time; they are not a claim that the scheduler was active earlier.

Final local regression suites passed **54 robotics tests**, **31 tech tests**, and **8 scheduler tests**. The workflow also passed its regression step in each successful live run. [Post-cutover inspection of all four modules](20261110_repair_verification.json) records tech and robotics without warnings; the separate sports-teams runtime still has failed executions and scheduling gaps.

## Evidence, limits and rollback

Local release receipts: `D:\abet_ops\jobs_scrapers\20261110_release`. This contains pinned source revisions, changed-file lists, test outputs, deployment receipts, run manifests, scheduler health and the stale-row reconciliation result. Tests cover cleanup bounds, retry exhaustion, durable delivery, preservation of delivered chunks, partial source failures, empty sources, real subprocess deadlines, Workday pagination, scheduler overlap/idempotence and pause/authentication behavior.

The refreshed [database dictionary](inventory/DATABASE.md) comes from read-only audit [42965912679](https://github.com/misterplusev/job-radar/actions/runs/42965912679). It includes 22 relations and the new queues. The [source inventory](inventory/README.md) records file paths, physical line counts and definitions at explicit revisions. Source snapshots are historical, not silently rewritten to claim perpetual freshness.

Delivery remains at-least-once across the narrow crash window after Discord accepts a message and before its database acknowledgement succeeds. Previously lost historical notifications without receipts cannot be reconstructed exactly. No historical mass replay was performed. Long-term cadence must be assessed from actual run history; a successful cutover is not a week-long uptime measurement.

Rollback: pause the cloud scheduler first; revert only the affected production source with a normal reviewable commit. Preserve the notification tables and acknowledgements. Restore GitHub cron only while the cloud scheduler is paused; never run both owners. Prior source revisions are preserved in `base_revisions.json` and `github_deployments.json`.

## Exact deployed code and line references

These links are pinned to the final code revision. The comparisons show the changes from the production revisions inspected at the start of this repair.

[Robotics full repair diff](https://github.com/misterplusev/job-radar/compare/99ee50ea8b7c815e670b6af887c3dd6353e326b4...3b4bdecd6d9487ef61a8cc100472b568290724cd) · [Tech full repair diff](https://github.com/misterplusev/job-radar-tech/compare/d682fdeb8557ee40f3bb7ef429ea2dbc11014973...409457726fa8a9cc1ef04ec1d45bd696444bb038)

| Script / change | Robotics | Tech |
|---|---|---|
| `jobradar/publish.py` — Bound cleanup request URLs | [line 118](https://github.com/misterplusev/job-radar/blob/3b4bdecd6d9487ef61a8cc100472b568290724cd/jobradar/publish.py#L118) | [line 115](https://github.com/misterplusev/job-radar-tech/blob/409457726fa8a9cc1ef04ec1d45bd696444bb038/jobradar/publish.py#L115) |
| `jobradar/publish.py` — Count confirmed row updates | [line 142](https://github.com/misterplusev/job-radar/blob/3b4bdecd6d9487ef61a8cc100472b568290724cd/jobradar/publish.py#L142) | [line 139](https://github.com/misterplusev/job-radar-tech/blob/409457726fa8a9cc1ef04ec1d45bd696444bb038/jobradar/publish.py#L139) |
| `jobradar/publish.py` — Fail after exhausted database retries | [line 162](https://github.com/misterplusev/job-radar/blob/3b4bdecd6d9487ef61a8cc100472b568290724cd/jobradar/publish.py#L162) | [line 159](https://github.com/misterplusev/job-radar-tech/blob/409457726fa8a9cc1ef04ec1d45bd696444bb038/jobradar/publish.py#L159) |
| `jobradar/publish.py` — Drain persistent pending notifications | [line 309](https://github.com/misterplusev/job-radar/blob/3b4bdecd6d9487ef61a8cc100472b568290724cd/jobradar/publish.py#L309) | [line 284](https://github.com/misterplusev/job-radar-tech/blob/409457726fa8a9cc1ef04ec1d45bd696444bb038/jobradar/publish.py#L284) |
| `jobradar/publish.py` — Defer cleanup for incomplete scrapes | [line 457](https://github.com/misterplusev/job-radar/blob/3b4bdecd6d9487ef61a8cc100472b568290724cd/jobradar/publish.py#L457) | [line 432](https://github.com/misterplusev/job-radar-tech/blob/409457726fa8a9cc1ef04ec1d45bd696444bb038/jobradar/publish.py#L432) |
| `jobradar/fetch_worker.py` — Enforce process deadlines | [line 11](https://github.com/misterplusev/job-radar/blob/3b4bdecd6d9487ef61a8cc100472b568290724cd/jobradar/fetch_worker.py#L11) | [line 11](https://github.com/misterplusev/job-radar-tech/blob/409457726fa8a9cc1ef04ec1d45bd696444bb038/jobradar/fetch_worker.py#L11) |
| `jobradar/providers/workday.py` — Retain page-one total | [line 42](https://github.com/misterplusev/job-radar/blob/3b4bdecd6d9487ef61a8cc100472b568290724cd/jobradar/providers/workday.py#L42) | [line 42](https://github.com/misterplusev/job-radar-tech/blob/409457726fa8a9cc1ef04ec1d45bd696444bb038/jobradar/providers/workday.py#L42) |
| `jobradar/providers/amazon.py` — Complete query pagination | [line 22](https://github.com/misterplusev/job-radar/blob/3b4bdecd6d9487ef61a8cc100472b568290724cd/jobradar/providers/amazon.py#L22) | [line 22](https://github.com/misterplusev/job-radar-tech/blob/409457726fa8a9cc1ef04ec1d45bd696444bb038/jobradar/providers/amazon.py#L22) |
| `run.py` — Persist complete execution manifest | [line 56](https://github.com/misterplusev/job-radar/blob/3b4bdecd6d9487ef61a8cc100472b568290724cd/run.py#L56) | [line 56](https://github.com/misterplusev/job-radar-tech/blob/409457726fa8a9cc1ef04ec1d45bd696444bb038/run.py#L56) |
| `jobradar/diagnostics.py` — Redact public failure diagnostics | [line 7](https://github.com/misterplusev/job-radar/blob/3b4bdecd6d9487ef61a8cc100472b568290724cd/jobradar/diagnostics.py#L7) | [line 7](https://github.com/misterplusev/job-radar-tech/blob/409457726fa8a9cc1ef04ec1d45bd696444bb038/jobradar/diagnostics.py#L7) |
| `db/apply_schema.py` — Apply additive notification schema | [line 1](https://github.com/misterplusev/job-radar/blob/3b4bdecd6d9487ef61a8cc100472b568290724cd/db/apply_schema.py#L1) | [line 1](https://github.com/misterplusev/job-radar-tech/blob/409457726fa8a9cc1ef04ec1d45bd696444bb038/db/apply_schema.py#L1) |
| `db/schema_notifications.sql` — Create notification queues and RLS | [line 1](https://github.com/misterplusev/job-radar/blob/3b4bdecd6d9487ef61a8cc100472b568290724cd/db/schema_notifications.sql#L1) | [line 1](https://github.com/misterplusev/job-radar-tech/blob/409457726fa8a9cc1ef04ec1d45bd696444bb038/db/schema_notifications.sql#L1) |
| `.github/workflows/pipeline.yml` — Dispatch workflow, tests and receipts | [line 1](https://github.com/misterplusev/job-radar/blob/3b4bdecd6d9487ef61a8cc100472b568290724cd/.github/workflows/pipeline.yml#L1) | [line 1](https://github.com/misterplusev/job-radar-tech/blob/409457726fa8a9cc1ef04ec1d45bd696444bb038/.github/workflows/pipeline.yml#L1) |

The scheduler is [runtime/cloudflare/worker.mjs](https://github.com/misterplusev/job-radar/blob/3b4bdecd6d9487ef61a8cc100472b568290724cd/runtime/cloudflare/worker.mjs#L39). Its eight regression cases are versioned beside it.
