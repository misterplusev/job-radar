# Complete team coverage and independent jobs module proof

Verified November 11, 2026. Owner: ABET / Chris. This report supersedes the three remaining career-link gaps and the absence of browser proof in the earlier 00:10 report.

## Result

**124/124 teams have recorded official career-route evidence; 152/152 configured sources passed the production run.** Composite sports-teams health is now healthy, with zero partial or unverified teams. All four independently hosted boards and all four installed ABET dashboard modules passed actual browser loading and control checks. This is a dated verification, not a guarantee against future employer changes or outages.

[Public coverage report](https://misterplusev.github.io/job-radar/coverage.html) · [Complete 124-team evidence](https://misterplusev.github.io/job-radar/coverage.json) · [Screenshot and receipt gallery](https://misterplusev.github.io/job-radar/verification-20261111/) · [Production run 42990654685](https://github.com/misterplusev/job-radar/actions/runs/42990654685)

## Final three official-page proofs

| Team | Official career page | Observed route and comparison |
|---|---|---|
| Chicago Bulls | [Career opportunities](https://www.nba.com/bulls/career-opportunities) | All five rendered Paylocity job IDs exactly matched the configured employer feed `cdb52b85-73f7-4c58-bf01-80d3e5ee2ca3`. |
| LA Clippers | [Open positions](https://www.nba.com/clippers/company/careers/openpositions#laclippers) | All nine official page entries matched `gh:laclippers`: eight jobs and one talent-community entry. An official job detail embedded Greenhouse with `for=laclippers` and token `4723835006`. |
| Milwaukee Bucks | [Careers](https://www.nba.com/bucks/careers) | The rendered View Current Job Opportunities link points to ADP company `035c77cb-5b5c-4e48-b858-605ab1663076`, career center `19000101_000001`, exactly matching the configured source. That feed returned 23 listings. |

The browser established the previously missing official-site-to-provider relationship. It did not bypass a challenge. Direct HTTP fetches still returned 403 for those JavaScript pages; those failures remain in local evidence. Screenshots, observed URLs, job-ID sets, timestamps and feed results are retained in [the public proof](https://misterplusev.github.io/job-radar/verification-20261111/career-link-proof.json).

The other 121 teams retain their prior recorded official-page evidence; all 152 source routes were fetched again in the production run. Some official sites delegate through a league careers directory or ownership-group board. The registry labels those paths explicitly. This does not claim that 124 unique ATS instances exist or that every optional job-detail page loads. The 49ers use direct listing evidence on their official page rather than an ATS-board hyperlink.

## Independent execution and persistence

| Module | Production evidence | Result |
|---|---|---|
| Sports teams | [42990654685](https://github.com/misterplusev/job-radar/actions/runs/42990654685), revision `7f57a99b30d4eca9700375920c30918d2845cace` | 152/152 sources, 124/124 official routes, 2,104 active jobs; zero new jobs, 1,551 existing source rows updated; persistence and Pages publication succeeded. |
| Robotics | [42986391001](https://github.com/misterplusev/job-radar/actions/runs/42986391001), revision `5affb48cf3205da6d995f4b6f09e39cb65ebbbc4` | Repaired production verification passed 66/66 sources; 17,596 rows upserted, nine deactivated. The preceding failed timeout run remains in history. |
| Tech | [Automatic run 42988458277](https://github.com/misterplusev/job-radar-tech/actions/runs/42988458277), revision `ad03e4209f1c22f8988110757f055513bf71c99b` | Successful automatic :37 alarm execution; live board subsequently loaded 3,746 active / 5,239 total rows. Its receipt is retained locally. |
| Sportsbook | [Live health](https://abet-jobs-watchdog.abetco.workers.dev/jobs-health), manifest `e3197b0caa9a46b7bb57bbb943094f14` | 24 providers accounted for, zero errors/timeouts, 832 jobs published, database persistence succeeded. Latest scheduled completion was November 10 at 5:04 p.m. Pacific; next scheduled slot November 11 at 3:00 a.m. Pacific. |

The read-only four-module verifier completed at 09:00 UTC with **zero warnings for every module**. Robotics, tech and teams are separate Actions workflows and concurrency groups. They share the Cloudflare alarm scheduler, at :09/:37/:23 UTC respectively. Sportsbook runs separately in Hugging Face at 06:00–20:00 Eastern every two hours; its disabled legacy GitHub workflow is intentional. Each uses distinct jobs, applications, run, and publication destinations inside the shared Supabase project. These are independent module pipelines and pages, not four physically isolated databases or servers.

Sportsbook's latest manifest records no alert attempt (`discord_notify_ok=null`), so this run is not a fresh Discord-delivery test. Sports teams' preceding automatic run delivered 18 jobs in four messages; repeat runs sent zero duplicates. See the earlier repair report for delivery receipts. No application was submitted or marked applied during these UI checks.

## Eight real production views

Each view loaded 100 initial cards; changing the result count produced 200 cards; collapsing the summary worked; filtering by a visible title or company returned real matching jobs; visible employer logos loaded. Defaults were active jobs, newest first, and U.S. locations only. Screenshots show deliberately filtered results so individual cards are legible. They were captured in the existing narrow browser viewport without resizing; they are not mockups.

| Module | Standalone | Installed ABET dashboard |
|---|---|---|
| Sportsbook | [Open](https://sportsbook-jobs-dashboard.vercel.app/) | [Open](https://abet-dashboard.vercel.app/?section=jobs&tab=jobs-browser) |
| Robotics | [Open](https://misterplusev.github.io/robotics-jobradar-board/) | [Open](https://abet-dashboard.vercel.app/?section=jobs&tab=robotics-jobs) |
| Tech | [Open](https://misterplusev.github.io/jobradar-tech-board/) | [Open](https://abet-dashboard.vercel.app/?section=jobs&tab=tech-jobs) |
| Sports teams | [Open](https://misterplusev.github.io/job-radar/) | [Open](https://abet-dashboard.vercel.app/?section=jobs&tab=teams-jobs) |

The teams dashboard's Bulls filter showed four U.S.-recognized listings; including international/unspecified locations exposed all five feed entries. The ambiguous WCB location explains that default filtering difference. Robotics standalone also retains its extra default Hide off-topic filter, which is not present in the dashboard; the result sets are not asserted identical. Sportsbook active totals shifted from 853 to 852 between observations; each screenshot and JSON record retains its own time and count.

Opening the tested robotics job description displayed “Description unavailable. Open the employer listing for details.” Its employer link was present and the board remained usable. This is a missing optional stored description, not proof of description content retrieval. The verification does not cover every employer link, every responsive breakpoint, owner-only application writes or every job description.

## Installed version and exact source changes

The dashboard's successful Vercel deployment is tied to source revision `6127ab09ab129d88eaea64fbc8890ed6e529cc43`. The served main bundle was fetched and SHA-256 fingerprinted independently; all four actual production routes were then exercised in the browser. [Install receipt](https://misterplusev.github.io/job-radar/verification-20261111/dashboard-install.json). No dashboard code was changed for this verification.

Career evidence release: [commit 7f57a99](https://github.com/misterplusev/job-radar/commit/7f57a99b30d4eca9700375920c30918d2845cace). Changed runtime/documentation files:

- `sports_teams/official_careers_registry.json`: completed the three evidence records using observed page links.
- `sports_teams/career_link_proof_20261111.json`: exact employer feed and rendered-page comparison.
- `sports_teams/test_career_link_proof.py`: two regression tests requiring complete evidence and consistent provider linkage.
- `.github/workflows/sports-teams.yml`: includes the verification directory in the already existing Pages publication step.
- `sports_teams/verification-20261111/`: public evidence and screenshots; subsequent documentation publication adds this gallery and the eight production-view screenshots.

**64 sports-team tests passed**, including the two new coverage tests. The production workflow also passed before publishing. The existing exhaustive source inventory and database dictionary remain the system reference; the robotics-and-teams source inventory is refreshed to this deployed revision, including file paths, physical line counts, symbol locations and workflow metadata. No schema, token or schedule change was needed for these final three proofs. Existing dirty local checkouts and application history were preserved.

## Reproduction and handoff

Local report: `D:\abet_ops\jobs_scrapers\2026-11-11 0105 Complete Team Coverage and Independent Jobs Module Proof.md`. Local evidence root: `D:\abet_ops\jobs_scrapers\20261111_full_verification`. Public gallery contains browser observations, installation fingerprint, runtime inspection, health/coverage snapshots and screenshots. Raw failed HTTP fetches stay local.

Use the shared `verify_scrapers.py` for bounded, read-only runtime checks. For a new team or changed ATS route, retain the official entry URL, observed destination, timestamp, exact employer identity and a successful source receipt. Do not mark a guessed provider URL verified. Do not restore legacy cron while the Cloudflare scheduler owns a module.

The user explicitly authorized one controlled browser session despite the machine stop rule. That session was used for the three NBA pages and eight live views and was closed afterward. The stop file and watchdog were left intact; no subagents were started.
