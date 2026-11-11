# robotics-and-teams — file and symbol inventory

Revision: `7f57a99b30d4eca9700375920c30918d2845cace`. Root: `D:\abet\job-radar`.

inspection_status: Deployed Git objects read directly; dirty local checkout preserved.

| File | Physical lines | Nonblank | Bytes | Category |
|---|---:|---:|---:|---|
| [.env.example](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/.env.example) | — | — | 982 | sensitive/private content; metadata only |
| [.github/workflows/pipeline.yml](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/.github/workflows/pipeline.yml) | 64 | 60 | 2146 | workflow |
| [.github/workflows/sports-teams-board.yml](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/.github/workflows/sports-teams-board.yml) | 38 | 38 | 1443 | workflow |
| [.github/workflows/sports-teams-notification-audit.yml](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/.github/workflows/sports-teams-notification-audit.yml) | 28 | 28 | 997 | workflow |
| [.github/workflows/sports-teams-workday-repair.yml](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/.github/workflows/sports-teams-workday-repair.yml) | 23 | 23 | 675 | workflow |
| [.github/workflows/sports-teams.yml](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/.github/workflows/sports-teams.yml) | 108 | 108 | 4952 | workflow |
| [.gitignore](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/.gitignore) | 38 | 33 | 392 | support/module |
| [README.md](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/README.md) | 46 | 32 | 3969 | documentation |
| [audit_targets.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/audit_targets.py) | 129 | 104 | 4453 | support/module |
| [config/settings.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/config/settings.py) | 54 | 41 | 2141 | support/module |
| [config/skills_matrix.md](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/config/skills_matrix.md) | — | — | 26484 | sensitive/private content; metadata only |
| [config/targets.json](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/config/targets.json) | 100 | 100 | 3637 | configuration/data |
| [dashboard/.env.example](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/dashboard/.env.example) | — | — | 236 | sensitive/private content; metadata only |
| [dashboard/app/RadarBoard.tsx](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/dashboard/app/RadarBoard.tsx) | 104 | 92 | 6747 | support/module |
| [dashboard/app/api/apply/route.ts](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/dashboard/app/api/apply/route.ts) | 23 | 21 | 1251 | support/module |
| [dashboard/app/layout.tsx](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/dashboard/app/layout.tsx) | 5 | 4 | 287 | support/module |
| [dashboard/app/page.tsx](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/dashboard/app/page.tsx) | 31 | 27 | 1066 | support/module |
| [dashboard/board_template.html](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/dashboard/board_template.html) | 231 | 231 | 18617 | frontend/API |
| [dashboard/next.config.js](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/dashboard/next.config.js) | 2 | 2 | 83 | support/module |
| [dashboard/package.json](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/dashboard/package.json) | 21 | 21 | 410 | configuration/data |
| [dashboard/tsconfig.json](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/dashboard/tsconfig.json) | 16 | 16 | 357 | configuration/data |
| [db/apply_schema.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/db/apply_schema.py) | 38 | 30 | 1321 | storage |
| [db/schema.sql](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/db/schema.sql) | 92 | 86 | 3664 | database schema/migration |
| [db/schema_notifications.sql](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/db/schema_notifications.sql) | 22 | 21 | 1076 | database schema/migration |
| [db/schema_robotics.sql](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/db/schema_robotics.sql) | 124 | 109 | 5002 | database schema/migration |
| [docs/job-scrapers/2026-11-10 1030 Job Scrapers Architecture.md](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/2026-11-10%201030%20Job%20Scrapers%20Architecture.md) | 112 | 75 | 15695 | source ingestion |
| [docs/job-scrapers/2026-11-10 1030 Job Scrapers Operations Runbook.md](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/2026-11-10%201030%20Job%20Scrapers%20Operations%20Runbook.md) | 87 | 55 | 11598 | source ingestion |
| [docs/job-scrapers/2026-11-10 1030 New Industry Scraper Build Guide.md](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/2026-11-10%201030%20New%20Industry%20Scraper%20Build%20Guide.md) | 112 | 79 | 11881 | source ingestion |
| [docs/job-scrapers/2026-11-10 1145 Dashboard Jobs Wiring and Inventory Guide.md](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/2026-11-10%201145%20Dashboard%20Jobs%20Wiring%20and%20Inventory%20Guide.md) | 90 | 64 | 11497 | source ingestion |
| [docs/job-scrapers/2026-11-10 1235 Jobs Board UI Contract.md](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/2026-11-10%201235%20Jobs%20Board%20UI%20Contract.md) | 71 | 44 | 11588 | source ingestion |
| [docs/job-scrapers/2026-11-10 1345 Dashboard Presentation Parity Proof.md](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/2026-11-10%201345%20Dashboard%20Presentation%20Parity%20Proof.md) | 24 | 18 | 2727 | source ingestion |
| [docs/job-scrapers/2026-11-10 2004 Tech and Robotics Scraper Diagnosis.md](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/2026-11-10%202004%20Tech%20and%20Robotics%20Scraper%20Diagnosis.md) | 103 | 67 | 11742 | source ingestion |
| [docs/job-scrapers/2026-11-10 2135 Tech and Robotics Production Repair.md](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/2026-11-10%202135%20Tech%20and%20Robotics%20Production%20Repair.md) | 94 | 62 | 15285 | source ingestion |
| [docs/job-scrapers/2026-11-11 0010 Sports Teams Repair and Four Scraper Verification.md](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/2026-11-11%200010%20Sports%20Teams%20Repair%20and%20Four%20Scraper%20Verification.md) | 66 | 38 | 12623 | source ingestion |
| [docs/job-scrapers/20261110_repair_verification.json](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/20261110_repair_verification.json) | 323 | 323 | 10532 | source ingestion |
| [docs/job-scrapers/20261110_verification.json](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/20261110_verification.json) | 380 | 380 | 12443 | source ingestion |
| [docs/job-scrapers/20261111_four_scraper_proof.json](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/20261111_four_scraper_proof.json) | 12353 | 12353 | 456172 | source ingestion |
| [docs/job-scrapers/20261111_runtime_verification.json](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/20261111_runtime_verification.json) | 397 | 397 | 13247 | source ingestion |
| [docs/job-scrapers/README.md](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/README.md) | 41 | 28 | 5548 | source ingestion |
| [docs/job-scrapers/audit_20261110/dashboard_live_data.json](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/audit_20261110/dashboard_live_data.json) | 54 | 54 | 1818 | source ingestion |
| [docs/job-scrapers/audit_20261110/public_pages_verified.json](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/audit_20261110/public_pages_verified.json) | 81 | 81 | 2166 | source ingestion |
| [docs/job-scrapers/build_schema_dictionary.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/build_schema_dictionary.py) | 46 | 46 | 4467 | source ingestion |
| [docs/job-scrapers/export_job_schema.sql](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/export_job_schema.sql) | 27 | 27 | 2744 | database schema/migration |
| [docs/job-scrapers/generate_inventory.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/generate_inventory.py) | 161 | 153 | 13019 | source ingestion |
| [docs/job-scrapers/inventory/DATABASE.md](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/inventory/DATABASE.md) | — | — | 40660 | source ingestion |
| [docs/job-scrapers/inventory/README.md](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/inventory/README.md) | — | — | 2520 | source ingestion |
| [docs/job-scrapers/inventory/abet-dashboard.md](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/inventory/abet-dashboard.md) | — | — | 1490194 | source ingestion |
| [docs/job-scrapers/inventory/cross-module-operator-scripts.md](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/inventory/cross-module-operator-scripts.md) | — | — | 3444 | source ingestion |
| [docs/job-scrapers/inventory/database_catalog.json](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/inventory/database_catalog.json) | — | — | 191912 | source ingestion |
| [docs/job-scrapers/inventory/robotics-and-teams.md](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/inventory/robotics-and-teams.md) | — | — | 150395 | source ingestion |
| [docs/job-scrapers/inventory/robotics-standalone.md](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/inventory/robotics-standalone.md) | — | — | 17428 | source ingestion |
| [docs/job-scrapers/inventory/source_inventory.json](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/inventory/source_inventory.json) | — | — | 3999525 | source ingestion |
| [docs/job-scrapers/inventory/sportsbook-deployed-space.md](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/inventory/sportsbook-deployed-space.md) | — | — | 121761 | source ingestion |
| [docs/job-scrapers/inventory/sportsbook-frontend.md](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/inventory/sportsbook-frontend.md) | — | — | 98754 | source ingestion |
| [docs/job-scrapers/inventory/sportsbook-runtime.md](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/inventory/sportsbook-runtime.md) | — | — | 140640 | source ingestion |
| [docs/job-scrapers/inventory/sportsbook-watchdog.md](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/inventory/sportsbook-watchdog.md) | — | — | 621 | source ingestion |
| [docs/job-scrapers/inventory/sqlite_catalog.json](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/inventory/sqlite_catalog.json) | — | — | 3841 | source ingestion |
| [docs/job-scrapers/inventory/teams-operator-helpers.md](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/inventory/teams-operator-helpers.md) | — | — | 27017 | source ingestion |
| [docs/job-scrapers/inventory/tech-standalone.md](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/inventory/tech-standalone.md) | — | — | 10342 | source ingestion |
| [docs/job-scrapers/inventory/tech.md](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/inventory/tech.md) | — | — | 58550 | source ingestion |
| [docs/job-scrapers/inventory_runtimes.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/inventory_runtimes.py) | 55 | 53 | 4126 | source ingestion |
| [docs/job-scrapers/scrapers.json](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/scrapers.json) | 155 | 155 | 5879 | source ingestion |
| [docs/job-scrapers/ui/dashboard-parity-interaction-proof.json](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/ui/dashboard-parity-interaction-proof.json) | 70 | 70 | 1698 | source ingestion |
| [docs/job-scrapers/ui/dashboard-parity-live-proof.json](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/ui/dashboard-parity-live-proof.json) | 46 | 46 | 2015 | source ingestion |
| [docs/job-scrapers/ui/dashboard-parity-publication.json](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/ui/dashboard-parity-publication.json) | 36 | 36 | 1823 | source ingestion |
| [docs/job-scrapers/ui/fixture-verification.json](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/ui/fixture-verification.json) | 42 | 42 | 763 | source ingestion |
| [docs/job-scrapers/ui/job-board-core.mjs](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/ui/job-board-core.mjs) | 130 | 121 | 9915 | source ingestion |
| [docs/job-scrapers/ui/live-ui-verification.json](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/ui/live-ui-verification.json) | 49 | 49 | 1471 | source ingestion |
| [docs/job-scrapers/ui/presentation-dom-proof.json](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/ui/presentation-dom-proof.json) | 50 | 50 | 1165 | source ingestion |
| [docs/job-scrapers/ui/presentation-live-proof.json](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/ui/presentation-live-proof.json) | 48 | 48 | 1636 | source ingestion |
| [docs/job-scrapers/ui/presentation-publication.json](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/ui/presentation-publication.json) | 80 | 80 | 3111 | source ingestion |
| [docs/job-scrapers/ui/publication.json](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/ui/publication.json) | 106 | 106 | 4371 | source ingestion |
| [docs/job-scrapers/ui/standalone-ui.mjs](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/ui/standalone-ui.mjs) | 42 | 42 | 3999 | source ingestion |
| [docs/job-scrapers/ui/standalone.css](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/ui/standalone.css) | 10 | 10 | 7236 | source ingestion |
| [docs/job-scrapers/ui/verify_standalone_presentation.mjs](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/ui/verify_standalone_presentation.mjs) | 88 | 87 | 9283 | source ingestion |
| [docs/job-scrapers/verify_dashboard_presentation.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/verify_dashboard_presentation.py) | 39 | 39 | 3888 | source ingestion |
| [docs/job-scrapers/verify_jobs_ui.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/verify_jobs_ui.py) | 36 | 36 | 3773 | source ingestion |
| [docs/job-scrapers/verify_public_jobs_pages.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/verify_public_jobs_pages.py) | 51 | 50 | 4549 | source ingestion |
| [docs/job-scrapers/verify_scrapers.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/verify_scrapers.py) | 97 | 90 | 6893 | source ingestion |
| [docs/job-scrapers/verify_standalone_presentation.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/verify_standalone_presentation.py) | 32 | 32 | 3053 | source ingestion |
| [jobradar/__init__.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/__init__.py) | 2 | 2 | 113 | support/module |
| [jobradar/alerts/__init__.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/alerts/__init__.py) | 1 | 1 | 25 | support/module |
| [jobradar/alerts/discord.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/alerts/discord.py) | 52 | 39 | 1892 | support/module |
| [jobradar/dashboard.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/dashboard.py) | 102 | 92 | 5145 | support/module |
| [jobradar/diagnostics.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/diagnostics.py) | 16 | 14 | 768 | support/module |
| [jobradar/fetch_worker.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/fetch_worker.py) | 47 | 41 | 2353 | runtime/deployment |
| [jobradar/generate/__init__.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/generate/__init__.py) | 1 | 1 | 63 | support/module |
| [jobradar/generate/resume.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/generate/resume.py) | — | — | 4137 | sensitive/private content; metadata only |
| [jobradar/matcher/__init__.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/matcher/__init__.py) | 1 | 1 | 81 | support/module |
| [jobradar/matcher/judge.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/matcher/judge.py) | 131 | 112 | 5483 | support/module |
| [jobradar/matcher/llm_judge.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/matcher/llm_judge.py) | 201 | 169 | 9945 | support/module |
| [jobradar/matcher/prefilter.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/matcher/prefilter.py) | 45 | 35 | 1752 | support/module |
| [jobradar/matcher/profile.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/matcher/profile.py) | 38 | 31 | 1522 | support/module |
| [jobradar/matcher/score.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/matcher/score.py) | 44 | 35 | 1830 | support/module |
| [jobradar/models.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/models.py) | 53 | 40 | 1612 | support/module |
| [jobradar/providers/__init__.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/providers/__init__.py) | 37 | 32 | 1203 | source ingestion |
| [jobradar/providers/amazon.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/providers/amazon.py) | 72 | 65 | 3043 | source ingestion |
| [jobradar/providers/ashby.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/providers/ashby.py) | 55 | 44 | 2205 | source ingestion |
| [jobradar/providers/base.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/providers/base.py) | 39 | 28 | 1052 | source ingestion |
| [jobradar/providers/greenhouse.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/providers/greenhouse.py) | 66 | 55 | 2389 | source ingestion |
| [jobradar/providers/lever.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/providers/lever.py) | 45 | 37 | 1778 | source ingestion |
| [jobradar/providers/names.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/providers/names.py) | 93 | 87 | 2893 | source ingestion |
| [jobradar/providers/workday.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/providers/workday.py) | 97 | 87 | 3923 | source ingestion |
| [jobradar/publish.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/publish.py) | 492 | 434 | 21163 | publication/delivery |
| [jobradar/relevance.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/relevance.py) | 287 | 249 | 14458 | support/module |
| [jobradar/storage.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/storage.py) | 299 | 261 | 14418 | storage |
| [requirements.txt](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/requirements.txt) | 4 | 4 | 79 | configuration/data |
| [run.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/run.py) | 233 | 198 | 9367 | support/module |
| [runtime/cloudflare/test_scheduler.mjs](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/runtime/cloudflare/test_scheduler.mjs) | 72 | 71 | 4340 | test/verification |
| [runtime/cloudflare/worker.mjs](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/runtime/cloudflare/worker.mjs) | 161 | 150 | 7847 | runtime/deployment |
| [sports_teams/.gitignore](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/.gitignore) | 5 | 5 | 48 | support/module |
| [sports_teams/README.md](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/README.md) | 73 | 60 | 5111 | documentation |
| [sports_teams/board/job-board-core.mjs](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/board/job-board-core.mjs) | 130 | 121 | 9915 | support/module |
| [sports_teams/board/live.html](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/board/live.html) | 68 | 67 | 11947 | frontend/API |
| [sports_teams/board/standalone-ui.mjs](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/board/standalone-ui.mjs) | 42 | 42 | 3999 | support/module |
| [sports_teams/board/standalone.css](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/board/standalone.css) | 10 | 10 | 7236 | frontend/API |
| [sports_teams/career_link_proof_20261111.json](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/career_link_proof_20261111.json) | 198 | 198 | 11345 | configuration/data |
| [sports_teams/cloud_storage.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/cloud_storage.py) | 116 | 104 | 6820 | storage |
| [sports_teams/coverage_report.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/coverage_report.py) | 45 | 42 | 4842 | support/module |
| [sports_teams/db/schema_cloud.sql](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/db/schema_cloud.sql) | 56 | 56 | 4074 | database schema/migration |
| [sports_teams/enrichment.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/enrichment.py) | 96 | 88 | 4692 | support/module |
| [sports_teams/live_refresh.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/live_refresh.py) | 338 | 317 | 20851 | source ingestion |
| [sports_teams/mlb_clubs.json](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/mlb_clubs.json) | 296 | 296 | 6150 | configuration/data |
| [sports_teams/notification_audit.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/notification_audit.py) | 26 | 25 | 1773 | publication/delivery |
| [sports_teams/official_careers_registry.json](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/official_careers_registry.json) | 4408 | 4408 | 197653 | configuration/data |
| [sports_teams/official_link_reviews.json](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/official_link_reviews.json) | 199 | 199 | 8812 | configuration/data |
| [sports_teams/pipeline_local.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/pipeline_local.py) | 259 | 234 | 11657 | support/module |
| [sports_teams/providers/adp.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/providers/adp.py) | 84 | 74 | 3656 | source ingestion |
| [sports_teams/providers/base.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/providers/base.py) | 31 | 26 | 1094 | source ingestion |
| [sports_teams/providers/nba.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/providers/nba.py) | 87 | 77 | 3585 | source ingestion |
| [sports_teams/providers/nfl.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/providers/nfl.py) | 44 | 35 | 1711 | source ingestion |
| [sports_teams/providers/official_ats.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/providers/official_ats.py) | 351 | 331 | 22703 | source ingestion |
| [sports_teams/providers/teamwork.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/providers/teamwork.py) | 124 | 104 | 5005 | source ingestion |
| [sports_teams/providers/teamwork_vertical.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/providers/teamwork_vertical.py) | 87 | 74 | 3274 | source ingestion |
| [sports_teams/providers/ultipro.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/providers/ultipro.py) | 63 | 55 | 2844 | source ingestion |
| [sports_teams/publish_teams.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/publish_teams.py) | 390 | 336 | 14867 | publication/delivery |
| [sports_teams/repair_workday_cloud.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/repair_workday_cloud.py) | 93 | 89 | 6734 | support/module |
| [sports_teams/requirements.txt](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/requirements.txt) | 3 | 3 | 59 | configuration/data |
| [sports_teams/run.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/run.py) | 35 | 31 | 1781 | support/module |
| [sports_teams/runtime.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/runtime.py) | 126 | 106 | 6267 | runtime/deployment |
| [sports_teams/sources.json](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/sources.json) | 2015 | 2015 | 62135 | configuration/data |
| [sports_teams/team_logos.json](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/team_logos.json) | 622 | 622 | 18010 | configuration/data |
| [sports_teams/teams.json](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/teams.json) | 1430 | 1430 | 52673 | configuration/data |
| [sports_teams/test_career_link_proof.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_career_link_proof.py) | 37 | 33 | 2063 | test/verification |
| [sports_teams/test_cloud_parity.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_cloud_parity.py) | 145 | 124 | 10170 | test/verification |
| [sports_teams/test_official_routes.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_official_routes.py) | 120 | 99 | 9663 | test/verification |
| [sports_teams/test_pipeline_regressions.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_pipeline_regressions.py) | 136 | 111 | 7556 | test/verification |
| [sports_teams/test_repair_nov10.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_repair_nov10.py) | 62 | 51 | 3640 | test/verification |
| [sports_teams/test_source_delivery_parity.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_source_delivery_parity.py) | 42 | 36 | 2836 | test/verification |
| [sports_teams/verification-20261111/career-link-proof.json](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/verification-20261111/career-link-proof.json) | 198 | 198 | 11345 | configuration/data |
| [sports_teams/verification-20261111/screenshots/bucks-careers.jpg](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/verification-20261111/screenshots/bucks-careers.jpg) | — | — | 424721 | support/module |
| [sports_teams/verification-20261111/screenshots/bulls-careers.jpg](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/verification-20261111/screenshots/bulls-careers.jpg) | — | — | 176320 | support/module |
| [sports_teams/verification-20261111/screenshots/clippers-careers.jpg](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/verification-20261111/screenshots/clippers-careers.jpg) | — | — | 156252 | support/module |
| [sports_teams/workday_repair_plan.json](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/workday_repair_plan.json) | 472 | 472 | 22878 | configuration/data |
| [tests/test_board_filter.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_board_filter.py) | 90 | 68 | 3668 | test/verification |
| [tests/test_core.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_core.py) | 94 | 76 | 4036 | test/verification |
| [tests/test_diagnostics.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_diagnostics.py) | 23 | 18 | 1043 | test/verification |
| [tests/test_provider_completeness.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_provider_completeness.py) | 78 | 67 | 5217 | test/verification |
| [tests/test_relevance.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_relevance.py) | 210 | 177 | 9393 | test/verification |
| [tests/test_reliability.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_reliability.py) | 296 | 268 | 13774 | test/verification |
| [tests/test_render.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_render.py) | 63 | 52 | 2702 | test/verification |
| [validate_relevance.py](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/validate_relevance.py) | 90 | 72 | 3240 | support/module |

