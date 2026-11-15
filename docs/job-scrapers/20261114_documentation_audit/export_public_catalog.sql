-- Documentation-only SELECT. No job/applicant rows, data changes or schema changes.
WITH relations AS (
 SELECT c.oid,n.nspname AS schema,c.relname AS name,c.relkind,pg_get_userbyid(c.relowner) AS owner,
        c.relrowsecurity AS rls_enabled,c.relforcerowsecurity AS rls_forced,
        obj_description(c.oid,'pg_class') AS description
 FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
 WHERE n.nspname='public' AND c.relkind IN ('r','v','m','p')
)
SELECT jsonb_build_object(
 'exported_at',now(),'database',current_database(),'schema','public',
 'scope','All public relation and function metadata; no table contents; internal auth/storage schemas excluded',
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
   (SELECT r.name AS table_name,CASE WHEN a.grantee=0 THEN 'PUBLIC' ELSE pg_get_userbyid(a.grantee) END AS grantee,
           pg_get_userbyid(a.grantor) AS grantor,a.privilege_type,a.is_grantable
    FROM relations r JOIN pg_class c ON c.oid=r.oid
    CROSS JOIN LATERAL aclexplode(coalesce(c.relacl,acldefault('r',c.relowner))) a) x),
 'views',(SELECT coalesce(jsonb_agg(jsonb_build_object('name',r.name,'definition',pg_get_viewdef(r.oid,true)) ORDER BY r.name),'[]') FROM relations r WHERE r.relkind IN ('v','m')),
 'triggers',(SELECT coalesce(jsonb_agg(jsonb_build_object('table',r.name,'name',t.tgname,'definition',pg_get_triggerdef(t.oid),'function',p.proname,'function_definition',pg_get_functiondef(p.oid)) ORDER BY r.name,t.tgname),'[]')
   FROM pg_trigger t JOIN relations r ON r.oid=t.tgrelid JOIN pg_proc p ON p.oid=t.tgfoid WHERE NOT t.tgisinternal),
 'functions',(SELECT coalesce(jsonb_agg(jsonb_build_object('name',p.proname,'arguments',pg_get_function_identity_arguments(p.oid),'definition',pg_get_functiondef(p.oid),'security_definer',p.prosecdef,'config',p.proconfig,'acl',p.proacl) ORDER BY p.proname),'[]')
   FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='public' AND p.prokind IN ('f','p')),
 'sequences',(SELECT coalesce(jsonb_agg(to_jsonb(s) ORDER BY s.sequencename),'[]') FROM
   (SELECT schemaname,sequencename,sequenceowner,data_type,start_value,min_value,max_value,increment_by,cycle,cache_size FROM pg_sequences WHERE schemaname='public') s),
 'extensions',(SELECT coalesce(jsonb_agg(jsonb_build_object('name',e.extname,'version',e.extversion,'schema',n.nspname) ORDER BY e.extname),'[]') FROM pg_extension e JOIN pg_namespace n ON n.oid=e.extnamespace)
) AS catalog;
