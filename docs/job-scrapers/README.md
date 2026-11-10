# ABET job scrapers — start here

Verified against deployed configuration and recent executions on **November 10, 2026**. This is the shared entry point for the robotics, tech, sportsbook and sports-team job scrapers. Owner: ABET / Chris; maintainers are the operator and sessions assigned to this system.

1. [Architecture and source-of-truth map](2026-11-10%201030%20Job%20Scrapers%20Architecture.md) — repositories, branches, runtimes, schedules, storage, alerts, boards and actual differences.
2. [Operations and verification](2026-11-10%201030%20Job%20Scrapers%20Operations%20Runbook.md) — read-only inspection, diagnosis, deployment and rollback boundaries.
3. [Build another industry scraper](2026-11-10%201030%20New%20Industry%20Scraper%20Build%20Guide.md) — implementation contract, file map, source verification and acceptance evidence.
4. [Machine-readable inventory](scrapers.json) and [read-only verifier](verify_scrapers.py).
5. [November 10 verification receipt](20261110_verification.json) — a historical snapshot; rerun the checker for current state.

Canonical version-controlled copy: [job-radar/docs/job-scrapers](https://github.com/misterplusev/job-radar/tree/master/docs/job-scrapers). Local operator copy: `D:\abet_ops\jobs_scrapers`. The four module READMEs link here. Consult live source and a fresh verification receipt when these documents disagree with production; update both the inventory and the prose after a change.

```powershell
& 'C:\Program Files\Python314\python.exe' -X utf8 'D:\abet_ops\jobs_scrapers\verify_scrapers.py'
```

Requires existing GitHub CLI authentication. This performs bounded GET requests and writes a local JSON receipt. It does **not** run scrapers, start browsers or agents, send messages, apply SQL or change schedules. Default exit zero means the inspection finished; inspect `warnings`, or use `--strict` to fail on warnings. It is an inspection tool, not a newly installed monitor.

## Current limits a new session must know

- Robotics, tech and sports teams are **configured hourly**, but the recent scheduled-run histories contain multi-hour gaps. A cron declaration is not proof of hourly execution. Cause and remedy remain open.
- Sportsbook is healthy on its **Hugging Face** schedule, every two hours from 06:00 through 20:00 Eastern, every day. Its legacy GitHub workflow is disabled and has no schedule on the default branch.
- Sports teams has working source observations for 124 teams; only 118 official-career-page links are independently proved. Five alternate source routes also fail. Coverage is not silently called complete.
- Teams has a durable notification queue. Robotics, tech and sportsbook do not have the same queue guarantee; a failed alert after a successful database write can be lost.
- Current repositories and workflows are not interchangeable templates. The new-industry guide identifies which parts to reuse and which historical behavior to fix.

No credential values, personal resumes or application ledger belong in this public documentation. Local instructions and stop switches continue to apply. On this Windows machine, read `D:\AGENTS.md` and `D:\abet_ops\20261019_AGENT_RUNAWAY_AND_MEMORY_SAFETY_RULES_v1_0_0.md` before running tools; never clear an operator stop switch.
