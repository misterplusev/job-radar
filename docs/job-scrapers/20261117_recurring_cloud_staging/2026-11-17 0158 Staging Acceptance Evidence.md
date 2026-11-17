# Recurring staging acceptance evidence

Observed November 17, 2026 UTC. The cloud development environment has completed its first automatic cycle for all four modules. The proposed Workday repair has NOT passed live acceptance. Production remains at its temporary twelve-hour cadence.

## Actual automatic cloud runs

All four were dispatched by the new Durable Object alarm, not manually dispatched from a laptop. Every run reported back into isolated persistent staging storage. Their red Actions conclusions reflect real failed canaries, not a missing scheduled environment.

| Module | Cloud run | Regression result | Live result |
|---|---|---|---|
| Robotics | [43997984357](https://github.com/misterplusev/job-radar/actions/runs/43997984357) | 112 tests passed | Boston Dynamics: five requests, HTTP 429 retry exhaustion. Anthropic: original 4 MiB response cap exceeded. |
| Tech | [43998255324](https://github.com/misterplusev/job-radar-tech/actions/runs/43998255324) | 89 tests completed successfully; four expected skips | Cloudflare and Stripe exceeded original 4 MiB response cap. This is a staging budget result, not proof those sources are down. |
| Sports teams | [43998385133](https://github.com/misterplusev/job-radar/actions/runs/43998385133) | 74 tests passed | AMBSE Workday: five requests, HTTP 429. Houston Texans official TeamWork Online route: one request, four valid jobs; sample persisted. |
| Sportsbook | [43998642966](https://github.com/misterplusev/sportsbook-jobs-dashboard/actions/runs/43998642966) | 15 Workday + 17 launcher tests passed | BetMGM: twelve guarded requests across provider attempts, ending in HTTP 429 retry exhaustion. |

Total regression cases reported: 307, including the four expected tech skips. No staging production-database writes or Discord sends. Staging run results, sample jobs, exact SHA, HTTP metadata and cooldowns are visible in [live status](https://abet-jobs-staging.abetscrape.workers.dev/status).

The first controller/sandbox revision passed fourteen controller tests and three HTTP guard tests in [43997219658](https://github.com/misterplusev/job-radar/actions/runs/43997219658). The measured response-limit failures led to an isolated harness revision, `81e39fa9978f2cae0eded5d95e46c1a12ee86f6c`: 16 MiB per response, 24 MiB per source, same request/time limits, plus removal of the unused HTTP server mode. Four guard tests, including streamed and cumulative byte-limit enforcement, and all fourteen controller tests passed in [43998776166](https://github.com/misterplusev/job-radar/actions/runs/43998776166). The prior failures remain recorded; this change does not retroactively mark them successful.

## Persistence and production isolation

`before-redeploy-state.json`, `after-redeploy-state.json` and `persistence-proof.json` record a real staging controller redeploy after all four initial receipts. All five checks passed: still enabled; same run count; durable alarm still present; all four latest receipts unchanged; every observed source state/cooldown/sample unchanged.

`deployment-parity-proof.json` records exact remote deployment versions and GitHub branch comparisons. Production scheduler version remains `2b3d123d-3f56-4532-a556-efa7495fea36`; private production sportsbook Space remains `7026b4a72b90747c13d6b94f426044f8bdf40cf8`. Branch changes during this build are documentation or the newly registered staging workflow. No production collection code, sender, job schema or twelve-hour cadence was replaced.

The production health endpoint still reports existing robotics/teams failures and sportsbook degradation, while its database check is healthy and tech's last run succeeded. This build does not relabel those failures fixed. The sportsbook staging workflow additionally had to be registered on repository default branch `main`; its actual run uses `prod/sportsbook-jobs`. Registration completed before the first sportsbook lease was dispatched successfully.

## Remaining acceptance

- Recurrence verified: the 02:05 UTC robotics slot started automatically after redeployment, completed, and saved another receipt. See the second-cycle evidence below.
- Final bindings verified: only STAGING, GITHUB_TOKEN, REPORT_TOKEN and CONTROL_TOKEN remain. Obsolete HF_READ_TOKEN and RUN_TOKEN were removed; Cloudflare settings propagation was then verified. See binding-cleanup-proof.json.
- The second robotics cycle exercised the enlarged response guard. Its actual source outcomes are below; initial tech/Anthropic budget failures remain recorded until their scheduled rechecks.
- Restore actual Workday access before calling the candidate repair proven. Longer retries alone still yielded 429s.
- Continue source rotation; initial observations cover seven source routes, not all registered sources. Six sportsbook transports remain outside this HTTP sandbox. Full-source acceptance and an isolated production-schema integration exercise are not established.
- No automatic promotion is enabled. New acceptance evidence must identify the tested revision and actual scope.

## Durable handoff and source package

Start with `2026-11-17 0113 Staging Build Handoff.md`, then `2026-11-17 0150 Recurring Staging Operations.md`. `2026-11-17 0155 Staging Source Inventory.md` and `source_inventory.json` give every active staging file's absolute location, line counts, hashes and static function/class positions. The operations guide explains workflow, accounts, schemas, resource budgets, failure diagnosis, pause/resume and rollback. Raw state/deployment receipts live in this directory. No secrets are included in the review package.

## Second automatic cycle and final deployment

Observed 2026-11-17T02:07:43.779070+00:00: [44000337581](https://github.com/misterplusev/job-radar/actions/runs/44000337581) completed the next scheduled robotics slot, `2026-11-17T02:05:00.000Z`, with 112 regression tests passing. Live results: workday:rockwellautomation: failed, 0 jobs, 5 requests; greenhouse:stripe: passed, 791 jobs, 1 requests. Its harness SHA was `34670ee4687d8d6346c195d3c286e02a2312778a`. Boston Dynamics was not re-requested while its persisted cooldown was active. The controller remained enabled through deployment, with five run receipts and a future alarm; this task sent no manual tick or workflow dispatch for this cycle. `recurrence-proof.json` records the comparisons.

Final controller version: `edf0ca19-1015-4cf6-9d90-705993bae74a`. Controller/harness source revision `34670ee4687d8d6346c195d3c286e02a2312778a` passed [44000280990](https://github.com/misterplusev/job-radar/actions/runs/44000280990): fifteen controller tests plus four HTTP guard tests. The final added test verifies that an outage producing only timeout receipts still enforces the seven-day retention rule. Production code remains unchanged; recurring staging is operational, while full Workday repair acceptance remains blocked by real source failures.
