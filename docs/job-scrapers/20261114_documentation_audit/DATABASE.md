# Public database dictionary — November 14, 2026 Pacific

Metadata read from the cloud at `2026-11-14T17:44:11.725027-08:00`. Project `abet-app-core` / `alxgteasytezekyunyjk`. No job or applicant records were exported; no database data/schema was changed.

30 relations, 313 columns, 46 constraints, 88 indexes, 29 RLS policies, 896 relation ACL entries, 4 triggers, 8 public functions and 22 sequences.

[Raw catalog](public_database_catalog.json) · [Exact SELECT](export_public_catalog.sql)

Scope is the entire public schema, including non-job legacy tables. Supabase-managed auth/storage schemas and other projects are not presented as exhaustively documented here. Grants are decoded from pg_class ACLs (or PostgreSQL owner defaults); they are not filtered by the metadata caller’s role. They do not alone prove effective access through RLS or inherited roles. Row counts, job data and credential values are excluded.

The four jobs tables retain inactive records. Application tables are separate from the user’s external job-hunt tracker. `sportsbook_job_notifications` is a live delivery ledger; descriptions of it as unused in older documents are historical. The eight November 14 read indexes are included in this snapshot.

## Relations

| Relation | Kind | Owner | RLS |
|---|---|---|---|
| `abet_alerts` | r | `postgres` | True |
| `abet_metrics` | r | `postgres` | True |
| `applications` | r | `postgres` | True |
| `job_scrape_runs` | r | `postgres` | True |
| `jobs` | r | `postgres` | True |
| `jobs_backup_20261007` | r | `postgres` | True |
| `jobs_with_applied` | v | `postgres` | False |
| `mlb_monitor_state` | r | `postgres` | True |
| `profiles` | r | `postgres` | True |
| `robotics_applications` | r | `postgres` | True |
| `robotics_job_notifications` | r | `postgres` | True |
| `robotics_job_scrape_runs` | r | `postgres` | True |
| `robotics_jobs` | r | `postgres` | True |
| `robotics_jobs_with_applied` | v | `postgres` | False |
| `scraper_logs` | r | `postgres` | True |
| `sportsbook_job_notifications` | r | `postgres` | True |
| `tasks` | r | `postgres` | True |
| `team_applications` | r | `postgres` | True |
| `team_job_notifications` | r | `postgres` | True |
| `team_job_observations` | r | `postgres` | True |
| `team_job_scrape_runs` | r | `postgres` | True |
| `team_job_url_aliases` | r | `postgres` | True |
| `team_jobs` | r | `postgres` | True |
| `team_jobs_with_applied` | v | `postgres` | False |
| `team_workday_repair_backup` | r | `postgres` | True |
| `tech_applications` | r | `postgres` | True |
| `tech_job_notifications` | r | `postgres` | True |
| `tech_job_scrape_runs` | r | `postgres` | True |
| `tech_jobs` | r | `postgres` | True |
| `tech_jobs_with_applied` | v | `postgres` | False |

## public.abet_alerts

| Column | Type | Nullable | Default | Identity |
|---|---|---|---|---|
| id | int8 | NO | nextval('abet_alerts_id_seq'::regclass) | — |
| alert_name | text | YES | — | — |
| domain | text | YES | — | — |
| metric | text | YES | — | — |
| metric_value | float8 | YES | — | — |
| threshold | jsonb | NO | '{}'::jsonb | — |
| severity | text | YES | — | — |
| ts | timestamptz | NO | now() | — |
| metadata | jsonb | NO | '{}'::jsonb | — |

### Constraints

- `abet_alerts_pkey`: `PRIMARY KEY (id)`

### Indexes

- `abet_alerts_pkey`: `CREATE UNIQUE INDEX abet_alerts_pkey ON public.abet_alerts USING btree (id)`
- `idx_abet_alerts_ts`: `CREATE INDEX idx_abet_alerts_ts ON public.abet_alerts USING btree (ts DESC)`

### Policies and grants

- `abet_alerts_public_read`: SELECT / ['anon', 'authenticated'] / PERMISSIVE; USING `true`; CHECK `—`.
- `anon`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `authenticated`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `postgres`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `service_role`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.

## public.abet_metrics

| Column | Type | Nullable | Default | Identity |
|---|---|---|---|---|
| id | int8 | NO | nextval('abet_metrics_id_seq'::regclass) | — |
| domain | text | NO | — | — |
| metric | text | NO | — | — |
| value | float8 | YES | — | — |
| ts | timestamptz | NO | now() | — |
| metadata | jsonb | NO | '{}'::jsonb | — |

### Constraints

- `abet_metrics_pkey`: `PRIMARY KEY (id)`

### Indexes

- `abet_metrics_pkey`: `CREATE UNIQUE INDEX abet_metrics_pkey ON public.abet_metrics USING btree (id)`
- `idx_abet_metrics_domain_metric_ts`: `CREATE INDEX idx_abet_metrics_domain_metric_ts ON public.abet_metrics USING btree (domain, metric, ts DESC)`
- `idx_abet_metrics_ts`: `CREATE INDEX idx_abet_metrics_ts ON public.abet_metrics USING btree (ts DESC)`

### Policies and grants

- `abet_metrics_public_read`: SELECT / ['anon', 'authenticated'] / PERMISSIVE; USING `true`; CHECK `—`.
- `anon`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `authenticated`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `postgres`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `service_role`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.

## public.applications

| Column | Type | Nullable | Default | Identity |
|---|---|---|---|---|
| id | int8 | NO | nextval('applications_id_seq'::regclass) | — |
| company | text | NO | — | — |
| job_url | text | NO | — | — |
| job_title | text | YES | — | — |
| status | text | NO | 'applied'::text | — |
| notes | text | YES | — | — |
| applied_at | timestamptz | NO | now() | — |
| updated_at | timestamptz | NO | now() | — |

### Constraints

- `applications_pkey`: `PRIMARY KEY (id)`

### Indexes

- `applications_pkey`: `CREATE UNIQUE INDEX applications_pkey ON public.applications USING btree (id)`
- `idx_applications_applied_at`: `CREATE INDEX idx_applications_applied_at ON public.applications USING btree (applied_at DESC)`
- `idx_applications_company`: `CREATE INDEX idx_applications_company ON public.applications USING btree (company)`
- `idx_applications_company_url_unique`: `CREATE UNIQUE INDEX idx_applications_company_url_unique ON public.applications USING btree (company, job_url)`
- `idx_applications_status`: `CREATE INDEX idx_applications_status ON public.applications USING btree (status, updated_at DESC)`

### Policies and grants

- `anon delete applications`: DELETE / ['anon'] / PERMISSIVE; USING `true`; CHECK `—`.
- `anon insert applications`: INSERT / ['anon'] / PERMISSIVE; USING `—`; CHECK `true`.
- `anon read applications`: SELECT / ['anon'] / PERMISSIVE; USING `true`; CHECK `—`.
- `applications_auth_read`: SELECT / ['authenticated'] / PERMISSIVE; USING `true`; CHECK `—`.
- `applications_auth_write`: ALL / ['authenticated'] / PERMISSIVE; USING `true`; CHECK `true`.
- `anon`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `authenticated`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `postgres`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `service_role`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.

