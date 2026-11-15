# November 14 recovery release and cloud acceptance

## Scope and authorization

The operator requested corrections and cloud proof after two robotics failures and intermittent database query timeouts. All provider probes, regression tests, isolated PostgreSQL tests and browser checks run on GitHub-hosted Linux. The operator computer is used only for source editing, remote administration and reading downloaded evidence. No new scheduler, sender, local runtime or recurring scraper is introduced.

## Observed failure and targeted correction

Robotics runs 43574414988 and 43593376035 failed at 00:09 and 04:09 Pacific on November 14. The first had Workday HTTP 521 responses from Boston Dynamics and Rockwell Automation and a non-JSON AutoStore response; the second had non-JSON responses from Boston Dynamics and Rockwell. Successful sources still published. Run 43614011281 subsequently passed all 66 sources on the same old revision. That recovery was not a repair.

`jobradar/providers/workday.py` previously posted each CXS search page once and immediately called `raise_for_status()` and `json()`. `_fetch_page()` now retries the identical page at most three times for timeouts, connection failures, HTTP 429/selected 5xx responses and invalid JSON. It waits 1 then 2 seconds, honors numeric Retry-After up to 30 seconds, preserves the existing provider-process hard timeout, and reports offset/status/content type/CF-Ray when attempts are exhausted. HTTP 403 and invalid JSON schemas are not turned into successful empty boards. No partial list is returned after a failed later page. The same change is made in `job-radar-tech`.

These diagnostics do not prove why Workday originally returned those responses; the response body and edge request ID were not retained in the old run. This repair addresses the proven absence of recovery and improves the next failure's diagnostics.

The public robotics and sportsbook queries returned HTTP 500 / SQLSTATE 57014 at about 11:03 Pacific, then succeeded at 11:05. Later read-only EXPLAIN ANALYZE showed the robotics active/newest read processing 17,824 rows and sorting them to return 50 (1,500.503 ms). Its latest-scraped-at read scanned 27,764 rows (82.364 ms). Existing descending indexes did not match NULLS LAST plus the ID tie-breaker; robotics had no scraped_at index.

`db/migrations/20261114_job_read_indexes.sql` adds matching active/newest and freshness indexes to each of the four job tables. It is a separate one-time maintenance operation with a two-second lock timeout and 30-second statement timeout. It changes no job, application or notification history and does not reload the REST schema. Exact historic CPU/lock conditions at 11:03 were not captured; an inefficient plan is demonstrated, not asserted to be the only cause of that earlier timeout.

## Exact implementation inventory

| Path in job-radar | Purpose |
|---|---|
| `jobradar/providers/workday.py` | Bounded page retries; schema and pagination completeness retained |
| `tests/test_workday_recovery.py` | Reproduce 521/non-JSON/timeout/429, retry exhaustion, later-page failures, auth errors and verified empty results |
| `db/migrations/20261114_job_read_indexes.sql` | Eight additive indexes, two per table; no table/schema/row deletion |
| `runtime/verification/check_indexes.py` | Apply/reapply the migration in isolated cloud PostgreSQL and require index plans without Sort nodes |
| `runtime/verification/probe_workday.py` | Read the three affected actual career sources in bounded subprocesses; never publish |
| `runtime/verification/read_discord.py` | GET the latest delivery row and read its actual Discord message; require matching webhook/channel IDs; never send |
| `runtime/verification/browser_proof.mjs` | One guarded cloud browser; eight sequential real pages; GET-only routing; filters, job cards, links and screenshots; always close |
| `.github/workflows/recovery-proof.yml` | Cloud regression/recovery, teams tests, isolated database, live source/Discord/browser checks; evidence artifacts retained 14 days; no cron |

The tech repository contains the same Workday implementation/test, the same read-only Discord script, and its own small cloud regression/readback workflow so it uses its existing repository credentials. Common publisher files, notification selection policies, source inventories, the Cloudflare scheduler and the Hugging Face runtime are unchanged.

## Evidence and interpretation

Cloud proof artifacts contain `index-tests.json`, `workday-live.json`, `discord-readback.json`, `browser-proof.json` and eight screenshot PNGs. Test failures remain in GitHub history. The initial runner/browser compatibility failure and the retry-helper naming collision were found on the test branch before promotion. Static legacy controls have different labels/IDs; the browser check uses their observed IDs and does not pretend a selector failure means data was absent.

