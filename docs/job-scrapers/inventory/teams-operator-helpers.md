# teams-operator-helpers — file and symbol inventory

Revision: `local working copy; may include retired operators`. Root: `D:\abet_ops\sports_teams`.

| File | Physical lines | Nonblank | Bytes | Category |
|---|---:|---:|---:|---|
| `_stats.py` | 12 | 10 | 717 | support/module |
| `audit_official_careers.py` | 128 | 118 | 7188 | support/module |
| `build_board.py` | 88 | 82 | 5256 | support/module |
| `build_official_registry.py` | 139 | 135 | 14123 | support/module |
| `build_registry.py` | 75 | 68 | 4540 | support/module |
| `build_team_logos.py` | 91 | 80 | 3153 | support/module |
| `cloud_storage.py` | 116 | 104 | 6820 | storage |
| `consolidate.py` | 33 | 32 | 1072 | support/module |
| `coverage_report.py` | 43 | 40 | 4642 | support/module |
| `db/schema_cloud.sql` | 56 | 56 | 4074 | database schema/migration |
| `db/schema_team_jobs.sql` | 64 | 58 | 3084 | database schema/migration |
| `deploy_cloud.py` | 95 | 84 | 4359 | runtime/deployment |
| `deploy_github.py` | 131 | 126 | 6574 | runtime/deployment |
| `deploy_notification_audit.py` | 43 | 43 | 1989 | publication/delivery |
| `deploy_workday_repair.py` | 40 | 39 | 1810 | runtime/deployment |
| `deploy_worker.py` | 33 | 29 | 2364 | runtime/deployment |
| `enrichment.py` | 96 | 88 | 4692 | support/module |
| `expand_nfl_clubs.py` | 94 | 83 | 3677 | support/module |
| `live_refresh.py` | 320 | 301 | 19482 | source ingestion |
| `notification_audit.py` | 26 | 25 | 1773 | publication/delivery |
| `patch_canonical.py` | 12 | 11 | 509 | support/module |
| `patch_embed_parity.py` | 99 | 87 | 3697 | support/module |
| `patch_guard.py` | 20 | 17 | 861 | support/module |
| `patch_new_badge.py` | 62 | 58 | 2937 | support/module |
| `patch_nonteam.py` | 20 | 19 | 680 | support/module |
| `patch_pipeline.py` | 33 | 28 | 1462 | support/module |
| `patch_publish_logos.py` | 81 | 71 | 3055 | publication/delivery |
| `pipeline_local.py` | 252 | 227 | 11450 | support/module |
| `prepare_workday_repair.py` | 34 | 31 | 1786 | support/module |
| `probe_org_shapes.py` | 41 | 37 | 1625 | support/module |
| `probe_remaining.py` | 23 | 23 | 1328 | support/module |
| `providers/adp.py` | 84 | 74 | 3656 | source ingestion |
| `providers/base.py` | 31 | 26 | 1094 | source ingestion |
| `providers/nba.py` | 87 | 77 | 3585 | source ingestion |
| `providers/nfl.py` | 44 | 35 | 1711 | source ingestion |
| `providers/official_ats.py` | 351 | 331 | 22703 | source ingestion |
| `providers/teamwork.py` | 120 | 100 | 4637 | source ingestion |
| `providers/teamwork_vertical.py` | 87 | 74 | 3274 | source ingestion |
| `providers/ultipro.py` | 63 | 55 | 2844 | source ingestion |
| `publish_cloud_bundle.py` | 74 | 69 | 4942 | publication/delivery |
| `publish_teams.py` | 390 | 336 | 15257 | publication/delivery |
| `repair_workday_cloud.py` | 93 | 89 | 6734 | support/module |
| `resolve_twork_slugs.py` | 36 | 33 | 1575 | support/module |
| `run.py` | 35 | 31 | 1816 | support/module |
| `runtime.py` | 126 | 106 | 6267 | runtime/deployment |
| `scrape_mlb_clubs.py` | 93 | 82 | 4473 | source ingestion |
| `scrape_mlb_round2.py` | 80 | 70 | 3135 | source ingestion |
| `scrape_mlb_round3.py` | 56 | 49 | 2492 | source ingestion |
| `scrape_twork_all.py` | 91 | 78 | 3160 | source ingestion |
| `scrape_twork_orgs.py` | 87 | 73 | 3238 | source ingestion |
| `test_cloud_parity.py` | 145 | 124 | 10170 | test/verification |
| `test_official_routes.py` | 120 | 99 | 9663 | test/verification |
| `test_pipeline_regressions.py` | 136 | 111 | 7556 | test/verification |
| `test_source_delivery_parity.py` | 42 | 36 | 2836 | test/verification |
| `test_worker.mjs` | 17 | 17 | 1754 | test/verification |
| `verify_deployment.py` | 63 | 58 | 3835 | runtime/deployment |
| `verify_official_sources.py` | 29 | 26 | 1680 | support/module |
| `verify_route_evidence.py` | 59 | 56 | 3660 | support/module |
| `wire_dashboard.py` | 75 | 65 | 2598 | support/module |
| `wrangler.toml` | 6 | 6 | 154 | runtime/deployment |