## Script definitions and dependencies

### .github/workflows/pipeline.yml

workflow; inspect linked source and symbol map for exact behavior

Location: `D:\abet\job-radar\.github\workflows\pipeline.yml`.

Workflow metadata: `{"crons": [], "step_names": ["job-radar-pipeline", "Install dependencies", "Regression checks", "Apply additive schema", "Scrape, reconcile, and deliver pending notifications", "Render dashboard artifact", "job-radar-receipt"], "run_lines": [{"line": 35, "text": "run: pip install -r requirements.txt"}, {"line": 37, "text": "run: python -m unittest discover -s tests -v"}, {"line": 42, "text": "run: python db/apply_schema.py"}, {"line": 50, "text": "run: python -u run.py ingest"}, {"line": 56, "text": "run: python run.py render --out out/dashboard.html"}], "timeouts": ["45"]}`


### .github/workflows/sports-teams-board.yml

workflow; inspect linked source and symbol map for exact behavior

Location: `D:\abet\job-radar\.github\workflows\sports-teams-board.yml`.

Workflow metadata: `{"crons": [], "step_names": ["sports-teams-board-only", "github-pages", "Prepare UI and preserve latest public scrape receipts"], "run_lines": [{"line": 22, "text": "run: |"}], "timeouts": ["10"]}`


### .github/workflows/sports-teams-notification-audit.yml

workflow; inspect linked source and symbol map for exact behavior

Location: `D:\abet\job-radar\.github\workflows\sports-teams-notification-audit.yml`.

Workflow metadata: `{"crons": [], "step_names": ["sports-teams-notification-audit", "Regression checks without publishing", "Inspect delivery state without publishing", "sports-teams-notification-audit"], "run_lines": [{"line": 17, "text": "run: python -m unittest discover -p 'test_*.py'"}, {"line": 24, "text": "run: python notification_audit.py"}], "timeouts": ["5"]}`


### .github/workflows/sports-teams-workday-repair.yml

workflow; inspect linked source and symbol map for exact behavior

Location: `D:\abet\job-radar\.github\workflows\sports-teams-workday-repair.yml`.

Workflow metadata: `{"crons": [], "step_names": ["sports-teams-workday-repair", "Back up and atomically repair legacy URLs"], "run_lines": [{"line": 23, "text": "run: python repair_workday_cloud.py"}], "timeouts": ["5"]}`


### .github/workflows/sports-teams.yml

workflow; inspect linked source and symbol map for exact behavior

Location: `D:\abet\job-radar\.github\workflows\sports-teams.yml`.

Workflow metadata: `{"crons": [], "step_names": ["sports-teams-jobs", "github-pages", "Regression checks", "Scrape and persist all supported sources", "Notification guard and delivery", "Prepare live board and health receipt", "sports-teams-scrape-receipt", "Surface source failures"], "run_lines": [{"line": 40, "text": "run:"}, {"line": 55, "text": "run: python -m unittest discover -p 'test_*.py'"}, {"line": 58, "text": "run: python -u pipeline_local.py --cloud --trigger '${{ inputs.trigger_source || github.event_name }}' --detail-limit '${{ github.event.inputs.detail_limit || 250 }}' ${{ github.event.inputs.recover_pending == 'true' && '--recover-pending' || '' }}"}, {"line": 62, "text": "run: |"}, {"line": 69, "text": "run: |"}, {"line": 99, "text": "run: |"}], "timeouts": ["45"]}`


### audit_targets.py

One-off audit: are the robots actually the right robots?

Location: `D:\abet\job-radar\audit_targets.py`.

Imports: `json`, `re`, `sys`, `pathlib`, `requests`, `config`.