### Trigger SQL

```sql
CREATE TRIGGER trg_applications_touch BEFORE UPDATE ON public.applications FOR EACH ROW EXECUTE FUNCTION touch_updated_at();
```

## public.job_scrape_runs

| Column | Type | Nullable | Default | Identity |
|---|---|---|---|---|
| id | int8 | NO | nextval('job_scrape_runs_id_seq'::regclass) | — |
| provider | text | NO | — | — |
| status | text | NO | 'unknown'::text | — |
| job_count | int4 | NO | 0 | — |
| error_summary | text | YES | — | — |
| trigger_source | text | YES | — | — |
| started_at | timestamptz | NO | now() | — |
| finished_at | timestamptz | YES | — | — |
| metadata | jsonb | NO | '{}'::jsonb | — |

### Constraints

- `job_scrape_runs_pkey`: `PRIMARY KEY (id)`

### Indexes

- `idx_job_scrape_runs_provider_started`: `CREATE INDEX idx_job_scrape_runs_provider_started ON public.job_scrape_runs USING btree (provider, started_at DESC)`
- `idx_job_scrape_runs_started`: `CREATE INDEX idx_job_scrape_runs_started ON public.job_scrape_runs USING btree (started_at DESC)`
- `job_scrape_runs_pkey`: `CREATE UNIQUE INDEX job_scrape_runs_pkey ON public.job_scrape_runs USING btree (id)`

### Policies and grants

- `job_scrape_runs_public_read`: SELECT / ['anon', 'authenticated'] / PERMISSIVE; USING `true`; CHECK `—`.
- `anon`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `authenticated`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `postgres`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `service_role`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.

## public.jobs

| Column | Type | Nullable | Default | Identity |
|---|---|---|---|---|
| id | int8 | NO | nextval('jobs_id_seq'::regclass) | — |
| company | text | NO | — | — |
| title | text | NO | — | — |
| url | text | NO | — | — |
| location | text | YES | — | — |
| description | text | YES | — | — |
| is_active | bool | NO | true | — |
| first_seen_at | timestamptz | NO | now() | — |
| last_seen_at | timestamptz | NO | now() | — |
| scraped_at | timestamptz | NO | now() | — |
| source_payload | jsonb | NO | '{}'::jsonb | — |
| ats | text | YES | — | — |
| posted_at | text | YES | — | — |
| closed_at | text | YES | — | — |
| description_raw | text | YES | — | — |
| description_clean | text | YES | — | — |

### Constraints

- `jobs_pkey`: `PRIMARY KEY (id)`

### Indexes

- `idx_jobs_company`: `CREATE INDEX idx_jobs_company ON public.jobs USING btree (company)`
- `idx_jobs_company_active`: `CREATE INDEX idx_jobs_company_active ON public.jobs USING btree (company, is_active, scraped_at DESC)`
- `idx_jobs_company_url_unique`: `CREATE UNIQUE INDEX idx_jobs_company_url_unique ON public.jobs USING btree (company, url)`
- `idx_jobs_is_active`: `CREATE INDEX idx_jobs_is_active ON public.jobs USING btree (is_active)`
- `idx_jobs_posted_at`: `CREATE INDEX idx_jobs_posted_at ON public.jobs USING btree (posted_at DESC)`
- `idx_jobs_scraped_at`: `CREATE INDEX idx_jobs_scraped_at ON public.jobs USING btree (scraped_at DESC)`
- `idx_jobs_url`: `CREATE INDEX idx_jobs_url ON public.jobs USING btree (url)`
- `jobs_active_newest_idx`: `CREATE INDEX jobs_active_newest_idx ON public.jobs USING btree (posted_at DESC NULLS LAST, id DESC) WHERE (is_active = true)`
- `jobs_freshness_idx`: `CREATE INDEX jobs_freshness_idx ON public.jobs USING btree (scraped_at DESC NULLS LAST)`
- `jobs_pkey`: `CREATE UNIQUE INDEX jobs_pkey ON public.jobs USING btree (id)`

### Policies and grants

- `jobs_public_read`: SELECT / ['anon', 'authenticated'] / PERMISSIVE; USING `true`; CHECK `—`.
- `anon`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `authenticated`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `postgres`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `service_role`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.

## public.jobs_backup_20261007

| Column | Type | Nullable | Default | Identity |
|---|---|---|---|---|
| id | int8 | YES | — | — |
| company | text | YES | — | — |
| title | text | YES | — | — |
| url | text | YES | — | — |
| location | text | YES | — | — |
| description | text | YES | — | — |
| is_active | bool | YES | — | — |
| first_seen_at | timestamptz | YES | — | — |
| last_seen_at | timestamptz | YES | — | — |
| scraped_at | timestamptz | YES | — | — |
| source_payload | jsonb | YES | — | — |
| ats | text | YES | — | — |
| posted_at | text | YES | — | — |
| closed_at | text | YES | — | — |
| description_raw | text | YES | — | — |
| description_clean | text | YES | — | — |

### Constraints


### Indexes


### Policies and grants

- `anon`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `authenticated`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `postgres`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `service_role`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.

## public.jobs_with_applied

| Column | Type | Nullable | Default | Identity |
|---|---|---|---|---|
| id | int8 | YES | — | — |
| company | text | YES | — | — |
| title | text | YES | — | — |
| url | text | YES | — | — |
| location | text | YES | — | — |
| description | text | YES | — | — |
| is_active | bool | YES | — | — |
| first_seen_at | timestamptz | YES | — | — |
| last_seen_at | timestamptz | YES | — | — |
| scraped_at | timestamptz | YES | — | — |
| source_payload | jsonb | YES | — | — |
| ats | text | YES | — | — |
| posted_at | text | YES | — | — |
| closed_at | text | YES | — | — |
| description_raw | text | YES | — | — |
| description_clean | text | YES | — | — |
| is_applied | bool | YES | — | — |
| applied_status | text | YES | — | — |
| applied_at | timestamptz | YES | — | — |

### Constraints


### Indexes


### Policies and grants

- `anon`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `authenticated`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `postgres`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `service_role`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.

### View SQL

```sql
 SELECT j.id,
    j.company,
    j.title,
    j.url,
    j.location,
    j.description,
    j.is_active,
    j.first_seen_at,
    j.last_seen_at,
    j.scraped_at,
    j.source_payload,
    j.ats,
    j.posted_at,
    j.closed_at,
    j.description_raw,
    j.description_clean,
    a.id IS NOT NULL AS is_applied,
    a.status AS applied_status,
    a.applied_at
   FROM jobs j
     LEFT JOIN applications a ON a.company = j.company AND a.job_url = j.url;
```

## public.mlb_monitor_state

| Column | Type | Nullable | Default | Identity |
|---|---|---|---|---|
| monitor_name | text | NO | — | — |
| last_state | jsonb | NO | '{}'::jsonb | — |
| last_run_pt | text | YES | — | — |
| last_success_at | timestamptz | YES | — | — |
| updated_at | timestamptz | NO | now() | — |

### Constraints

- `mlb_monitor_state_pkey`: `PRIMARY KEY (monitor_name)`

