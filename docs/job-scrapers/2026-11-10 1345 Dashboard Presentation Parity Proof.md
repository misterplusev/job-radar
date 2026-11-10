# Dashboard jobs presentation parity — November 10, 2026

The audit initially found presentation drift: the standalone boards were standardized, but dashboard headers/cards still differed. That gap is now repaired in all four dashboard modules.

- Production source: `6127ab09ab129d88eaea64fbc8890ed6e529cc43`.
- Vercel deployment: `dpl_Dtp6fRRjAZ1riqN7mnd5QCnkLr3S`, verified READY.
- Presentation version: `2026-11-10.3`.
- [Comparison preview](https://abet-dashboard.vercel.app/jobs-standard-proof.html): actual components with public samples; static preview, not a browser screenshot. Controls are disabled; live links provide the working application.
- [Published interaction results](https://abet-dashboard.vercel.app/jobs-standard-proof.json): four rendered widgets, shared headers/cards, summary collapse, scrolling, company selection, result quantities, date ordering and descriptions. Authenticated application requests were mocked; user ID handling and the anonymous gate were preserved.
- [Production verification receipt](ui/dashboard-parity-live-proof.json): deployed commit, version, exact asset imports, CSS and all four routes.
- [Publication receipt](ui/dashboard-parity-publication.json): file-by-file Git blob hashes and previous revision.

| Module | Live dashboard |
|---|---|
| Sportsbook | [Open](https://abet-dashboard.vercel.app/?section=jobs&tab=jobs-browser) |
| Robotics | [Open](https://abet-dashboard.vercel.app/?section=jobs&tab=robotics-jobs) |
| Tech | [Open](https://abet-dashboard.vercel.app/?section=jobs&tab=tech-jobs) |
| Sports teams | [Open](https://abet-dashboard.vercel.app/?section=jobs&tab=teams-jobs) |

All four use `src/widgets/shared/JobBoardPresentation.jsx`, the same original CSS as the standalone boards, two-row horizontal company panels, employer logos with fallback initials, and the canonical chip loader. Dashboard styles are scoped to the jobs widget. Status/geography/date/result-count defaults remain active, U.S., newest posted first, 100; missing dates remain last.

The complete dashboard build and 18 jobs checks passed. The original sportsbook source-health history, authentication gate, application statuses and update/delete handlers are preserved. Other industries still have their original capabilities; uniform presentation does not mean adding new application write permissions.

The published HTML preview is an artifact of the component tests. It samples public roles, displays two cards per module and labels sample counts explicitly. It is not evidence of pixel-level browser QA. The separate production receipt verifies that the corresponding code and stylesheet reached the live deployment. Existing machine stop rules prevented a browser launch.