## Script definitions and dependencies

### audit_official_careers.py

Bounded, sequential official-careers audit. Owner: this sports-scraper repair.

Location: `D:\abet_ops\sports_teams\audit_official_careers.py`.

Imports: `argparse`, `gzip`, `hashlib`, `json`, `re`, `time`, `unicodedata`, `datetime`, `pathlib`, `urllib.parse`, `requests`, `bs4`.

- `norm` (FunctionDef), line 27–27
- `stamp` (FunctionDef), line 28–28
- `seeds` (FunctionDef), line 30–56
- `fetch` (FunctionDef), line 58–74
- `links` (FunctionDef), line 76–86
- `audit` (FunctionDef), line 88–110
- `main` (FunctionDef), line 112–126

### build_official_registry.py

Turn reviewed official-link evidence into a team coverage registry.

Location: `D:\abet_ops\sports_teams\build_official_registry.py`.

Imports: `json, re`, `pathlib`, `urllib.parse`, `audit_official_careers`, `live_refresh`.

- `main` (FunctionDef), line 85–137

### build_team_logos.py

Build team_logos.json from ESPN's public team endpoints (name -> logo URL).

Location: `D:\abet_ops\sports_teams\build_team_logos.py`.

Imports: `json`, `re`, `unicodedata`, `urllib.request`, `pathlib`.

- `norm` (FunctionDef), line 26–29
- `fetch` (FunctionDef), line 32–35

### cloud_storage.py

Supabase persistence matching the other jobs modules; SQLite is a working cache.

Location: `D:\abet_ops\sports_teams\cloud_storage.py`.

Imports: `json`, `os`, `sqlite3`, `time`, `requests`, `pathlib`.

- `CloudStorage` (ClassDef), line 17–116
- `CloudStorage.__init__` (FunctionDef), line 18–22
- `CloudStorage.request` (FunctionDef), line 24–38
- `CloudStorage.rows` (FunctionDef), line 40–48
- `CloudStorage.upsert` (FunctionDef), line 50–52
- `CloudStorage.restore` (FunctionDef), line 54–83
- `CloudStorage.persist` (FunctionDef), line 85–100
- `CloudStorage.notification_state` (FunctionDef), line 102–105
- `CloudStorage.queue_notifications` (FunctionDef), line 107–110
- `CloudStorage.save_notification_state` (FunctionDef), line 112–116

### coverage_report.py

Report each team's official route and current run, without equating discovery with proof.

Location: `D:\abet_ops\sports_teams\coverage_report.py`.

Imports: `json, html`, `pathlib`, `datetime`.

- `build` (FunctionDef), line 7–26
- `write` (FunctionDef), line 28–39

### db/schema_cloud.sql

database schema/migration; inspect linked source and symbol map for exact behavior

Location: `D:\abet_ops\sports_teams\db\schema_cloud.sql`.

