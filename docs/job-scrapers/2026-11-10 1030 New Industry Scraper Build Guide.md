# Build another industry job scraper — November 10, 2026

This is a build specification and reference map, not a claim that any existing repository is a clean one-command template. A new session should read the [architecture](2026-11-10%201030%20Job%20Scrapers%20Architecture.md), inspect current source, then follow this contract. Existing credentials and authorization for the chosen deployment destinations are prerequisites. No new scraper or channel is created by this document.

## 1. Define the industry before collecting jobs

Choose a module ID such as `healthcare_jobs`, an explicit employer list, geography, inclusion/exclusion rules and the operator's desired cadence. Separate collection breadth from alert relevance. A healthcare employer can have finance/operations jobs worth storing even if a clinical role should not alert this user.

Each employer needs a stable organization ID, display name, official website, official careers URL, exact linked ATS board, provider type and evidence date. For parent companies, preserve the parent/employer relationship. Do not label parent-company jobs as exclusively belonging to a subsidiary. Do not auto-add production sources from aggregator search results or old job URLs.

Suggested registry record:

```json
{
  "organization_id": "example-health",
  "organization_name": "Example Health",
  "official_home_url": "https://example.org",
  "official_careers_url": "https://example.org/careers",
  "source_id": "example-health-primary",
  "source_type": "greenhouse",
  "source_url": "https://job-boards.greenhouse.io/examplehealth",
  "source_slug": "examplehealth",
  "career_link_verified": false,
  "link_evidence": null,
  "verified_at": null
}
```

This is an illustrative placeholder, not a verified employer or live source. Mark linkage true only after inspecting the actual careers page and its outbound link/redirect. Independently prove that the endpoint returns valid listings, pagination and an employer identity. Store a bounded evidence receipt. Preserve “blocked” or “unproven” when that is the result.

## 2. Reuse specific modules, not stale assumptions

| Need | Reference implementation | Adaptation required |
|---|---|---|
| Greenhouse/Lever/Ashby/Workday adapters | `jobradar/providers/` in robotics/tech | Supply new targets; verify employer identity, pagination and explicit errors |
| Industry-specific providers | Sportsbook `scripts/providers/` on `prod/sportsbook-jobs` | Implement `company` and `scrape()`; adapt outputs to the new module model |
| Organization registry and official-link proof | Teams `official_careers_registry.json`, `sources.json`, `live_refresh.py` | Replace sports inventory; retain independent source/link proof |
| Observation-based retirement | Teams persistence and source observations | Namespace tables; preserve jobs when a source fails or crosslists remain |
| Durable delivery | Teams `publish_teams.py`, notification state and tests | New channel/secret; retain pending state and per-chunk acknowledgement |
| Scheduled cloud worker | `.github/workflows/sports-teams.yml` or robotics/tech workflow | Own workflow/concurrency group, deadlines and secrets; no duplicate scheduler |
| Manifest-based long-running service | Sportsbook launcher/bundle builder | Use only if this runtime is needed; own service and schedule |
| Searchable board | Teams `board/`, or separate robotics/tech static frontends | New table/API, title, filters, branding and deployment destination |

Review the exact production revision before copying. Some older adapters catch errors and return an empty list; that is unsuitable for authoritative closure decisions. A future timeout around a thread does not necessarily stop a blocked network call when an executor exits. Require HTTP timeouts and a whole-run deadline. Old schema/application policies may permit anonymous writes; do not copy those into the new module. Optional skills matching and resume generation are not required for an industry scraper.

Suggested layout:

```text
README.md                    # module purpose and shared-doc pointer
sources.json                 # explicit employer/source registry
providers/                   # bounded HTTP adapters
models.py                    # normalized job + source receipt types
ingest.py                    # source collection and persistence
publish.py                   # durable pending -> delivered queue
db/                          # namespaced migrations and RLS
board/                       # searchable jobs and health/coverage
tests/                       # pagination, failure, dedup, delivery tests
requirements.txt
.github/workflows/jobs.yml   # one production scheduler
```

Do not import the full legacy runtime merely to discover providers: imports can have side effects. Start with bounded HTTP and fixtures. On the operator machine, browser/agent stop switches and resource rules apply; do not add browser loops or evade blocked sites.

## 3. Establish data and observation contracts

A normalized job needs stable employer/source identity, canonical application URL, requisition ID when available, title, location/remote status, employer description and salary evidence, source URL, employer posting timestamp (nullable), immutable discovery time, latest observation time and active state. Preserve raw evidence separately from normalized text. Unknown pay stays unknown. Never invent a posting date or salary to make an alert look fresh or desirable.