- `gh` (FunctionDef), [line 23–32](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/audit_targets.py#L23)
- `lever` (FunctionDef), [line 35–42](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/audit_targets.py#L35)
- `ashby` (FunctionDef), [line 45–52](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/audit_targets.py#L45)
- `_slugs` (FunctionDef), [line 58–69](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/audit_targets.py#L58)
- `main` (FunctionDef), [line 80–125](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/audit_targets.py#L80)

### config/settings.py

Central config: loads .env + config/targets.json and exposes tuning knobs.

Location: `D:\abet\job-radar\config\settings.py`.

Imports: `__future__`, `json`, `os`, `pathlib`, `dotenv`.

- `_get` (FunctionDef), [line 17–18](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/config/settings.py#L17)
- `load_targets` (FunctionDef), [line 52–54](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/config/settings.py#L52)

### dashboard/app/RadarBoard.tsx

support/module; inspect linked source and symbol map for exact behavior

Location: `D:\abet\job-radar\dashboard\app\RadarBoard.tsx`.

Imports: `react`.

- `color` (JS declaration (text scan)), [line 18](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/dashboard/app/RadarBoard.tsx#L18)
- `RadarBoard` (JS declaration (text scan)), [line 20](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/dashboard/app/RadarBoard.tsx#L20)
- `markApplied` (JS declaration (text scan)), [line 43](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/dashboard/app/RadarBoard.tsx#L43)

### dashboard/app/api/apply/route.ts

support/module; inspect linked source and symbol map for exact behavior

Location: `D:\abet\job-radar\dashboard\app\api\apply\route.ts`.

Imports: `next/server`.

- `POST` (JS declaration (text scan)), [line 4](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/dashboard/app/api/apply/route.ts#L4)

### dashboard/app/layout.tsx

support/module; inspect linked source and symbol map for exact behavior

Location: `D:\abet\job-radar\dashboard\app\layout.tsx`.

- `RootLayout` (JS declaration (text scan)), [line 3](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/dashboard/app/layout.tsx#L3)

### dashboard/app/page.tsx

support/module; inspect linked source and symbol map for exact behavior

Location: `D:\abet\job-radar\dashboard\app\page.tsx`.

Imports: `./RadarBoard`.

- `sb` (JS declaration (text scan)), [line 5](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/dashboard/app/page.tsx#L5)
- `Page` (JS declaration (text scan)), [line 17](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/dashboard/app/page.tsx#L17)

### db/schema.sql

database schema/migration; inspect linked source and symbol map for exact behavior

Location: `D:\abet\job-radar\db\schema.sql`.

- `public.jobs` (table), [line 3](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/db/schema.sql#L3)
- `idx_jobs_company` (index), [line 23](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/db/schema.sql#L23)
- `idx_jobs_scraped_at` (index), [line 24](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/db/schema.sql#L24)
- `public.job_scores` (table), [line 25](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/db/schema.sql#L25)
- `idx_job_scores_fit` (index), [line 40](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/db/schema.sql#L40)
- `public.applications` (table), [line 41](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/db/schema.sql#L41)
- `public.scrape_runs` (table), [line 56](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/db/schema.sql#L56)
- `public.radar` (view), [line 70](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/db/schema.sql#L70)
- `public.source_health` (view), [line 84](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/db/schema.sql#L84)

### db/schema_notifications.sql

database schema/migration; inspect linked source and symbol map for exact behavior

Location: `D:\abet\job-radar\db\schema_notifications.sql`.

- `public.robotics_job_notifications` (table), [line 3](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/db/schema_notifications.sql#L3)
- `robotics_job_notifications_pending_idx` (index), [line 19](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/db/schema_notifications.sql#L19)

### db/schema_robotics.sql

database schema/migration; inspect linked source and symbol map for exact behavior

Location: `D:\abet\job-radar\db\schema_robotics.sql`.

- `public.robotics_jobs` (table), [line 9](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/db/schema_robotics.sql#L9)
- `idx_robotics_jobs_company` (index), [line 25](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/db/schema_robotics.sql#L25)
- `idx_robotics_jobs_url` (index), [line 27](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/db/schema_robotics.sql#L27)
- `idx_robotics_jobs_is_active` (index), [line 28](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/db/schema_robotics.sql#L28)
- `idx_robotics_jobs_posted_at` (index), [line 29](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/db/schema_robotics.sql#L29)
- `public.robotics_applications` (table), [line 32](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/db/schema_robotics.sql#L32)
- `idx_robotics_applications_company` (index), [line 43](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/db/schema_robotics.sql#L43)
- `idx_robotics_applications_applied_at` (index), [line 45](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/db/schema_robotics.sql#L45)
- `public.touch_robotics_updated_at` (function), [line 46](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/db/schema_robotics.sql#L46)
- `trg_robotics_applications_touch` (trigger), [line 56](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/db/schema_robotics.sql#L56)
- `public.robotics_job_scrape_runs` (table), [line 61](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/db/schema_robotics.sql#L61)
- `idx_robotics_job_scrape_runs_provider` (index), [line 70](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/db/schema_robotics.sql#L70)
- `"anon` (policy), [line 80](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/db/schema_robotics.sql#L80)
- `"anon` (policy), [line 86](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/db/schema_robotics.sql#L86)
- `"anon` (policy), [line 98](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/db/schema_robotics.sql#L98)
- `"anon` (policy), [line 104](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/db/schema_robotics.sql#L104)
- `"anon` (policy), [line 110](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/db/schema_robotics.sql#L110)
- `public.robotics_jobs_with_applied` (view), [line 116](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/db/schema_robotics.sql#L116)

### docs/job-scrapers/build_schema_dictionary.py

Read a catalog artifact and local SQLite metadata; produce no job/applicant rows.

Location: `D:\abet\job-radar\docs\job-scrapers\build_schema_dictionary.py`.

Imports: `argparse, json, sqlite3`, `pathlib`.

- `cell` (FunctionDef), [line 6–6](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/build_schema_dictionary.py#L6)
- `main` (FunctionDef), [line 7–45](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/build_schema_dictionary.py#L7)

### docs/job-scrapers/generate_inventory.py

Bounded, read-only source inventory. Owner: ABET jobs documentation.

Location: `D:\abet\job-radar\docs\job-scrapers\generate_inventory.py`.

Imports: `ast, base64, hashlib, io, json, re, subprocess, sys`, `datetime`, `pathlib`, `urllib.parse`.

- `command` (FunctionDef), [line 18–21](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/generate_inventory.py#L18)
- `gh` (FunctionDef), [line 22–22](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/generate_inventory.py#L22)
- `category` (FunctionDef), [line 23–37](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/generate_inventory.py#L23)
- `eligible` (FunctionDef), [line 38–42](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/generate_inventory.py#L38)
- `details` (FunctionDef), [line 43–70](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/generate_inventory.py#L43)
- `details.walk` (FunctionDef), [line 50–56](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/generate_inventory.py#L50)
- `git_inventory` (FunctionDef), [line 72–90](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/generate_inventory.py#L72)
- `remote_inventory` (FunctionDef), [line 92–101](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/generate_inventory.py#L92)
- `local_helpers` (FunctionDef), [line 103–110](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/generate_inventory.py#L103)
- `write` (FunctionDef), [line 112–139](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/generate_inventory.py#L112)
- `main` (FunctionDef), [line 141–159](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/generate_inventory.py#L141)

### docs/job-scrapers/inventory_runtimes.py

Finite GET-only HF/Cloudflare metadata inventory; no runtime triggers or secret output.

Location: `D:\abet\job-radar\docs\job-scrapers\inventory_runtimes.py`.

Imports: `email.policy, json, sys`, `email.parser`, `pathlib`, `urllib.parse`, `requests`, `generate_inventory`, `deploy_cloud`.

- `main` (FunctionDef), [line 11–53](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/inventory_runtimes.py#L11)
- `main.get` (FunctionDef), [line 16–17](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/inventory_runtimes.py#L16)

### docs/job-scrapers/ui/job-board-core.mjs

source ingestion; inspect linked source and symbol map for exact behavior

Location: `D:\abet\job-radar\docs\job-scrapers\ui\job-board-core.mjs`.

- `postedTime` (JS declaration (text scan)), [line 7](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/ui/job-board-core.mjs#L7)
- `postedLabel` (JS declaration (text scan)), [line 13](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/ui/job-board-core.mjs#L13)
- `compareJobs` (JS declaration (text scan)), [line 18](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/ui/job-board-core.mjs#L18)
- `jobGeography` (JS declaration (text scan)), [line 41](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/ui/job-board-core.mjs#L41)
- `filterJobs` (JS declaration (text scan)), [line 65](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/ui/job-board-core.mjs#L65)
- `initialVisibleCount` (JS declaration (text scan)), [line 83](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/ui/job-board-core.mjs#L83)
- `nextVisibleCount` (JS declaration (text scan)), [line 86](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/ui/job-board-core.mjs#L86)
- `safeJobUrl` (JS declaration (text scan)), [line 90](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/ui/job-board-core.mjs#L90)
- `fetchAllJobRows` (JS declaration (text scan)), [line 96](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/ui/job-board-core.mjs#L96)
- `cancel` (JS declaration (text scan)), [line 100](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/ui/job-board-core.mjs#L100)

### docs/job-scrapers/ui/standalone-ui.mjs

source ingestion; inspect linked source and symbol map for exact behavior

Location: `D:\abet\job-radar\docs\job-scrapers\ui\standalone-ui.mjs`.

Imports: `./job-board-core.mjs`.

- `escapeHTML` (JS declaration (text scan)), [line 3](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/ui/standalone-ui.mjs#L3)
- `jobCardMarkup` (JS declaration (text scan)), [line 4](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/ui/standalone-ui.mjs#L4)
- `wireJobDetails` (JS declaration (text scan)), [line 18](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/ui/standalone-ui.mjs#L18)
- `wireCompanyScroll` (JS declaration (text scan)), [line 39](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/ui/standalone-ui.mjs#L39)
- `scroll` (JS declaration (text scan)), [line 40](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/ui/standalone-ui.mjs#L40)

### docs/job-scrapers/ui/verify_standalone_presentation.mjs

source ingestion; inspect linked source and symbol map for exact behavior

Location: `D:\abet\job-radar\docs\job-scrapers\ui\verify_standalone_presentation.mjs`.

Imports: `node:assert/strict`, `node:fs/promises`, `node:module`, `node:path`, `node:url`.

- `fakeResponse` (JS declaration (text scan)), [line 21](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/ui/verify_standalone_presentation.mjs#L21)
- `settle` (JS declaration (text scan)), [line 25](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/ui/verify_standalone_presentation.mjs#L25)
- `component` (JS declaration (text scan)), [line 65](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/ui/verify_standalone_presentation.mjs#L65)
- `Harness` (JS declaration (text scan)), [line 76](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/ui/verify_standalone_presentation.mjs#L76)

### docs/job-scrapers/verify_dashboard_presentation.py

Read-only proof of the production dashboard's four-module presentation version.

Location: `D:\abet\job-radar\docs\job-scrapers\verify_dashboard_presentation.py`.

Imports: `pathlib`, `urllib.parse`, `datetime`, `json, re, subprocess, requests`.

- `main` (FunctionDef), [line 7–38](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/verify_dashboard_presentation.py#L7)
- `main.get` (FunctionDef), [line 9–10](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/verify_dashboard_presentation.py#L9)

### docs/job-scrapers/verify_jobs_ui.py

Read-only deployed jobs UI contract verification. No browser or application writes.

Location: `D:\abet\job-radar\docs\job-scrapers\verify_jobs_ui.py`.

Imports: `pathlib`, `datetime`, `urllib.parse`, `hashlib, re, json, requests`.

- `main` (FunctionDef), [line 7–35](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/verify_jobs_ui.py#L7)

### docs/job-scrapers/verify_public_jobs_pages.py

Bounded HTTP/data/CORS deployment proof. No browser, messages or writes to services.

Location: `D:\abet\job-radar\docs\job-scrapers\verify_public_jobs_pages.py`.

Imports: `base64, json, re, subprocess`, `datetime`, `pathlib`, `urllib.parse`, `requests`.

- `main` (FunctionDef), [line 9–50](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/verify_public_jobs_pages.py#L9)

### docs/job-scrapers/verify_scrapers.py

Read-only, bounded architecture/cadence inspection. No scraper imports or writes to services.

Location: `D:\abet\job-radar\docs\job-scrapers\verify_scrapers.py`.

Imports: `argparse, base64, json, re, shutil, subprocess, sys`, `datetime`, `pathlib`, `urllib.request`, `urllib.error`.

- `gh_json` (FunctionDef), [line 15–18](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/verify_scrapers.py#L15)
- `public_json` (FunctionDef), [line 20–26](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/verify_scrapers.py#L20)
- `inspect` (FunctionDef), [line 28–84](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/verify_scrapers.py#L28)
- `main` (FunctionDef), [line 86–95](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/verify_scrapers.py#L86)

### docs/job-scrapers/verify_standalone_presentation.py

Read-only proof of shared standalone headers, cards and styles on production.

Location: `D:\abet\job-radar\docs\job-scrapers\verify_standalone_presentation.py`.

Imports: `pathlib`, `datetime`, `urllib.parse`, `requests, re, hashlib, json`.

- `digest` (FunctionDef), [line 7–7](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/verify_standalone_presentation.py#L7)
- `main` (FunctionDef), [line 8–31](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/verify_standalone_presentation.py#L8)
- `main.get` (FunctionDef), [line 11–12](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/docs/job-scrapers/verify_standalone_presentation.py#L11)

### jobradar/alerts/discord.py

Discord alerts: one compact digest of strong new matches, deduped via `alerted` flag.

Location: `D:\abet\job-radar\jobradar\alerts\discord.py`.

Imports: `__future__`, `json`, `typing`, `requests`.

- `_active_model` (FunctionDef), [line 17–18](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/alerts/discord.py#L17)
- `_digest` (FunctionDef), [line 21–30](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/alerts/discord.py#L21)
- `send_alerts` (FunctionDef), [line 33–52](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/alerts/discord.py#L33)

### jobradar/dashboard.py

Render a self-contained, filterable HTML dashboard from scored jobs.

Location: `D:\abet\job-radar\jobradar\dashboard.py`.

Imports: `__future__`, `json`, `pathlib`.

- `_normalize` (FunctionDef), [line 12–27](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/dashboard.py#L12)
- `_from_active` (FunctionDef), [line 30–42](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/dashboard.py#L30)
- `render_dashboard` (FunctionDef), [line 45–55](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/dashboard.py#L45)

### jobradar/diagnostics.py

Keep credentials out of public execution receipts and failure alerts.

Location: `D:\abet\job-radar\jobradar\diagnostics.py`.

Imports: `os`, `re`, `urllib.parse`.

- `safe_error` (FunctionDef), [line 7–16](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/diagnostics.py#L7)

### jobradar/fetch_worker.py

Bounded provider subprocess. It fetches public careers data; it never publishes.

Location: `D:\abet\job-radar\jobradar\fetch_worker.py`.

Imports: `__future__`, `json`, `os`, `pathlib`, `subprocess`, `sys`, `tempfile`, `models`, `resource`, `providers`.

- `fetch_provider` (FunctionDef), [line 11–30](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/fetch_worker.py#L11)
- `main` (FunctionDef), [line 33–43](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/fetch_worker.py#L33)

### jobradar/matcher/judge.py

Scoring: a free heuristic judge (always available) and a Claude judge (when keyed).

Location: `D:\abet\job-radar\jobradar\matcher\judge.py`.

Imports: `__future__`, `json`, `re`, `typing`, `anthropic`.

- `_count` (FunctionDef), [line 24–25](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/matcher/judge.py#L24)
- `heuristic_score` (FunctionDef), [line 28–78](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/matcher/judge.py#L28)
- `_lead_with` (FunctionDef), [line 81–88](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/matcher/judge.py#L81)
- `claude_score` (FunctionDef), [line 111–131](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/matcher/judge.py#L111)

### jobradar/matcher/llm_judge.py

LLM judge chain v2 — OpenRouter :free (multi-key, rotating) -> NVIDIA NIM -> None.

Location: `D:\abet\job-radar\jobradar\matcher\llm_judge.py`.

Imports: `__future__`, `json`, `os`, `re`, `time`, `urllib.request`, `concurrent.futures`.

- `_chat` (FunctionDef), [line 69–81](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/matcher/llm_judge.py#L69)
- `_parse_json` (FunctionDef), [line 84–95](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/matcher/llm_judge.py#L84)
- `_gate_once` (FunctionDef), [line 100–116](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/matcher/llm_judge.py#L100)
- `_score_once` (FunctionDef), [line 119–136](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/matcher/llm_judge.py#L119)
- `_or_keys` (FunctionDef), [line 139–141](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/matcher/llm_judge.py#L139)
- `llm_score` (FunctionDef), [line 144–201](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/matcher/llm_judge.py#L144)

### jobradar/matcher/prefilter.py

Cheap rules pass: is a job even worth scoring/LLM-judging?

Location: `D:\abet\job-radar\jobradar\matcher\prefilter.py`.

Imports: `__future__`, `typing`.

- `_has` (FunctionDef), [line 21–23](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/matcher/prefilter.py#L21)
- `prefilter` (FunctionDef), [line 26–45](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/matcher/prefilter.py#L26)

### jobradar/matcher/profile.py

Load the candidate profile from the skills matrix markdown.

Location: `D:\abet\job-radar\jobradar\matcher\profile.py`.

Imports: `__future__`, `dataclasses`, `pathlib`, `typing`.

- `CandidateProfile` (ClassDef), [line 19–26](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/matcher/profile.py#L19)
- `CandidateProfile.prompt_block` (FunctionDef), [line 25–26](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/matcher/profile.py#L25)
- `load_profile` (FunctionDef), [line 29–38](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/matcher/profile.py#L29)

### jobradar/matcher/score.py

Score unscored jobs: prefilter -> (Claude judge if keyed, else heuristic) -> save.

Location: `D:\abet\job-radar\jobradar\matcher\score.py`.

Imports: `__future__`, `judge`, `prefilter`, `profile`.

- `score_unscored` (FunctionDef), [line 9–22](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/matcher/score.py#L9)
- `_score_batch` (FunctionDef), [line 25–44](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/matcher/score.py#L25)

### jobradar/models.py

Core data model: the Job contract shared by every provider and the storage layer.

Location: `D:\abet\job-radar\jobradar\models.py`.

Imports: `__future__`, `re`, `dataclasses`, `datetime`, `typing`.

- `now_iso` (FunctionDef), [line 10–11](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/models.py#L10)
- `clean_ws` (FunctionDef), [line 14–15](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/models.py#L14)
- `_norm_key` (FunctionDef), [line 18–19](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/models.py#L18)
- `Job` (ClassDef), [line 23–45](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/models.py#L23)
- `Job.dedup_key` (FunctionDef), [line 40–42](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/models.py#L40)
- `Job.to_row` (FunctionDef), [line 44–45](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/models.py#L44)

### jobradar/providers/__init__.py

Ingestion providers. One module per source; each returns List[Job] via the Job contract.

Location: `D:\abet\job-radar\jobradar\providers\__init__.py`.

Imports: `typing`, `base`, `greenhouse`, `lever`, `ashby`, `amazon`, `workday`.

- `build_providers` (FunctionDef), [line 20–37](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/providers/__init__.py#L20)

### jobradar/providers/amazon.py

Amazon.jobs provider - public JSON search API, no auth.

Location: `D:\abet\job-radar\jobradar\providers\amazon.py`.

Imports: `__future__`, `time`, `typing`, `models`, `base`.

- `AmazonProvider` (ClassDef), [line 19–72](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/providers/amazon.py#L19)
- `AmazonProvider.fetch` (FunctionDef), [line 22–72](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/providers/amazon.py#L22)

### jobradar/providers/ashby.py

Ashby provider — public job-board posting API (no auth).

Location: `D:\abet\job-radar\jobradar\providers\ashby.py`.

Imports: `__future__`, `html`, `re`, `typing`, `bs4`, `models`, `base`, `names`.

- `_strip` (FunctionDef), [line 20–23](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/providers/ashby.py#L20)
- `AshbyProvider` (ClassDef), [line 26–55](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/providers/ashby.py#L26)
- `AshbyProvider.__init__` (FunctionDef), [line 29–31](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/providers/ashby.py#L29)
- `AshbyProvider.fetch` (FunctionDef), [line 33–55](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/providers/ashby.py#L33)

### jobradar/providers/base.py

Provider base class + shared HTTP helper.

Location: `D:\abet\job-radar\jobradar\providers\base.py`.

Imports: `__future__`, `time`, `typing`, `requests`, `models`.

- `http_get` (FunctionDef), [line 15–25](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/providers/base.py#L15)
- `Provider` (ClassDef), [line 28–39](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/providers/base.py#L28)
- `Provider.__init__` (FunctionDef), [line 31–32](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/providers/base.py#L31)
- `Provider.provider_slug` (FunctionDef), [line 35–36](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/providers/base.py#L35)
- `Provider.fetch` (FunctionDef), [line 38–39](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/providers/base.py#L38)

### jobradar/providers/greenhouse.py

Greenhouse provider — uses the public boards API (no auth).

Location: `D:\abet\job-radar\jobradar\providers\greenhouse.py`.

Imports: `__future__`, `html`, `re`, `typing`, `bs4`, `models`, `base`, `names`.

- `_strip_html` (FunctionDef), [line 21–25](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/providers/greenhouse.py#L21)
- `GreenhouseProvider` (ClassDef), [line 28–66](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/providers/greenhouse.py#L28)
- `GreenhouseProvider.__init__` (FunctionDef), [line 31–33](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/providers/greenhouse.py#L31)
- `GreenhouseProvider.fetch` (FunctionDef), [line 35–66](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/providers/greenhouse.py#L35)

### jobradar/providers/lever.py

Lever provider — public postings API (no auth).

Location: `D:\abet\job-radar\jobradar\providers\lever.py`.

Imports: `__future__`, `typing`, `models`, `base`, `names`.

- `LeverProvider` (ClassDef), [line 16–45](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/providers/lever.py#L16)
- `LeverProvider.__init__` (FunctionDef), [line 19–21](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/providers/lever.py#L19)
- `LeverProvider.fetch` (FunctionDef), [line 23–45](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/providers/lever.py#L23)

### jobradar/providers/names.py

Canonical company names for ATS slugs.

Location: `D:\abet\job-radar\jobradar\providers\names.py`.

Imports: `__future__`, `typing`.

- `board_company` (FunctionDef), [line 86–93](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/providers/names.py#L86)

### jobradar/providers/workday.py

Workday cxs API provider (direct career-portal JSON, no auth).

Location: `D:\abet\job-radar\jobradar\providers\workday.py`.

Imports: `requests`, `typing`, `base`, `models`.

- `WorkdayProvider` (ClassDef), [line 36–97](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/providers/workday.py#L36)
- `WorkdayProvider.__init__` (FunctionDef), [line 39–40](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/providers/workday.py#L39)
- `WorkdayProvider.fetch` (FunctionDef), [line 42–97](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/providers/workday.py#L42)

### jobradar/publish.py

Robotics jobs publisher — Supabase persistence + Discord alerts for Job Radar.

Location: `D:\abet\job-radar\jobradar\publish.py`.

Imports: `__future__`, `json`, `os`, `time`, `datetime`, `typing`, `requests`, `requests`, `relevance`, `relevance`.

- `_logo_url` (FunctionDef), [line 52–54](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/publish.py#L52)
- `now_iso` (FunctionDef), [line 57–58](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/publish.py#L57)
- `supabase_env` (FunctionDef), [line 61–66](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/publish.py#L61)
- `_headers` (FunctionDef), [line 69–74](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/publish.py#L69)
- `_discord_retry_after` (FunctionDef), [line 77–86](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/publish.py#L77)
- `_rest` (FunctionDef), [line 89–90](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/publish.py#L89)
- `fetch_existing_urls` (FunctionDef), [line 96–115](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/publish.py#L96)
- `_deactivation_batches` (FunctionDef), [line 118–139](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/publish.py#L118)
- `deactivate` (FunctionDef), [line 142–159](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/publish.py#L142)
- `upsert` (FunctionDef), [line 162–191](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/publish.py#L162)
- `record_run` (FunctionDef), [line 194–202](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/publish.py#L194)
- `_is_recently_posted` (FunctionDef), [line 208–217](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/publish.py#L208)
- `_embed` (FunctionDef), [line 220–242](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/publish.py#L220)
- `_split_relevant` (FunctionDef), [line 245–264](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/publish.py#L245)
- `queue_new_jobs` (FunctionDef), [line 267–280](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/publish.py#L267)
- `_send_notification_chunk` (FunctionDef), [line 283–297](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/publish.py#L283)
- `_ack_notifications` (FunctionDef), [line 300–308](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/publish.py#L300)
- `notify_new_jobs` (FunctionDef), [line 311–374](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/publish.py#L311)
- `notify_failure` (FunctionDef), [line 377–391](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/publish.py#L377)
- `serialize` (FunctionDef), [line 397–433](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/publish.py#L397)
- `retire_empty_sources` (FunctionDef), [line 436–456](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/publish.py#L436)
- `publish` (FunctionDef), [line 459–491](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/publish.py#L459)

### jobradar/relevance.py

Robotics relevance classifier — stdlib only, deterministic, no network.

Location: `D:\abet\job-radar\jobradar\relevance.py`.

Imports: `__future__`, `re`, `typing`.

- `_rx` (FunctionDef), [line 41–45](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/relevance.py#L41)
- `_norm_company` (FunctionDef), [line 156–170](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/relevance.py#L156)
- `_text` (FunctionDef), [line 237–239](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/relevance.py#L237)
- `explain` (FunctionDef), [line 242–281](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/relevance.py#L242)
- `is_relevant` (FunctionDef), [line 284–287](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/relevance.py#L284)

### jobradar/storage.py

Storage abstraction: SQLite for local dev, Supabase (PostgREST) for prod.

Location: `D:\abet\job-radar\jobradar\storage.py`.

Imports: `__future__`, `json`, `os`, `sqlite3`, `pathlib`, `typing`, `requests`, `models`.

- `get_storage` (FunctionDef), [line 27–30](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/storage.py#L27)
- `Storage` (ClassDef), [line 33–44](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/storage.py#L33)
- `Storage.init_schema` (FunctionDef), [line 34–34](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/storage.py#L34)
- `Storage.upsert_jobs` (FunctionDef), [line 35–35](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/storage.py#L35)
- `Storage.log_run` (FunctionDef), [line 36–36](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/storage.py#L36)
- `Storage.fetch_unscored` (FunctionDef), [line 37–37](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/storage.py#L37)
- `Storage.save_score` (FunctionDef), [line 38–38](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/storage.py#L38)
- `Storage.fetch_alertable` (FunctionDef), [line 39–39](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/storage.py#L39)
- `Storage.mark_alerted` (FunctionDef), [line 40–40](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/storage.py#L40)
- `Storage.get_job` (FunctionDef), [line 41–41](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/storage.py#L41)
- `Storage.upsert_application` (FunctionDef), [line 42–42](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/storage.py#L42)
- `Storage.recent_scored` (FunctionDef), [line 43–43](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/storage.py#L43)
- `Storage.recent_active_jobs` (FunctionDef), [line 44–44](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/storage.py#L44)
- `SQLiteBackend` (ClassDef), [line 50–191](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/storage.py#L50)
- `SQLiteBackend.__init__` (FunctionDef), [line 51–54](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/storage.py#L51)
- `SQLiteBackend._conn` (FunctionDef), [line 56–60](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/storage.py#L56)
- `SQLiteBackend.init_schema` (FunctionDef), [line 62–93](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/storage.py#L62)
- `SQLiteBackend.upsert_jobs` (FunctionDef), [line 95–110](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/storage.py#L95)
- `SQLiteBackend.log_run` (FunctionDef), [line 112–120](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/storage.py#L112)
- `SQLiteBackend.fetch_unscored` (FunctionDef), [line 122–129](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/storage.py#L122)
- `SQLiteBackend.save_score` (FunctionDef), [line 131–141](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/storage.py#L131)
- `SQLiteBackend.fetch_alertable` (FunctionDef), [line 143–151](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/storage.py#L143)
- `SQLiteBackend.mark_alerted` (FunctionDef), [line 153–157](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/storage.py#L153)
- `SQLiteBackend.get_job` (FunctionDef), [line 159–162](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/storage.py#L159)
- `SQLiteBackend.upsert_application` (FunctionDef), [line 164–173](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/storage.py#L164)
- `SQLiteBackend.recent_scored` (FunctionDef), [line 175–182](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/storage.py#L175)
- `SQLiteBackend.recent_active_jobs` (FunctionDef), [line 184–191](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/storage.py#L184)
- `SupabaseBackend` (ClassDef), [line 197–299](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/storage.py#L197)
- `SupabaseBackend.__init__` (FunctionDef), [line 198–200](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/storage.py#L198)
- `SupabaseBackend._h` (FunctionDef), [line 202–207](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/storage.py#L202)
- `SupabaseBackend.init_schema` (FunctionDef), [line 209–211](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/storage.py#L209)
- `SupabaseBackend.upsert_jobs` (FunctionDef), [line 213–221](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/storage.py#L213)
- `SupabaseBackend.log_run` (FunctionDef), [line 223–226](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/storage.py#L223)
- `SupabaseBackend.fetch_unscored` (FunctionDef), [line 228–236](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/storage.py#L228)
- `SupabaseBackend.save_score` (FunctionDef), [line 238–245](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/storage.py#L238)
- `SupabaseBackend.fetch_alertable` (FunctionDef), [line 247–257](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/storage.py#L247)
- `SupabaseBackend.mark_alerted` (FunctionDef), [line 259–262](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/storage.py#L259)
- `SupabaseBackend.get_job` (FunctionDef), [line 264–266](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/storage.py#L264)
- `SupabaseBackend.upsert_application` (FunctionDef), [line 268–272](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/storage.py#L268)
- `SupabaseBackend.recent_scored` (FunctionDef), [line 274–285](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/storage.py#L274)
- `SupabaseBackend.recent_active_jobs` (FunctionDef), [line 287–299](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/jobradar/storage.py#L287)

### run.py

Job Radar orchestrator CLI.

Location: `D:\abet\job-radar\run.py`.

Imports: `__future__`, `argparse`, `concurrent.futures`, `sys`, `time`, `pathlib`, `config`, `jobradar.diagnostics`, `jobradar.models`, `jobradar.providers`, `jobradar.storage`, `concurrent.futures`, `json`, `os`, `jobradar`, `jobradar.fetch_worker`, `concurrent.futures`, `jobradar.publish`, `jobradar.matcher.score`, `jobradar.alerts.discord`, `jobradar.generate.resume`, `jobradar.dashboard`.

- `_run_id` (FunctionDef), [line 31–32](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/run.py#L31)
- `_scrape_all` (FunctionDef), [line 35–53](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/run.py#L35)
- `_ingest_supabase` (FunctionDef), [line 56–124](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/run.py#L56)
- `_ingest_supabase.save` (FunctionDef), [line 70–73](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/run.py#L70)
- `_ingest_sqlite` (FunctionDef), [line 127–148](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/run.py#L127)
- `cmd_ingest` (FunctionDef), [line 151–162](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/run.py#L151)
- `cmd_score` (FunctionDef), [line 165–169](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/run.py#L165)
- `cmd_alert` (FunctionDef), [line 172–176](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/run.py#L172)
- `cmd_generate` (FunctionDef), [line 179–183](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/run.py#L179)
- `cmd_report` (FunctionDef), [line 186–195](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/run.py#L186)
- `cmd_render` (FunctionDef), [line 198–205](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/run.py#L198)
- `cmd_pipeline` (FunctionDef), [line 208–212](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/run.py#L208)
- `main` (FunctionDef), [line 215–228](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/run.py#L215)

### runtime/cloudflare/test_scheduler.mjs

test/verification; inspect linked source and symbol map for exact behavior

Location: `D:\abet\job-radar\runtime\cloudflare\test_scheduler.mjs`.

Imports: `./worker.mjs`, `node:assert/strict`, `node:test`.

- `fixture` (JS declaration (text scan)), [line 5](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/runtime/cloudflare/test_scheduler.mjs#L5)

### runtime/cloudflare/worker.mjs

runtime/deployment; inspect linked source and symbol map for exact behavior

Location: `D:\abet\job-radar\runtime\cloudflare\worker.mjs`.

- `dueSlot` (JS declaration (text scan)), [line 9](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/runtime/cloudflare/worker.mjs#L9)
- `nextWake` (JS declaration (text scan)), [line 16](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/runtime/cloudflare/worker.mjs#L16)
- `json` (JS declaration (text scan)), [line 22](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/runtime/cloudflare/worker.mjs#L22)
- `JobsScheduler` (JS declaration (text scan)), [line 24](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/runtime/cloudflare/worker.mjs#L24)
- `scheduler` (JS declaration (text scan)), [line 148](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/runtime/cloudflare/worker.mjs#L148)

### sports_teams/board/job-board-core.mjs

support/module; inspect linked source and symbol map for exact behavior

Location: `D:\abet\job-radar\sports_teams\board\job-board-core.mjs`.

- `postedTime` (JS declaration (text scan)), [line 7](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/board/job-board-core.mjs#L7)
- `postedLabel` (JS declaration (text scan)), [line 13](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/board/job-board-core.mjs#L13)
- `compareJobs` (JS declaration (text scan)), [line 18](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/board/job-board-core.mjs#L18)
- `jobGeography` (JS declaration (text scan)), [line 41](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/board/job-board-core.mjs#L41)
- `filterJobs` (JS declaration (text scan)), [line 65](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/board/job-board-core.mjs#L65)
- `initialVisibleCount` (JS declaration (text scan)), [line 83](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/board/job-board-core.mjs#L83)
- `nextVisibleCount` (JS declaration (text scan)), [line 86](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/board/job-board-core.mjs#L86)
- `safeJobUrl` (JS declaration (text scan)), [line 90](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/board/job-board-core.mjs#L90)
- `fetchAllJobRows` (JS declaration (text scan)), [line 96](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/board/job-board-core.mjs#L96)
- `cancel` (JS declaration (text scan)), [line 100](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/board/job-board-core.mjs#L100)

### sports_teams/board/standalone-ui.mjs

support/module; inspect linked source and symbol map for exact behavior

Location: `D:\abet\job-radar\sports_teams\board\standalone-ui.mjs`.

Imports: `./job-board-core.mjs`.

- `escapeHTML` (JS declaration (text scan)), [line 3](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/board/standalone-ui.mjs#L3)
- `jobCardMarkup` (JS declaration (text scan)), [line 4](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/board/standalone-ui.mjs#L4)
- `wireJobDetails` (JS declaration (text scan)), [line 18](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/board/standalone-ui.mjs#L18)
- `wireCompanyScroll` (JS declaration (text scan)), [line 39](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/board/standalone-ui.mjs#L39)
- `scroll` (JS declaration (text scan)), [line 40](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/board/standalone-ui.mjs#L40)

### sports_teams/cloud_storage.py

Supabase persistence matching the other jobs modules; SQLite is a working cache.

Location: `D:\abet\job-radar\sports_teams\cloud_storage.py`.

Imports: `json`, `os`, `sqlite3`, `time`, `requests`, `pathlib`.

- `CloudStorage` (ClassDef), [line 17–116](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/cloud_storage.py#L17)
- `CloudStorage.__init__` (FunctionDef), [line 18–22](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/cloud_storage.py#L18)
- `CloudStorage.request` (FunctionDef), [line 24–38](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/cloud_storage.py#L24)
- `CloudStorage.rows` (FunctionDef), [line 40–48](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/cloud_storage.py#L40)
- `CloudStorage.upsert` (FunctionDef), [line 50–52](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/cloud_storage.py#L50)
- `CloudStorage.restore` (FunctionDef), [line 54–83](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/cloud_storage.py#L54)
- `CloudStorage.persist` (FunctionDef), [line 85–100](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/cloud_storage.py#L85)
- `CloudStorage.notification_state` (FunctionDef), [line 102–105](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/cloud_storage.py#L102)
- `CloudStorage.queue_notifications` (FunctionDef), [line 107–110](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/cloud_storage.py#L107)
- `CloudStorage.save_notification_state` (FunctionDef), [line 112–116](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/cloud_storage.py#L112)

### sports_teams/coverage_report.py

Report each team's official route and current run, without equating discovery with proof.

Location: `D:\abet\job-radar\sports_teams\coverage_report.py`.

Imports: `json, html`, `pathlib`, `datetime`.

- `build` (FunctionDef), [line 7–26](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/coverage_report.py#L7)
- `write` (FunctionDef), [line 28–41](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/coverage_report.py#L28)

### sports_teams/db/schema_cloud.sql

database schema/migration; inspect linked source and symbol map for exact behavior

Location: `D:\abet\job-radar\sports_teams\db\schema_cloud.sql`.

- `public.team_jobs` (table), [line 2](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/db/schema_cloud.sql#L2)
- `team_jobs_active_idx` (index), [line 10](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/db/schema_cloud.sql#L10)
- `team_jobs_first_idx` (index), [line 11](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/db/schema_cloud.sql#L11)
- `public.team_keep_first_seen` (function), [line 12](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/db/schema_cloud.sql#L12)
- `team_keep_first_seen` (trigger), [line 15](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/db/schema_cloud.sql#L15)
- `public.team_job_observations` (table), [line 16](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/db/schema_cloud.sql#L16)
- `public.team_job_scrape_runs` (table), [line 20](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/db/schema_cloud.sql#L20)
- `team_job_runs_date_idx` (index), [line 25](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/db/schema_cloud.sql#L25)
- `public.team_job_notifications` (table), [line 26](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/db/schema_cloud.sql#L26)
- `public.team_applications` (table), [line 30](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/db/schema_cloud.sql#L30)
- `team_jobs_read` (policy), [line 42](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/db/schema_cloud.sql#L42)
- `team_runs_read` (policy), [line 44](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/db/schema_cloud.sql#L44)
- `team_applications_owner` (policy), [line 46](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/db/schema_cloud.sql#L46)
- `public.team_jobs_with_applied` (view), [line 52](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/db/schema_cloud.sql#L52)

### sports_teams/enrichment.py

Employer job detail extraction. Bounded, cached, and independent of listing health.

Location: `D:\abet\job-radar\sports_teams\enrichment.py`.

Imports: `json`, `re`, `time`, `datetime`, `urllib.parse`, `bs4`, `live_refresh`, `providers.teamwork`, `publish_teams`.

- `jsonld_job` (FunctionDef), [line 15–32](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/enrichment.py#L15)
- `fetch_detail` (FunctionDef), [line 35–58](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/enrichment.py#L35)
- `enrich` (FunctionDef), [line 61–96](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/enrichment.py#L61)

### sports_teams/live_refresh.py

Bounded live refresh for the existing scheduled sports-team pipeline.

Location: `D:\abet\job-radar\sports_teams\live_refresh.py`.

Imports: `__future__`, `json`, `os`, `re`, `time`, `threading`, `concurrent.futures`, `dataclasses`, `datetime`, `urllib.parse`, `requests`, `providers`, `bs4`, `publish_teams`.

- `BoundedSession` (ClassDef), [line 35–86](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/live_refresh.py#L35)
- `BoundedSession.__init__` (FunctionDef), [line 38–41](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/live_refresh.py#L38)
- `BoundedSession.request` (FunctionDef), [line 43–60](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/live_refresh.py#L43)
- `BoundedSession._request_once` (FunctionDef), [line 62–86](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/live_refresh.py#L62)
- `source_from_row` (FunctionDef), [line 89–172](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/live_refresh.py#L89)
- `build_sources` (FunctionDef), [line 175–184](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/live_refresh.py#L175)
- `retired_replacements` (FunctionDef), [line 187–190](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/live_refresh.py#L187)
- `fetch_source` (FunctionDef), [line 193–276](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/live_refresh.py#L193)
- `collect` (FunctionDef), [line 279–289](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/live_refresh.py#L279)
- `apply_results` (FunctionDef), [line 292–338](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/live_refresh.py#L292)

### sports_teams/pipeline_local.py

Live HTTP sources -> SQLite tracking -> local board and dashboard feed.

Location: `D:\abet\job-radar\sports_teams\pipeline_local.py`.

Imports: `__future__`, `argparse`, `os`, `uuid`, `json`, `re`, `sqlite3`, `sys`, `unicodedata`, `collections`, `datetime`, `pathlib`, `importlib.util`, `cloud_storage`, `live_refresh`, `enrichment`, `coverage_report`.

- `now` (FunctionDef), [line 72–73](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/pipeline_local.py#L72)
- `connect` (FunctionDef), [line 76–80](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/pipeline_local.py#L76)
- `ingest` (FunctionDef), [line 83–124](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/pipeline_local.py#L83)
- `deactivate_missing` (FunctionDef), [line 127–134](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/pipeline_local.py#L127)
- `snapshot` (FunctionDef), [line 137–147](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/pipeline_local.py#L137)
- `write_outputs` (FunctionDef), [line 150–167](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/pipeline_local.py#L150)
- `main` (FunctionDef), [line 170–255](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/pipeline_local.py#L170)

### sports_teams/providers/adp.py

ADP Workforce Now public career-center API.

Location: `D:\abet\job-radar\sports_teams\providers\adp.py`.

Imports: `__future__`, `typing`, `requests`, `providers.base`.

- `_loc` (FunctionDef), [line 28–36](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/providers/adp.py#L28)
- `scrape` (FunctionDef), [line 39–84](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/providers/adp.py#L39)

### sports_teams/providers/base.py

Sports-teams jobs scraper — base contract.

Location: `D:\abet\job-radar\sports_teams\providers\base.py`.

Imports: `__future__`, `dataclasses`, `typing`.

- `Job` (ClassDef), [line 21–31](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/providers/base.py#L21)

### sports_teams/providers/nba.py

NBA — careers.nba.com (Phenom People in front of Workday).

Location: `D:\abet\job-radar\sports_teams\providers\nba.py`.

Imports: `__future__`, `json`, `typing`, `requests`, `providers.base`.

- `payload` (FunctionDef), [line 33–42](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/providers/nba.py#L33)
- `scrape` (FunctionDef), [line 45–87](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/providers/nba.py#L45)

### sports_teams/providers/nfl.py

NFL — league-office jobs straight from the NFL's own Greenhouse board.

Location: `D:\abet\job-radar\sports_teams\providers\nfl.py`.

Imports: `__future__`, `html`, `re`, `requests`, `providers.base`.

- `_text` (FunctionDef), [line 22–23](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/providers/nfl.py#L22)
- `scrape` (FunctionDef), [line 26–44](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/providers/nfl.py#L26)

### sports_teams/providers/official_ats.py

Public feeds linked by official team careers pages. No browser or authentication.

Location: `D:\abet\job-radar\sports_teams\providers\official_ats.py`.

Imports: `json, re`, `urllib.parse`, `bs4`.

- `dayforce` (FunctionDef), [line 11–41](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/providers/official_ats.py#L11)
- `bamboohr` (FunctionDef), [line 43–54](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/providers/official_ats.py#L43)
- `lever` (FunctionDef), [line 56–69](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/providers/official_ats.py#L56)
- `paylocity` (FunctionDef), [line 71–84](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/providers/official_ats.py#L71)
- `paycor` (FunctionDef), [line 86–100](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/providers/official_ats.py#L86)
- `jazzhr` (FunctionDef), [line 102–113](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/providers/official_ats.py#L102)
- `tnse` (FunctionDef), [line 115–121](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/providers/official_ats.py#L115)
- `clearcompany` (FunctionDef), [line 123–142](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/providers/official_ats.py#L123)
- `applicantpro` (FunctionDef), [line 144–158](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/providers/official_ats.py#L144)
- `icims` (FunctionDef), [line 160–179](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/providers/official_ats.py#L160)
- `msg` (FunctionDef), [line 181–192](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/providers/official_ats.py#L181)
- `bkse` (FunctionDef), [line 194–214](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/providers/official_ats.py#L194)
- `hireology` (FunctionDef), [line 216–237](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/providers/official_ats.py#L216)
- `paycom` (FunctionDef), [line 239–264](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/providers/official_ats.py#L239)
- `hirebridge` (FunctionDef), [line 266–281](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/providers/official_ats.py#L266)
- `aeg_kings` (FunctionDef), [line 283–296](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/providers/official_ats.py#L283)
- `jobvite` (FunctionDef), [line 298–309](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/providers/official_ats.py#L298)
- `bruins` (FunctionDef), [line 311–346](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/providers/official_ats.py#L311)

### sports_teams/providers/teamwork.py

TeamWork Online organisation portal provider.

Location: `D:\abet\job-radar\sports_teams\providers\teamwork.py`.

Imports: `__future__`, `html`, `re`, `urllib.parse`, `bs4`, `dataclasses`, `typing`, `requests`, `providers.base`.

- `TeamWorkOrg` (ClassDef), [line 45–49](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/providers/teamwork.py#L45)
- `_clean` (FunctionDef), [line 52–53](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/providers/teamwork.py#L52)
- `org_url` (FunctionDef), [line 56–58](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/providers/teamwork.py#L56)
- `pages` (FunctionDef), [line 61–85](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/providers/teamwork.py#L61)
- `scrape_org` (FunctionDef), [line 88–116](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/providers/teamwork.py#L88)
- `scrape_many` (FunctionDef), [line 119–124](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/providers/teamwork.py#L119)

### sports_teams/providers/teamwork_vertical.py

TeamWork Online: vertical page -> org slugs -> each org's own portal.

Location: `D:\abet\job-radar\sports_teams\providers\teamwork_vertical.py`.

Imports: `__future__`, `html`, `re`, `collections`, `dataclasses`, `typing`, `requests`, `providers.base`, `providers.teamwork`.

- `DetectedOrg` (ClassDef), [line 31–36](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/providers/teamwork_vertical.py#L31)
- `_cards` (FunctionDef), [line 39–52](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/providers/teamwork_vertical.py#L39)
- `discover` (FunctionDef), [line 55–74](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/providers/teamwork_vertical.py#L55)
- `scrape_all_orgs` (FunctionDef), [line 77–87](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/providers/teamwork_vertical.py#L77)

### sports_teams/providers/ultipro.py

UltiPro / UKG public job board API.

Location: `D:\abet\job-radar\sports_teams\providers\ultipro.py`.

Imports: `__future__`, `typing`, `requests`, `providers.base`.

- `scrape` (FunctionDef), [line 25–63](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/providers/ultipro.py#L25)

### sports_teams/publish_teams.py

publish_teams.py — sports-team job announcements.

Location: `D:\abet\job-radar\sports_teams\publish_teams.py`.

Imports: `__future__`, `argparse`, `json`, `os`, `re`, `sys`, `time`, `unicodedata`, `urllib.error`, `urllib.request`, `datetime`, `pathlib`, `html`, `datetime`, `sqlite3`, `cloud_storage`, `cloud_storage`, `urllib.parse`.

- `now_iso` (FunctionDef), [line 65–66](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/publish_teams.py#L65)
- `guard` (FunctionDef), [line 69–74](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/publish_teams.py#L69)
- `webhook` (FunctionDef), [line 77–84](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/publish_teams.py#L77)
- `_norm` (FunctionDef), [line 87–88](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/publish_teams.py#L87)
- `_clean_text` (FunctionDef), [line 95–100](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/publish_teams.py#L95)
- `_iso` (FunctionDef), [line 103–124](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/publish_teams.py#L103)
- `_display_team` (FunctionDef), [line 127–141](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/publish_teams.py#L127)
- `logo_for` (FunctionDef), [line 144–162](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/publish_teams.py#L144)
- `load_legacy_rows` (FunctionDef), [line 165–192](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/publish_teams.py#L165)
- `load_rows` (FunctionDef), [line 195–211](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/publish_teams.py#L195)
- `load_state` (FunctionDef), [line 214–220](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/publish_teams.py#L214)
- `save_state` (FunctionDef), [line 223–228](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/publish_teams.py#L223)
- `_is_recent` (FunctionDef), [line 231–240](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/publish_teams.py#L231)
- `embed` (FunctionDef), [line 243–275](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/publish_teams.py#L243)
- `notify` (FunctionDef), [line 278–303](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/publish_teams.py#L278)
- `main` (FunctionDef), [line 306–386](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/publish_teams.py#L306)

### sports_teams/repair_workday_cloud.py

One-off atomic URL repair. Preserves original job IDs, first-seen and delivery history.

Location: `D:\abet\job-radar\sports_teams\repair_workday_cloud.py`.

Imports: `json, os`, `pathlib`, `requests`.

- `main` (FunctionDef), [line 83–91](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/repair_workday_cloud.py#L83)

### sports_teams/run.py

Sports teams CLI, matching the other jobs modules' ingest/render workflow.

Location: `D:\abet\job-radar\sports_teams\run.py`.

Imports: `argparse`, `json`, `os`, `sys`, `pathlib`, `pipeline_local`, `live_refresh`.

- `main` (FunctionDef), [line 11–32](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/run.py#L11)

### sports_teams/runtime.py

Cloud scheduler and read-only board, patterned on the sportsbook HF runtime.

Location: `D:\abet\job-radar\sports_teams\runtime.py`.

Imports: `hmac`, `json`, `os`, `subprocess`, `sys`, `threading`, `time`, `datetime`, `http.server`, `pathlib`, `zoneinfo`.

- `now` (FunctionDef), [line 27–27](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/runtime.py#L27)
- `schedule` (FunctionDef), [line 30–35](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/runtime.py#L30)
- `read_json` (FunctionDef), [line 38–40](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/runtime.py#L38)
- `health` (FunctionDef), [line 43–56](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/runtime.py#L43)
- `run` (FunctionDef), [line 59–79](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/runtime.py#L59)
- `scheduler` (FunctionDef), [line 82–89](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/runtime.py#L82)
- `Handler` (ClassDef), [line 92–116](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/runtime.py#L92)
- `Handler.do_GET` (FunctionDef), [line 93–107](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/runtime.py#L93)
- `Handler.do_POST` (FunctionDef), [line 109–114](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/runtime.py#L109)
- `Handler.log_message` (FunctionDef), [line 116–116](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/runtime.py#L116)

### sports_teams/test_career_link_proof.py

Keep a verified flag from substituting for the actual official source chain.

Location: `D:\abet\job-radar\sports_teams\test_career_link_proof.py`.

Imports: `json`, `pathlib`, `unittest`, `urllib.parse`.

- `OfficialCareerProofTests` (ClassDef), [line 9–35](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_career_link_proof.py#L9)
- `OfficialCareerProofTests.test_every_team_has_evidence_for_a_configured_source` (FunctionDef), [line 10–20](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_career_link_proof.py#L10)
- `OfficialCareerProofTests.test_rendered_nba_evidence_matches_exact_employers` (FunctionDef), [line 22–35](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_career_link_proof.py#L22)

### sports_teams/test_cloud_parity.py

test/verification; inspect linked source and symbol map for exact behavior

Location: `D:\abet\job-radar\sports_teams\test_cloud_parity.py`.

Imports: `json`, `os`, `sqlite3`, `unittest`, `datetime`, `unittest.mock`, `pathlib`, `cloud_storage`, `enrichment`, `live_refresh`, `pipeline_local`, `publish_teams`, `providers`, `providers.base`, `sys`, `runtime`.

- `ParityTests` (ClassDef), [line 16–142](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_cloud_parity.py#L16)
- `ParityTests.test_transient_timeout_retries_within_request_budget` (FunctionDef), [line 17–23](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_cloud_parity.py#L17)
- `ParityTests.test_forbidden_response_is_not_retried` (FunctionDef), [line 25–30](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_cloud_parity.py#L25)
- `ParityTests.test_detail_request_uses_working_listing_headers_and_full_text` (FunctionDef), [line 32–40](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_cloud_parity.py#L32)
- `ParityTests.test_complete_description_updates_even_when_shorter` (FunctionDef), [line 42–46](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_cloud_parity.py#L42)
- `ParityTests.test_league_portal_preserves_actual_employer` (FunctionDef), [line 48–53](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_cloud_parity.py#L48)
- `ParityTests.test_owner_correction_preserves_identity_and_first_seen` (FunctionDef), [line 55–61](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_cloud_parity.py#L55)
- `ParityTests.test_old_unannounced_job_is_not_announced_as_new` (FunctionDef), [line 63–67](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_cloud_parity.py#L63)
- `ParityTests.test_verified_empty_source_retires_jobs` (FunctionDef), [line 69–75](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_cloud_parity.py#L69)
- `ParityTests.test_cloud_source_relay_preserves_canonical_url` (FunctionDef), [line 77–84](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_cloud_parity.py#L77)
- `ParityTests.page` (FunctionDef), [line 86–87](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_cloud_parity.py#L86)
- `ParityTests.test_teamwork_follows_next_page_and_deduplicates` (FunctionDef), [line 89–94](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_cloud_parity.py#L89)
- `ParityTests.test_malformed_and_cycle_pages_fail_instead_of_closing_jobs` (FunctionDef), [line 96–100](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_cloud_parity.py#L96)
- `ParityTests.test_jsonld_extracts_full_description_and_salary_without_guessing` (FunctionDef), [line 102–105](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_cloud_parity.py#L102)
- `ParityTests.test_supabase_pagination_and_retries_exhaustion_raise` (FunctionDef), [line 107–114](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_cloud_parity.py#L107)
- `ParityTests.test_restoring_cloud_preserves_first_seen_and_inactive_status` (FunctionDef), [line 116–122](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_cloud_parity.py#L116)
- `ParityTests.test_cloud_notification_guard_never_posts` (FunctionDef), [line 124–127](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_cloud_parity.py#L124)
- `ParityTests.test_full_description_survives_long_listing_teaser` (FunctionDef), [line 129–134](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_cloud_parity.py#L129)
- `ParityTests.test_runtime_schedule_is_same_each_day_and_dst_aware` (FunctionDef), [line 136–142](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_cloud_parity.py#L136)

### sports_teams/test_official_routes.py

Offline regressions for discovered coverage gaps and notification history.

Location: `D:\abet\job-radar\sports_teams\test_official_routes.py`.

Imports: `json, os, sqlite3, unittest, sys, contextlib, io`, `unittest.mock`, `live_refresh`, `publish_teams`, `cloud_storage, pipeline_local, coverage_report`, `providers`.

- `response` (FunctionDef), [line 9–10](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_official_routes.py#L9)
- `OfficialRoutes` (ClassDef), [line 12–118](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_official_routes.py#L12)
- `OfficialRoutes.test_dayforce_language_is_not_silently_changed` (FunctionDef), [line 13–16](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_official_routes.py#L13)
- `OfficialRoutes.test_dayforce_pagination_uses_real_offset_and_rejects_truncation` (FunctionDef), [line 18–26](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_official_routes.py#L18)
- `OfficialRoutes.test_dayforce_missing_nonce_and_repeated_jobs_are_errors` (FunctionDef), [line 28–33](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_official_routes.py#L28)
- `OfficialRoutes.test_bamboohr_incomplete_payload_does_not_mean_empty` (FunctionDef), [line 35–37](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_official_routes.py#L35)
- `OfficialRoutes.test_adp_preserves_celtics_career_center_in_request_and_links` (FunctionDef), [line 39–44](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_official_routes.py#L39)
- `OfficialRoutes.test_teamwork_organization_filter_remains_distinct` (FunctionDef), [line 46–49](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_official_routes.py#L46)
- `OfficialRoutes.test_adp_truncated_final_page_fails` (FunctionDef), [line 51–53](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_official_routes.py#L51)
- `OfficialRoutes.test_adp_server_page_cap_does_not_skip_jobs` (FunctionDef), [line 55–58](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_official_routes.py#L55)
- `OfficialRoutes.test_workday_missing_total_cannot_close_jobs` (FunctionDef), [line 60–63](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_official_routes.py#L60)
- `OfficialRoutes.test_workday_later_page_zero_total_keeps_first_page_total` (FunctionDef), [line 65–70](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_official_routes.py#L65)
- `OfficialRoutes.test_jobvite_loading_page_is_error_not_zero_jobs` (FunctionDef), [line 72–74](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_official_routes.py#L72)
- `OfficialRoutes.test_notification_rejects_broken_workday_link` (FunctionDef), [line 76–77](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_official_routes.py#L76)
- `OfficialRoutes.test_embed_separates_employer_date_from_delivery_timestamp` (FunctionDef), [line 79–84](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_official_routes.py#L79)
- `OfficialRoutes.test_notification_save_preserves_seeded_status_and_timestamp` (FunctionDef), [line 86–90](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_official_routes.py#L86)
- `OfficialRoutes.test_baseline_rows_are_never_marked_delivered` (FunctionDef), [line 92–96](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_official_routes.py#L92)
- `OfficialRoutes.test_old_database_rows_are_not_implicitly_queued` (FunctionDef), [line 98–100](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_official_routes.py#L98)
- `OfficialRoutes.test_zero_limit_delivers_all_and_acknowledges_each_chunk` (FunctionDef), [line 102–106](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_official_routes.py#L102)
- `OfficialRoutes.test_alias_restore_drops_only_stale_local_copy` (FunctionDef), [line 108–114](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_official_routes.py#L108)
- `OfficialRoutes.test_coverage_does_not_claim_all_teams_from_source_count` (FunctionDef), [line 116–118](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_official_routes.py#L116)

### sports_teams/test_pipeline_regressions.py

Offline regression checks. All notification and HTTP calls are mocked.

Location: `D:\abet\job-radar\sports_teams\test_pipeline_regressions.py`.

Imports: `contextlib`, `io`, `json`, `sqlite3`, `sys`, `unittest`, `unittest.mock`, `live_refresh`, `pipeline_local`, `publish_teams`, `providers`, `providers.base`.

- `PipelineTests` (ClassDef), [line 16–132](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_pipeline_regressions.py#L16)
- `PipelineTests.setUp` (FunctionDef), [line 17–19](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_pipeline_regressions.py#L17)
- `PipelineTests.tearDown` (FunctionDef), [line 21–22](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_pipeline_regressions.py#L21)
- `PipelineTests.row` (FunctionDef), [line 24–27](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_pipeline_regressions.py#L24)
- `PipelineTests.result` (FunctionDef), [line 29–32](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_pipeline_regressions.py#L29)
- `PipelineTests.test_failed_source_preserves_jobs_and_last_seen` (FunctionDef), [line 34–39](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_pipeline_regressions.py#L34)
- `PipelineTests.test_empty_source_cannot_close_previous_jobs` (FunctionDef), [line 41–44](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_pipeline_regressions.py#L41)
- `PipelineTests.test_only_successful_source_can_close_its_missing_job` (FunctionDef), [line 46–49](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_pipeline_regressions.py#L46)
- `PipelineTests.test_first_seen_stable_and_runs_are_per_source` (FunctionDef), [line 51–58](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_pipeline_regressions.py#L51)
- `PipelineTests.test_cross_listed_job_survives_other_source_failure` (FunctionDef), [line 60–66](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_pipeline_regressions.py#L60)
- `PipelineTests.test_same_url_under_different_team_label_is_not_duplicated` (FunctionDef), [line 68–71](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_pipeline_regressions.py#L68)
- `PipelineTests.test_short_listing_does_not_destroy_full_description` (FunctionDef), [line 73–76](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_pipeline_regressions.py#L73)
- `PipelineTests.test_workday_url_and_legacy_incomplete_link` (FunctionDef), [line 78–81](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_pipeline_regressions.py#L78)
- `PipelineTests.test_irregular_teamwork_slug` (FunctionDef), [line 83–87](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_pipeline_regressions.py#L83)
- `PipelineTests.test_request_budget` (FunctionDef), [line 89–93](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_pipeline_regressions.py#L89)
- `PipelineTests.test_nba_keeps_workday_as_ats_platform` (FunctionDef), [line 95–100](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_pipeline_regressions.py#L95)
- `PipelineTests.publishing` (FunctionDef), [line 102–107](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_pipeline_regressions.py#L102)
- `PipelineTests.test_limit_does_not_mark_backlog_as_posted` (FunctionDef), [line 109–112](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_pipeline_regressions.py#L109)
- `PipelineTests.test_failed_chunk_remains_unseen` (FunctionDef), [line 114–117](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_pipeline_regressions.py#L114)
- `PipelineTests.test_all_failed_does_not_change_state` (FunctionDef), [line 119–122](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_pipeline_regressions.py#L119)
- `PipelineTests.test_publish_without_mode_does_not_send` (FunctionDef), [line 124–127](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_pipeline_regressions.py#L124)
- `PipelineTests.test_dry_run_never_sends_or_updates_state` (FunctionDef), [line 129–132](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_pipeline_regressions.py#L129)

### sports_teams/test_repair_nov10.py

test/verification; inspect linked source and symbol map for exact behavior

Location: `D:\abet\job-radar\sports_teams\test_repair_nov10.py`.

Imports: `sqlite3`, `types`, `unittest`, `unittest.mock`, `live_refresh`, `pipeline_local`, `providers`.

- `SourceRepairTests` (ClassDef), [line 11–59](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_repair_nov10.py#L11)
- `SourceRepairTests.test_filtered_portal_must_confirm_requested_employer` (FunctionDef), [line 12–18](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_repair_nov10.py#L12)
- `SourceRepairTests.test_confirmed_empty_team_is_valid` (FunctionDef), [line 20–23](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_repair_nov10.py#L20)
- `SourceRepairTests.fixture` (FunctionDef), [line 25–31](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_repair_nov10.py#L25)
- `SourceRepairTests.result` (FunctionDef), [line 33–35](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_repair_nov10.py#L33)
- `SourceRepairTests.test_phantom_inferred_observation_cannot_keep_absent_job_active` (FunctionDef), [line 37–44](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_repair_nov10.py#L37)
- `SourceRepairTests.test_failed_cross_listing_preserves_job` (FunctionDef), [line 46–51](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_repair_nov10.py#L46)
- `SourceRepairTests.test_retired_route_waits_for_successful_replacement` (FunctionDef), [line 53–59](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_repair_nov10.py#L53)

### sports_teams/test_source_delivery_parity.py

test/verification; inspect linked source and symbol map for exact behavior

Location: `D:\abet\job-radar\sports_teams\test_source_delivery_parity.py`.

Imports: `contextlib, io, json, os, sys, tempfile, unittest`, `pathlib`, `types`, `unittest.mock`, `live_refresh`, `publish_teams`, `cloud_storage`.

- `Parity` (ClassDef), [line 9–40](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_source_delivery_parity.py#L9)
- `Parity.test_only_explicit_team_sources_can_enter_production` (FunctionDef), [line 10–17](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_source_delivery_parity.py#L10)
- `Parity.test_no_generic_league_discovery` (FunctionDef), [line 19–22](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_source_delivery_parity.py#L19)
- `Parity.test_queued_new_job_only_and_failed_delivery_stays_pending` (FunctionDef), [line 24–30](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_source_delivery_parity.py#L24)
- `Parity.test_queue_creation_never_resets_delivered_history` (FunctionDef), [line 32–36](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_source_delivery_parity.py#L32)
- `Parity.test_old_dayforce_links_keep_team_tenant_board_and_language` (FunctionDef), [line 38–40](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/sports_teams/test_source_delivery_parity.py#L38)

### tests/test_board_filter.py

Drift guard for the static board template.

Location: `D:\abet\job-radar\tests\test_board_filter.py`.

Imports: `re`, `sys`, `unittest`, `pathlib`, `jobradar.relevance`.

- `_read_board` (FunctionDef), [line 22–23](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_board_filter.py#L22)
- `_js_array` (FunctionDef), [line 26–29](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_board_filter.py#L26)
- `_js_set` (FunctionDef), [line 32–35](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_board_filter.py#L32)
- `TestBoardTemplateConsistency` (ClassDef), [line 38–86](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_board_filter.py#L38)
- `TestBoardTemplateConsistency.setUp` (FunctionDef), [line 39–40](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_board_filter.py#L39)
- `TestBoardTemplateConsistency.test_offtopic_companies_matches_python_source_of_truth` (FunctionDef), [line 42–48](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_board_filter.py#L42)
- `TestBoardTemplateConsistency.test_corp_suffixes_matches_python_source_of_truth` (FunctionDef), [line 50–56](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_board_filter.py#L50)
- `TestBoardTemplateConsistency.test_offtopic_toggle_exists_and_defaults_on` (FunctionDef), [line 58–62](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_board_filter.py#L58)
- `TestBoardTemplateConsistency.test_toggle_is_wired_to_render` (FunctionDef), [line 64–68](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_board_filter.py#L64)
- `TestBoardTemplateConsistency.test_figure_regex_separates_lending_from_figure_ai` (FunctionDef), [line 70–77](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_board_filter.py#L70)
- `TestBoardTemplateConsistency.test_board_uses_namespaced_applications_table` (FunctionDef), [line 79–83](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_board_filter.py#L79)
- `TestBoardTemplateConsistency.test_board_reads_robotics_jobs` (FunctionDef), [line 85–86](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_board_filter.py#L85)

### tests/test_core.py

Core unit tests — run: python -m unittest discover -s tests

Location: `D:\abet\job-radar\tests\test_core.py`.

Imports: `sys`, `tempfile`, `unittest`, `pathlib`, `jobradar.models`, `jobradar.matcher.prefilter`, `jobradar.matcher.judge`, `jobradar.matcher.profile`, `jobradar.storage`.

- `TestModel` (ClassDef), [line 27–31](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_core.py#L27)
- `TestModel.test_dedup_key_normalizes` (FunctionDef), [line 28–31](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_core.py#L28)
- `TestPrefilter` (ClassDef), [line 34–49](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_core.py#L34)
- `TestPrefilter.test_passes_ml_remote` (FunctionDef), [line 35–40](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_core.py#L35)
- `TestPrefilter.test_drops_offshore` (FunctionDef), [line 42–45](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_core.py#L42)
- `TestPrefilter.test_flags_intern` (FunctionDef), [line 47–49](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_core.py#L47)
- `TestHeuristic` (ClassDef), [line 52–64](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_core.py#L52)
- `TestHeuristic.test_ml_remote_beats_retail` (FunctionDef), [line 53–59](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_core.py#L53)
- `TestHeuristic.test_offshore_penalized` (FunctionDef), [line 61–64](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_core.py#L61)
- `TestStorage` (ClassDef), [line 67–90](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_core.py#L67)
- `TestStorage.setUp` (FunctionDef), [line 68–71](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_core.py#L68)
- `TestStorage.test_roundtrip` (FunctionDef), [line 73–90](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_core.py#L73)

### tests/test_diagnostics.py

test/verification; inspect linked source and symbol map for exact behavior

Location: `D:\abet\job-radar\tests\test_diagnostics.py`.

Imports: `os`, `unittest`, `urllib.parse`, `unittest.mock`, `jobradar.diagnostics`.

- `DiagnosticTests` (ClassDef), [line 9–23](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_diagnostics.py#L9)
- `DiagnosticTests.test_redacts_configured_credentials_and_encoded_forms` (FunctionDef), [line 10–14](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_diagnostics.py#L10)
- `DiagnosticTests.test_redacts_webhook_even_without_environment_value` (FunctionDef), [line 16–19](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_diagnostics.py#L16)
- `DiagnosticTests.test_preserves_ordinary_provider_diagnostics` (FunctionDef), [line 21–23](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_diagnostics.py#L21)

### tests/test_provider_completeness.py

test/verification; inspect linked source and symbol map for exact behavior

Location: `D:\abet\job-radar\tests\test_provider_completeness.py`.

Imports: `contextlib`, `datetime`, `io`, `json`, `pathlib`, `subprocess`, `tempfile`, `types`, `unittest`, `unittest.mock`, `jobradar.providers.greenhouse`, `jobradar.providers.lever`, `jobradar.providers.ashby`, `jobradar.providers.amazon`, `jobradar.providers.workday`, `jobradar.fetch_worker`, `jobradar`, `run`.

- `response` (FunctionDef), [line 21–22](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_provider_completeness.py#L21)
- `CompletenessTests` (ClassDef), [line 24–76](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_provider_completeness.py#L24)
- `CompletenessTests.test_http_errors_never_become_successful_empty_boards` (FunctionDef), [line 25–28](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_provider_completeness.py#L25)
- `CompletenessTests.test_invalid_board_payload_is_not_empty` (FunctionDef), [line 30–32](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_provider_completeness.py#L30)
- `CompletenessTests.test_amazon_page_failure_is_not_partial_success` (FunctionDef), [line 34–37](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_provider_completeness.py#L34)
- `CompletenessTests.test_workday_page_failure_is_not_partial_success` (FunctionDef), [line 39–42](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_provider_completeness.py#L39)
- `CompletenessTests.test_provider_process_has_a_real_deadline` (FunctionDef), [line 44–47](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_provider_completeness.py#L44)
- `CompletenessTests.test_workday_retains_first_page_total_when_later_totals_are_zero` (FunctionDef), [line 49–55](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_provider_completeness.py#L49)
- `CompletenessTests.test_partial_run_writes_degraded_manifest_and_preserves_existing_jobs` (FunctionDef), [line 57–67](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_provider_completeness.py#L57)
- `CompletenessTests.test_verified_empty_source_is_passed_for_reconciliation` (FunctionDef), [line 69–76](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_provider_completeness.py#L69)

### tests/test_relevance.py

Robotics relevance gate tests — run: python -m unittest discover -s tests

Location: `D:\abet\job-radar\tests\test_relevance.py`.

Imports: `sys`, `unittest`, `pathlib`, `jobradar`, `jobradar.publish`, `jobradar`.

- `row` (FunctionDef), [line 24–26](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_relevance.py#L24)
- `TestRejectsNoise` (ClassDef), [line 29–75](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_relevance.py#L29)
- `TestRejectsNoise.test_rejects_pure_tech_and_business_roles` (FunctionDef), [line 32–57](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_relevance.py#L32)
- `TestRejectsNoise.test_rejects_weak_title_without_corroboration` (FunctionDef), [line 59–61](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_relevance.py#L59)
- `TestRejectsNoise.test_rejects_weak_title_with_uncorroborating_prose` (FunctionDef), [line 63–68](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_relevance.py#L63)
- `TestRejectsNoise.test_rejects_internships_even_when_robotics_title` (FunctionDef), [line 70–72](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_relevance.py#L70)
- `TestRejectsNoise.test_no_signal_at_all` (FunctionDef), [line 74–75](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_relevance.py#L74)
- `TestKeepsRobotics` (ClassDef), [line 78–133](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_relevance.py#L78)
- `TestKeepsRobotics.test_accepts_unambiguous_robotics_titles_without_description` (FunctionDef), [line 79–98](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_relevance.py#L79)
- `TestKeepsRobotics.test_accepts_weak_title_backed_by_robotics_description` (FunctionDef), [line 100–115](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_relevance.py#L100)
- `TestKeepsRobotics.test_generic_job_families_need_robotics_in_the_title` (FunctionDef), [line 117–128](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_relevance.py#L117)
- `TestKeepsRobotics.test_deny_beats_allow` (FunctionDef), [line 130–133](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_relevance.py#L130)
- `TestStrictTechBoards` (ClassDef), [line 136–165](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_relevance.py#L136)
- `TestStrictTechBoards.test_weak_title_rejected_on_tech_boards_even_with_robotics_prose` (FunctionDef), [line 139–148](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_relevance.py#L139)
- `TestStrictTechBoards.test_strong_title_still_accepted_on_tech_boards` (FunctionDef), [line 150–155](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_relevance.py#L150)
- `TestStrictTechBoards.test_strict_policy_does_not_apply_to_robotics_boards` (FunctionDef), [line 157–160](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_relevance.py#L157)
- `TestStrictTechBoards.test_company_matching_tolerates_suffixes_and_case` (FunctionDef), [line 162–165](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_relevance.py#L162)
- `TestExplain` (ClassDef), [line 168–180](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_relevance.py#L168)
- `TestExplain.test_reason_is_actionable` (FunctionDef), [line 169–180](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_relevance.py#L169)
- `TestSplitRelevant` (ClassDef), [line 183–206](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_relevance.py#L183)
- `TestSplitRelevant.test_partitions_without_mutating` (FunctionDef), [line 184–194](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_relevance.py#L184)
- `TestSplitRelevant.test_kill_switch_restores_legacy_behaviour` (FunctionDef), [line 196–206](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_relevance.py#L196)

### tests/test_reliability.py

Offline regression checks for review copies. HTTP is always replaced by a fake.

Location: `D:\abet\job-radar\tests\test_reliability.py`.

Imports: `ast`, `concurrent.futures`, `contextlib`, `copy`, `datetime`, `io`, `json`, `pathlib`, `sys`, `types`, `unittest`, `unittest.mock`, `requests`.

- `Response` (ClassDef), [line 20–27](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_reliability.py#L20)
- `Response.__init__` (FunctionDef), [line 21–22](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_reliability.py#L21)
- `Response.json` (FunctionDef), [line 23–24](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_reliability.py#L23)
- `Response.raise_for_status` (FunctionDef), [line 25–27](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_reliability.py#L25)
- `Database` (ClassDef), [line 30–101](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_reliability.py#L30)
- `Database.__init__` (FunctionDef), [line 33–45](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_reliability.py#L33)
- `Database.get` (FunctionDef), [line 46–56](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_reliability.py#L46)
- `Database.post` (FunctionDef), [line 57–82](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_reliability.py#L57)
- `Database.patch` (FunctionDef), [line 83–101](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_reliability.py#L83)
- `load_publisher` (FunctionDef), [line 104–116](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_reliability.py#L104)
- `make_job` (FunctionDef), [line 119–125](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_reliability.py#L119)
- `RepairTests` (ClassDef), [line 128–289](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_reliability.py#L128)
- `RepairTests.test_cleanup_bounds_and_exact_counts` (FunctionDef), [line 129–141](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_reliability.py#L129)
- `RepairTests.test_cleanup_special_characters_and_no_false_counts` (FunctionDef), [line 143–149](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_reliability.py#L143)
- `RepairTests.test_cleanup_failure_raises` (FunctionDef), [line 151–157](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_reliability.py#L151)
- `RepairTests.test_exhausted_database_retry_raises` (FunctionDef), [line 159–167](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_reliability.py#L159)
- `RepairTests.test_transport_retry_reuses_exact_upsert_batch` (FunctionDef), [line 170–177](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_reliability.py#L170)
- `RepairTests.test_exhausted_transport_retry_preserves_pending_intent` (FunctionDef), [line 179–195](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_reliability.py#L179)
- `RepairTests.test_exhausted_transport_retry_preserves_pending_intent.interrupted` (FunctionDef), [line 183–187](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_reliability.py#L183)
- `RepairTests.test_committed_upsert_with_lost_response_does_not_duplicate` (FunctionDef), [line 197–212](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_reliability.py#L197)
- `RepairTests.test_committed_upsert_with_lost_response_does_not_duplicate.commit_then_disconnect` (FunctionDef), [line 201–206](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_reliability.py#L201)
- `RepairTests.test_nonretryable_database_error_fails_immediately` (FunctionDef), [line 214–219](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_reliability.py#L214)
- `RepairTests.test_failed_write_preserves_intent_and_next_run_delivers_once` (FunctionDef), [line 221–237](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_reliability.py#L221)
- `RepairTests.test_partial_discord_failure_retries_only_pending_chunk` (FunctionDef), [line 239–252](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_reliability.py#L239)
- `RepairTests.test_existing_rows_are_not_backfilled_as_new_alerts` (FunctionDef), [line 254–262](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_reliability.py#L254)
- `RepairTests.test_partial_observation_does_not_retire_existing_job` (FunctionDef), [line 264–272](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_reliability.py#L264)
- `RepairTests.test_receipt_http_error_is_exposed` (FunctionDef), [line 274–280](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_reliability.py#L274)
- `RepairTests.test_discord_retry_seconds_and_budget` (FunctionDef), [line 282–289](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_reliability.py#L282)

### tests/test_render.py

Render smoke test — proves the workflow's dashboard artifact actually gets written.

Location: `D:\abet\job-radar\tests\test_render.py`.

Imports: `sys`, `tempfile`, `unittest`, `pathlib`, `jobradar.dashboard`, `jobradar.models`, `jobradar.storage`.

- `TestRender` (ClassDef), [line 21–59](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_render.py#L21)
- `TestRender.setUp` (FunctionDef), [line 22–36](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_render.py#L22)
- `TestRender.test_writes_non_empty_artifact` (FunctionDef), [line 38–45](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_render.py#L38)
- `TestRender.test_excludes_inactive_jobs` (FunctionDef), [line 47–52](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_render.py#L47)
- `TestRender.test_unscored_rows_render_without_fit_column_crashing` (FunctionDef), [line 54–59](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/tests/test_render.py#L54)

### validate_relevance.py

One-off validation: run the relevance gate over REAL board titles.

Location: `D:\abet\job-radar\validate_relevance.py`.

Imports: `sys`, `json`, `html`, `re`, `pathlib`, `requests`, `bs4`, `jobradar`.

- `strip_html` (FunctionDef), [line 29–32](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/validate_relevance.py#L29)
- `main` (FunctionDef), [line 35–86](https://github.com/misterplusev/job-radar/blob/7f57a99b30d4eca9700375920c30918d2845cace/validate_relevance.py#L35)