- `public.team_jobs` (table), line 2
- `team_jobs_active_idx` (index), line 10
- `team_jobs_first_idx` (index), line 11
- `public.team_keep_first_seen` (function), line 12
- `team_keep_first_seen` (trigger), line 15
- `public.team_job_observations` (table), line 16
- `public.team_job_scrape_runs` (table), line 20
- `team_job_runs_date_idx` (index), line 25
- `public.team_job_notifications` (table), line 26
- `public.team_applications` (table), line 30
- `team_jobs_read` (policy), line 42
- `team_runs_read` (policy), line 44
- `team_applications_owner` (policy), line 46
- `public.team_jobs_with_applied` (view), line 52

### db/schema_team_jobs.sql

database schema/migration; inspect linked source and symbol map for exact behavior

Location: `D:\abet_ops\sports_teams\db\schema_team_jobs.sql`.

- `public.team_jobs` (table), line 10
- `team_jobs_league_idx` (index), line 30
- `team_jobs_team_idx` (index), line 32
- `team_jobs_active_idx` (index), line 33
- `team_jobs_first_seen_idx` (index), line 34
- `team_jobs_posted_idx` (index), line 35
- `public.team_job_scrape_runs` (table), line 36
- `team_job_runs_created_idx` (index), line 48
- `team_job_runs_source_idx` (index), line 50
- `team_jobs_public_read` (policy), line 61

### deploy_cloud.py

Operator deployment helper. Secrets stay in stdin/API bodies, never output. Uses existing job-radar migration credentials on an isolated one-time branch; no changes to its default branch or recurring workflow. Sports code is versioned in its own private Hugging Face repository. Does not send Discord messages.

Location: `D:\abet_ops\sports_teams\deploy_cloud.py`.

Imports: `base64`, `json`, `re`, `secrets`, `subprocess`, `pathlib`, `huggingface_hub`.

- `envfile` (FunctionDef), line 21–26
- `gh` (FunctionDef), line 29–32
- `api` (FunctionDef), line 35–36
- `setup` (FunctionDef), line 39–92

### deploy_github.py

Deploy the sports module beside robotics, preserving its existing workflow.

Location: `D:\abet_ops\sports_teams\deploy_github.py`.

Imports: `json`, `pathlib`, `deploy_cloud`, `argparse`.

- `main` (FunctionDef), line 103–123

### deploy_worker.py

Deploy read-only board and keepalive. Notification relay stays parked.

Location: `D:\abet_ops\sports_teams\deploy_worker.py`.

Imports: `json`, `requests`, `pathlib`, `deploy_cloud`, `huggingface_hub`.

- `main` (FunctionDef), line 8–30

### enrichment.py

Employer job detail extraction. Bounded, cached, and independent of listing health.

Location: `D:\abet_ops\sports_teams\enrichment.py`.

Imports: `json`, `re`, `time`, `datetime`, `urllib.parse`, `bs4`, `live_refresh`, `providers.teamwork`, `publish_teams`.

- `jsonld_job` (FunctionDef), line 15–32
- `fetch_detail` (FunctionDef), line 35–58
- `enrich` (FunctionDef), line 61–96

### expand_nfl_clubs.py

Extract NFL club careers destinations, classify them, update teams.json, scrape the TWork ones.

Location: `D:\abet_ops\sports_teams\expand_nfl_clubs.py`.

Imports: `json`, `re`, `sys`, `urllib.request`, `pathlib`, `providers.teamwork`, `requests`, `providers`.

- `match` (FunctionDef), line 43–48

### live_refresh.py

Bounded live refresh for the existing scheduled sports-team pipeline.

Location: `D:\abet_ops\sports_teams\live_refresh.py`.

Imports: `__future__`, `json`, `os`, `re`, `time`, `threading`, `concurrent.futures`, `dataclasses`, `datetime`, `urllib.parse`, `requests`, `providers`, `bs4`, `publish_teams`.

