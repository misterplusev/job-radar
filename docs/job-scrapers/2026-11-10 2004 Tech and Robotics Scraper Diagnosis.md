# Tech and robotics scraper diagnosis

Inspected November 10, 2026, approximately 19:57–20:04 Pacific. This is a read-only production diagnosis, with local evidence and offline fault simulations. No deployment, scraper execution, schedule change, database mutation, or Discord message was performed.

The scrapers still fetch and save jobs, but neither is operating at its intended hourly cadence. Robotics also has a confirmed active-listing cleanup failure. Both publishers can report success after failed operations.

## 1. Confirmed: hourly schedules do not produce hourly executions

The fixed comparison window is November 4 00:00 UTC through November 11 00:00 UTC, exclusive of the endpoint: seven complete UTC days.

| Measure | Robotics | Tech |
|---|---:|---:|
| Production cron | `9 * * * *` | `37 * * * *` |
| Expected hourly invocations | 168 | 168 |
| Observed scheduled workflow runs | 26 | 26 |
| Observed / expected | 15.48% | 15.48% |
| Median gap between scheduled starts | 6.75 hours | 6.79 hours |
| Longest observed gap within the window | 11.23 hours | 11.37 hours |
| Created-to-runner-start, latest six scheduled runs | 2–3 seconds | 2–3 seconds |
| Execution duration, latest six scheduled runs | 321–426 seconds | 80–226 seconds |

Tech has one additional scheduled run after the comparison window, at November 11 00:50:56 UTC. Robotics also has five manual runs in the wider inspection history; they are not counted as scheduled runs.

The cron declarations are on the default branch (`master`), Actions is enabled, and both repositories are public and not archived/disabled. The hourly cron changes date to October 12. The inspected workflow runs are completed successfully; there is no visible backlog of queued runs in this history. Short execution times and immediate runner assignment do not explain the missing hours. A concurrency guard exists, but the observed jobs are not occupying runners for hours.

**Diagnosis:** the missing cadence is at or before creation of scheduled workflow runs, rather than slow provider fetches or runner startup. The public run history does not identify GitHub's internal reason for each absent invocation. GitHub explicitly documents that scheduled events may be delayed or dropped during high load; that is a supported possibility, not proof that load caused this entire week of gaps. The November 10 status incident alone does not explain a week-long pattern.

