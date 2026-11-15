"""Render already-exported cloud metadata into documentation; no database calls."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent
d = json.loads((ROOT/'public_database_catalog.json').read_text(encoding='utf-8-sig'))
def esc(v):
    return str(v if v is not None else '—').replace('|', '\\|').replace('\n', ' ')
lines = ['# Public database dictionary — November 14, 2026 Pacific', '',
    f"Metadata read from the cloud at `{d['exported_at']}`. Project `abet-app-core` / `alxgteasytezekyunyjk`. No job or applicant records were exported; no database data/schema was changed.", '',
    f"{len(d['relations'])} relations, {len(d['columns'])} columns, {len(d['constraints'])} constraints, {len(d['indexes'])} indexes, {len(d['policies'])} RLS policies, {len(d['grants'])} relation ACL entries, {len(d['triggers'])} triggers, {len(d['functions'])} public functions and {len(d['sequences'])} sequences.", '',
    '[Raw catalog](public_database_catalog.json) · [Exact SELECT](export_public_catalog.sql)', '',
    'Scope is the entire public schema, including non-job legacy tables. Supabase-managed auth/storage schemas and other projects are not presented as exhaustively documented here. Grants are decoded from pg_class ACLs (or PostgreSQL owner defaults); they are not filtered by the metadata caller’s role. They do not alone prove effective access through RLS or inherited roles. Row counts, job data and credential values are excluded.', '',
    'The four jobs tables retain inactive records. Application tables are separate from the user’s external job-hunt tracker. `sportsbook_job_notifications` is a live delivery ledger; descriptions of it as unused in older documents are historical. The eight November 14 read indexes are included in this snapshot.', '',
    '## Relations', '', '| Relation | Kind | Owner | RLS |', '|---|---|---|---|']
for r in d['relations']:
    lines.append(f"| `{r['name']}` | {r['relkind']} | `{r['owner']}` | {r['rls_enabled']} |")
for r in d['relations']:
    n=r['name']; lines += ['', f'## public.{n}', '', '| Column | Type | Nullable | Default | Identity |', '|---|---|---|---|---|']
    for c in d['columns']:
        if c['table_name']==n: lines.append('| '+' | '.join(esc(c[k]) for k in ['column_name','udt_name','is_nullable','column_default','identity_generation'])+' |')
    for title, key, match, name, definition in [('Constraints','constraints','table','name','definition'),('Indexes','indexes','tablename','indexname','indexdef')]:
        lines += ['', '### '+title, '']
        for obj in d[key]:
            if obj[match]==n: lines.append(f"- `{obj[name]}`: `{esc(obj[definition])}`")
    lines += ['', '### Policies and grants', '']
    for p in d['policies']:
        if p['tablename']==n: lines.append(f"- `{p['policyname']}`: {p['cmd']} / {p['roles']} / {p['permissive']}; USING `{esc(p['qual'])}`; CHECK `{esc(p['with_check'])}`.")
    for who in sorted({g['grantee'] for g in d['grants'] if g['table_name']==n}):
        grants=[g for g in d['grants'] if g['table_name']==n and g['grantee']==who]
        lines.append(f"- `{who}`: "+', '.join(g['privilege_type']+(' WITH GRANT OPTION' if g['is_grantable'] else '') for g in grants)+'.')
    for v in d['views']:
        if v['name']==n: lines += ['', '### View SQL', '', '```sql', v['definition'], '```']
    for t in d['triggers']:
        if t['table']==n: lines += ['', '### Trigger SQL', '', '```sql', t['definition']+';', '```']
lines += ['', '## Public functions', '']
for f in d['functions']:
    lines += [f"### {f['name']}({f['arguments']})", '', f"Security definer: `{f['security_definer']}`. Config: `{f['config']}`. ACL: `{f['acl']}`.", '', '```sql', f['definition'], '```', '']
lines += ['## Sequences', '', '| Name | Owner | Type | Increment | Cycle |', '|---|---|---|---|---|']
for s in d['sequences']: lines.append('| '+' | '.join(esc(s[k]) for k in ['sequencename','sequenceowner','data_type','increment_by','cycle'])+' |')
lines += ['', '## Extensions', '', '| Name | Version | Schema |', '|---|---|---|']
for e in d['extensions']: lines.append('| '+' | '.join(esc(e[k]) for k in ['name','version','schema'])+' |')
(ROOT/'DATABASE.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
print('Rendered metadata dictionary:', len(lines), 'lines')