- `BoundedSession` (ClassDef), line 35–86
- `BoundedSession.__init__` (FunctionDef), line 38–41
- `BoundedSession.request` (FunctionDef), line 43–60
- `BoundedSession._request_once` (FunctionDef), line 62–86
- `source_from_row` (FunctionDef), line 89–172
- `build_sources` (FunctionDef), line 175–184
- `fetch_source` (FunctionDef), line 187–270
- `collect` (FunctionDef), line 273–283
- `apply_results` (FunctionDef), line 286–320

### pipeline_local.py

Live HTTP sources -> SQLite tracking -> local board and dashboard feed.

Location: `D:\abet_ops\sports_teams\pipeline_local.py`.

Imports: `__future__`, `argparse`, `os`, `uuid`, `json`, `re`, `sqlite3`, `sys`, `unicodedata`, `collections`, `datetime`, `pathlib`, `importlib.util`, `cloud_storage`, `live_refresh`, `enrichment`, `coverage_report`.

- `now` (FunctionDef), line 72–73
- `connect` (FunctionDef), line 76–80
- `ingest` (FunctionDef), line 83–124
- `deactivate_missing` (FunctionDef), line 127–134
- `snapshot` (FunctionDef), line 137–147
- `write_outputs` (FunctionDef), line 150–167
- `main` (FunctionDef), line 170–248

### prepare_workday_repair.py

Bounded read-only verification of legacy Workday URLs; no database writes.

Location: `D:\abet_ops\sports_teams\prepare_workday_repair.py`.

Imports: `json, time`, `pathlib`, `urllib.parse`, `requests`.

- `main` (FunctionDef), line 12–32

### providers/adp.py

ADP Workforce Now public career-center API.

Location: `D:\abet_ops\sports_teams\providers\adp.py`.

Imports: `__future__`, `typing`, `requests`, `providers.base`.

- `_loc` (FunctionDef), line 28–36
- `scrape` (FunctionDef), line 39–84

### providers/base.py

Sports-teams jobs scraper — base contract.

Location: `D:\abet_ops\sports_teams\providers\base.py`.

Imports: `__future__`, `dataclasses`, `typing`.

- `Job` (ClassDef), line 21–31

### providers/nba.py

NBA — careers.nba.com (Phenom People in front of Workday).

Location: `D:\abet_ops\sports_teams\providers\nba.py`.

Imports: `__future__`, `json`, `typing`, `requests`, `providers.base`.

- `payload` (FunctionDef), line 33–42
- `scrape` (FunctionDef), line 45–87

### providers/nfl.py

NFL — league-office jobs straight from the NFL's own Greenhouse board.

Location: `D:\abet_ops\sports_teams\providers\nfl.py`.

Imports: `__future__`, `html`, `re`, `requests`, `providers.base`.

- `_text` (FunctionDef), line 22–23
- `scrape` (FunctionDef), line 26–44

### providers/official_ats.py

Public feeds linked by official team careers pages. No browser or authentication.

Location: `D:\abet_ops\sports_teams\providers\official_ats.py`.

Imports: `json, re`, `urllib.parse`, `bs4`.

- `dayforce` (FunctionDef), line 11–41
- `bamboohr` (FunctionDef), line 43–54
- `lever` (FunctionDef), line 56–69
- `paylocity` (FunctionDef), line 71–84
- `paycor` (FunctionDef), line 86–100
- `jazzhr` (FunctionDef), line 102–113
- `tnse` (FunctionDef), line 115–121
- `clearcompany` (FunctionDef), line 123–142
- `applicantpro` (FunctionDef), line 144–158
- `icims` (FunctionDef), line 160–179
- `msg` (FunctionDef), line 181–192
- `bkse` (FunctionDef), line 194–214
- `hireology` (FunctionDef), line 216–237
- `paycom` (FunctionDef), line 239–264
- `hirebridge` (FunctionDef), line 266–281
- `aeg_kings` (FunctionDef), line 283–296
- `jobvite` (FunctionDef), line 298–309
- `bruins` (FunctionDef), line 311–346

### providers/teamwork.py

TeamWork Online organisation portal provider.