The existing recovery suites exercise database write errors and retries, a committed write with a lost response, persistence before announcing, preservation of existing jobs on incomplete observations, Discord 429/server failures, pending queue retention and retry of only unsent chunks. Teams has its own mocked HTTP and ephemeral SQLite tests in the cloud. External provider, database and Discord failures are not injected into production.

Discord success means an existing message was fetched from Discord with matching channel and webhook IDs. It does not mean a synthetic test was posted. A scrape with no new eligible jobs can finish without a new message. The legacy 773 older sports-team pending rows remain governed by the existing recency rule; this release does not resend them.

## Release and rollback

1. Require passing cloud regression, source, database-plan and browser evidence before promoting the provider changes.
2. Preserve the single four-hour staggered scheduler and single sender per module.
3. Apply the reviewed index SQL once while the scheduler reports no active scraper; verify the eight definitions and repeat the measured query plans and public reads.
4. Promote the tested branches without force-pushing or replacing unrelated changes. Record exact commits and the maintenance receipt in the final release record.
5. Start the observation interval only after deployment and verification have finished.

To roll back the provider change, restore only `jobradar/providers/workday.py` from robotics revision `0594e2058df03dfb37caca8bc5f9c96ec4dcb3d6` and tech revision `738cdfb07e0d1fac8f5fffbb524a2b29f0dfa1bc`, remove the new recovery tests that require the new behavior in the same reviewed commit, run the cloud regression checks, and promote normally. Do not rewind other commits, histories, queues or credentials.

Indexes can remain during a provider rollback. If a measured index regression requires removal, the only names added here are `<table>_active_newest_idx` and `<table>_freshness_idx` for `robotics_jobs`, `tech_jobs`, `team_jobs` and `jobs`. Drop only those eight indexes in separate controlled maintenance; do not run full schema recreation or reset a table. A lock timeout is a refusal to perform maintenance, not a reason to repeatedly hammer the database.

## Sustained acceptance

Seven calendar days cannot be claimed on release day. At the existing six slots per day, the target is 42 scheduled runs per scraper, with complete source receipts, fresh persisted data, readable boards, and no overdue eligible deliveries. Any failed slot must be reconciled with its next recovery and any unsent queue. The existing Cloudflare scheduler and watchdog remain the ongoing monitors; no second clock or extra scraper cadence is added for observation.

The final release record must provide the observation start/end dates and clearly say pending until enough actual scheduled evidence exists. A later review uses cloud run receipts, the scheduler's slot/last-success data, Supabase run/notification tables and Discord readback. No future success is assumed from today's green check.

## Maintenance receipt

The index migration completed in production on November 15 at 00:23:07 UTC (November 14, 16:23 Pacific), HTTP 201. The scheduler was healthy with no active scraper. File SHA-256 as administered from Windows: `26d55992653caec5182e562136e013e78a41558c9c907cbd574a85266081cee2`.

Cloud run 43657582859 passed the robotics recovery suite, teams recovery suite, isolated PostgreSQL index tests, all three real Workday probes, and three Discord readbacks. Tech run 43657285357 passed 78 tests (four scheduler tests skipped because scheduler source lives in the robotics repository) and actual tech Discord readback. Workday live counts: Boston Dynamics 85, AutoStore 37, Rockwell 443.

After maintenance, all eight production query plans used the intended indexes, with no Sort node. Measured robotics active/newest execution changed from 1,500.503 ms to 67.153 ms and freshness from 82.364 ms to 5.119 ms. These are observed executions, not latency guarantees. The sportsbook baseline and after samples were 16.479 ms and 35.915 ms respectively; the structural improvement is scanning only the requested range instead of sorting the active set, and wall-clock variation still needs observation.

The first full browser run rendered all eight pages with jobs; all four dashboard controls passed. Two standalone controls encode active as `1`, not `active`, and all as an empty string. The final assertion uses those observed values; no application code was changed to satisfy the test. Final run IDs and the provider promotion commits are recorded in the release receipt after completion.