### Indexes

- `mlb_monitor_state_pkey`: `CREATE UNIQUE INDEX mlb_monitor_state_pkey ON public.mlb_monitor_state USING btree (monitor_name)`

### Policies and grants

- `mlb_monitor_state_public_read`: SELECT / ['anon', 'authenticated'] / PERMISSIVE; USING `true`; CHECK `—`.
- `anon`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `authenticated`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `postgres`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `service_role`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.

## public.profiles

| Column | Type | Nullable | Default | Identity |
|---|---|---|---|---|
| id | uuid | NO | — | — |
| email | text | YES | — | — |
| display_name | text | YES | — | — |
| tier | text | NO | 'free'::text | — |
| created_at | timestamptz | NO | now() | — |
| updated_at | timestamptz | NO | now() | — |

### Constraints

- `profiles_id_fkey`: `FOREIGN KEY (id) REFERENCES auth.users(id) ON DELETE CASCADE`
- `profiles_pkey`: `PRIMARY KEY (id)`

### Indexes

- `profiles_pkey`: `CREATE UNIQUE INDEX profiles_pkey ON public.profiles USING btree (id)`

### Policies and grants

- `profiles_select_own`: SELECT / ['authenticated'] / PERMISSIVE; USING `(auth.uid() = id)`; CHECK `—`.
- `profiles_update_own`: UPDATE / ['authenticated'] / PERMISSIVE; USING `(auth.uid() = id)`; CHECK `(auth.uid() = id)`.
- `anon`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `authenticated`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `postgres`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `service_role`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.

## public.robotics_applications

| Column | Type | Nullable | Default | Identity |
|---|---|---|---|---|
| id | int8 | NO | nextval('robotics_applications_id_seq'::regclass) | — |
| company | text | NO | — | — |
| job_url | text | NO | — | — |
| job_title | text | YES | — | — |
| status | text | NO | 'applied'::text | — |
| applied_at | timestamptz | NO | now() | — |
| updated_at | timestamptz | NO | now() | — |
| notes | text | YES | — | — |

### Constraints

- `robotics_applications_company_job_url_key`: `UNIQUE (company, job_url)`
- `robotics_applications_pkey`: `PRIMARY KEY (id)`

### Indexes

- `idx_robotics_applications_applied_at`: `CREATE INDEX idx_robotics_applications_applied_at ON public.robotics_applications USING btree (applied_at DESC)`
- `idx_robotics_applications_company`: `CREATE INDEX idx_robotics_applications_company ON public.robotics_applications USING btree (company)`
- `robotics_applications_company_job_url_key`: `CREATE UNIQUE INDEX robotics_applications_company_job_url_key ON public.robotics_applications USING btree (company, job_url)`
- `robotics_applications_pkey`: `CREATE UNIQUE INDEX robotics_applications_pkey ON public.robotics_applications USING btree (id)`

### Policies and grants

- `anon delete robotics_applications`: DELETE / ['anon'] / PERMISSIVE; USING `true`; CHECK `—`.
- `anon insert robotics_applications`: INSERT / ['anon'] / PERMISSIVE; USING `—`; CHECK `true`.
- `anon read robotics_applications`: SELECT / ['anon'] / PERMISSIVE; USING `true`; CHECK `—`.
- `anon`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `authenticated`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `postgres`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `service_role`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.

### Trigger SQL

```sql
CREATE TRIGGER trg_robotics_applications_touch BEFORE UPDATE ON public.robotics_applications FOR EACH ROW EXECUTE FUNCTION touch_robotics_updated_at();
```

## public.robotics_job_notifications

| Column | Type | Nullable | Default | Identity |
|---|---|---|---|---|
| id | int8 | NO | — | BY DEFAULT |
| company | text | NO | — | — |
| job_url | text | NO | — | — |
| payload | jsonb | NO | — | — |
| state | text | NO | 'pending'::text | — |
| created_at | timestamptz | NO | now() | — |
| delivered_at | timestamptz | YES | — | — |
| discord_message_id | text | YES | — | — |

### Constraints

- `robotics_job_notifications_company_job_url_key`: `UNIQUE (company, job_url)`
- `robotics_job_notifications_pkey`: `PRIMARY KEY (id)`
- `robotics_job_notifications_state_check`: `CHECK ((state = ANY (ARRAY['pending'::text, 'delivered'::text, 'expired'::text, 'inactive'::text])))`

### Indexes

- `robotics_job_notifications_company_job_url_key`: `CREATE UNIQUE INDEX robotics_job_notifications_company_job_url_key ON public.robotics_job_notifications USING btree (company, job_url)`
- `robotics_job_notifications_pending_idx`: `CREATE INDEX robotics_job_notifications_pending_idx ON public.robotics_job_notifications USING btree (id) WHERE (state = 'pending'::text)`
- `robotics_job_notifications_pkey`: `CREATE UNIQUE INDEX robotics_job_notifications_pkey ON public.robotics_job_notifications USING btree (id)`

### Policies and grants

- `postgres`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `service_role`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.

## public.robotics_job_scrape_runs

| Column | Type | Nullable | Default | Identity |
|---|---|---|---|---|
| id | int8 | NO | nextval('robotics_job_scrape_runs_id_seq'::regclass) | — |
| provider | text | YES | — | — |
| status | text | YES | — | — |
| job_count | int4 | NO | 0 | — |
| trigger_source | text | YES | — | — |
| error_summary | text | YES | — | — |
| created_at | timestamptz | NO | now() | — |

### Constraints

- `robotics_job_scrape_runs_pkey`: `PRIMARY KEY (id)`

### Indexes

- `idx_robotics_job_scrape_runs_provider`: `CREATE INDEX idx_robotics_job_scrape_runs_provider ON public.robotics_job_scrape_runs USING btree (provider)`
- `robotics_job_scrape_runs_pkey`: `CREATE UNIQUE INDEX robotics_job_scrape_runs_pkey ON public.robotics_job_scrape_runs USING btree (id)`

### Policies and grants

- `anon read robotics_job_scrape_runs`: SELECT / ['anon'] / PERMISSIVE; USING `true`; CHECK `—`.
- `anon`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `authenticated`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `postgres`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `service_role`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.

## public.robotics_jobs

| Column | Type | Nullable | Default | Identity |
|---|---|---|---|---|
| id | int8 | NO | nextval('robotics_jobs_id_seq'::regclass) | — |
| company | text | NO | — | — |
| title | text | NO | — | — |
| url | text | NO | — | — |
| location | text | YES | — | — |
| description | text | YES | — | — |
| is_active | bool | NO | true | — |
| last_seen_at | timestamptz | YES | — | — |
| scraped_at | timestamptz | YES | — | — |
| ats | text | YES | — | — |
| posted_at | text | YES | — | — |
| closed_at | timestamptz | YES | — | — |
| source_payload | jsonb | YES | — | — |

### Constraints

- `robotics_jobs_company_url_key`: `UNIQUE (company, url)`
- `robotics_jobs_pkey`: `PRIMARY KEY (id)`

### Indexes

