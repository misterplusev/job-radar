# Job scraper execution requirements

User instruction reaffirmed November 13, 2026: **CLOUD ONLY. No local-machine execution.**

- All four job scrapers, their schedules, databases, delivery workers, integration tests, and runtime verification must run on cloud infrastructure. The user's computer must not be required for operation or recovery.
- Do not launch local scrapers, provider workers, PostgreSQL instances, test databases, browser automation, or local runtime substitutes. Do not present local test results as cloud or production verification.
- Local source/document inspection and remote API administration are distinct from runtime execution; they do not authorize local scraper or database processes. Keep actual execution and tests in the cloud.
- Use the existing cloud system documented in RUNBOOK.md: one Cloudflare scheduler; GitHub Actions for robotics, tech, sports teams, and the sportsbook sender; the existing Hugging Face sportsbook runtime until a replacement is proven and authorized; Supabase for shared data; existing hosted boards and dashboard.
- Preserve the single-sender-per-module rule, temporary twelve-hour staggered cadence (November 16 user instruction; see RUNBOOK.md), free-tier constraints, histories, and existing operator holds. Do not create a second clock or sender.
- The November 13 shared-engine local candidate is undeployed and is NOT evidence that the cloud system is fixed. Its local PostgreSQL harness is not an authorized next step. Port any further tests to a reviewed cloud workflow before execution.
- Report actual cloud run links, source coverage/failures, persistence results, and delivery receipts. Distinguish infrastructure availability from complete source collection and delivery. Never call a degraded source run fully healthy.
- Consult this file and RUNBOOK.md before implementation or verification. A local path in older documentation is not permission to run a local service.

- Authorized recurring staging, November 17 UTC: `abet-jobs-staging` is a separate isolated cloud clock, not a second production clock. Use the dedicated staging runbook linked from RUNBOOK.md. It may dispatch only `staging-recurring.yml`, has no production database/Discord credentials, and performs bounded canaries plus fixtures. Keep production at twelve hours. No automatic promotion; existing Workday failures remain unproven.