Location: `D:\abet_ops\sports_teams\providers\teamwork.py`.

Imports: `__future__`, `html`, `re`, `urllib.parse`, `bs4`, `dataclasses`, `typing`, `requests`, `providers.base`.

- `TeamWorkOrg` (ClassDef), line 45–49
- `_clean` (FunctionDef), line 52–53
- `org_url` (FunctionDef), line 56–58
- `pages` (FunctionDef), line 61–81
- `scrape_org` (FunctionDef), line 84–112
- `scrape_many` (FunctionDef), line 115–120

### providers/teamwork_vertical.py

TeamWork Online: vertical page -> org slugs -> each org's own portal.

Location: `D:\abet_ops\sports_teams\providers\teamwork_vertical.py`.

Imports: `__future__`, `html`, `re`, `collections`, `dataclasses`, `typing`, `requests`, `providers.base`, `providers.teamwork`.

- `DetectedOrg` (ClassDef), line 31–36
- `_cards` (FunctionDef), line 39–52
- `discover` (FunctionDef), line 55–74
- `scrape_all_orgs` (FunctionDef), line 77–87

### providers/ultipro.py

UltiPro / UKG public job board API.

Location: `D:\abet_ops\sports_teams\providers\ultipro.py`.

Imports: `__future__`, `typing`, `requests`, `providers.base`.

- `scrape` (FunctionDef), line 25–63

### publish_cloud_bundle.py

Upload the tested module, with an isolated route in the existing HF launcher.

Location: `D:\abet_ops\sports_teams\publish_cloud_bundle.py`.

Imports: `json`, `sqlite3`, `pathlib`, `huggingface_hub`, `requests`, `deploy_cloud`.

- `main` (FunctionDef), line 14–71

### publish_teams.py

publish_teams.py — sports-team job announcements.

Location: `D:\abet_ops\sports_teams\publish_teams.py`.

Imports: `__future__`, `argparse`, `json`, `os`, `re`, `sys`, `time`, `unicodedata`, `urllib.error`, `urllib.request`, `datetime`, `pathlib`, `html`, `datetime`, `sqlite3`, `cloud_storage`, `cloud_storage`, `urllib.parse`.

- `now_iso` (FunctionDef), line 65–66
- `guard` (FunctionDef), line 69–74
- `webhook` (FunctionDef), line 77–84
- `_norm` (FunctionDef), line 87–88
- `_clean_text` (FunctionDef), line 95–100
- `_iso` (FunctionDef), line 103–124
- `_display_team` (FunctionDef), line 127–141
- `logo_for` (FunctionDef), line 144–162
- `load_legacy_rows` (FunctionDef), line 165–192
- `load_rows` (FunctionDef), line 195–211
- `load_state` (FunctionDef), line 214–220
- `save_state` (FunctionDef), line 223–228
- `_is_recent` (FunctionDef), line 231–240
- `embed` (FunctionDef), line 243–275
- `notify` (FunctionDef), line 278–303
- `main` (FunctionDef), line 306–386

### repair_workday_cloud.py

One-off atomic URL repair. Preserves original job IDs, first-seen and delivery history.

Location: `D:\abet_ops\sports_teams\repair_workday_cloud.py`.

Imports: `json, os`, `pathlib`, `requests`.

- `main` (FunctionDef), line 83–91

### run.py

Sports teams CLI, matching the other jobs modules' ingest/render workflow.

Location: `D:\abet_ops\sports_teams\run.py`.

Imports: `argparse`, `json`, `os`, `sys`, `pathlib`, `pipeline_local`, `live_refresh`.

- `main` (FunctionDef), line 11–32

### runtime.py

Cloud scheduler and read-only board, patterned on the sportsbook HF runtime.

Location: `D:\abet_ops\sports_teams\runtime.py`.

Imports: `hmac`, `json`, `os`, `subprocess`, `sys`, `threading`, `time`, `datetime`, `http.server`, `pathlib`, `zoneinfo`.