- `idx_robotics_jobs_company`: `CREATE INDEX idx_robotics_jobs_company ON public.robotics_jobs USING btree (company)`
- `idx_robotics_jobs_is_active`: `CREATE INDEX idx_robotics_jobs_is_active ON public.robotics_jobs USING btree (is_active)`
- `idx_robotics_jobs_posted_at`: `CREATE INDEX idx_robotics_jobs_posted_at ON public.robotics_jobs USING btree (posted_at DESC)`
- `idx_robotics_jobs_url`: `CREATE INDEX idx_robotics_jobs_url ON public.robotics_jobs USING btree (url)`
- `robotics_jobs_active_newest_idx`: `CREATE INDEX robotics_jobs_active_newest_idx ON public.robotics_jobs USING btree (posted_at DESC NULLS LAST, id DESC) WHERE (is_active = true)`
- `robotics_jobs_company_url_key`: `CREATE UNIQUE INDEX robotics_jobs_company_url_key ON public.robotics_jobs USING btree (company, url)`
- `robotics_jobs_freshness_idx`: `CREATE INDEX robotics_jobs_freshness_idx ON public.robotics_jobs USING btree (scraped_at DESC NULLS LAST)`
- `robotics_jobs_pkey`: `CREATE UNIQUE INDEX robotics_jobs_pkey ON public.robotics_jobs USING btree (id)`

### Policies and grants

- `anon read robotics_jobs`: SELECT / ['anon'] / PERMISSIVE; USING `true`; CHECK `—`.
- `anon`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `authenticated`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `postgres`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `service_role`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.

## public.robotics_jobs_with_applied

| Column | Type | Nullable | Default | Identity |
|---|---|---|---|---|
| id | int8 | YES | — | — |
| company | text | YES | — | — |
| title | text | YES | — | — |
| url | text | YES | — | — |
| location | text | YES | — | — |
| description | text | YES | — | — |
| is_active | bool | YES | — | — |
| last_seen_at | timestamptz | YES | — | — |
| scraped_at | timestamptz | YES | — | — |
| ats | text | YES | — | — |
| posted_at | text | YES | — | — |
| closed_at | timestamptz | YES | — | — |
| source_payload | jsonb | YES | — | — |
| is_applied | bool | YES | — | — |
| applied_status | text | YES | — | — |
| applied_at | timestamptz | YES | — | — |

### Constraints


### Indexes


### Policies and grants

- `anon`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `authenticated`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `postgres`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `service_role`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.

### View SQL

```sql
 SELECT j.id,
    j.company,
    j.title,
    j.url,
    j.location,
    j.description,
    j.is_active,
    j.last_seen_at,
    j.scraped_at,
    j.ats,
    j.posted_at,
    j.closed_at,
    j.source_payload,
    a.id IS NOT NULL AS is_applied,
    a.status AS applied_status,
    a.applied_at
   FROM robotics_jobs j
     LEFT JOIN robotics_applications a ON a.company = j.company AND a.job_url = j.url;
```

## public.scraper_logs

| Column | Type | Nullable | Default | Identity |
|---|---|---|---|---|
| id | int8 | NO | nextval('scraper_logs_id_seq'::regclass) | — |
| bookmaker | text | NO | — | — |
| level | text | NO | 'info'::text | — |
| message | text | NO | — | — |
| context | jsonb | NO | '{}'::jsonb | — |
| created_at | timestamptz | NO | now() | — |

### Constraints

- `scraper_logs_pkey`: `PRIMARY KEY (id)`

### Indexes

- `idx_scraper_logs_bookmaker_created`: `CREATE INDEX idx_scraper_logs_bookmaker_created ON public.scraper_logs USING btree (bookmaker, created_at DESC)`
- `scraper_logs_pkey`: `CREATE UNIQUE INDEX scraper_logs_pkey ON public.scraper_logs USING btree (id)`

### Policies and grants

- `scraper_logs_public_read`: SELECT / ['anon', 'authenticated'] / PERMISSIVE; USING `true`; CHECK `—`.
- `anon`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `authenticated`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `postgres`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `service_role`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.

## public.sportsbook_job_notifications

| Column | Type | Nullable | Default | Identity |
|---|---|---|---|---|
| id | int8 | NO | — | ALWAYS |
| company | text | NO | — | — |
| job_url | text | NO | — | — |
| payload | jsonb | NO | — | — |
| kind | text | NO | 'job'::text | — |
| state | text | NO | 'pending'::text | — |
| created_at | timestamptz | NO | now() | — |
| available_at | timestamptz | NO | now() | — |
| lease_token | uuid | YES | — | — |
| lease_until | timestamptz | YES | — | — |
| attempts | int4 | NO | 0 | — |
| last_error | text | YES | — | — |
| delivered_at | timestamptz | YES | — | — |
| discord_message_id | text | YES | — | — |
| discord_channel_id | text | YES | — | — |
| discord_webhook_id | text | YES | — | — |

### Constraints

- `sportsbook_job_notifications_company_job_url_key`: `UNIQUE (company, job_url)`
- `sportsbook_job_notifications_kind_check`: `CHECK ((kind = ANY (ARRAY['job'::text, 'verification'::text])))`
- `sportsbook_job_notifications_pkey`: `PRIMARY KEY (id)`
- `sportsbook_job_notifications_state_check`: `CHECK ((state = ANY (ARRAY['pending'::text, 'sending'::text, 'delivered'::text, 'expired'::text, 'inactive'::text])))`

### Indexes

- `sportsbook_job_notifications_company_job_url_key`: `CREATE UNIQUE INDEX sportsbook_job_notifications_company_job_url_key ON public.sportsbook_job_notifications USING btree (company, job_url)`
- `sportsbook_job_notifications_pkey`: `CREATE UNIQUE INDEX sportsbook_job_notifications_pkey ON public.sportsbook_job_notifications USING btree (id)`
- `sportsbook_notifications_delivered_idx`: `CREATE INDEX sportsbook_notifications_delivered_idx ON public.sportsbook_job_notifications USING btree (delivered_at DESC) WHERE (state = 'delivered'::text)`
- `sportsbook_notifications_lease_idx`: `CREATE INDEX sportsbook_notifications_lease_idx ON public.sportsbook_job_notifications USING btree (lease_token) WHERE (state = 'sending'::text)`
- `sportsbook_notifications_ready_idx`: `CREATE INDEX sportsbook_notifications_ready_idx ON public.sportsbook_job_notifications USING btree (available_at, id) WHERE (state = ANY (ARRAY['pending'::text, 'sending'::text]))`

### Policies and grants

- `postgres`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `service_role`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.

## public.tasks

| Column | Type | Nullable | Default | Identity |
|---|---|---|---|---|
| id | uuid | NO | gen_random_uuid() | — |
| title | text | NO | — | — |
| description | text | YES | — | — |
| priority | text | NO | 'p2'::text | — |
| category | text | NO | 'general'::text | — |
| status | text | NO | 'backlog'::text | — |
| created_by | uuid | YES | — | — |
| created_at | timestamptz | NO | now() | — |
| updated_at | timestamptz | NO | now() | — |

### Constraints

- `tasks_created_by_fkey`: `FOREIGN KEY (created_by) REFERENCES auth.users(id) ON DELETE SET NULL`
- `tasks_pkey`: `PRIMARY KEY (id)`

