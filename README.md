# Job Radar

Automated job-hunting platform: **scrape** many sources → **match** each posting against a
skills matrix → **alert** strong fits to Discord → **draft** a tailored resume + cover letter.
Wide net across tech companies + startups (and, in a separate isolated track, sportsbooks).

```
sources ─▶ ingest ─▶ jobs (SQLite/Supabase) ─▶ score (heuristic | Claude judge) ─▶ job_scores
                                                                     │
                                              Discord digest ◀───────┤
                                              resume+cover draft ◀────┤ (on demand)
                                              HTML dashboard ◀────────┘
```

## Status (working, tested end-to-end)
- **Ingestion:** Greenhouse ✅, Ashby ✅ (live: 3k+ real jobs incl. Anthropic/OpenAI/Databricks/Stripe), Lever ✅ (wired; needs real slugs), Workday/Indeed = roadmap.
- **Storage:** SQLite (local dev, zero setup) or Supabase (prod) behind one interface.
- **Matcher:** free **heuristic scorer** (runs now) + **Claude judge** (when `ANTHROPIC_API_KEY` set). Prefilter drops off-target/offshore/internship roles.
- **Alerts:** single deduped Discord digest of matches ≥ threshold.
- **Generation:** resume + cover-letter drafts with hard truth-guardrails, written to `GENERATED_DOCS_DIR` + tracked in `applications`.
- **Dashboard:** self-contained filterable HTML (`out/dashboard.html`).
- **Scheduler:** GitHub Actions (`.github/workflows/pipeline.yml`, every 3h).

## Quickstart (local, no cloud)
```bash
pip install -r requirements.txt
python run.py ingest      # scrape providers -> local SQLite
python run.py score       # rate every job against the matrix
python run.py report      # top matches in the terminal
python run.py render      # -> out/dashboard.html  (open it)
python run.py alert       # dry-run digest (no webhook set = prints instead of posting)
python run.py generate --job-id 2247   # draft resume+cover for a job
python run.py pipeline    # ingest -> score -> alert in one shot
```

## Configuration
- Copy `.env.example` → `.env` (gitignored). Keys: `SUPABASE_URL`/`SUPABASE_SERVICE_ROLE_KEY` (omit → SQLite), `ANTHROPIC_API_KEY` (omit → heuristic scorer), `DISCORD_JOB_RADAR_WEBHOOK`, `ALERT_MIN_SCORE`, `MATRIX_PATH`, `GENERATED_DOCS_DIR`.
- **Targets:** `config/targets.json` — company slugs per ATS + Indeed queries. Populate the sportsbook + tech slugs from the career-page discovery task.
- **Profile:** `config/skills_matrix.md` (bundled copy of the master matrix — keep it in sync; it *is* the scoring rubric).

## Storage / prod
Apply `db/schema.sql` once in the Supabase SQL editor, set `SUPABASE_URL` + `SUPABASE_SERVICE_ROLE_KEY`, and the same commands write to Supabase instead of SQLite. **Use a current project — not the dead legacy `kiujpszjsszqzinyxkoi`.**

## Deploy (automated)
Add repo secrets (Settings → Secrets → Actions): `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `DISCORD_JOB_RADAR_WEBHOOK`, `ANTHROPIC_API_KEY` (optional), `ANTHROPIC_MODEL`, `ALERT_MIN_SCORE`. The workflow runs the pipeline every 3h and uploads the dashboard as an artifact.

## Guardrails & security
- **Repo must stay private** — it bundles the personal skills matrix.
- Secrets live only in `.env` / provider secret stores — never committed (`.gitignore` enforces `.env*`, `*secret*`, `PROJECT_KEYS*`).
- Generation obeys: Columbia Bank = **Seattle** (not Tacoma); **never** claim the Umpqua merger; Series 7/63 = **lapsed**; **no fabrication**.
- **Assisted apply, not auto-submit:** the platform finds/scores/drafts/tracks; a human reviews and submits.

## Roadmap
Lever/Workday/Indeed providers + real slugs (from the career-page discovery task) · sportsbook career pages in the isolated `sportsbook-jobs-dashboard` repo · PDF export of generated docs · Radar dashboard on Vercel/Pages · feedback loop to tune the threshold.