- `now` (FunctionDef), line 27–27
- `schedule` (FunctionDef), line 30–35
- `read_json` (FunctionDef), line 38–40
- `health` (FunctionDef), line 43–56
- `run` (FunctionDef), line 59–79
- `scheduler` (FunctionDef), line 82–89
- `Handler` (ClassDef), line 92–116
- `Handler.do_GET` (FunctionDef), line 93–107
- `Handler.do_POST` (FunctionDef), line 109–114
- `Handler.log_message` (FunctionDef), line 116–116

### scrape_mlb_clubs.py

MLB clubs — extract each club's platform target, then scrape every one with a public API.

Location: `D:\abet_ops\sports_teams\scrape_mlb_clubs.py`.

Imports: `json`, `re`, `sys`, `urllib.error`, `urllib.request`, `pathlib`, `providers`.

- `get` (FunctionDef), line 17–24

### scrape_mlb_round2.py

MLB clubs round 2: normalise TeamWork portals + scrape the Workday tenants.

Location: `D:\abet_ops\sports_teams\scrape_mlb_round2.py`.

Imports: `json`, `re`, `sys`, `urllib.error`, `urllib.request`, `pathlib`, `providers`.

- `norm_twork` (FunctionDef), line 18–23
- `post` (FunctionDef), line 26–34

### scrape_twork_all.py

Walk all three TeamWork verticals -> per-org portals -> jobs; attribute to registry teams.

Location: `D:\abet_ops\sports_teams\scrape_twork_all.py`.

Imports: `json`, `re`, `sys`, `unicodedata`, `collections`, `datetime`, `pathlib`, `providers`.

- `norm` (FunctionDef), line 16–18
- `attribute` (FunctionDef), line 34–50

### scrape_twork_orgs.py

Scrape every TeamWork org portal discovered on the three vertical pages.

Location: `D:\abet_ops\sports_teams\scrape_twork_orgs.py`.

Imports: `json`, `re`, `sys`, `unicodedata`, `datetime`, `pathlib`, `requests`, `providers.teamwork_vertical`, `providers`.

- `norm` (FunctionDef), line 25–26
- `attribute` (FunctionDef), line 37–44

### test_cloud_parity.py

test/verification; inspect linked source and symbol map for exact behavior

Location: `D:\abet_ops\sports_teams\test_cloud_parity.py`.

Imports: `json`, `os`, `sqlite3`, `unittest`, `datetime`, `unittest.mock`, `pathlib`, `cloud_storage`, `enrichment`, `live_refresh`, `pipeline_local`, `publish_teams`, `providers`, `providers.base`, `sys`, `runtime`.

- `ParityTests` (ClassDef), line 16–142
- `ParityTests.test_transient_timeout_retries_within_request_budget` (FunctionDef), line 17–23
- `ParityTests.test_forbidden_response_is_not_retried` (FunctionDef), line 25–30
- `ParityTests.test_detail_request_uses_working_listing_headers_and_full_text` (FunctionDef), line 32–40
- `ParityTests.test_complete_description_updates_even_when_shorter` (FunctionDef), line 42–46
- `ParityTests.test_league_portal_preserves_actual_employer` (FunctionDef), line 48–53
- `ParityTests.test_owner_correction_preserves_identity_and_first_seen` (FunctionDef), line 55–61
- `ParityTests.test_old_unannounced_job_is_not_announced_as_new` (FunctionDef), line 63–67
- `ParityTests.test_verified_empty_source_retires_jobs` (FunctionDef), line 69–75
- `ParityTests.test_cloud_source_relay_preserves_canonical_url` (FunctionDef), line 77–84
- `ParityTests.page` (FunctionDef), line 86–87
- `ParityTests.test_teamwork_follows_next_page_and_deduplicates` (FunctionDef), line 89–94
- `ParityTests.test_malformed_and_cycle_pages_fail_instead_of_closing_jobs` (FunctionDef), line 96–100
- `ParityTests.test_jsonld_extracts_full_description_and_salary_without_guessing` (FunctionDef), line 102–105
- `ParityTests.test_supabase_pagination_and_retries_exhaustion_raise` (FunctionDef), line 107–114
- `ParityTests.test_restoring_cloud_preserves_first_seen_and_inactive_status` (FunctionDef), line 116–122
- `ParityTests.test_cloud_notification_guard_never_posts` (FunctionDef), line 124–127
- `ParityTests.test_full_description_survives_long_listing_teaser` (FunctionDef), line 129–134
- `ParityTests.test_runtime_schedule_is_same_each_day_and_dst_aware` (FunctionDef), line 136–142