A source receipt needs run ID, source ID, start/end, status (`success`, `verified_empty`, `blocked`, `error`, `timeout`), observed count, pages fetched, completeness flag and sanitized failure detail. Separate listing completeness from optional detail enrichment. A detail error need not discard a valid listing or its prior description.

Pagination must follow the provider's actual next-page/cursor mechanism until exhaustion, with maximum page/job/time guards and repeated-page detection. Hitting a guard is incomplete, not success. Empty is valid only when the endpoint is positively identified as the intended employer board and its response actually establishes zero openings.

Create separate namespaced tables, for example:

- `healthcare_jobs`: stable primary key, employer plus canonical URL uniqueness, posting/discovery/observation dates, content and active state.
- `healthcare_job_observations`: source/run/job presence and completeness evidence.
- `healthcare_job_scrape_runs`: aggregate run state and source receipts.
- `healthcare_job_notifications`: unique job/destination identity, pending/delivered status, attempts, last error, delivery timestamp and returned message ID where supported.
- `healthcare_applications`: authenticated owner ID, job ID, status and timestamps, with owner-scoped RLS.

Use additive migrations. Give the public frontend only the minimum read access to public job data. Keep service credentials server-side and application records private. Make first-seen immutable across upserts, retries, aliases and rebuilds. Only retire a missing job when every relevant observation needed for that decision is complete; one failed alternate source must not erase still-active crosslisted jobs.

## 4. Make alert retries survive a crash

Treat job persistence and enqueueing as one atomic database operation where feasible, or use a recoverable reconciliation pass. A successful upsert followed by a failed Discord call must leave pending delivery state. Relevance/date rules should be explicit and should not rewrite employer data.

Send individual job embeds with direct employer application URLs, company, location, source, employer date if known and relevant salary evidence. Keep title/link content faithful. Use batches of five embeds, rate-limit-aware waits and bounded retries. Honor Discord's retry response, persist unsent items, and stop after a documented run budget. A successful chunk should be acknowledged before proceeding to the next.

Document the unavoidable crash window between remote acceptance and local acknowledgement. Use stored message identifiers/reconciliation where possible; do not claim perfect exactly-once delivery. Never mark a failed message as delivered merely to drain the queue.

For the first population, explicitly choose whether existing jobs are seeded without alerts or sent as a catch-up. Keep a preview and preserve that decision in the deployment receipt. After initialization, ordinary runs alert eligible newly discovered jobs. Do not add an unexplained 20-job cap or silently replace individual job alerts with a summary.

## 5. Give it one scheduler and observable health

Choose one runtime. A GitHub Actions worker should have its own concurrency group, explicit UTC cron, manual trigger, hard job deadline, bounded provider execution and durable storage. GitHub timing can slip; record actual starts and due-slot age. A service launcher should have an explicit IANA timezone, serialized execution, whole-process timeout, termination handling and manifest-based health. Neither should spawn autonomous agents.

Health should expose intended schedule, last actual start/end, last successful complete observation, next due slot where applicable, expected/success/empty/failed sources, job counts, pending eligible alerts and delivery status. Keep scrape success distinct from notification success and frontend deployment. Publish source coverage from current receipts, not a count of configured employers. A healthy exit code alone is insufficient.

Set up the industry's own secret names/destinations and verify channel identity without leaking the webhook URL. Namespaced database tables do not require duplicating the entire Supabase project. A module must never accidentally publish into another industry's channel or retire another industry's jobs.

## 6. Acceptance evidence before claiming completion

Use meaningful tests against fixtures and a bounded read-only source proof, then an authorized end-to-end deployment:

1. Every intended employer has an explicit registry record and official career link evidence, or a clearly listed unresolved status. A valid ATS response alone is insufficient.
2. Multi-page and empty fixtures prove pagination and completeness. HTTP 403, 429, 500, timeout and malformed JSON produce explicit failure receipts.
3. A second identical ingest makes no duplicate job rows, preserves first-seen, and creates no second notification for delivered jobs.
4. A successful complete disappearance can retire a job. Failed/incomplete sources and crosslisted active observations cannot falsely retire it.
5. Simulated Discord failures preserve pending work; successful chunks remain acknowledged when a later chunk fails. Restart tests verify recovery without resetting the queue.
6. Public board URLs open the employer's actual application listing. Source, employer, salary and dates match captured evidence. Private application state and secrets are absent from public outputs.
7. Production evidence identifies source commit, migration version, runtime revision, schedule, destinations, first run receipt, subsequent unchanged run, coverage gaps and rollback target. Inspect scheduled execution separately from manual tests.

Finish by adding the module to `scrapers.json`, extending the read-only verifier for its runtime/health contract, linking this package from its README, and documenting the owner and exact deployment path. Keep the source registry, schema, provider contract, tests and operational notes together so the next session can reproduce the result instead of discovering it from Discord history.
