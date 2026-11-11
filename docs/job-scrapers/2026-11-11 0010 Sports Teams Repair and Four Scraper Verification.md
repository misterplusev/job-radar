# Sports teams repair and four-scraper verification

> Superseded coverage/UI status: [2026-11-11 0105 Complete Team Coverage and Independent Jobs Module Proof.md](2026-11-11%200105%20Complete%20Team%20Coverage%20and%20Independent%20Jobs%20Module%20Proof.md) closes all three official-page gaps and supplies actual browser proof for all eight views. Historical failure and repair evidence below is retained.

Owner: ABET / Chris. Repair authorized November 10, 2026, with live verification continuing after midnight Pacific on November 11. This record separates operational ingestion from the remaining career-link audit. It does not claim every historical listing or every official link has been independently reverified.

## Deployed repair

Production commit: [2508f306a4b16bc47c1c15a5eadab5923d071145](https://github.com/misterplusev/job-radar/commit/2508f306a4b16bc47c1c15a5eadab5923d071145). [Exact ten-file diff](https://github.com/misterplusev/job-radar/compare/5303ebc33d07f07fdfa6041150e477b577b321f9...2508f306a4b16bc47c1c15a5eadab5923d071145).

- Replaced four failing TeamWork transport URLs with verified employer-selected public ATS routes: Detroit Red Wings (28282), Detroit Tigers (30212), Washington Capitals (30003), and Miami Dolphins & Hard Rock Stadium (28263). These IDs were read from TeamWork's own organization selectors. The parser now requires the requested ID to be selected in every response; an ignored filter raises an error instead of ingesting a broad league feed. Existing logical source IDs and job URLs were retained to preserve observation and notification history.
- Retired the Astros' HTTP-404 TeamWork route, retaining its evidence and replacement in `retired_routes`. Their official career page's active Apply Today destination is the existing UKG source. The replacement must succeed before observations belonging to the retired source are deactivated.
- Fixed observation bootstrapping: inferring a source from every job URL could create a phantom active copy of a cross-listed job. Bootstrap now runs only for legacy rows without observation history, preserves active state/timestamps, and supersedes timestamp-less inferred observations when real source receipts exist. Genuine active cross-listings and failed sources remain protected.
- Added sports teams to the existing Cloudflare Durable Object alarm scheduler at **:23 UTC**, between robotics at **:09** and tech at **:37**. The old sports-team GitHub cron is removed. Each module has its own workflow, title prefix and slot history. Updating the Worker preserved its existing alarm and the two working schedules; deployed Worker source was read back and matched.
- Added separate `runtime_status` and `career_link_audit_status` fields. **The composite `overall_status` still remains degraded when career-link evidence is incomplete.** The workflow fails on actual source/persistence/delivery failures and emits an explicit warning for the separate career-link audit. A green workflow is therefore operational evidence, not a claim of 124 verified links.

No schema or credential rotation was required. Existing application records, first-seen dates, queues, acknowledgement history, dirty local Git worktrees and machine stop switches were preserved.

### Additional defect caught during live verification

The next robotics automatic run [42984748739](https://github.com/misterplusev/job-radar/actions/runs/42984748739) failed at 08:17 UTC after a 120-second Supabase response timeout. All 66 source fetches had succeeded; persistence stopped partway through Zipline. The existing upsert retry handler caught `HTTPError` only, so a `ReadTimeout` escaped its three-attempt budget. This failed run is retained in the proof instead of presenting the earlier success as the latest result.

Both independent publishers now catch `Timeout` and `ConnectionError` within that same bounded retry loop. The unchanged merge-upsert conflict key makes a retry safe when the server committed but the response was lost. Nonretryable HTTP errors still fail immediately, and exhausted retries still raise. The notification queue is preserved. No automatic transport retry was added to Discord sends.

Exact deployed changes: [robotics commit 5affb48](https://github.com/misterplusev/job-radar/commit/5affb48cf3205da6d995f4b6f09e39cb65ebbbc4) and [tech commit ad03e42](https://github.com/misterplusev/job-radar-tech/commit/ad03e4209f1c22f8988110757f055513bf71c99b), each changing `jobradar/publish.py` and `tests/test_reliability.py`. Four new tests per module cover successful transport recovery, three-attempt exhaustion with preserved intent, a committed write whose response is lost, and immediate failure on HTTP 400. All **58 robotics tests and 35 tech tests** passed locally before deployment. Production verification was explicitly dispatched on the repaired revisions; it is distinct from automatic alarm evidence.

## Live proof

[Machine-readable execution, database and delivery receipts](20261111_four_scraper_proof.json) · [Independent four-module configuration/health inspection](20261111_runtime_verification.json)

| Module | Observed execution | Source and persistence evidence |
|---|---|---|
| Sports teams | [Automatic run 42983577543](https://github.com/misterplusev/job-radar/actions/runs/42983577543) | **152/152 sources successful**, zero source failures; **124/124 teams** have a functioning source. 18 new and 1,533 existing source rows processed; 2,104 active database jobs. Supabase persistence and Pages deployment succeeded. |
| Robotics | [Repair verification 42986391001](https://github.com/misterplusev/job-radar/actions/runs/42986391001) | **66/66 configured sources complete**; 17,596 distinct rows upserted, nine deactivated, zero new alerts. Finished 08:30:47 UTC on repaired revision `5affb48`. Earlier hourly run 42977386635 confirmed three eligible alerts. |
| Tech | [Repair verification 42986397070](https://github.com/misterplusev/job-radar-tech/actions/runs/42986397070) | **13/13 sources complete**; 3,747 rows upserted, one deactivated, zero new alerts. Finished 08:25:40 UTC on repaired revision `ad03e42`. |
| Sportsbook | [Live health and schedule](https://abet-jobs-watchdog.abetco.workers.dev/jobs-health) | Latest scheduled run `e3197b0caa9a46b7bb57bbb943094f14`: **24/24 providers accounted for** (23 returned jobs; Chalkboard returned no listings), zero errors/timeouts, 832 jobs published. |

Teams' automatic alarm fired at **08:00:00 UTC / midnight Pacific** and ran the due activation slot. It finished scraping at 08:04:04 UTC. The publisher successfully posted **18 jobs in four messages** (5, 5, 5, 3 embeds), preserving acknowledgement state. The console's `fresh=771` count is general date eligibility, not the number of alerts sent; only the pending intersection was delivered.

The sportsbook worker was independently inspected on its deployed Hugging Face revision `95db2a29832416e9fc86df276b5e7fce7de88314`. It is running and healthy. Its last scheduled scrape finished at **5:04 p.m. Pacific on November 10**; the next scheduled slot is **3:00 a.m. Pacific on November 11**. There is no missing overnight slot. Its latest manifest has `database_publish_ok=true` and `discord_notify_ok=null`: no notification attempt was recorded for that run, so this is not a fresh Discord-delivery test. An authenticated on-demand request was rejected because the separate run-control token was unavailable; no token was reset and no second scheduler was enabled.

Repeat verification [42984492408](https://github.com/misterplusev/job-radar/actions/runs/42984492408) also passed all 152 sources, with **zero new jobs and zero repeated alert messages**. The acknowledged/seeded set increased from 864 before the first delivery to 882 on the repeat, exactly matching the 18 delivered jobs. The repeat used cached details (`detail_limit=0`) while performing all source and database checks; it is idempotence evidence, not a second hourly alarm claim.

The next actual alarm dispatched [sports teams run 42986593593](https://github.com/misterplusev/job-radar/actions/runs/42986593593) at the configured **08:23 UTC** slot. It passed, processed all 152 sources, updated 1,551 rows, discovered zero new jobs, and sent zero repeated alerts. The acknowledgement set remained 882. This verifies the normal scheduled boundary after the activation run, while remaining a short observation window rather than a long-term uptime claim.

All four standalone board URLs returned HTTP 200. Database reads independently confirmed recent `last_seen_at`/`scraped_at` values corresponding to the execution receipts. Counts differ between a run's processed rows and a table's total active rows; neither is represented as the other.

The final database check used the deployed board loader's `id.asc` keyset pagination, 1,000 rows per page, with no request retries. It read the complete tables and counted active jobs locally: robotics **18,664 active / 27,045 total** in 27.1 seconds; tech **3,747 / 5,239** in 6.6 seconds; sportsbook **853 / 5,429** in 6.68 seconds; teams **2,104 / 2,170** in 2.58 seconds. All four data reads completed successfully. This verifies the data-loading path, not a browser screenshot or visual UI inspection.

An earlier audit-only query (`last_seen_at.desc` plus an exact count over the active robotics table) repeatedly returned HTTP 500 / PostgreSQL `57014`, statement timeout. That query is not how the board loads data. The final audit uses the board's existing indexed pagination and computes the same counts/timestamps locally; the failed diagnostic is retained in the machine-readable proof. No database timeout setting was relaxed. The robotics recovery run also logged two HTTP 500 upserts, both successfully retried. The new connection-timeout handling was verified by regression tests; this recovery run did not encounter another transport timeout.

## Coverage limits retained visibly

Official career-route evidence is now **121/124**. Remaining unproved website-to-ATS links: **Chicago Bulls, LA Clippers, Milwaukee Bucks**. Their Paylocity, Greenhouse and ADP feeds respectively passed; the missing evidence concerns their JavaScript-rendered official career pages. The linked NBA scripts returned HTTP 403 both locally and in bounded read-only GitHub audits [42981847676](https://github.com/misterplusev/job-radar/actions/runs/42981847676) and [42982255234](https://github.com/misterplusev/job-radar/actions/runs/42982255234), on `codex/teams-source-evidence-20261110`. That branch's temporary workflow only fetched public career pages/assets and uploaded evidence; it has no schedule or production secrets. No browser, challenge bypass, or inferred success was used.

Giants evidence now follows the official NFL club careers directory through MetLife Stadium's NFL Teams page to its New York Giants View Positions link. Bruins and Penguins evidence follows their official team footer Employment link through NHL Careers and the ATS's named organization selector. These are explicitly recorded as **league-linked career paths**, not direct team-page hyperlinks. Bruins' selected employer route was also added as a live checked source.

The [coverage report](https://misterplusev.github.io/job-radar/coverage.html) and [full JSON evidence](https://misterplusev.github.io/job-radar/coverage.json) retain those distinctions. Individual job-detail enrichment can still encounter blocked or missing detail pages; it preserves listings and known descriptions and reports errors in the manifest. Source-listing success does not imply every optional detail page loaded.

## Tests, files and rollback

**62 Python tests and nine scheduler tests passed.** Added cases cover ignored employer filters, valid empty teams, phantom observations, failed cross-listing preservation, retirement only after successful replacement, and independent sports-team scheduling. The live workflow passed its test step before scraping.

Changed code is itemized in the pinned production diff above. The refreshed shared [source inventory](inventory/README.md) includes file paths, physical line counts and symbol locations. The shared database schema did not change.

Local release evidence: `D:\abet_ops\jobs_scrapers\20261110_teams_repair`. Key records: `base_revision.json`, `production.patch`, `github_deployment.json`, `scheduler_deployment.json`, `teams_tests.txt`, `first_live_receipt`, `robotics_live_receipt`, `tech_live_receipt`, `sportsbook_before_health.json`, and `four_scraper_proof.json`. Source-page evidence contains URLs, check times and content hashes. It is not a public credential store.

Rollback requires reverting only the affected runtime paths and updating the existing Worker with matching module configuration. Keep observation and notification history. Never restore GitHub cron while the cloud scheduler still owns sports teams. The previous runtime revision was `5303ebc33d07f07fdfa6041150e477b577b321f9`.
