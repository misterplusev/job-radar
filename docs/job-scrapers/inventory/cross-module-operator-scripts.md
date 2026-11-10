# cross-module-operator-scripts — file and symbol inventory

Revision: `local working copy on 2026-11-10`. Root: `D:\abet_ops\jobs_scrapers`.

| File | Physical lines | Nonblank | Bytes | Category |
|---|---:|---:|---:|---|
| `build_schema_dictionary.py` | 42 | 42 | 4212 | documentation/verification helper |
| `generate_inventory.py` | 151 | 143 | 12403 | documentation/verification helper |
| `inventory_runtimes.py` | 55 | 53 | 4126 | documentation/verification helper |
| `verify_public_jobs_pages.py` | 51 | 50 | 4549 | documentation/verification helper |
| `verify_scrapers.py` | 73 | 66 | 5176 | documentation/verification helper |
| `verify_jobs_expansion.py` | 221 | 191 | 10075 | documentation/verification helper |

## Script definitions and dependencies

### build_schema_dictionary.py

Read a catalog artifact and local SQLite metadata; produce no job/applicant rows.

Location: `D:\abet_ops\jobs_scrapers\build_schema_dictionary.py`.

Imports: `json, sqlite3`, `pathlib`.

- `cell` (FunctionDef), line 6–6
- `main` (FunctionDef), line 7–41

### generate_inventory.py

Bounded, read-only source inventory. Owner: ABET jobs documentation.

Location: `D:\abet_ops\jobs_scrapers\generate_inventory.py`.

Imports: `ast, base64, hashlib, io, json, re, subprocess, sys`, `datetime`, `pathlib`, `urllib.parse`.

- `command` (FunctionDef), line 18–21
- `gh` (FunctionDef), line 22–22
- `category` (FunctionDef), line 23–37
- `eligible` (FunctionDef), line 38–42
- `details` (FunctionDef), line 43–70
- `details.walk` (FunctionDef), line 50–56
- `git_inventory` (FunctionDef), line 72–90
- `remote_inventory` (FunctionDef), line 92–101
- `local_helpers` (FunctionDef), line 103–110
- `write` (FunctionDef), line 112–139
- `main` (FunctionDef), line 141–149

### inventory_runtimes.py

Finite GET-only HF/Cloudflare metadata inventory; no runtime triggers or secret output.

Location: `D:\abet_ops\jobs_scrapers\inventory_runtimes.py`.

Imports: `email.policy, json, sys`, `email.parser`, `pathlib`, `urllib.parse`, `requests`, `generate_inventory`, `deploy_cloud`.

- `main` (FunctionDef), line 11–53
- `main.get` (FunctionDef), line 16–17

### verify_public_jobs_pages.py

Bounded HTTP/data/CORS deployment proof. No browser, messages or writes to services.

Location: `D:\abet_ops\jobs_scrapers\verify_public_jobs_pages.py`.

Imports: `base64, json, re, subprocess`, `datetime`, `pathlib`, `urllib.parse`, `requests`.

- `main` (FunctionDef), line 9–50

### verify_scrapers.py

Read-only, bounded architecture/cadence inspection. No scraper imports or writes to services.

Location: `D:\abet_ops\jobs_scrapers\verify_scrapers.py`.

Imports: `argparse, base64, json, re, shutil, subprocess, sys`, `datetime`, `pathlib`, `urllib.request`.

- `gh_json` (FunctionDef), line 14–17
- `public_json` (FunctionDef), line 19–21
- `inspect` (FunctionDef), line 23–60
- `main` (FunctionDef), line 62–71

### verify_jobs_expansion.py

verify_jobs_expansion.py — proof harness for the 2026-11-01 jobs expansion + repairs.

Location: `D:\abet_ops\scripts\verify_jobs_expansion.py`.

Imports: `__future__`, `argparse`, `json`, `os`, `re`, `subprocess`, `sys`, `urllib.request`, `pathlib`, `importlib.util`, `providers`, `providers._direct_api`, `provider_runner`, `jobradar.providers.names`.

- `check` (FunctionDef), line 39–42
- `read` (FunctionDef), line 45–46
- `count` (FunctionDef), line 196–202