### Indexes

- `idx_tasks_category`: `CREATE INDEX idx_tasks_category ON public.tasks USING btree (category, created_at DESC)`
- `idx_tasks_priority`: `CREATE INDEX idx_tasks_priority ON public.tasks USING btree (priority, created_at DESC)`
- `idx_tasks_status`: `CREATE INDEX idx_tasks_status ON public.tasks USING btree (status, updated_at DESC)`
- `tasks_pkey`: `CREATE UNIQUE INDEX tasks_pkey ON public.tasks USING btree (id)`

### Policies and grants

- `tasks_auth_write`: ALL / ['authenticated'] / PERMISSIVE; USING `true`; CHECK `true`.
- `tasks_public_read`: SELECT / ['anon', 'authenticated'] / PERMISSIVE; USING `true`; CHECK `—`.
- `anon`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `authenticated`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `postgres`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `service_role`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.

## public.team_applications

| Column | Type | Nullable | Default | Identity |
|---|---|---|---|---|
| id | int8 | NO | nextval('team_applications_id_seq'::regclass) | — |
| user_id | uuid | NO | auth.uid() | — |
| company | text | NO | — | — |
| job_url | text | NO | — | — |
| job_title | text | YES | — | — |
| status | text | NO | 'applied'::text | — |
| applied_at | timestamptz | NO | now() | — |
| updated_at | timestamptz | NO | now() | — |
| notes | text | YES | — | — |

### Constraints

- `team_applications_pkey`: `PRIMARY KEY (id)`
- `team_applications_user_id_company_job_url_key`: `UNIQUE (user_id, company, job_url)`
- `team_applications_user_id_fkey`: `FOREIGN KEY (user_id) REFERENCES auth.users(id)`

### Indexes

- `team_applications_pkey`: `CREATE UNIQUE INDEX team_applications_pkey ON public.team_applications USING btree (id)`
- `team_applications_user_id_company_job_url_key`: `CREATE UNIQUE INDEX team_applications_user_id_company_job_url_key ON public.team_applications USING btree (user_id, company, job_url)`

### Policies and grants

- `team_applications_owner`: ALL / ['authenticated'] / PERMISSIVE; USING `(user_id = auth.uid())`; CHECK `(user_id = auth.uid())`.
- `anon`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `authenticated`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `postgres`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `service_role`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.

## public.team_job_notifications

| Column | Type | Nullable | Default | Identity |
|---|---|---|---|---|
| id | int8 | NO | nextval('team_job_notifications_id_seq'::regclass) | — |
| url | text | NO | — | — |
| status | text | NO | — | — |
| delivered_at | timestamptz | YES | — | — |
| discord_message_id | text | YES | — | — |

### Constraints

- `team_job_notifications_pkey`: `PRIMARY KEY (id)`
- `team_job_notifications_url_key`: `UNIQUE (url)`

### Indexes

- `team_job_notifications_pkey`: `CREATE UNIQUE INDEX team_job_notifications_pkey ON public.team_job_notifications USING btree (id)`
- `team_job_notifications_url_key`: `CREATE UNIQUE INDEX team_job_notifications_url_key ON public.team_job_notifications USING btree (url)`

### Policies and grants

- `anon`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `authenticated`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `postgres`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `service_role`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.

## public.team_job_observations

| Column | Type | Nullable | Default | Identity |
|---|---|---|---|---|
| id | int8 | NO | nextval('team_job_observations_id_seq'::regclass) | — |
| source_id | text | NO | — | — |
| url | text | NO | — | — |
| is_active | bool | NO | — | — |
| observed_at | timestamptz | YES | — | — |

### Constraints

- `team_job_observations_pkey`: `PRIMARY KEY (id)`
- `team_job_observations_source_id_url_key`: `UNIQUE (source_id, url)`

### Indexes

- `team_job_observations_pkey`: `CREATE UNIQUE INDEX team_job_observations_pkey ON public.team_job_observations USING btree (id)`
- `team_job_observations_source_id_url_key`: `CREATE UNIQUE INDEX team_job_observations_source_id_url_key ON public.team_job_observations USING btree (source_id, url)`

### Policies and grants

- `anon`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `authenticated`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `postgres`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `service_role`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.

## public.team_job_scrape_runs

| Column | Type | Nullable | Default | Identity |
|---|---|---|---|---|
| id | int8 | NO | nextval('team_job_scrape_runs_id_seq'::regclass) | — |
| run_id | uuid | NO | — | — |
| provider | text | NO | — | — |
| source | text | YES | — | — |
| platform | text | YES | — | — |
| status | text | NO | — | — |
| job_count | int4 | NO | 0 | — |
| duration_ms | int4 | YES | — | — |
| error_summary | text | YES | — | — |
| trigger_source | text | YES | — | — |
| created_at | timestamptz | NO | now() | — |

### Constraints

- `team_job_scrape_runs_pkey`: `PRIMARY KEY (id)`
- `team_job_scrape_runs_run_id_provider_key`: `UNIQUE (run_id, provider)`

### Indexes

- `team_job_runs_date_idx`: `CREATE INDEX team_job_runs_date_idx ON public.team_job_scrape_runs USING btree (created_at DESC)`
- `team_job_scrape_runs_pkey`: `CREATE UNIQUE INDEX team_job_scrape_runs_pkey ON public.team_job_scrape_runs USING btree (id)`
- `team_job_scrape_runs_run_id_provider_key`: `CREATE UNIQUE INDEX team_job_scrape_runs_run_id_provider_key ON public.team_job_scrape_runs USING btree (run_id, provider)`

### Policies and grants

- `team_runs_read`: SELECT / ['anon', 'authenticated'] / PERMISSIVE; USING `true`; CHECK `—`.
- `anon`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `authenticated`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `postgres`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `service_role`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.

## public.team_job_url_aliases

| Column | Type | Nullable | Default | Identity |
|---|---|---|---|---|
| id | int8 | NO | nextval('team_job_url_aliases_id_seq'::regclass) | — |
| old_url | text | NO | — | — |
| canonical_url | text | NO | — | — |
| original_job_id | int8 | NO | — | — |
| repaired_at | timestamptz | NO | now() | — |

### Constraints

- `team_job_url_aliases_old_url_key`: `UNIQUE (old_url)`
- `team_job_url_aliases_pkey`: `PRIMARY KEY (id)`

### Indexes

- `team_job_url_aliases_old_url_key`: `CREATE UNIQUE INDEX team_job_url_aliases_old_url_key ON public.team_job_url_aliases USING btree (old_url)`
- `team_job_url_aliases_pkey`: `CREATE UNIQUE INDEX team_job_url_aliases_pkey ON public.team_job_url_aliases USING btree (id)`

### Policies and grants

- `team_aliases_read`: SELECT / ['anon', 'authenticated'] / PERMISSIVE; USING `true`; CHECK `—`.
- `anon`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `authenticated`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `postgres`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `service_role`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.

## public.team_jobs