### test_official_routes.py

Offline regressions for discovered coverage gaps and notification history.

Location: `D:\abet_ops\sports_teams\test_official_routes.py`.

Imports: `json, os, sqlite3, unittest, sys, contextlib, io`, `unittest.mock`, `live_refresh`, `publish_teams`, `cloud_storage, pipeline_local, coverage_report`, `providers`.

- `response` (FunctionDef), line 9–10
- `OfficialRoutes` (ClassDef), line 12–118
- `OfficialRoutes.test_dayforce_language_is_not_silently_changed` (FunctionDef), line 13–16
- `OfficialRoutes.test_dayforce_pagination_uses_real_offset_and_rejects_truncation` (FunctionDef), line 18–26
- `OfficialRoutes.test_dayforce_missing_nonce_and_repeated_jobs_are_errors` (FunctionDef), line 28–33
- `OfficialRoutes.test_bamboohr_incomplete_payload_does_not_mean_empty` (FunctionDef), line 35–37
- `OfficialRoutes.test_adp_preserves_celtics_career_center_in_request_and_links` (FunctionDef), line 39–44
- `OfficialRoutes.test_teamwork_organization_filter_remains_distinct` (FunctionDef), line 46–49
- `OfficialRoutes.test_adp_truncated_final_page_fails` (FunctionDef), line 51–53
- `OfficialRoutes.test_adp_server_page_cap_does_not_skip_jobs` (FunctionDef), line 55–58
- `OfficialRoutes.test_workday_missing_total_cannot_close_jobs` (FunctionDef), line 60–63
- `OfficialRoutes.test_workday_later_page_zero_total_keeps_first_page_total` (FunctionDef), line 65–70
- `OfficialRoutes.test_jobvite_loading_page_is_error_not_zero_jobs` (FunctionDef), line 72–74
- `OfficialRoutes.test_notification_rejects_broken_workday_link` (FunctionDef), line 76–77
- `OfficialRoutes.test_embed_separates_employer_date_from_delivery_timestamp` (FunctionDef), line 79–84
- `OfficialRoutes.test_notification_save_preserves_seeded_status_and_timestamp` (FunctionDef), line 86–90
- `OfficialRoutes.test_baseline_rows_are_never_marked_delivered` (FunctionDef), line 92–96
- `OfficialRoutes.test_old_database_rows_are_not_implicitly_queued` (FunctionDef), line 98–100
- `OfficialRoutes.test_zero_limit_delivers_all_and_acknowledges_each_chunk` (FunctionDef), line 102–106
- `OfficialRoutes.test_alias_restore_drops_only_stale_local_copy` (FunctionDef), line 108–114
- `OfficialRoutes.test_coverage_does_not_claim_all_teams_from_source_count` (FunctionDef), line 116–118

### test_pipeline_regressions.py

Offline regression checks. All notification and HTTP calls are mocked.

Location: `D:\abet_ops\sports_teams\test_pipeline_regressions.py`.

Imports: `contextlib`, `io`, `json`, `sqlite3`, `sys`, `unittest`, `unittest.mock`, `live_refresh`, `pipeline_local`, `publish_teams`, `providers`, `providers.base`.

