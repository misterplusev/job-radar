# ABET isolated cloud staging runner

Runs on GitHub-hosted Actions through `ci_run.py`. The separate Cloudflare Worker `abet-jobs-staging` owns the schedule and persistent SQLite-backed receipts. There is no timer, boot scrape, HTTP server, production database credential or Discord webhook in this runner.

Workflow: `.github/workflows/staging-recurring.yml` in each owning repository. It checks out this harness and the exact candidate SHA independently. `ci_run.py` verifies an active staging lease before invoking `server.py` as a library; it never starts a local service. `live_probe.py` calls the real candidate provider with the network/request/response/deadline guard. Regression fixtures execute with external networking disabled.

The earlier Hugging Face Docker proposal was abandoned after the API required a paid plan. The old Dockerfile is historical and not an execution/deployment instruction. Do not create a staging Space or run this on the user's computer.

Read the current [staging operations guide](https://github.com/misterplusev/job-radar/blob/master/docs/job-scrapers/20261117_recurring_cloud_staging/2026-11-17%200150%20Recurring%20Staging%20Operations.md) and [live results](https://abet-jobs-staging.abetscrape.workers.dev/). Passing regression tests or a few canaries does not establish restored access to every employer.
