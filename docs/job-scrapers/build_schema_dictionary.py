"""Read a catalog artifact and local SQLite metadata; produce no job/applicant rows."""
import argparse,json,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'inventory'
def cell(value):return str(value if value is not None else '—').replace('|','\\|').replace('\n',' ')
def main():
 parser=argparse.ArgumentParser()
 parser.add_argument('--catalog',type=Path,default=ROOT/'audit_20261110/job_schema_catalog.json')
 parser.add_argument('--run-id',default='42879922731')
 args=parser.parse_args()
 d=json.loads(args.catalog.read_text(encoding='utf-8'))
 OUT.joinpath('database_catalog.json').write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
 lines=['# Live job database dictionary — November 10, 2026','',f"Read-only PostgreSQL catalog export at `{d['exported_at']}`. Project `alxgteasytezekyunyjk`, schema `public`. No job or applicant rows were exported.",'',f"{len(d['relations'])} tables/views; {len(d['columns'])} columns; {len(d['constraints'])} constraints; {len(d['indexes'])} indexes; {len(d['policies'])} RLS policies; {len(d['triggers'])} triggers; {len(d['grants'])} grants.",'','SQL: [export_job_schema.sql](../export_job_schema.sql). Evidence: [read-only workflow run](https://github.com/misterplusev/job-radar/actions/runs/42879922731). Raw structure: [database_catalog.json](database_catalog.json).','',
 'Important observed differences: `robotics_jobs` and `tech_jobs` currently have no `first_seen_at` column despite local migration files. Their source-run timestamps are `created_at`; sportsbook run timestamps are `started_at`. Do not query guessed common columns. Policies below describe deployed access, not recommended defaults for a new module.','']
 for rel in d['relations']:
  name=rel['name'];lines += [f'## public.{name}','',f"Kind `{rel['relkind']}`; RLS enabled `{rel['rls_enabled']}`; RLS forced `{rel['rls_forced']}`.",'','| # | Column | Type | Nullable | Default | Identity |','|---:|---|---|---|---|---|']
  for col in d['columns']:
   if col['table_name']==name:lines.append('| '+' | '.join(cell(col[k]) for k in ['ordinal_position','column_name','udt_name','is_nullable','column_default','identity_generation'])+' |')
  lines+=['','### Constraints and indexes','']
  for c in d['constraints']:
   if c['table']==name:lines.append(f"- `{c['name']}`: `{cell(c['definition'])}`")
  for i in d['indexes']:
   if i['tablename']==name:lines.append(f"- `{i['indexname']}`: `{cell(i['indexdef'])}`")
  lines+=['','### Access policies and grants','']
  for p in d['policies']:
   if p['tablename']==name:lines.append(f"- `{p['policyname']}`: {p['cmd']}, roles `{p['roles']}`, {p['permissive']}; USING `{cell(p['qual'])}`; WITH CHECK `{cell(p['with_check'])}`.")
  grantees=sorted({g['grantee'] for g in d['grants'] if g['table_name']==name})
  for who in grantees:lines.append(f"- Grants to `{who}`: "+', '.join(g['privilege_type'] for g in d['grants'] if g['table_name']==name and g['grantee']==who)+'.')
  for v in d['views']:
   if v['name']==name:lines+=['','### View definition','','```sql',v['definition'],'```']
  for t in d['triggers']:
   if t['table']==name:lines+=['','### Trigger and function','','```sql',t['definition']+';',t['function_definition'],'```']
  lines.append('')
 local=[]
 for name in ['team_jobs.db','cloud_seed.db']:
  p=Path(r'D:\abet_ops\sports_teams\data')/name
  with sqlite3.connect(p.as_uri()+'?mode=ro',uri=True) as db:
   objects=[{'type':r[0],'name':r[1],'table':r[2],'definition':r[3]} for r in db.execute("SELECT type,name,tbl_name,sql FROM sqlite_master WHERE name NOT LIKE 'sqlite_%' ORDER BY type,name")]
  local.append({'path':str(p),'bytes':p.stat().st_size,'role':'local historical/cache or migration seed; not the production scheduler database','objects':objects})
 lines+=['## Local SQLite files','', 'These are retained operator cache/seed files. Production teams use Supabase. [SQLite schema metadata](sqlite_catalog.json).','']
 for item in local:lines.append(f"- `{item['path']}`: {item['bytes']:,} bytes; {len(item['objects'])} schema objects. {item['role']}.")
 OUT.joinpath('sqlite_catalog.json').write_text(json.dumps(local,indent=2)+'\n',encoding='utf-8')
 OUT.joinpath('DATABASE.md').write_text(('\n'.join(lines)+'\n').replace('/actions/runs/42879922731','/actions/runs/'+args.run_id),encoding='utf-8')
 print('Database dictionary written:',len(d['relations']),'relations; local SQLite metadata:',len(local))
if __name__=='__main__':main()
