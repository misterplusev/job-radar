# ABET job scrapers — start here

Verified against deployed configuration and recent executions on **November 11, 2026**. This is the shared entry point for the robotics, tech, sportsbook and sports-team job scrapers. Owner: ABET / Chris; maintainers are the operator and sessions assigned to this system.

1. [Architecture and source-of-truth map](2026-11-10%201030%20Job%20Scrapers%20Architecture.md) — repositories, branches, runtimes, schedules, storage, alerts, boards and actual differences.
2. [Operations and verification](2026-11-10%201030%20Job%20Scrapers%20Operations%20Runbook.md) — read-only inspection, diagnosis, deployment and rollback boundaries.
3. [Build another industry scraper](2026-11-10%201030%20New%20Industry%20Scraper%20Build%20Guide.md) — implementation contract, file map, source verification and acceptance evidence.
4. [Machine-readable inventory](scrapers.json) and [read-only verifier](verify_scrapers.py).
5. [November 10 verification receipt](20261110_verification.json) — a historical snapshot; rerun the checker for current state.
6. [File-by-file inventory and live database dictionary](inventory/README.md) — paths, revisions, line counts, definitions, workflows and schema objects.
7. [Dashboard module URLs, wiring and inventory guide](2026-11-10%201145%20Dashboard%20Jobs%20Wiring%20and%20Inventory%20Guide.md) — all eight standalone/dashboard links and the actual data flow.

8. [Shared jobs UI defaults and maintenance contract](2026-11-10%201235%20Jobs%20Board%20UI%20Contract.md) — filters, dates, logos, loaders, source map and deployment checks.

9. [Dashboard presentation parity proof](2026-11-10%201345%20Dashboard%20Presentation%20Parity%20Proof.md) — shared components, live links, comparison preview and deployment evidence.

10. [Tech and robotics diagnosis, November 10 at 20:04 Pacific](2026-11-10%202004%20Tech%20and%20Robotics%20Scraper%20Diagnosis.md) — historical evidence of missing hourly starts, failed cleanup and error-handling defects. See the production repair below for current status.

11. [Tech and robotics production repair](2026-11-10%202135%20Tech%20and%20Robotics%20Production%20Repair.md) — deployed code, alarm scheduler, durable queues, cleanup reconciliation, tests, live receipts and rollback. This supersedes the diagnosis/review-only status above.

12. [Sports teams repair and four-scraper verification](2026-11-11%200010%20Sports%20Teams%20Repair%20and%20Four%20Scraper%20Verification.md) — historical source repair and delivery receipts. The final audit gaps are closed by the complete verification below.

13. [Complete 124-team coverage and eight live production views](2026-11-11%200105%20Complete%20Team%20Coverage%20and%20Independent%20Jobs%20Module%20Proof.md) — official Bulls/Clippers/Bucks proofs, screenshots, independent runtime receipts and the installed dashboard revision.

14. [Discord wiring and documentation verification](2026-11-11%200145%20Discord%20Wiring%20Verification%20and%20Documentation%20Status.md) — production webhook checks, existing-message readbacks, fresh health results and the historical limits of that audit. The correction below supersedes its blanket sportsbook recovery claim.

15. [Sportsbook delivery correction and recovery evidence](2026-11-11%200225%20Sportsbook%20Delivery%20Correction%20and%20Recovery%20Evidence.md) — user-confirmed live delivery, existing persistent watchdog recovery, a reproduced timestamp edge case, and the exact boundary between deployed and staged work.

Canonical version-controlled copy: [job-radar/docs/job-scrapers](https://github.com/misterplusev/job-radar/tree/master/docs/job-scrapers). Local operator copy: `D:\abet_ops\jobs_scrapers`. The four module READMEs link here. Consult live source and a fresh verification receipt when these documents disagree with production; update both the inventory and the prose after a change.

```powershell
& 'C:\Program Files\Python314\python.exe' -X utf8 'D:\abet_ops\jobs_scrapers\verify_scrapers.py'
```

Requires existing GitHub CLI authentication. This performs bounded GET requests and writes a local JSON receipt. It does **not** run scrapers, start browsers or agents, send messages, apply SQL or change schedules. Default exit zero means the inspection finished; inspect `warnings`, or use `--strict` to fail on warnings. It is an inspection tool, not a newly installed monitor.

## Current limits a new session must know

- Robotics, tech and sports teams use one Cloudflare Durable Object alarm scheduler for hourly dispatch, with GitHub Actions for execution. Sports teams joined after its GitHub schedule showed multi-hour gaps. A configuration declaration alone is not cadence proof.
- Historical diagnosis: tech/robotics had 26 scheduled starts each instead of 168, and oversized robotics cleanup requests left 3,136 matching rows active. The evening production repair replaces scheduling, batches cleanup, exposes failures and adds persistent notification queues. Consult the release receipt for live verification, rather than interpreting that historical diagnosis as current state.
- Sportsbook is healthy on its **Hugging Face** schedule, every two hours from 06:00 through 20:00 Eastern, every day. Its legacy GitHub workflow is disabled and has no schedule on the default branch.
- Sports teams passed 152/152 sources with 124/124 official career-route evidence records. Bulls, Clippers and Bucks were completed through rendered official-page observations on November 11. Composite health is healthy. The public proof gallery includes all eight live board/dashboard views; this remains a dated verification, not a future uptime guarantee.
- Teams, robotics and tech have durable notification queues. Sportsbook has a separate watchdog announcer with a persistent KV cursor in versioned source; mocked tests confirm that a failed send retains the cursor and retries successfully. The user supplied a live November 10 delivery receipt. A timestamp-boundary defect is reproduced in repository source; deployed-source parity and whether it affected a real job remain unverified. See the correction report.
- The watchdog source/configuration is inventoried, but current Cloudflare credentials cannot inspect the deployed copy. Its public health endpoint works; deployed-source parity is unverified.
- Current repositories and workflows are not interchangeable templates. The new-industry guide identifies which parts to reuse and which historical behavior to fix.

No credential values, personal resumes or application ledger belong in this public documentation. Local instructions and stop switches continue to apply. On this Windows machine, read `D:\AGENTS.md` and `D:\abet_ops\20261019_AGENT_RUNAWAY_AND_MEMORY_SAFETY_RULES_v1_0_0.md` before running tools; never clear an operator stop switch.