- `PipelineTests` (ClassDef), line 16–132
- `PipelineTests.setUp` (FunctionDef), line 17–19
- `PipelineTests.tearDown` (FunctionDef), line 21–22
- `PipelineTests.row` (FunctionDef), line 24–27
- `PipelineTests.result` (FunctionDef), line 29–32
- `PipelineTests.test_failed_source_preserves_jobs_and_last_seen` (FunctionDef), line 34–39
- `PipelineTests.test_empty_source_cannot_close_previous_jobs` (FunctionDef), line 41–44
- `PipelineTests.test_only_successful_source_can_close_its_missing_job` (FunctionDef), line 46–49
- `PipelineTests.test_first_seen_stable_and_runs_are_per_source` (FunctionDef), line 51–58
- `PipelineTests.test_cross_listed_job_survives_other_source_failure` (FunctionDef), line 60–66
- `PipelineTests.test_same_url_under_different_team_label_is_not_duplicated` (FunctionDef), line 68–71
- `PipelineTests.test_short_listing_does_not_destroy_full_description` (FunctionDef), line 73–76
- `PipelineTests.test_workday_url_and_legacy_incomplete_link` (FunctionDef), line 78–81
- `PipelineTests.test_irregular_teamwork_slug` (FunctionDef), line 83–87
- `PipelineTests.test_request_budget` (FunctionDef), line 89–93
- `PipelineTests.test_nba_keeps_workday_as_ats_platform` (FunctionDef), line 95–100
- `PipelineTests.publishing` (FunctionDef), line 102–107
- `PipelineTests.test_limit_does_not_mark_backlog_as_posted` (FunctionDef), line 109–112
- `PipelineTests.test_failed_chunk_remains_unseen` (FunctionDef), line 114–117
- `PipelineTests.test_all_failed_does_not_change_state` (FunctionDef), line 119–122
- `PipelineTests.test_publish_without_mode_does_not_send` (FunctionDef), line 124–127
- `PipelineTests.test_dry_run_never_sends_or_updates_state` (FunctionDef), line 129–132

### test_source_delivery_parity.py

test/verification; inspect linked source and symbol map for exact behavior

Location: `D:\abet_ops\sports_teams\test_source_delivery_parity.py`.

Imports: `contextlib, io, json, os, sys, tempfile, unittest`, `pathlib`, `types`, `unittest.mock`, `live_refresh`, `publish_teams`, `cloud_storage`.

- `Parity` (ClassDef), line 9–40
- `Parity.test_only_explicit_team_sources_can_enter_production` (FunctionDef), line 10–17
- `Parity.test_no_generic_league_discovery` (FunctionDef), line 19–22
- `Parity.test_queued_new_job_only_and_failed_delivery_stays_pending` (FunctionDef), line 24–30
- `Parity.test_queue_creation_never_resets_delivered_history` (FunctionDef), line 32–36
- `Parity.test_old_dayforce_links_keep_team_tenant_board_and_language` (FunctionDef), line 38–40

### test_worker.mjs

test/verification; inspect linked source and symbol map for exact behavior

Location: `D:\abet_ops\sports_teams\test_worker.mjs`.

Imports: `./cloud_worker.js`, `node:assert/strict`.

- `request` (JS declaration (text scan)), line 6

### verify_deployment.py

Read-only production certification; no credentials or individual jobs in output.

Location: `D:\abet_ops\sports_teams\verify_deployment.py`.

Imports: `json`, `sqlite3`, `datetime`, `pathlib`, `requests`, `deploy_cloud`.

- `main` (FunctionDef), line 12–60
- `main.utc` (FunctionDef), line 28–30

### verify_official_sources.py

Sequential, checkpointed source verification. HTTP only, no production writes.

Location: `D:\abet_ops\sports_teams\verify_official_sources.py`.

Imports: `argparse, json, hashlib`, `pathlib`, `live_refresh`.

- `main` (FunctionDef), line 12–27

### verify_route_evidence.py

Check retained official-page evidence without equating a branded ATS with a referral.

Location: `D:\abet_ops\sports_teams\verify_route_evidence.py`.

Imports: `gzip, hashlib, json, re`, `html`, `pathlib`, `urllib.parse`, `live_refresh`, `audit_official_careers`.

- `key` (FunctionDef), line 11–13
- `check` (FunctionDef), line 15–57