Sources: [GitHub schedule behavior](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule), [robotics production workflow](https://github.com/misterplusev/job-radar/blob/99ee50ea8b7c815e670b6af887c3dd6353e326b4/.github/workflows/pipeline.yml), [tech production workflow](https://github.com/misterplusev/job-radar-tech/blob/d682fdeb8557ee40f3bb7ef429ea2dbc11014973/.github/workflows/pipeline.yml).

Evidence: `20261110_1957_tech_robotics_diagnosis/cadence_metrics.json` and each module's `evidence.json`. The run API returned fewer than 100 records, so the inspected window was not truncated by pagination.

## 2. Confirmed: robotics cannot retire thousands of absent URLs

The latest inspected robotics run failed cleanup requests for eight companies, yet GitHub marked the run successful. Its publisher puts every absent URL for a company into one `url=in.(...)` request, without batching. Those request URLs were approximately 30,000–145,000 characters long. Responses were HTTP 400 or 414.

The database check intersected URLs from those exact failed requests with rows that were still active and last seen before the run began. **3,136 rows matched.**

| Company | Failed cleanup HTTP status | Matching rows still active |
|---|---:|---:|
| Amazon | 414 | 1,394 |
| Anduril Industries | 414 | 763 |
| Databricks | 400 | 235 |
| SpaceX | 400 | 224 |
| Rockwell Automation | 400 | 210 |
| Stripe | 400 | 174 |
| Anthropic | 400 | 79 |
| Zipline | 400 | 57 |
| **Total** | | **3,136** |

These are URLs the scrape no longer observed, not 3,136 individually verified closed requisitions. URL changes, duplicate URLs, or partial source results can also make a URL disappear. A repair must reconcile against a fresh, complete provider result before retiring records.

Read-only reproduction using the same filters:

- Anthropic: 411 URLs / 30,115-character GET request → HTTP 400; ten URLs / 842 characters → HTTP 200.
- Anduril: 1,003 URLs / 99,418-character GET request → HTTP 414; ten URLs / 1,111 characters → HTTP 200.

No PATCH was used in the reproduction. These results isolate the oversized request as the failure mechanism. The publisher catches the cleanup HTTP error and prints it without raising. The caller subsequently prints the intended number as “deactivated,” regardless of whether the update succeeded. That makes the log summary and green workflow misleading.

Code: [robotics deactivate](https://github.com/misterplusev/job-radar/blob/99ee50ea8b7c815e670b6af887c3dd6353e326b4/jobradar/publish.py#L118), [unconditional completion summary](https://github.com/misterplusev/job-radar/blob/99ee50ea8b7c815e670b6af887c3dd6353e326b4/jobradar/publish.py#L370). Tech has the same unbatched cleanup implementation at [line 101](https://github.com/misterplusev/job-radar-tech/blob/d682fdeb8557ee40f3bb7ef429ea2dbc11014973/jobradar/publish.py#L101), although its latest inspected run did not exhibit this failure.

Evidence: `robotics/filtered_latest_run_log.txt`, `robotics/deactivation_errors.json`, `robotics/deactivation_query_evidence.json`, `database_evidence.json`, and `readonly_batch_probe.json` under the evidence directory.

## 3. Confirmed code defects: success can conceal failed writes or alerts

Offline fault injection used the saved production function bodies, with all HTTP calls and sleeps replaced by local stubs. No external requests or messages were made.

| Injected condition | Robotics | Tech |
|---|---|---|
| Database returns HTTP 429 on every upsert attempt | Three attempts, then returns without raising | Same |
| Discord returns HTTP 429 on every attempt | Eight attempts; logs a dropped chunk, then “Posted 1” | Three attempts; prints “Posted 1” despite zero deliveries |

Both upsert loops also have the same exhausted-retry behavior for the listed retryable server errors. There is no terminal raise after the final retry. The failure scenario is reproduced, but the latest production logs do not prove that an upsert or Discord chunk was lost in those specific runs.

Both publishers persist new jobs before notification and determine novelty from existing database URLs. Neither keeps a durable pending-delivery queue. A notification that fails after persistence will not automatically be considered new on the next scrape. This is a real delivery-loss risk; the number of historical lost alerts cannot be determined from these receipts.

Tech and robotics also differ: tech waits 0.5 seconds between notification chunks and retries 429 three times with fixed waits; robotics paces chunks at 2.1 seconds and uses up to eight rate-limit-aware retries. They do not have the same notification reliability implementation.

Code: robotics `production_publish.py` lines 147, 252, 346; tech `production_publish.py` lines 130, 213, 299 in the saved evidence. Reproduction: `offline_fault_probe.json`; source script `E:\abet\.cache\tmp\opencode\probe_scraper_error_handling_20261110.py`.

## What is working, and what a green run actually proves

- Latest robotics run: [42921450845](https://github.com/misterplusev/job-radar/actions/runs/42921450845), November 10 15:12 Pacific. It fetched 17,552 provider job results across 66 providers before company/URL deduplication. Its log reported 57 Discord jobs posted and 41 recent new jobs suppressed by the robotics relevance filter.
- Latest tech run: [42934545744](https://github.com/misterplusev/job-radar-tech/actions/runs/42934545744), November 10 16:50 Pacific. It fetched 3,757 provider job results across 13 providers and logged 32 jobs posted. No cleanup or provider error appears in that inspected run.
- The live database's newest job observations align with those executions. Provider telemetry since November 4 contained 1,716 robotics rows and 351 tech rows, all marked successful. That telemetry describes fetching, not successful downstream cleanup or delivery.
- Both modules currently suppress notification for jobs with missing/unparseable posted dates or dates older than 14 days. Robotics additionally applies its relevance filter. A quiet Discord channel alone does not prove there are no newly stored jobs.
- Neither a successful provider receipt nor a green workflow proves that every employer's source is complete, that every inactive flag is correct, or that every alert arrived. No end-to-end Discord delivery audit was performed here.

Additional source-level weaknesses: provider exceptions are caught and a run can remain successful if any jobs were collected; telemetry writes do not check HTTP response status; a company returning zero jobs never enters the grouped publish loop, so it cannot have its old jobs retired. The advertised 120-second provider “hard timeout” uses a thread executor context manager that waits for its running thread during exit, so it is not a true kill deadline. None of these explains the observed absence of hourly workflow starts. See [Python executor shutdown semantics](https://docs.python.org/3/library/concurrent.futures.html#concurrent.futures.Executor.shutdown).

## Repair order and acceptance checks

1. **Repair cleanup and truthful status reporting.** Batch updates by safe request size or use a body-based database function with validated IDs. Report confirmed updated rows, propagate failed batches, and distinguish partial runs from complete runs. Reconcile stale rows only after a fresh complete provider observation. Verify the eight affected companies and retain before/after receipts.
2. **Restore reliable cadence.** Use one authoritative scheduler with explicit overlap protection and independent overdue-run detection. Do not add a second uncontrolled producer alongside the current cron. Acceptance must use actual execution history over a full day, rather than the YAML declaration or one manual success.
3. **Make persistence and delivery retry-safe.** Raise on exhausted writes; persist pending notifications and acknowledge actual delivery; retry pending items without treating them as already delivered. Align tech's pacing/retries with the intended shared contract. Count only successful deliveries.
4. **Improve health reporting.** Separate scheduled start, provider completeness, persistence, cleanup, render, and notification outcomes. Record run IDs and actual trigger source, and flag stale success timestamps.

No production repair is claimed by this report. The evidence supports a scheduling failure and an active-listing cleanup failure today, plus reproduced error-handling defects that can hide additional failures.

## Evidence location and collection limits

All receipts are under `D:\abet_ops\jobs_scrapers\20261110_1957_tech_robotics_diagnosis`. Production source was fetched by the exact commit used by each latest inspected run, rather than assumed from the dirty local worktrees. The local checkouts were left untouched.

The initial `gh run view --log` commands exited zero but returned empty output. Those empty `latest_run_log.txt` files are not evidence of clean runs. Actual job logs were retrieved through the GitHub connector; the filtered extracts and request metadata above are the evidence used for this diagnosis. Schedule and database snapshots are point-in-time observations, not a newly installed continuous monitor.
