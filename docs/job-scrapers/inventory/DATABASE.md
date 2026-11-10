# Live job database dictionary — November 10, 2026

Read-only PostgreSQL catalog export at `2026-11-10T18:54:45.378584+00:00`. Project `alxgteasytezekyunyjk`, schema `public`. No job or applicant rows were exported.

20 tables/views; 223 columns; 28 constraints; 56 indexes; 21 RLS policies; 4 triggers; 546 grants.

SQL: [export_job_schema.sql](../export_job_schema.sql). Evidence: [read-only workflow run](https://github.com/misterplusev/job-radar/actions/runs/42879922731). Raw structure: [database_catalog.json](database_catalog.json).

Important observed differences: `robotics_jobs` and `tech_jobs` currently have no `first_seen_at` column despite local migration files. Their source-run timestamps are `created_at`; sportsbook run timestamps are `started_at`. Do not query guessed common columns. Policies below describe deployed access, not recommended defaults for a new module.

## public.applications

Kind `r`; RLS enabled `True`; RLS forced `False`.

| # | Column | Type | Nullable | Default | Identity |
|---:|---|---|---|---|---|
| 1 | id | int8 | NO | nextval('applications_id_seq'::regclass) | — |
| 2 | company | text | NO | — | — |
| 3 | job_url | text | NO | — | — |
| 4 | job_title | text | YES | — | — |
| 5 | status | text | NO | 'applied'::text | — |
| 6 | notes | text | YES | — | — |
| 7 | applied_at | timestamptz | NO | now() | — |
| 8 | updated_at | timestamptz | NO | now() | — |

### Constraints and indexes

- `applications_pkey`: `PRIMARY KEY (id)`
- `applications_pkey`: `CREATE UNIQUE INDEX applications_pkey ON public.applications USING btree (id)`
- `idx_applications_applied_at`: `CREATE INDEX idx_applications_applied_at ON public.applications USING btree (applied_at DESC)`
- `idx_applications_company`: `CREATE INDEX idx_applications_company ON public.applications USING btree (company)`
- `idx_applications_company_url_unique`: `CREATE UNIQUE INDEX idx_applications_company_url_unique ON public.applications USING btree (company, job_url)`
- `idx_applications_status`: `CREATE INDEX idx_applications_status ON public.applications USING btree (status, updated_at DESC)`

### Access policies and grants

- `anon delete applications`: DELETE, roles `['anon']`, PERMISSIVE; USING `true`; WITH CHECK `—`.
- `anon insert applications`: INSERT, roles `['anon']`, PERMISSIVE; USING `—`; WITH CHECK `true`.
- `anon read applications`: SELECT, roles `['anon']`, PERMISSIVE; USING `true`; WITH CHECK `—`.
- `applications_auth_read`: SELECT, roles `['authenticated']`, PERMISSIVE; USING `true`; WITH CHECK `—`.
- `applications_auth_write`: ALL, roles `['authenticated']`, PERMISSIVE; USING `true`; WITH CHECK `true`.
- Grants to `anon`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- Grants to `authenticated`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- Grants to `postgres`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- Grants to `service_role`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.

### Trigger and function

```sql
CREATE TRIGGER trg_applications_touch BEFORE UPDATE ON public.applications FOR EACH ROW EXECUTE FUNCTION touch_updated_at();
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

## public.job_scrape_runs

Kind `r`; RLS enabled `True`; RLS forced `False`.

| # | Column | Type | Nullable | Default | Identity |
|---:|---|---|---|---|---|
| 1 | id | int8 | NO | nextval('job_scrape_runs_id_seq'::regclass) | — |
| 2 | provider | text | NO | — | — |
| 3 | status | text | NO | 'unknown'::text | — |
| 4 | job_count | int4 | NO | 0 | — |
| 5 | error_summary | text | YES | — | — |
| 6 | trigger_source | text | YES | — | — |
| 7 | started_at | timestamptz | NO | now() | — |
| 8 | finished_at | timestamptz | YES | — | — |
| 9 | metadata | jsonb | NO | '{}'::jsonb | — |

### Constraints and indexes

- `job_scrape_runs_pkey`: `PRIMARY KEY (id)`
- `idx_job_scrape_runs_provider_started`: `CREATE INDEX idx_job_scrape_runs_provider_started ON public.job_scrape_runs USING btree (provider, started_at DESC)`
- `idx_job_scrape_runs_started`: `CREATE INDEX idx_job_scrape_runs_started ON public.job_scrape_runs USING btree (started_at DESC)`
- `job_scrape_runs_pkey`: `CREATE UNIQUE INDEX job_scrape_runs_pkey ON public.job_scrape_runs USING btree (id)`

### Access policies and grants

- `job_scrape_runs_public_read`: SELECT, roles `['anon', 'authenticated']`, PERMISSIVE; USING `true`; WITH CHECK `—`.
- Grants to `anon`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- Grants to `authenticated`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- Grants to `postgres`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- Grants to `service_role`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.

## public.jobs

Kind `r`; RLS enabled `True`; RLS forced `False`.

| # | Column | Type | Nullable | Default | Identity |
|---:|---|---|---|---|---|
| 1 | id | int8 | NO | nextval('jobs_id_seq'::regclass) | — |
| 2 | company | text | NO | — | — |
| 3 | title | text | NO | — | — |
| 4 | url | text | NO | — | — |
| 5 | location | text | YES | — | — |
| 6 | description | text | YES | — | — |
| 7 | is_active | bool | NO | true | — |
| 8 | first_seen_at | timestamptz | NO | now() | — |
| 9 | last_seen_at | timestamptz | NO | now() | — |
| 10 | scraped_at | timestamptz | NO | now() | — |
| 11 | source_payload | jsonb | NO | '{}'::jsonb | — |
| 12 | ats | text | YES | — | — |
| 13 | posted_at | text | YES | — | — |
| 14 | closed_at | text | YES | — | — |
| 15 | description_raw | text | YES | — | — |
| 16 | description_clean | text | YES | — | — |

### Constraints and indexes

- `jobs_pkey`: `PRIMARY KEY (id)`
- `idx_jobs_company`: `CREATE INDEX idx_jobs_company ON public.jobs USING btree (company)`
- `idx_jobs_company_active`: `CREATE INDEX idx_jobs_company_active ON public.jobs USING btree (company, is_active, scraped_at DESC)`
- `idx_jobs_company_url_unique`: `CREATE UNIQUE INDEX idx_jobs_company_url_unique ON public.jobs USING btree (company, url)`
- `idx_jobs_is_active`: `CREATE INDEX idx_jobs_is_active ON public.jobs USING btree (is_active)`
- `idx_jobs_posted_at`: `CREATE INDEX idx_jobs_posted_at ON public.jobs USING btree (posted_at DESC)`
- `idx_jobs_scraped_at`: `CREATE INDEX idx_jobs_scraped_at ON public.jobs USING btree (scraped_at DESC)`
- `idx_jobs_url`: `CREATE INDEX idx_jobs_url ON public.jobs USING btree (url)`
- `jobs_pkey`: `CREATE UNIQUE INDEX jobs_pkey ON public.jobs USING btree (id)`

### Access policies and grants

- `jobs_public_read`: SELECT, roles `['anon', 'authenticated']`, PERMISSIVE; USING `true`; WITH CHECK `—`.
- Grants to `anon`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- Grants to `authenticated`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- Grants to `postgres`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- Grants to `service_role`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.

## public.jobs_with_applied

Kind `v`; RLS enabled `False`; RLS forced `False`.

| # | Column | Type | Nullable | Default | Identity |
|---:|---|---|---|---|---|
| 1 | id | int8 | YES | — | — |
| 2 | company | text | YES | — | — |
| 3 | title | text | YES | — | — |
| 4 | url | text | YES | — | — |
| 5 | location | text | YES | — | — |
| 6 | description | text | YES | — | — |
| 7 | is_active | bool | YES | — | — |
| 8 | first_seen_at | timestamptz | YES | — | — |
| 9 | last_seen_at | timestamptz | YES | — | — |
| 10 | scraped_at | timestamptz | YES | — | — |
| 11 | source_payload | jsonb | YES | — | — |
| 12 | ats | text | YES | — | — |
| 13 | posted_at | text | YES | — | — |
| 14 | closed_at | text | YES | — | — |
| 15 | description_raw | text | YES | — | — |
| 16 | description_clean | text | YES | — | — |
| 17 | is_applied | bool | YES | — | — |
| 18 | applied_status | text | YES | — | — |
| 19 | applied_at | timestamptz | YES | — | — |

### Constraints and indexes


### Access policies and grants

- Grants to `anon`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- Grants to `authenticated`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- Grants to `postgres`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- Grants to `service_role`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.

### View definition

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

## public.robotics_applications

Kind `r`; RLS enabled `True`; RLS forced `False`.

| # | Column | Type | Nullable | Default | Identity |
|---:|---|---|---|---|---|
| 1 | id | int8 | NO | nextval('robotics_applications_id_seq'::regclass) | — |
| 2 | company | text | NO | — | — |
| 3 | job_url | text | NO | — | — |
| 4 | job_title | text | YES | — | — |
| 5 | status | text | NO | 'applied'::text | — |
| 6 | applied_at | timestamptz | NO | now() | — |
| 7 | updated_at | timestamptz | NO | now() | — |
| 8 | notes | text | YES | — | — |

### Constraints and indexes

- `robotics_applications_company_job_url_key`: `UNIQUE (company, job_url)`
- `robotics_applications_pkey`: `PRIMARY KEY (id)`
- `idx_robotics_applications_applied_at`: `CREATE INDEX idx_robotics_applications_applied_at ON public.robotics_applications USING btree (applied_at DESC)`
- `idx_robotics_applications_company`: `CREATE INDEX idx_robotics_applications_company ON public.robotics_applications USING btree (company)`
- `robotics_applications_company_job_url_key`: `CREATE UNIQUE INDEX robotics_applications_company_job_url_key ON public.robotics_applications USING btree (company, job_url)`
- `robotics_applications_pkey`: `CREATE UNIQUE INDEX robotics_applications_pkey ON public.robotics_applications USING btree (id)`

### Access policies and grants

- `anon delete robotics_applications`: DELETE, roles `['anon']`, PERMISSIVE; USING `true`; WITH CHECK `—`.
- `anon insert robotics_applications`: INSERT, roles `['anon']`, PERMISSIVE; USING `—`; WITH CHECK `true`.
- `anon read robotics_applications`: SELECT, roles `['anon']`, PERMISSIVE; USING `true`; WITH CHECK `—`.
- Grants to `anon`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- Grants to `authenticated`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- Grants to `postgres`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- Grants to `service_role`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.

### Trigger and function

```sql
CREATE TRIGGER trg_robotics_applications_touch BEFORE UPDATE ON public.robotics_applications FOR EACH ROW EXECUTE FUNCTION touch_robotics_updated_at();
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

## public.robotics_job_scrape_runs

Kind `r`; RLS enabled `True`; RLS forced `False`.

| # | Column | Type | Nullable | Default | Identity |
|---:|---|---|---|---|---|
| 1 | id | int8 | NO | nextval('robotics_job_scrape_runs_id_seq'::regclass) | — |
| 2 | provider | text | YES | — | — |
| 3 | status | text | YES | — | — |
| 4 | job_count | int4 | NO | 0 | — |
| 5 | trigger_source | text | YES | — | — |
| 6 | error_summary | text | YES | — | — |
| 7 | created_at | timestamptz | NO | now() | — |

### Constraints and indexes

- `robotics_job_scrape_runs_pkey`: `PRIMARY KEY (id)`
- `idx_robotics_job_scrape_runs_provider`: `CREATE INDEX idx_robotics_job_scrape_runs_provider ON public.robotics_job_scrape_runs USING btree (provider)`
- `robotics_job_scrape_runs_pkey`: `CREATE UNIQUE INDEX robotics_job_scrape_runs_pkey ON public.robotics_job_scrape_runs USING btree (id)`

### Access policies and grants

- `anon read robotics_job_scrape_runs`: SELECT, roles `['anon']`, PERMISSIVE; USING `true`; WITH CHECK `—`.
- Grants to `anon`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- Grants to `authenticated`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- Grants to `postgres`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- Grants to `service_role`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.

## public.robotics_jobs

Kind `r`; RLS enabled `True`; RLS forced `False`.

| # | Column | Type | Nullable | Default | Identity |
|---:|---|---|---|---|---|
| 1 | id | int8 | NO | nextval('robotics_jobs_id_seq'::regclass) | — |
| 2 | company | text | NO | — | — |
| 3 | title | text | NO | — | — |
| 4 | url | text | NO | — | — |
| 5 | location | text | YES | — | — |
| 6 | description | text | YES | — | — |
| 7 | is_active | bool | NO | true | — |
| 8 | last_seen_at | timestamptz | YES | — | — |
| 9 | scraped_at | timestamptz | YES | — | — |
| 10 | ats | text | YES | — | — |
| 11 | posted_at | text | YES | — | — |
| 12 | closed_at | timestamptz | YES | — | — |
| 13 | source_payload | jsonb | YES | — | — |

### Constraints and indexes

- `robotics_jobs_company_url_key`: `UNIQUE (company, url)`
- `robotics_jobs_pkey`: `PRIMARY KEY (id)`
- `idx_robotics_jobs_company`: `CREATE INDEX idx_robotics_jobs_company ON public.robotics_jobs USING btree (company)`
- `idx_robotics_jobs_is_active`: `CREATE INDEX idx_robotics_jobs_is_active ON public.robotics_jobs USING btree (is_active)`
- `idx_robotics_jobs_posted_at`: `CREATE INDEX idx_robotics_jobs_posted_at ON public.robotics_jobs USING btree (posted_at DESC)`
- `idx_robotics_jobs_url`: `CREATE INDEX idx_robotics_jobs_url ON public.robotics_jobs USING btree (url)`
- `robotics_jobs_company_url_key`: `CREATE UNIQUE INDEX robotics_jobs_company_url_key ON public.robotics_jobs USING btree (company, url)`
- `robotics_jobs_pkey`: `CREATE UNIQUE INDEX robotics_jobs_pkey ON public.robotics_jobs USING btree (id)`

### Access policies and grants

- `anon read robotics_jobs`: SELECT, roles `['anon']`, PERMISSIVE; USING `true`; WITH CHECK `—`.
- Grants to `anon`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- Grants to `authenticated`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- Grants to `postgres`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- Grants to `service_role`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.

## public.robotics_jobs_with_applied

Kind `v`; RLS enabled `False`; RLS forced `False`.

| # | Column | Type | Nullable | Default | Identity |
|---:|---|---|---|---|---|
| 1 | id | int8 | YES | — | — |
| 2 | company | text | YES | — | — |
| 3 | title | text | YES | — | — |
| 4 | url | text | YES | — | — |
| 5 | location | text | YES | — | — |
| 6 | description | text | YES | — | — |
| 7 | is_active | bool | YES | — | — |
| 8 | last_seen_at | timestamptz | YES | — | — |
| 9 | scraped_at | timestamptz | YES | — | — |
| 10 | ats | text | YES | — | — |
| 11 | posted_at | text | YES | — | — |
| 12 | closed_at | timestamptz | YES | — | — |
| 13 | source_payload | jsonb | YES | — | — |
| 14 | is_applied | bool | YES | — | — |
| 15 | applied_status | text | YES | — | — |
| 16 | applied_at | timestamptz | YES | — | — |

### Constraints and indexes


### Access policies and grants

- Grants to `anon`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- Grants to `authenticated`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- Grants to `postgres`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- Grants to `service_role`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.

### View definition

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

## public.team_applications

Kind `r`; RLS enabled `True`; RLS forced `False`.

| # | Column | Type | Nullable | Default | Identity |
|---:|---|---|---|---|---|
| 1 | id | int8 | NO | nextval('team_applications_id_seq'::regclass) | — |
| 2 | user_id | uuid | NO | auth.uid() | — |
| 3 | company | text | NO | — | — |
| 4 | job_url | text | NO | — | — |
| 5 | job_title | text | YES | — | — |
| 6 | status | text | NO | 'applied'::text | — |
| 7 | applied_at | timestamptz | NO | now() | — |
| 8 | updated_at | timestamptz | NO | now() | — |
| 9 | notes | text | YES | — | — |

### Constraints and indexes

- `team_applications_pkey`: `PRIMARY KEY (id)`
- `team_applications_user_id_company_job_url_key`: `UNIQUE (user_id, company, job_url)`
- `team_applications_user_id_fkey`: `FOREIGN KEY (user_id) REFERENCES auth.users(id)`
- `team_applications_pkey`: `CREATE UNIQUE INDEX team_applications_pkey ON public.team_applications USING btree (id)`
- `team_applications_user_id_company_job_url_key`: `CREATE UNIQUE INDEX team_applications_user_id_company_job_url_key ON public.team_applications USING btree (user_id, company, job_url)`

### Access policies and grants

- `team_applications_owner`: ALL, roles `['authenticated']`, PERMISSIVE; USING `(user_id = auth.uid())`; WITH CHECK `(user_id = auth.uid())`.
- Grants to `anon`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- Grants to `authenticated`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- Grants to `postgres`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- Grants to `service_role`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.

## public.team_job_notifications

Kind `r`; RLS enabled `True`; RLS forced `False`.

| # | Column | Type | Nullable | Default | Identity |
|---:|---|---|---|---|---|
| 1 | id | int8 | NO | nextval('team_job_notifications_id_seq'::regclass) | — |
| 2 | url | text | NO | — | — |
| 3 | status | text | NO | — | — |
| 4 | delivered_at | timestamptz | YES | — | — |

### Constraints and indexes

- `team_job_notifications_pkey`: `PRIMARY KEY (id)`
- `team_job_notifications_url_key`: `UNIQUE (url)`
- `team_job_notifications_pkey`: `CREATE UNIQUE INDEX team_job_notifications_pkey ON public.team_job_notifications USING btree (id)`
- `team_job_notifications_url_key`: `CREATE UNIQUE INDEX team_job_notifications_url_key ON public.team_job_notifications USING btree (url)`

### Access policies and grants

- Grants to `anon`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- Grants to `authenticated`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- Grants to `postgres`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- Grants to `service_role`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.

## public.team_job_observations

Kind `r`; RLS enabled `True`; RLS forced `False`.

| # | Column | Type | Nullable | Default | Identity |
|---:|---|---|---|---|---|
| 1 | id | int8 | NO | nextval('team_job_observations_id_seq'::regclass) | — |
| 2 | source_id | text | NO | — | — |
| 3 | url | text | NO | — | — |
| 4 | is_active | bool | NO | — | — |
| 5 | observed_at | timestamptz | YES | — | — |

### Constraints and indexes

- `team_job_observations_pkey`: `PRIMARY KEY (id)`
- `team_job_observations_source_id_url_key`: `UNIQUE (source_id, url)`
- `team_job_observations_pkey`: `CREATE UNIQUE INDEX team_job_observations_pkey ON public.team_job_observations USING btree (id)`
- `team_job_observations_source_id_url_key`: `CREATE UNIQUE INDEX team_job_observations_source_id_url_key ON public.team_job_observations USING btree (source_id, url)`

### Access policies and grants

- Grants to `anon`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- Grants to `authenticated`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- Grants to `postgres`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- Grants to `service_role`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.

## public.team_job_scrape_runs

Kind `r`; RLS enabled `True`; RLS forced `False`.

| # | Column | Type | Nullable | Default | Identity |
|---:|---|---|---|---|---|
| 1 | id | int8 | NO | nextval('team_job_scrape_runs_id_seq'::regclass) | — |
| 2 | run_id | uuid | NO | — | — |
| 3 | provider | text | NO | — | — |
| 4 | source | text | YES | — | — |
| 5 | platform | text | YES | — | — |
| 6 | status | text | NO | — | — |
| 7 | job_count | int4 | NO | 0 | — |
| 8 | duration_ms | int4 | YES | — | — |
| 9 | error_summary | text | YES | — | — |
| 10 | trigger_source | text | YES | — | — |
| 11 | created_at | timestamptz | NO | now() | — |

### Constraints and indexes

- `team_job_scrape_runs_pkey`: `PRIMARY KEY (id)`
- `team_job_scrape_runs_run_id_provider_key`: `UNIQUE (run_id, provider)`
- `team_job_runs_date_idx`: `CREATE INDEX team_job_runs_date_idx ON public.team_job_scrape_runs USING btree (created_at DESC)`
- `team_job_scrape_runs_pkey`: `CREATE UNIQUE INDEX team_job_scrape_runs_pkey ON public.team_job_scrape_runs USING btree (id)`
- `team_job_scrape_runs_run_id_provider_key`: `CREATE UNIQUE INDEX team_job_scrape_runs_run_id_provider_key ON public.team_job_scrape_runs USING btree (run_id, provider)`

### Access policies and grants

- `team_runs_read`: SELECT, roles `['anon', 'authenticated']`, PERMISSIVE; USING `true`; WITH CHECK `—`.
- Grants to `anon`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- Grants to `authenticated`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- Grants to `postgres`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- Grants to `service_role`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.

## public.team_job_url_aliases

Kind `r`; RLS enabled `True`; RLS forced `False`.

| # | Column | Type | Nullable | Default | Identity |
|---:|---|---|---|---|---|
| 1 | id | int8 | NO | nextval('team_job_url_aliases_id_seq'::regclass) | — |
| 2 | old_url | text | NO | — | — |
| 3 | canonical_url | text | NO | — | — |
| 4 | original_job_id | int8 | NO | — | — |
| 5 | repaired_at | timestamptz | NO | now() | — |

### Constraints and indexes

- `team_job_url_aliases_old_url_key`: `UNIQUE (old_url)`
- `team_job_url_aliases_pkey`: `PRIMARY KEY (id)`
- `team_job_url_aliases_old_url_key`: `CREATE UNIQUE INDEX team_job_url_aliases_old_url_key ON public.team_job_url_aliases USING btree (old_url)`
- `team_job_url_aliases_pkey`: `CREATE UNIQUE INDEX team_job_url_aliases_pkey ON public.team_job_url_aliases USING btree (id)`

### Access policies and grants

- `team_aliases_read`: SELECT, roles `['anon', 'authenticated']`, PERMISSIVE; USING `true`; WITH CHECK `—`.
- Grants to `anon`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- Grants to `authenticated`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- Grants to `postgres`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- Grants to `service_role`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.

## public.team_jobs

Kind `r`; RLS enabled `True`; RLS forced `False`.

| # | Column | Type | Nullable | Default | Identity |
|---:|---|---|---|---|---|
| 1 | id | int8 | NO | nextval('team_jobs_id_seq'::regclass) | — |
| 2 | league | text | NO | — | — |
| 3 | team | text | NO | — | — |
| 4 | company | text | NO | — | — |
| 5 | title | text | NO | — | — |
| 6 | url | text | NO | — | — |
| 7 | location | text | YES | — | — |
| 8 | description | text | YES | — | — |
| 9 | platform | text | YES | — | — |
| 10 | ats | text | YES | — | — |
| 11 | posted_at | text | YES | — | — |
| 12 | first_seen_at | timestamptz | NO | now() | — |
| 13 | last_seen_at | timestamptz | YES | — | — |
| 14 | scraped_at | timestamptz | YES | — | — |
| 15 | is_active | bool | NO | true | — |
| 16 | closed_at | timestamptz | YES | — | — |
| 17 | logo_url | text | YES | — | — |
| 18 | source_id | text | YES | — | — |
| 19 | salary | text | YES | — | — |
| 20 | detail_status | text | YES | — | — |
| 21 | detail_checked_at | timestamptz | YES | — | — |

### Constraints and indexes

- `team_jobs_pkey`: `PRIMARY KEY (id)`
- `team_jobs_url_key`: `UNIQUE (url)`
- `team_workday_site_required`: `CHECK ((url !~ '^https://[^/]+\.myworkdayjobs\.com/job/'::text))`
- `team_jobs_active_idx`: `CREATE INDEX team_jobs_active_idx ON public.team_jobs USING btree (is_active)`
- `team_jobs_first_idx`: `CREATE INDEX team_jobs_first_idx ON public.team_jobs USING btree (first_seen_at DESC)`
- `team_jobs_pkey`: `CREATE UNIQUE INDEX team_jobs_pkey ON public.team_jobs USING btree (id)`
- `team_jobs_url_key`: `CREATE UNIQUE INDEX team_jobs_url_key ON public.team_jobs USING btree (url)`

### Access policies and grants

- `team_jobs_read`: SELECT, roles `['anon', 'authenticated']`, PERMISSIVE; USING `true`; WITH CHECK `—`.
- Grants to `anon`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- Grants to `authenticated`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- Grants to `postgres`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- Grants to `service_role`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.

### Trigger and function

```sql
CREATE TRIGGER team_keep_first_seen BEFORE UPDATE ON public.team_jobs FOR EACH ROW EXECUTE FUNCTION team_keep_first_seen();
CREATE OR REPLACE FUNCTION public.team_keep_first_seen()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
begin new.first_seen_at=old.first_seen_at; return new; end; $function$

```

## public.team_jobs_with_applied

Kind `v`; RLS enabled `False`; RLS forced `False`.

| # | Column | Type | Nullable | Default | Identity |
|---:|---|---|---|---|---|
| 1 | id | int8 | YES | — | — |
| 2 | league | text | YES | — | — |
| 3 | team | text | YES | — | — |
| 4 | company | text | YES | — | — |
| 5 | title | text | YES | — | — |
| 6 | url | text | YES | — | — |
| 7 | location | text | YES | — | — |
| 8 | description | text | YES | — | — |
| 9 | platform | text | YES | — | — |
| 10 | ats | text | YES | — | — |
| 11 | posted_at | text | YES | — | — |
| 12 | first_seen_at | timestamptz | YES | — | — |
| 13 | last_seen_at | timestamptz | YES | — | — |
| 14 | scraped_at | timestamptz | YES | — | — |
| 15 | is_active | bool | YES | — | — |
| 16 | closed_at | timestamptz | YES | — | — |
| 17 | logo_url | text | YES | — | — |
| 18 | source_id | text | YES | — | — |
| 19 | salary | text | YES | — | — |
| 20 | detail_status | text | YES | — | — |
| 21 | detail_checked_at | timestamptz | YES | — | — |
| 22 | is_applied | bool | YES | — | — |
| 23 | applied_status | text | YES | — | — |
| 24 | applied_at | timestamptz | YES | — | — |

### Constraints and indexes


### Access policies and grants

- Grants to `anon`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- Grants to `authenticated`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- Grants to `postgres`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- Grants to `service_role`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.

### View definition

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

Kind `r`; RLS enabled `True`; RLS forced `False`.

| # | Column | Type | Nullable | Default | Identity |
|---:|---|---|---|---|---|
| 1 | id | int8 | NO | nextval('team_workday_repair_backup_id_seq'::regclass) | — |
| 2 | captured_at | timestamptz | YES | now() | — |
| 3 | table_name | text | NO | — | — |
| 4 | payload | jsonb | NO | — | — |

### Constraints and indexes

- `team_workday_repair_backup_pkey`: `PRIMARY KEY (id)`
- `team_workday_repair_backup_pkey`: `CREATE UNIQUE INDEX team_workday_repair_backup_pkey ON public.team_workday_repair_backup USING btree (id)`

### Access policies and grants

- Grants to `postgres`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- Grants to `service_role`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.

## public.tech_applications

Kind `r`; RLS enabled `True`; RLS forced `False`.

| # | Column | Type | Nullable | Default | Identity |
|---:|---|---|---|---|---|
| 1 | id | int8 | NO | nextval('tech_applications_id_seq'::regclass) | — |
| 2 | company | text | NO | — | — |
| 3 | job_url | text | NO | — | — |
| 4 | job_title | text | YES | — | — |
| 5 | status | text | NO | 'applied'::text | — |
| 6 | applied_at | timestamptz | NO | now() | — |
| 7 | updated_at | timestamptz | NO | now() | — |
| 8 | notes | text | YES | — | — |

### Constraints and indexes

- `tech_applications_company_job_url_key`: `UNIQUE (company, job_url)`
- `tech_applications_pkey`: `PRIMARY KEY (id)`
- `idx_tech_applications_applied_at`: `CREATE INDEX idx_tech_applications_applied_at ON public.tech_applications USING btree (applied_at DESC)`
- `idx_tech_applications_company`: `CREATE INDEX idx_tech_applications_company ON public.tech_applications USING btree (company)`
- `tech_applications_company_job_url_key`: `CREATE UNIQUE INDEX tech_applications_company_job_url_key ON public.tech_applications USING btree (company, job_url)`
- `tech_applications_pkey`: `CREATE UNIQUE INDEX tech_applications_pkey ON public.tech_applications USING btree (id)`

### Access policies and grants

- `anon delete tech_applications`: DELETE, roles `['anon']`, PERMISSIVE; USING `true`; WITH CHECK `—`.
- `anon insert tech_applications`: INSERT, roles `['anon']`, PERMISSIVE; USING `—`; WITH CHECK `true`.
- `anon read tech_applications`: SELECT, roles `['anon']`, PERMISSIVE; USING `true`; WITH CHECK `—`.
- Grants to `anon`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- Grants to `authenticated`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- Grants to `postgres`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- Grants to `service_role`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.

### Trigger and function

```sql
CREATE TRIGGER trg_tech_applications_touch BEFORE UPDATE ON public.tech_applications FOR EACH ROW EXECUTE FUNCTION touch_tech_updated_at();
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

## public.tech_job_scrape_runs

Kind `r`; RLS enabled `True`; RLS forced `False`.

| # | Column | Type | Nullable | Default | Identity |
|---:|---|---|---|---|---|
| 1 | id | int8 | NO | nextval('tech_job_scrape_runs_id_seq'::regclass) | — |
| 2 | provider | text | YES | — | — |
| 3 | status | text | YES | — | — |
| 4 | job_count | int4 | NO | 0 | — |
| 5 | trigger_source | text | YES | — | — |
| 6 | error_summary | text | YES | — | — |
| 7 | created_at | timestamptz | NO | now() | — |

### Constraints and indexes

- `tech_job_scrape_runs_pkey`: `PRIMARY KEY (id)`
- `idx_tech_job_scrape_runs_provider`: `CREATE INDEX idx_tech_job_scrape_runs_provider ON public.tech_job_scrape_runs USING btree (provider)`
- `tech_job_scrape_runs_pkey`: `CREATE UNIQUE INDEX tech_job_scrape_runs_pkey ON public.tech_job_scrape_runs USING btree (id)`

### Access policies and grants

- `anon read Tech_job_scrape_runs`: SELECT, roles `['anon']`, PERMISSIVE; USING `true`; WITH CHECK `—`.
- Grants to `anon`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- Grants to `authenticated`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- Grants to `postgres`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- Grants to `service_role`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.

## public.tech_jobs

Kind `r`; RLS enabled `True`; RLS forced `False`.

| # | Column | Type | Nullable | Default | Identity |
|---:|---|---|---|---|---|
| 1 | id | int8 | NO | nextval('tech_jobs_id_seq'::regclass) | — |
| 2 | company | text | NO | — | — |
| 3 | title | text | NO | — | — |
| 4 | url | text | NO | — | — |
| 5 | location | text | YES | — | — |
| 6 | description | text | YES | — | — |
| 7 | is_active | bool | NO | true | — |
| 8 | last_seen_at | timestamptz | YES | — | — |
| 9 | scraped_at | timestamptz | YES | — | — |
| 10 | ats | text | YES | — | — |
| 11 | posted_at | text | YES | — | — |
| 12 | closed_at | timestamptz | YES | — | — |
| 13 | source_payload | jsonb | YES | — | — |

### Constraints and indexes

- `tech_jobs_company_url_key`: `UNIQUE (company, url)`
- `tech_jobs_pkey`: `PRIMARY KEY (id)`
- `idx_tech_jobs_company`: `CREATE INDEX idx_tech_jobs_company ON public.tech_jobs USING btree (company)`
- `idx_tech_jobs_is_active`: `CREATE INDEX idx_tech_jobs_is_active ON public.tech_jobs USING btree (is_active)`
- `idx_tech_jobs_posted_at`: `CREATE INDEX idx_tech_jobs_posted_at ON public.tech_jobs USING btree (posted_at DESC)`
- `idx_tech_jobs_url`: `CREATE INDEX idx_tech_jobs_url ON public.tech_jobs USING btree (url)`
- `tech_jobs_company_url_key`: `CREATE UNIQUE INDEX tech_jobs_company_url_key ON public.tech_jobs USING btree (company, url)`
- `tech_jobs_pkey`: `CREATE UNIQUE INDEX tech_jobs_pkey ON public.tech_jobs USING btree (id)`

### Access policies and grants

- `anon read tech_jobs`: SELECT, roles `['anon']`, PERMISSIVE; USING `true`; WITH CHECK `—`.
- Grants to `anon`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- Grants to `authenticated`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- Grants to `postgres`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- Grants to `service_role`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.

## public.tech_jobs_with_applied

Kind `v`; RLS enabled `False`; RLS forced `False`.

| # | Column | Type | Nullable | Default | Identity |
|---:|---|---|---|---|---|
| 1 | id | int8 | YES | — | — |
| 2 | company | text | YES | — | — |
| 3 | title | text | YES | — | — |
| 4 | url | text | YES | — | — |
| 5 | location | text | YES | — | — |
| 6 | description | text | YES | — | — |
| 7 | is_active | bool | YES | — | — |
| 8 | last_seen_at | timestamptz | YES | — | — |
| 9 | scraped_at | timestamptz | YES | — | — |
| 10 | ats | text | YES | — | — |
| 11 | posted_at | text | YES | — | — |
| 12 | closed_at | timestamptz | YES | — | — |
| 13 | source_payload | jsonb | YES | — | — |
| 14 | is_applied | bool | YES | — | — |
| 15 | applied_status | text | YES | — | — |
| 16 | applied_at | timestamptz | YES | — | — |

### Constraints and indexes


### Access policies and grants

- Grants to `anon`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- Grants to `authenticated`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- Grants to `postgres`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.
- Grants to `service_role`: DELETE, INSERT, REFERENCES, SELECT, TRIGGER, TRUNCATE, UPDATE.

### View definition

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

## Local SQLite files

These are retained operator cache/seed files. Production teams use Supabase. [SQLite schema metadata](sqlite_catalog.json).

- `D:\abet_ops\sports_teams\data\team_jobs.db`: 3,706,880 bytes; 5 schema objects. local historical/cache or migration seed; not the production scheduler database.
- `D:\abet_ops\sports_teams\data\cloud_seed.db`: 1,941,504 bytes; 5 schema objects. local historical/cache or migration seed; not the production scheduler database.
