# Discord wiring verification and documentation status

Observed November 11, 2026, approximately 01:41–01:45 Pacific. This supplements the complete coverage/browser proof; it does not replace historical receipts.

> **Correction, November 11 at 02:25 Pacific:** this audit overlooked the watchdog job announcer when assessing recovery. The user subsequently supplied a live sportsbook Discord receipt. Versioned watchdog code already has persistent KV-cursor recovery, confirmed by offline tests. Statements below about a system-wide recovery gap are superseded by the [correction report](2026-11-11%200225%20Sportsbook%20Delivery%20Correction%20and%20Recovery%20Evidence.md); the original observation timestamps and read-only audit records remain historical evidence.

## Answer at the time of this audit

All four scraper runtimes passed the fresh read-only configuration/health inspection with zero warnings. Robotics, tech and sports teams have verified production Discord destinations and confirmed delivery records. Robotics and tech additionally passed direct readback of existing messages through their production webhooks. Sportsbook is healthy and the operator-store webhook is valid, but its current live-runtime Discord path is only partially verified. An unconditional four-module Discord all-clear would exceed the evidence.

| Module | Destination and delivery evidence | Latest confirmed delivery in Pacific time |
|---|---|---|
| Robotics | Production secret resolved to the robotics webhook; Discord metadata HTTP 200. Two existing messages read back with HTTP 200 and matching channel/webhook IDs. | November 10, 11:14 p.m.; latest message contained three job embeds. |
| Tech | Production secret resolved to the tech webhook; Discord metadata HTTP 200. Two existing messages read back with HTTP 200 and matching channel/webhook IDs. | November 11, 1:38 a.m.; latest message contained two job embeds. |
| Sports teams | Production secret resolved to the expected sports-teams-jobs channel. Discord metadata HTTP 200 and database delivery records agree with the earlier successful 18-job/four-message run. | November 11, 12:04 a.m. |
| Sportsbook | Operator-store webhook metadata HTTP 200. Deployed Space is RUNNING and reports healthy. The latest scheduled run had `discord_notify_ok=null`, meaning no recorded notification attempt. | No current runtime-originated delivery certified by this audit. |

The three GitHub production workflows were read directly and map their publishers to the audited secrets: repository-scoped `DISCORD_WEBHOOK_JOBS` for robotics and tech; `DISCORD_WEBHOOK_TEAMS` for teams. The channels are distinct. Teams' queue does not retain Discord message IDs, so its evidence is webhook metadata plus acknowledged delivery records and publisher logs, not a message readback.

Sportsbook's runtime source reads `DISCORD_WEBHOOK_JOBS` from the Space environment. The operator copy is not proof of the Space's current secret value. The control token for its protected notifier test is unavailable; no token was reset and no test message was sent. The next scheduled sportsbook slot is 3:00 a.m. Pacific on November 11; a slot without new eligible jobs may produce no notification. The HF direct sender has no persistent failed-alert queue. This audit incorrectly generalized that fact to the whole system: the separate watchdog announcer already has persistent KV-cursor recovery. See the correction above.

## Read-only audit execution

- [Robotics and teams audit](https://github.com/misterplusev/job-radar/actions/runs/42997275403), revision `c9d005d670d22be5f679ee5006846459463e4f1b`.
- [Tech audit](https://github.com/misterplusev/job-radar-tech/actions/runs/42997287833), revision `d008031e6f135d6407e7347c8f6a90daceba6da7`.
- Both use branch `codex/discord-wiring-audit-20261111`. Their branch-specific `.github/workflows/pipeline.yml` has only `workflow_dispatch`, a five-minute timeout, read-only repository permission and no notification send step. Production branch workflow files were unchanged.
- Script: `audit_discord_job_routes.py` at each pinned audit revision, 70 physical lines, SHA-256 `048c9432282c94c15a3833636d29c344d63b00a922e0e4e51027076f23c2b44b`. It performs bounded GET requests for webhook metadata, at most ten delivery rows per module, and at most two existing messages per module. It records identifiers and timestamps, never webhook URLs, tokens or message bodies. It makes no Discord POST requests and no database writes.
- Local evidence: `D:\abet_ops\jobs_scrapers\20261111_discord_audit`, including dispatch revisions, per-module results, sportsbook runtime inspection and `summary.json`. Fresh runtime receipt: `D:\abet_ops\jobs_scrapers\20261111_discord_runtime_verification.json`.

No production source, secret, pause flag, schedule, application record or delivery state was changed. No browser, agent or test message was started by this audit.

## Documentation coverage and explicit boundaries

The [documentation entry point](README.md) links architecture, repositories and deployment branches, cadence, data flow, secret names/scopes, provider registries, database tables/views/functions/policies, Discord behavior, dashboard wiring, all eight live URLs, operational checks, recovery/rollback and the guide for another industry scraper.

The [itemized inventory](inventory/README.md) contains 3,762 file entries across pinned source/runtime snapshots, with physical line counts and symbol locations for eligible source text. Binaries, generated datasets and private content are metadata-only; snapshots from different branches are not a count of unique code. The dashboard snapshot includes unrelated dashboard modules. The latest verification reports cover final source changes and screenshots; documentation-only commits after a pinned inventory do not change its stated revision.

The documentation is sufficient to locate and maintain the system without reconstructing its architecture. It explicitly does not claim complete deployed-source inspection of the sportsbook watchdog: current credentials cannot read that deployment. Its versioned source and working public endpoint are recorded. This audit did not establish deployed watchdog-source parity. Later user-provided delivery evidence and persistent-cursor tests supersede its assessment of sportsbook recovery and current delivery. Optional missing job descriptions and the robotics standalone relevance-filter difference remain visible.

Do not equate a green scrape, zero audit warnings, an existing secret name or a valid local webhook with end-to-end Discord delivery. Future verification should preserve the distinction between configuration, destination metadata, confirmed HTTP acceptance, stored acknowledgement and an actual message readback. Test failure recovery with mocks rather than sending duplicate jobs.
