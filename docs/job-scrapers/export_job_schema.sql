-- Read-only catalog export. No job rows, applicant records or credentials.
WITH relations AS (
 SELECT c.oid,n.nspname AS schema,c.relname AS name,c.relkind,c.relrowsecurity AS rls_enabled,c.relforcerowsecurity AS rls_forced,
        obj_description(c.oid,'pg_class') AS description
 FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
 WHERE n.nspname='public' AND c.relkind IN ('r','v','m','p')
 AND (c.relname IN ('jobs','job_scrape_runs','applications','jobs_with_applied')
      OR c.relname LIKE 'robotics\_%' ESCAPE '\' OR c.relname LIKE 'tech\_%' ESCAPE '\' OR c.relname LIKE 'team\_%' ESCAPE '\')
)
SELECT jsonb_build_object(
 'exported_at',now(),'database',current_database(),'schema','public',
 'relations',(SELECT coalesce(jsonb_agg(to_jsonb(r) ORDER BY r.name),'[]') FROM relations r),
 'columns',(SELECT coalesce(jsonb_agg(to_jsonb(x) ORDER BY x.table_name,x.ordinal_position),'[]') FROM
   (SELECT table_name,column_name,ordinal_position,data_type,udt_name,is_nullable,column_default,is_identity,identity_generation
    FROM information_schema.columns WHERE table_schema='public' AND table_name IN (SELECT name FROM relations)) x),
 'constraints',(SELECT coalesce(jsonb_agg(jsonb_build_object('table',r.name,'name',c.conname,'type',c.contype,'definition',pg_get_constraintdef(c.oid)) ORDER BY r.name,c.conname),'[]')
   FROM pg_constraint c JOIN relations r ON r.oid=c.conrelid),
 'indexes',(SELECT coalesce(jsonb_agg(to_jsonb(x) ORDER BY x.tablename,x.indexname),'[]') FROM
   (SELECT schemaname,tablename,indexname,indexdef FROM pg_indexes WHERE schemaname='public' AND tablename IN (SELECT name FROM relations)) x),
 'policies',(SELECT coalesce(jsonb_agg(to_jsonb(x) ORDER BY x.tablename,x.policyname),'[]') FROM
   (SELECT schemaname,tablename,policyname,permissive,roles,cmd,qual,with_check FROM pg_policies WHERE schemaname='public' AND tablename IN (SELECT name FROM relations)) x),
 'grants',(SELECT coalesce(jsonb_agg(to_jsonb(x) ORDER BY x.table_name,x.grantee,x.privilege_type),'[]') FROM
   (SELECT table_name,grantee,privilege_type,is_grantable FROM information_schema.role_table_grants WHERE table_schema='public' AND table_name IN (SELECT name FROM relations)) x),
 'views',(SELECT coalesce(jsonb_agg(jsonb_build_object('name',r.name,'definition',pg_get_viewdef(r.oid,true)) ORDER BY r.name),'[]') FROM relations r WHERE r.relkind IN ('v','m')),
 'triggers',(SELECT coalesce(jsonb_agg(jsonb_build_object('table',r.name,'name',t.tgname,'definition',pg_get_triggerdef(t.oid),'function',p.proname,'function_definition',pg_get_functiondef(p.oid)) ORDER BY r.name,t.tgname),'[]')
   FROM pg_trigger t JOIN relations r ON r.oid=t.tgrelid JOIN pg_proc p ON p.oid=t.tgfoid WHERE NOT t.tgisinternal)
) AS catalog;
