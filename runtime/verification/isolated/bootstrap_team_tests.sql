-- Supabase-managed objects for the disposable PostgreSQL service on a hosted development runner.
CREATE SCHEMA auth;
CREATE TABLE auth.users(id uuid PRIMARY KEY);
CREATE FUNCTION auth.uid() RETURNS uuid LANGUAGE sql STABLE AS 'SELECT NULL::uuid';
CREATE TABLE public.team_job_url_aliases(id bigserial PRIMARY KEY, old_url text UNIQUE, canonical_url text NOT NULL);