| Column | Type | Nullable | Default | Identity |
|---|---|---|---|---|
| id | int8 | NO | nextval('team_jobs_id_seq'::regclass) | — |
| league | text | NO | — | — |
| team | text | NO | — | — |
| company | text | NO | — | — |
| title | text | NO | — | — |
| url | text | NO | — | — |
| location | text | YES | — | — |
| description | text | YES | — | — |
| platform | text | YES | — | — |
| ats | text | YES | — | — |
| posted_at | text | YES | — | — |
| first_seen_at | timestamptz | NO | now() | — |
| last_seen_at | timestamptz | YES | — | — |
| scraped_at | timestamptz | YES | — | — |
| is_active | bool | NO | true | — |
| closed_at | timestamptz | YES | — | — |
| logo_url | text | YES | — | — |
| source_id | text | YES | — | — |
| salary | text | YES | — | — |
| detail_status | text | YES | — | — |
| detail_checked_at | timestamptz | YES | — | — |

### Constraints

- `team_jobs_pkey`: `PRIMARY KEY (id)`
- `team_jobs_url_key`: `UNIQUE (url)`
- `team_workday_site_required`: `CHECK ((url !~ '^https://[^/]+\.myworkdayjobs\.com/job/'::text))`

### Indexes

- `team_jobs_active_idx`: `CREATE INDEX team_jobs_active_idx ON public.team_jobs USING btree (is_active)`
- `team_jobs_active_newest_idx`: `CREATE INDEX team_jobs_active_newest_idx ON public.team_jobs USING btree (posted_at DESC NULLS LAST, id DESC) WHERE (is_active = true)`
- `team_jobs_first_idx`: `CREATE INDEX team_jobs_first_idx ON public.team_jobs USING btree (first_seen_at DESC)`
- `team_jobs_freshness_idx`: `CREATE INDEX team_jobs_freshness_idx ON public.team_jobs USING btree (scraped_at DESC NULLS LAST)`
- `team_jobs_pkey`: `CREATE UNIQUE INDEX team_jobs_pkey ON public.team_jobs USING btree (id)`
- `team_jobs_url_key`: `CREATE UNIQUE INDEX team_jobs_url_key ON public.team_jobs USING btree (url)`

### Policies and grants

- `team_jobs_read`: SELECT / ['anon', 'authenticated'] / PERMISSIVE; USING `true`; CHECK `—`.
- `anon`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `authenticated`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `postgres`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `service_role`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.

### Trigger SQL

```sql
CREATE TRIGGER team_keep_first_seen BEFORE UPDATE ON public.team_jobs FOR EACH ROW EXECUTE FUNCTION team_keep_first_seen();
```

## public.team_jobs_with_applied

| Column | Type | Nullable | Default | Identity |
|---|---|---|---|---|
| id | int8 | YES | — | — |
| league | text | YES | — | — |
| team | text | YES | — | — |
| company | text | YES | — | — |
| title | text | YES | — | — |
| url | text | YES | — | — |
| location | text | YES | — | — |
| description | text | YES | — | — |
| platform | text | YES | — | — |
| ats | text | YES | — | — |
| posted_at | text | YES | — | — |
| first_seen_at | timestamptz | YES | — | — |
| last_seen_at | timestamptz | YES | — | — |
| scraped_at | timestamptz | YES | — | — |
| is_active | bool | YES | — | — |
| closed_at | timestamptz | YES | — | — |
| logo_url | text | YES | — | — |
| source_id | text | YES | — | — |
| salary | text | YES | — | — |
| detail_status | text | YES | — | — |
| detail_checked_at | timestamptz | YES | — | — |
| is_applied | bool | YES | — | — |
| applied_status | text | YES | — | — |
| applied_at | timestamptz | YES | — | — |

### Constraints


### Indexes


### Policies and grants

- `anon`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `authenticated`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `postgres`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `service_role`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.

### View SQL

```sql
 SELECT j.id,
    j.league,
    j.team,
    j.company,
    j.title,
    j.url,
    j.location,
    j.description,
    j.platform,
    j.ats,
    j.posted_at,
    j.first_seen_at,
    j.last_seen_at,
    j.scraped_at,
    j.is_active,
    j.closed_at,
    j.logo_url,
    j.source_id,
    j.salary,
    j.detail_status,
    j.detail_checked_at,
    a.id IS NOT NULL AS is_applied,
    a.status AS applied_status,
    a.applied_at
   FROM team_jobs j
     LEFT JOIN team_applications a ON a.job_url = j.url AND a.company = j.company AND a.user_id = auth.uid();
```

## public.team_workday_repair_backup

| Column | Type | Nullable | Default | Identity |
|---|---|---|---|---|
| id | int8 | NO | nextval('team_workday_repair_backup_id_seq'::regclass) | — |
| captured_at | timestamptz | YES | now() | — |
| table_name | text | NO | — | — |
| payload | jsonb | NO | — | — |

### Constraints

- `team_workday_repair_backup_pkey`: `PRIMARY KEY (id)`

### Indexes

- `team_workday_repair_backup_pkey`: `CREATE UNIQUE INDEX team_workday_repair_backup_pkey ON public.team_workday_repair_backup USING btree (id)`

### Policies and grants

- `postgres`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `service_role`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.

## public.tech_applications

| Column | Type | Nullable | Default | Identity |
|---|---|---|---|---|
| id | int8 | NO | nextval('tech_applications_id_seq'::regclass) | — |
| company | text | NO | — | — |
| job_url | text | NO | — | — |
| job_title | text | YES | — | — |
| status | text | NO | 'applied'::text | — |
| applied_at | timestamptz | NO | now() | — |
| updated_at | timestamptz | NO | now() | — |
| notes | text | YES | — | — |

### Constraints

- `tech_applications_company_job_url_key`: `UNIQUE (company, job_url)`
- `tech_applications_pkey`: `PRIMARY KEY (id)`

### Indexes

- `idx_tech_applications_applied_at`: `CREATE INDEX idx_tech_applications_applied_at ON public.tech_applications USING btree (applied_at DESC)`
- `idx_tech_applications_company`: `CREATE INDEX idx_tech_applications_company ON public.tech_applications USING btree (company)`
- `tech_applications_company_job_url_key`: `CREATE UNIQUE INDEX tech_applications_company_job_url_key ON public.tech_applications USING btree (company, job_url)`
- `tech_applications_pkey`: `CREATE UNIQUE INDEX tech_applications_pkey ON public.tech_applications USING btree (id)`

### Policies and grants

- `anon delete tech_applications`: DELETE / ['anon'] / PERMISSIVE; USING `true`; CHECK `—`.
- `anon insert tech_applications`: INSERT / ['anon'] / PERMISSIVE; USING `—`; CHECK `true`.
- `anon read tech_applications`: SELECT / ['anon'] / PERMISSIVE; USING `true`; CHECK `—`.
- `anon`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `authenticated`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `postgres`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `service_role`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.

### Trigger SQL

```sql
CREATE TRIGGER trg_tech_applications_touch BEFORE UPDATE ON public.tech_applications FOR EACH ROW EXECUTE FUNCTION touch_tech_updated_at();
```

## public.tech_job_notifications

| Column | Type | Nullable | Default | Identity |
|---|---|---|---|---|
| id | int8 | NO | — | BY DEFAULT |
| company | text | NO | — | — |
| job_url | text | NO | — | — |
| payload | jsonb | NO | — | — |
| state | text | NO | 'pending'::text | — |
| created_at | timestamptz | NO | now() | — |
| delivered_at | timestamptz | YES | — | — |
| discord_message_id | text | YES | — | — |

