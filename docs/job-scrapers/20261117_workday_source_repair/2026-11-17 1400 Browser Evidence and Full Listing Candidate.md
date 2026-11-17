# Browser evidence and full-listing candidate

November 17, 2026, Pacific time. **The approved browser compatibility test succeeded. Full production Workday recovery is not yet established.**

## What actually ran

The user approved one controlled cloud browser test, with nothing local. It ran in a GitHub-hosted Windows job. The first workflow attempt failed while installing an invalid Python Playwright version; the browser installation and launch steps were both skipped. The pin was corrected from1.56.1 to1.65.2, and the same approved test then launched exactly one Chromium session. There was no local browser, local scraper, local runtime test, production database write, or Discord send.

Successful test: [44183404463](https://github.com/misterplusev/job-radar/actions/runs/44183404463), source revision `074adec5e72978199f50637d199b14ea910f4555`. Browser evidence was printed at13:48:35Pacific. The cloud report says `browser_count:1`, `remaining_owned_processes:0`, `cleanup.passed:true`. The original runaway guard was used. No challenge interaction, stealth, proxy or cookie replay was used.

| Page | Result | Boundary |
|---|---|---|
| Boston Dynamics corporate careers | HTTP200, actual careers page, no challenge | Not a complete independent job-feed validation |
| Boston Dynamics Workday | HTTP200; UI and native listing API advertised85 jobs; first20 returned | Remaining65 were not paginated in this compatibility test |
| BetMGM Workday | HTTP200; UI and native listing API advertised23 jobs; first20 returned | Remaining3 were not paginated in this compatibility test |

Screenshots and captured listing JSON: `approved-browser/evidence/`. The exact report is `approved-browser/evidence/report.json`; artifact ID/download receipt is `approved-browser/artifact-receipt.json`. Screenshot files: `boston-workday.png`, `betmgm.png`, `boston-official.png`. They are real cloud-browser output, not illustrations.

## HTTP-only comparison

[Run44184192358](https://github.com/misterplusev/job-radar/actions/runs/44184192358) tested ordinary HTTP session initialization, preserving the current production User-Agent and using the browser-observed listing payload if the public page loaded. It launched no browser and had no production credentials.

All seven public-page requests returned HTTP429 with `CF-Mitigated: challenge`: Boston Dynamics, AutoStore, Rockwell Automation, BetMGM, Betway, Hard Rock Bet and AMB Sports & Entertainment. The probe stopped after one request on each host; it did not attempt further requests behind the challenge. Evidence: `approved-browser/http-session/report.json`.

This comparison supports using the normal browser path for further verification. It does not prove that every Workday board or every browser request will succeed, or that changing one HTTP header would fix production. No failed session-only change was deployed.

## Concrete next test, prepared but not authorized to launch

Candidate branch: `codex/workday-browser-listings-20261117` in `misterplusev/job-radar`. Latest candidate revision: `79809b89792779e4c70e073ef7721283b7c3ec56`.

[Cloud fixture run44185856333](https://github.com/misterplusev/job-radar/actions/runs/44185856333) passed all nine safety checks; the browser job was confirmed **skipped**. A new question requesting one full-coverage cloud test was presented to the user after the code and fixtures were complete. No reply has been received at this checkpoint. Do not enable the browser input until the explicit answer arrives.

- `runtime/verification/browser_full_collection.py`: one normal browser; observes the website's own CXS responses and clicks its normal `Next` button. No fabricated API response, challenge solving, login or cookie replay.
- `runtime/verification/full-browser-catalog.json`: all19 currently configured Workday routes:13 sports teams,3 robotics,3 sportsbook. The tech registry has no Workday route. The Hawks Workday route is included even though it passed the last production run; the goal is complete configured coverage.
- `runtime/verification/test_browser_full_collection.py`: cloud-only fixtures for complete pagination, premature empty pages, duplicate pages, changing totals, invalid job paths, legitimate empty boards, unexpected offsets, over-counts and full-coverage/cleanup acceptance.
- `.github/workflows/workday-retry-review.yml`: fixture tests run normally. The browser job is disabled unless `allow_full_cloud_browser=true` is explicitly supplied after approval.
- Original guard and process-snapshot files are copied unchanged beside the script. No local stop file or watchdog was changed.

Limits: one Chromium session, pages sequentially,15-minute collection deadline,20-minute cloud job ceiling including setup,180seconds per board,2,000 total browser network requests,5,000 advertised jobs per board,250 listing pages per board. A challenged host is not retried elsewhere in the same session. Browser resources are closed, any remaining owned process trees killed, and cleanup checked. All19 listings and cleanup must pass for a successful acceptance exit code. No production database or Discord credentials are provided. There is no cron or new sender.

Artifacts contain each complete official listing, declared and observed counts, screenshots and failures. **This next test validates full listing identities, not every job description, production persistence or notification delivery.** Those still require appropriate integration and cloud validation before claiming all four scrapers recovered. Production integration of the browser collector is not deployed or represented as completed.

The original one-test exception has been consumed and the browser is closed. Another browser launch needs an extension of the exception under rule2 of `D:\abet_ops\20261019_AGENT_RUNAWAY_AND_MEMORY_SAFETY_RULES_v1_0_0.md`, which says "while it exists, start NO agent and NO browser anywhere." `STOP_ALL_AGENTS_MACHINE` remains untouched.

## Current production evidence and remaining work

Latest inspected production data remains useful despite source failures. The sportsbook run saved653 jobs with database publication successful and the separate delivery workflow successful. Its remaining errors include BetMGM/HardRock detail challenges, Betway listing challenge and unrelated Betr/Fliff Lever timeouts. Teams completed139/152 source routes. Robotics'12:09UTC run fetched86 Boston Dynamics jobs across all five pages, but AutoStore and Rockwell remained challenged; an unrelated OpenAI Ashby error also occurred. Tech's21:37UTC run succeeded. These are dated observations, not full-system health claims.

The production databases,12-hour schedule, existing senders and previous handling repair were not modified during this compatibility-test turn. Do not import the20-row samples as complete boards, reconcile closures from them, or label a passing diagnostic workflow as complete source recovery.
