# ABET jobs documentation — current index and coverage

## Recurring isolated staging — November 17, 2026 UTC

A separate cloud staging controller is now enabled: [live status](https://abet-jobs-staging.abetscrape.workers.dev/). Robotics, tech and sports teams validate hourly; sportsbook every four hours, capped at 800 reserved private Actions minutes/month. It runs pinned candidate regression suites and bounded rotating live canaries, keeps its own SQLite-backed Durable Object state, and has no production database or Discord credentials. This is not a full Supabase clone or an all-source scrape every hour. Production remains every twelve hours.

[Staging operations, schema, source paths, budgets and rollback](20261117_recurring_cloud_staging/2026-11-17%200150%20Recurring%20Staging%20Operations.md); [build handoff](20261117_recurring_cloud_staging/2026-11-17%200113%20Staging%20Build%20Handoff.md). Current Workday failures remain visible and unpromoted. One production clock and one isolated staging clock serve different environments; never let staging dispatch production pipelines.

Reviewed November 14, 2026 Pacific. Scope: the four job scrapers, their cloud runtime, shared database dependencies, Discord delivery, standalone boards and installed ABET dashboard job modules. This is not an inventory of every unrelated ABET account, Worker, application or database.

**Start with this index and RUNBOOK.md.** A file labelled historical is evidence of that time, not an instruction to restore an obsolete design. No single document currently provides a complete semantic description of every function or proves that documentation can never drift.

Latest cadence change and isolated cloud validation: [2026-11-17 0029 Temporary Cadence and Cloud Validation.md](2026-11-17%200029%20Temporary%20Cadence%20and%20Cloud%20Validation.md). The November 14 acceptance is historical; ongoing Workday failures mean sustained full-source health has not been established.

## Read order for a new maintainer

1. [Execution and operating rules](AGENTS.md), then [current runbook](RUNBOOK.md).
2. [Latest recovery release and evidence](2026-11-14%20Recovery%20Proof.md): deployed commits, full production run receipts, screenshots, database indexes, rollback and seven-day observation boundaries.
3. [Fresh repository file/function inventory](20261114_documentation_audit/source_inventory/README.md): exact source revisions, filenames, hashes, physical/nonblank line counts, Python symbols, JavaScript declaration scan, imports, workflows and secret-variable names.
4. [Fresh public database dictionary](20261114_documentation_audit/DATABASE.md) and [raw catalog](20261114_documentation_audit/public_database_catalog.json): structures and permissions read from the cloud, not inferred from migration files.
5. Private operator copy: `D:\abet_ops\jobs_scrapers\OPERATOR_APPENDIX.md`, for account IDs, credential *locations/names*, cloud secret assignments and operator recovery access. No credential values belong in review packages or public repositories.
6. Database consumers and retention investigation (operator copy: `20261113_database_consumers_audit/REVIEW.txt`), metrics origin/removal (operator copy: `20261113_1900_storage_and_limits/ABET_METRICS_ORIGIN.md`), and dated storage/limits measurements (operator copy: `20261113_1900_storage_and_limits/STORAGE_AND_LIMITS.md`). Their numeric measurements retain their original dates.
7. Common sender deployment and rollback history (operator copy: `20261112_2100_common_sender_review/REVIEW.md`). Its pre-cutover sections are historical; current sender ownership is in RUNBOOK.md.

## Coverage and evidence

| Topic | Where to find it | Current boundary |
|---|---|---|
| Architecture, execution hosts, cadence, sender ownership | RUNBOOK.md sections 1–3 | Current temporary twelve-hour cloud design; one scheduler and one sender per module |
| Source repositories, branches, files, line counts and symbol locations | Fresh source inventory, seven source snapshots | Git source inventory, not proof that every hosted deployment matches its current branch |
| Each Python function/class location | Source inventory: AST ranges and imports | Indexes definitions; does not supply a full behavior/side-effect specification for every function |
| JavaScript/TypeScript functions | Source inventory declaration scan | Text scan, not complete AST/call graph; anonymous callbacks and dynamic behavior may be omitted |
| Full dashboard source | Fresh abet-dashboard inventory | Includes unrelated modules; jobs wiring guide identifies the relevant subset |
| Entrypoint-to-scrape-to-persistence-to-Discord flow | RUNBOOK.md; SYSTEM_REFERENCE.md section 3 with its pinned older revision | Main flow described; exact current symbols are in the fresh inventory |
| Cloud accounts, services, secret names and recovery credential locations | Private OPERATOR_APPENDIX.md | No secret values copied; Vercel project/team IDs are recorded from link files, while current deployment/environment/rotation details remain incomplete |
| Deployed versions and release lineage | Latest release; dated deployment receipts; operator appendix | Robotics/tech release proven; all-service deployed-bundle parity is not regenerated automatically |
| Public database schema | Fresh DATABASE.md and catalog | 30 relations, 313 columns, 46 constraints, 88 indexes, 29 RLS policies, 896 relation ACL entries, 4 triggers, 8 functions, 22 sequences |
| Database dependencies outside jobs | November 13 consumers audit and public catalog | Identified legacy telemetry/alerts/backups; not every other Supabase project or managed auth/storage object is documented exhaustively |
| Retention and archive behavior | Consumers audit; STORAGE_AND_LIMITS.md | Inactive jobs remain stored; this is latest-state retention, not immutable version history; no proven ongoing archive/offload process |
| Backups and restoration | Operator appendix, tools and dated backup receipts | Metrics backup/restore evidence exists; a complete off-machine cloud disaster-recovery/restore exercise is not proven |
| Source coverage and actual career URLs | Production manifests and source config files linked by inventory | Teams latest receipt: 152 listing routes / 124 teams; 33 optional description requests returned 403 |
| Eight hosted views and Discord endpoints | Latest release receipt, screenshots and live links | November 14 actual evidence; not a future uptime promise |
| Failure handling, deployment, rollback | RUNBOOK.md and recovery release | Recovery tests and production proof linked; seven-day observation pending |
| Resource limits and measured use | Dated storage/limits audit; runbook | Current monthly egress, billing/grace status and stable long-term storage growth are not measured |
| New industry scraper recipe | November 10 new-industry guide, interpreted through current runbook | Historical guide needs a full rewrite around current cloud-only cadence/sender; do not clone its old timers or ledger assumptions |
| Automatic documentation freshness | No enforced cross-service drift check currently | A release checklist exists below; it is a maintenance rule, not a running automation |

## What was corrected in this audit

- The start page still described hourly scheduling, the sportsbook Space's retired two-hour timer, the removed watchdog sender and an obsolete credential-access blocker. It now points to the actual current design.
- The private operator appendix had old and new sender tables contradicting each other. Current sender/account facts are corrected; dated measurements are explicitly historical.
- The old database dictionary called `sportsbook_job_notifications` unused. The fresh cloud catalog and current runbook identify it as the live ledger and include the newly added indexes.
- The old “complete system reference” was generated November 13, excluded dashboard source and did not include the latest repairs. It is labelled a dated snapshot; its source list is supplemented by the fresh seven-source inventory.
- Metadata exports now decode relation grants directly from PostgreSQL ACLs. `information_schema.role_table_grants` returned zero entries to the read-only metadata caller, which is a visibility limitation, not evidence that grants were absent.

## Required documentation update with every release

For every changed function, database object, account binding, environment variable, workflow, source configuration or hosted module:

1. Record the exact source commit and the deployed version separately. Identify the component owner, account/project, entrypoint and caller.
2. Regenerate the affected file/symbol inventory; record added/removed files and the extraction method. Preserve historical snapshots and explicit exclusions.
3. For schema changes, export the affected cloud catalog after deployment, including constraints, indexes, policies, grants, views, triggers and functions. Never infer deployed schema from an unapplied SQL file.
4. Update the workflow/secret *name* map and private credential-location register when bindings change. Never place tokens in the documentation.
5. Attach actual cloud test/run receipts and production verification, rollback instructions and known failures. Record what was not verified.
6. Update README.md and RUNBOOK.md together; mark superseded instructions so a new session cannot mistake a draft for production. Keep private operator documents out of public repositories.
7. Review the remaining gaps above. Do not label the whole documentation “exhaustive/current” merely because one component's document was refreshed.

No scraper, timer, sender, schema, credential or deployment was changed in this documentation audit. The cloud catalog was read through the read-only management endpoint. Source parsing ran as static document inspection and did not import/execute scraper code, tests or browser processes.