### Constraints

- `tech_job_notifications_company_job_url_key`: `UNIQUE (company, job_url)`
- `tech_job_notifications_pkey`: `PRIMARY KEY (id)`
- `tech_job_notifications_state_check`: `CHECK ((state = ANY (ARRAY['pending'::text, 'delivered'::text, 'expired'::text, 'inactive'::text])))`

### Indexes

- `tech_job_notifications_company_job_url_key`: `CREATE UNIQUE INDEX tech_job_notifications_company_job_url_key ON public.tech_job_notifications USING btree (company, job_url)`
- `tech_job_notifications_pending_idx`: `CREATE INDEX tech_job_notifications_pending_idx ON public.tech_job_notifications USING btree (id) WHERE (state = 'pending'::text)`
- `tech_job_notifications_pkey`: `CREATE UNIQUE INDEX tech_job_notifications_pkey ON public.tech_job_notifications USING btree (id)`

### Policies and grants

- `postgres`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `service_role`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.

## public.tech_job_scrape_runs

| Column | Type | Nullable | Default | Identity |
|---|---|---|---|---|
| id | int8 | NO | nextval('tech_job_scrape_runs_id_seq'::regclass) | — |
| provider | text | YES | — | — |
| status | text | YES | — | — |
| job_count | int4 | NO | 0 | — |
| trigger_source | text | YES | — | — |
| error_summary | text | YES | — | — |
| created_at | timestamptz | NO | now() | — |

### Constraints

- `tech_job_scrape_runs_pkey`: `PRIMARY KEY (id)`

### Indexes

- `idx_tech_job_scrape_runs_provider`: `CREATE INDEX idx_tech_job_scrape_runs_provider ON public.tech_job_scrape_runs USING btree (provider)`
- `tech_job_scrape_runs_pkey`: `CREATE UNIQUE INDEX tech_job_scrape_runs_pkey ON public.tech_job_scrape_runs USING btree (id)`

### Policies and grants

- `anon read Tech_job_scrape_runs`: SELECT / ['anon'] / PERMISSIVE; USING `true`; CHECK `—`.
- `anon`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `authenticated`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `postgres`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `service_role`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.

## public.tech_jobs

| Column | Type | Nullable | Default | Identity |
|---|---|---|---|---|
| id | int8 | NO | nextval('tech_jobs_id_seq'::regclass) | — |
| company | text | NO | — | — |
| title | text | NO | — | — |
| url | text | NO | — | — |
| location | text | YES | — | — |
| description | text | YES | — | — |
| is_active | bool | NO | true | — |
| last_seen_at | timestamptz | YES | — | — |
| scraped_at | timestamptz | YES | — | — |
| ats | text | YES | — | — |
| posted_at | text | YES | — | — |
| closed_at | timestamptz | YES | — | — |
| source_payload | jsonb | YES | — | — |

### Constraints

- `tech_jobs_company_url_key`: `UNIQUE (company, url)`
- `tech_jobs_pkey`: `PRIMARY KEY (id)`

### Indexes

- `idx_tech_jobs_company`: `CREATE INDEX idx_tech_jobs_company ON public.tech_jobs USING btree (company)`
- `idx_tech_jobs_is_active`: `CREATE INDEX idx_tech_jobs_is_active ON public.tech_jobs USING btree (is_active)`
- `idx_tech_jobs_posted_at`: `CREATE INDEX idx_tech_jobs_posted_at ON public.tech_jobs USING btree (posted_at DESC)`
- `idx_tech_jobs_url`: `CREATE INDEX idx_tech_jobs_url ON public.tech_jobs USING btree (url)`
- `tech_jobs_active_newest_idx`: `CREATE INDEX tech_jobs_active_newest_idx ON public.tech_jobs USING btree (posted_at DESC NULLS LAST, id DESC) WHERE (is_active = true)`
- `tech_jobs_company_url_key`: `CREATE UNIQUE INDEX tech_jobs_company_url_key ON public.tech_jobs USING btree (company, url)`
- `tech_jobs_freshness_idx`: `CREATE INDEX tech_jobs_freshness_idx ON public.tech_jobs USING btree (scraped_at DESC NULLS LAST)`
- `tech_jobs_pkey`: `CREATE UNIQUE INDEX tech_jobs_pkey ON public.tech_jobs USING btree (id)`

### Policies and grants

- `anon read tech_jobs`: SELECT / ['anon'] / PERMISSIVE; USING `true`; CHECK `—`.
- `anon`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `authenticated`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `postgres`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `service_role`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.

## public.tech_jobs_with_applied

| Column | Type | Nullable | Default | Identity |
|---|---|---|---|---|
| id | int8 | YES | — | — |
| company | text | YES | — | — |
| title | text | YES | — | — |
| url | text | YES | — | — |
| location | text | YES | — | — |
| description | text | YES | — | — |
| is_active | bool | YES | — | — |
| last_seen_at | timestamptz | YES | — | — |
| scraped_at | timestamptz | YES | — | — |
| ats | text | YES | — | — |
| posted_at | text | YES | — | — |
| closed_at | timestamptz | YES | — | — |
| source_payload | jsonb | YES | — | — |
| is_applied | bool | YES | — | — |
| applied_status | text | YES | — | — |
| applied_at | timestamptz | YES | — | — |

### Constraints


### Indexes


### Policies and grants

- `anon`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `authenticated`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `postgres`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- `service_role`: DELETE, INSERT, MAINTAIN, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.

### View SQL

```sql
 SELECT j.id,
    j.company,
    j.title,
    j.url,
    j.location,
    j.description,
    j.is_active,
    j.last_seen_at,
    j.scraped_at,
    j.ats,
    j.posted_at,
    j.closed_at,
    j.source_payload,
    a.id IS NOT NULL AS is_applied,
    a.status AS applied_status,
    a.applied_at
   FROM tech_jobs j
     LEFT JOIN tech_applications a ON a.company = j.company AND a.job_url = j.url;
```

## Public functions

### claim_sportsbook_notifications(p_token uuid, p_limit integer)

Security definer: `False`. Config: `['search_path=public']`. ACL: `['postgres=X/postgres', 'service_role=X/postgres']`.

```sql
CREATE OR REPLACE FUNCTION public.claim_sportsbook_notifications(p_token uuid, p_limit integer DEFAULT 5)
 RETURNS SETOF sportsbook_job_notifications
 LANGUAGE plpgsql
 SET search_path TO 'public'
AS $function$
begin
  -- Repeating an RPC whose response was lost returns its original claim.
  if exists(select 1 from public.sportsbook_job_notifications where lease_token=p_token and state='sending') then
    return query select * from public.sportsbook_job_notifications
      where lease_token=p_token and state='sending' order by id;
    return;
  end if;
  return query
    with picked as (
      select id from public.sportsbook_job_notifications
      where ((state='pending' and available_at<=now()) or (state='sending' and lease_until<now()))
      order by id for update skip locked limit greatest(1,least(p_limit,5))
    )
    update public.sportsbook_job_notifications q
      set state='sending',lease_token=p_token,lease_until=now()+interval '15 minutes',attempts=q.attempts+1
    from picked where q.id=picked.id returning q.*;
end $function$

```

