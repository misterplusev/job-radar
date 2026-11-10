# Jobs board UI contract — November 10, 2026

All four standalone boards and four ABET dashboard modules use the same core filtering and sorting behavior. Their layouts evolved independently: robotics/tech use HTML tables, teams uses HTML cards, sportsbook uses Next/React, and ABET uses React widgets. Different ATS providers do not require different default filters. This change normalizes behavior while retaining application marking and existing source-health links.

## Defaults and semantics

- Status: active only. Closed/all controls remain available. Existing applied filters remain where supported; teams' application marks remain browser-local.
- Geography: stated U.S. locations only. The unchecked **Include international & unspecified locations** control broadens to every location. A company being American does not establish that a particular job is U.S.-based. Blank, Remote, Hybrid, Distributed and ambiguous abbreviations are unspecified. This is location inference, not a guarantee of work authorization or hiring eligibility.
- Sort: employer posting date, newest first. Parse timestamps numerically, including timezone offsets. Null, dash and invalid dates sort last in BOTH date directions. Never substitute discovery or refresh time for an employer date. Unknown dates display **Date not provided**. Discovery/last-observed dates remain distinct fields.
- Start with: 100, 200, 500 or All. Numeric selections render that initial quantity and a Show more button. All starts with 200 and adds 200 on scroll; no matching records are permanently capped. The button remains a fallback if IntersectionObserver is unavailable. Changing filters resets the initial quantity.
- All matching records participate in sorting/filtering, including records after the first database response. Avoid filtering only the first server page and presenting it as the complete result.
- Logos: existing standalone brand assets and actual team `logo_url` values, with initials when an asset is absent or fails. Do not fabricate brand logos. All ABET jobs widgets use the existing canonical `AbetChipLoader`; sportsbook standalone copies that component. Static boards use its existing chip visual and reduced-motion behavior.

## Source map

Canonical shared behavior: `docs/job-scrapers/ui/job-board-core.mjs` in job-radar; operator copy `D:\abet_ops\jobs_scrapers\ui\job-board-core.mjs`.

| Surface | Core copy | View code |
|---|---|---|
| ABET | `src/lib/jobBoardCore.mjs` | `src/widgets/IndustryJobsWidget.jsx`, `src/widgets/JobsBrowserWidget.jsx`, shared `src/lib/useJobVisibility.js` |
| Robotics standalone | `job-board-core.mjs` | `index.html`; legacy `browse_all.html` redirects here |
| Tech standalone | `job-board-core.mjs` | `index.html`; legacy `browse_all.html` redirects here |
| Sportsbook standalone | `app/lib/job-board-core.mjs` | `app/components/JobsBoard.tsx`, `DashboardClient.tsx`, `AbetChipLoader.jsx` |
| Teams standalone | `sports_teams/board/job-board-core.mjs` | `sports_teams/board/live.html` |

Keep all five core copies byte-identical and increment `JOB_BOARD_VERSION` for behavior changes. Update the canonical file first, copy it into each frontend, test each frontend and publish all five repositories. Do not update only a dashboard widget and leave the standalone views behind.

## Data, loading and safety

`fetchAllJobRows` accepts only the four public job tables, uses ordered ID keyset pagination, and continues until an empty response (including servers whose page cap is less than 1,000). It deduplicates IDs, rejects malformed responses and stalled pagination, allows cancellation, and has a 180-second/100-request bound. Hitting the bound is an error, not a silently truncated board. Metadata is fetched first; descriptions load on demand. Application tables and credentials are not part of this helper. Existing application handlers were retained rather than invoked during verification.

The teams standalone now reads `team_jobs` directly with the same existing public read key used by the other static boards. This allows closed/all filters. The published `team_jobs.json` feed remains active-only for existing consumers; its semantics were not changed. Descriptions are read only when expanded. `health.json` and coverage artifacts retain the pipeline's actual receipts.

The normal sports-teams workflow copies the shared `.mjs` asset alongside `index.html`. A separate manually dispatched `.github/workflows/sports-teams-board.yml` publishes UI changes while preserving the latest public feed, coverage and health receipt. It does not run scrapers or send Discord notifications. It shares the existing `sports-teams-jobs` concurrency group, so board deployments do not race the scheduled pipeline. Scraper cadence and delivery settings are unchanged.

## Verification and rollback

- ABET: `npm run test:job-modules`, `npm run build`; `node scripts/verify-job-ui-render.mjs` additionally checks real React rendering without a browser. The latter expects the operator's sportsbook checkout at `D:/abet/sportsbook-jobs-dashboard`.
- Sportsbook: `npm ci --no-audit --no-fund`, `npm run build`.
- Static pages: extract module scripts and run `node --check`; confirm selected active/newest/100 controls and unchecked international toggle.
- Core tests cover offset-aware chronology, missing dates, location ambiguity, combined filters, All reaching every row, server pagination caps, failed/cancelled pagination, and logo URL safety.
- Fixture verification ran against 38,681 cached rows. Raw fixture data stays local. No application writes were executed.
- Verify live HTTP pages, shared asset hashes, compiled bundles and representative logo URLs after publishing. Browser visual QA was not performed because the operator's machine-wide stop switch forbids browser launches.

For rollback, restore the previous frontend files and their matching core copies together using the publication receipt's before/after commits. No database migrations are part of this change. Do not roll back unrelated scraper changes or remove notification receipts.