### handle_new_user_profile()

Security definer: `True`. Config: `['search_path=public']`. ACL: `['=X/postgres', 'postgres=X/postgres', 'anon=X/postgres', 'authenticated=X/postgres', 'service_role=X/postgres']`.

```sql
CREATE OR REPLACE FUNCTION public.handle_new_user_profile()
 RETURNS trigger
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'public'
AS $function$

begin

  insert into public.profiles (id, email)

  values (new.id, new.email)

  on conflict (id) do nothing;

  return new;

end;

$function$

```

### rls_auto_enable()

Security definer: `True`. Config: `['search_path=pg_catalog']`. ACL: `['=X/postgres', 'postgres=X/postgres', 'anon=X/postgres', 'authenticated=X/postgres', 'service_role=X/postgres']`.

```sql
CREATE OR REPLACE FUNCTION public.rls_auto_enable()
 RETURNS event_trigger
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO 'pg_catalog'
AS $function$
DECLARE
  cmd record;
BEGIN
  FOR cmd IN
    SELECT *
    FROM pg_event_trigger_ddl_commands()
    WHERE command_tag IN ('CREATE TABLE', 'CREATE TABLE AS', 'SELECT INTO')
      AND object_type IN ('table','partitioned table')
  LOOP
     IF cmd.schema_name IS NOT NULL AND cmd.schema_name IN ('public') AND cmd.schema_name NOT IN ('pg_catalog','information_schema') AND cmd.schema_name NOT LIKE 'pg_toast%' AND cmd.schema_name NOT LIKE 'pg_temp%' THEN
      BEGIN
        EXECUTE format('alter table if exists %s enable row level security', cmd.object_identity);
        RAISE LOG 'rls_auto_enable: enabled RLS on %', cmd.object_identity;
      EXCEPTION
        WHEN OTHERS THEN
          RAISE LOG 'rls_auto_enable: failed to enable RLS on %', cmd.object_identity;
      END;
     ELSE
        RAISE LOG 'rls_auto_enable: skip % (either system schema or not in enforced list: %.)', cmd.object_identity, cmd.schema_name;
     END IF;
  END LOOP;
END;
$function$

```

### sportsbook_notification_status()

Security definer: `False`. Config: `['search_path=public']`. ACL: `['postgres=X/postgres', 'service_role=X/postgres']`.

```sql
CREATE OR REPLACE FUNCTION public.sportsbook_notification_status()
 RETURNS jsonb
 LANGUAGE sql
 SET search_path TO 'public'
AS $function$
 select jsonb_build_object(
  'pending',count(*) filter(where state='pending'),
  'sending',count(*) filter(where state='sending'),
  'delivered',count(*) filter(where state='delivered'),
  'expired',count(*) filter(where state='expired'),
  'inactive',count(*) filter(where state='inactive'),
  'retry_pending',count(*) filter(where state in ('pending','sending') and last_error is not null),
  'oldest_pending_at',min(created_at) filter(where state in ('pending','sending')),
  'last_delivered_at',max(delivered_at),
  'latest_delivery',(select jsonb_build_object('message_id',n.discord_message_id,
    'channel_id',n.discord_channel_id,'webhook_id',n.discord_webhook_id,'delivered_at',n.delivered_at)
    from public.sportsbook_job_notifications n where n.state='delivered'
    order by n.delivered_at desc limit 1)) from public.sportsbook_job_notifications;
$function$

```

### team_keep_first_seen()

Security definer: `False`. Config: `None`. ACL: `['=X/postgres', 'postgres=X/postgres', 'anon=X/postgres', 'authenticated=X/postgres', 'service_role=X/postgres']`.

```sql
CREATE OR REPLACE FUNCTION public.team_keep_first_seen()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
begin new.first_seen_at=old.first_seen_at; return new; end; $function$

```

### touch_robotics_updated_at()

Security definer: `False`. Config: `None`. ACL: `['=X/postgres', 'postgres=X/postgres', 'anon=X/postgres', 'authenticated=X/postgres', 'service_role=X/postgres']`.

```sql
CREATE OR REPLACE FUNCTION public.touch_robotics_updated_at()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
begin
  new.updated_at = now();
  return new;
end;
$function$

```

### touch_tech_updated_at()

Security definer: `False`. Config: `None`. ACL: `['=X/postgres', 'postgres=X/postgres', 'anon=X/postgres', 'authenticated=X/postgres', 'service_role=X/postgres']`.

```sql
CREATE OR REPLACE FUNCTION public.touch_tech_updated_at()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
begin
  new.updated_at = now();
  return new;
end;
$function$

```

### touch_updated_at()

Security definer: `False`. Config: `None`. ACL: `['=X/postgres', 'postgres=X/postgres', 'anon=X/postgres', 'authenticated=X/postgres', 'service_role=X/postgres']`.

```sql
CREATE OR REPLACE FUNCTION public.touch_updated_at()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
begin
  new.updated_at = now();
  return new;
end;
$function$

```

## Sequences

| Name | Owner | Type | Increment | Cycle |
|---|---|---|---|---|
| abet_alerts_id_seq | postgres | bigint | 1 | False |
| abet_metrics_id_seq | postgres | bigint | 1 | False |
| applications_id_seq | postgres | bigint | 1 | False |
| job_scrape_runs_id_seq | postgres | bigint | 1 | False |
| jobs_id_seq | postgres | bigint | 1 | False |
| robotics_applications_id_seq | postgres | bigint | 1 | False |
| robotics_job_notifications_id_seq | postgres | bigint | 1 | False |
| robotics_job_scrape_runs_id_seq | postgres | bigint | 1 | False |
| robotics_jobs_id_seq | postgres | bigint | 1 | False |
| scraper_logs_id_seq | postgres | bigint | 1 | False |
| sportsbook_job_notifications_id_seq | postgres | bigint | 1 | False |
| team_applications_id_seq | postgres | bigint | 1 | False |
| team_job_notifications_id_seq | postgres | bigint | 1 | False |
| team_job_observations_id_seq | postgres | bigint | 1 | False |
| team_job_scrape_runs_id_seq | postgres | bigint | 1 | False |
| team_job_url_aliases_id_seq | postgres | bigint | 1 | False |
| team_jobs_id_seq | postgres | bigint | 1 | False |
| team_workday_repair_backup_id_seq | postgres | bigint | 1 | False |
| tech_applications_id_seq | postgres | bigint | 1 | False |
| tech_job_notifications_id_seq | postgres | bigint | 1 | False |
| tech_job_scrape_runs_id_seq | postgres | bigint | 1 | False |
| tech_jobs_id_seq | postgres | bigint | 1 | False |

## Extensions

| Name | Version | Schema |
|---|---|---|
| pg_stat_statements | 1.11 | extensions |
| pgcrypto | 1.3 | extensions |
| plpgsql | 1.0 | pg_catalog |
| supabase_vault | 0.3.1 | vault |
| uuid-ossp | 1.1 | extensions |
