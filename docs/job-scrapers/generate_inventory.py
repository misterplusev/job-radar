"""Bounded, read-only source inventory. Owner: ABET jobs documentation.

Reads Git objects and explicit operator directories; never imports scraper code.
Optional network GETs use existing gh/HF/Cloudflare authentication. No secrets or
source contents are written to the inventory. Output is metadata and symbol maps.
"""
import ast,base64,hashlib,io,json,re,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import quote

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'inventory';OUT.mkdir(exist_ok=True)
GH=r'C:\Program Files\GitHub CLI\gh.exe'
CODE={'.py','.js','.jsx','.mjs','.cjs','.ts','.tsx','.sql','.sh','.bash','.ps1','.bat','.cmd','.html','.css','.yml','.yaml','.toml','.ini','.json','.md','.txt'}
SENSITIVE=re.compile(r'(^|/)(\.env(?:\.|$)|.*secret.*|.*credential.*|.*skills_matrix.*|.*resume.*|.*cover_letter.*)',re.I)
GENERATED=('node_modules/','dist/','.git/','data/','public/data/','out/','proof/','proofs/','logs/','backups/','_backups/','docs/job-scrapers/inventory/')
def command(args,**kwargs):
 p=subprocess.run(args,capture_output=True,timeout=120,**kwargs)
 if p.returncode:raise RuntimeError('Read operation failed: '+str(args[:3]))
 return p.stdout
def gh(path):return json.loads(command([GH,'api',path],text=True,encoding='utf-8'))
def category(path):
 lower=path.lower()
 if SENSITIVE.search(path):return 'sensitive/private content; metadata only'
 if any(part in lower.split('/') for part in ['archive','archived','backups','_backups']):return 'historical/backup'
 if path.startswith('.github/workflows/'):return 'workflow'
 if Path(path).suffix.lower()=='.sql':return 'database schema/migration'
 if '/test' in lower or lower.startswith(('test','scripts/verify','scripts/proof')):return 'test/verification'
 if any(x in lower for x in ['provider','scrape','ingest','live_refresh']):return 'source ingestion'
 if any(x in lower for x in ['publish','notify','notification']):return 'publication/delivery'
 if any(x in lower for x in ['deploy','launcher','runtime','worker','wrangler']):return 'runtime/deployment'
 if any(x in lower for x in ['schema','storage','database','migration']):return 'storage'
 if lower.startswith(('src/','app/','board/','api/','embeds/')) or Path(lower).suffix in {'.html','.css'}:return 'frontend/API'
 if Path(lower).suffix=='.md':return 'documentation'
 if Path(lower).suffix in {'.json','.toml','.ini','.yml','.yaml','.txt'}:return 'configuration/data'
 return 'support/module'
def eligible(path,size):
 if SENSITIVE.search(path):return False
 if any(path.startswith(x) for x in GENERATED):return False
 if Path(path).suffix.lower() not in CODE and Path(path).name not in {'Dockerfile','Procfile','Makefile','.gitignore','.gitattributes'}:return False
 return size<=8_000_000
def details(row,raw):
 text=raw.decode('utf-8-sig',errors='replace');lines=text.splitlines()
 row.update(sha256=hashlib.sha256(raw).hexdigest(),lines=len(lines),nonblank_lines=sum(bool(x.strip()) for x in lines),symbols=[],imports=[])
 if row['path'].endswith('.py'):
  try:
   tree=ast.parse(text);doc=ast.get_docstring(tree)
   if doc:row['purpose']=doc.split('\n\n')[0][:350]
   def walk(node,prefix=''):
    for n in ast.iter_child_nodes(node):
     if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):
      name=prefix+n.name;row['symbols'].append({'name':name,'kind':type(n).__name__,'line':n.lineno,'end_line':n.end_lineno});walk(n,name+'.')
     elif isinstance(n,(ast.Import,ast.ImportFrom)):
      row['imports'].append(n.module if isinstance(n,ast.ImportFrom) else ', '.join(a.name for a in n.names))
     else:walk(n,prefix)
   walk(tree)
  except SyntaxError as e:row['parse_note']=f'Python AST unavailable at line {e.lineno}; physical counts remain valid'
 elif Path(row['path']).suffix in {'.js','.jsx','.mjs','.cjs','.ts','.tsx'}:
  for i,line in enumerate(lines,1):
   m=re.match(r'\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?(?:function|class)\s+([\w$]+)',line)
   if not m:m=re.match(r'\s*(?:export\s+)?(?:const|let)\s+([\w$]+)\s*=\s*(?:async\s*)?(?:\([^)]*\)|[\w$]+)\s*=>',line)
   if m:row['symbols'].append({'name':m[1],'kind':'JS declaration (text scan)','line':i})
  row['imports']=sorted(set(re.findall(r'(?:from\s+|import\s*)[\"\x27]([^\"\x27]+)',text)))
 elif row['path'].endswith('.sql'):
  row['symbols']=[{'name':m[2],'kind':m[1].lower(),'line':text[:m.start()].count('\n')+1} for m in re.finditer(r'(?im)^\s*create\s+(?:or\s+replace\s+)?(table|view|function|index|policy|trigger)\s+(?:if\s+not\s+exists\s+)?([^\s(]+)',text)]
 if row['path'].startswith('.github/workflows/'):
  row['workflow']={'crons':re.findall(r'cron:\s*[\"\x27]([^\"\x27]+)',text),'step_names':re.findall(r'^\s*-?\s*name:\s*(.+)',text,re.M),'run_lines':[{'line':i,'text':x.strip()} for i,x in enumerate(lines,1) if re.match(r'\s*run:',x)],'timeouts':re.findall(r'timeout-minutes:\s*(\d+)',text)}
 if not row.get('purpose'):row['purpose']=category(row['path'])+'; inspect linked source and symbol map for exact behavior'
 return row

def git_inventory(id,repo,folder,ref):
 sha=command(['git','-C',folder,'rev-parse',ref],text=True).strip()
 listing=command(['git','-C',folder,'ls-tree','-r','-l',sha],text=True,encoding='utf-8')
 rows=[];selected=[]
 for line in listing.splitlines():
  meta,path=line.split('\t',1);parts=meta.split()
  if parts[1]!='blob':continue
  row={'source':id,'repo':repo,'revision':sha,'path':path,'local_path':str(Path(folder)/path),'git_blob':parts[2],'bytes':int(parts[3]),'category':category(path),'lines':None,'url':f'https://github.com/{repo}/blob/{sha}/{quote(path)}'}
  rows.append(row)
  if eligible(path,row['bytes']):selected.append(row)
  else:row['count_note']='Metadata only: generated/dataset/binary/private/non-source artifact'
 assert sum(x['bytes'] for x in selected)<150_000_000,'Source read budget exceeded'
 payload=''.join(x['git_blob']+'\n' for x in selected).encode()
 data=io.BytesIO(command(['git','-C',folder,'cat-file','--batch'],input=payload))
 for row in selected:
  header=data.readline().decode().split();size=int(header[2]);raw=data.read(size);data.read(1);details(row,raw)
 local_head=command(['git','-C',folder,'rev-parse','HEAD'],text=True).strip()
 local_status=command(['git','-C',folder,'status','--short'],text=True,encoding='utf-8').splitlines()
 return {'id':id,'repo':repo,'revision':sha,'ref':ref,'local_root':folder,'local_checkout_head':local_head,'local_worktree_status':local_status,'files':rows}

def remote_inventory(id,repo,ref):
 tree=gh(f'repos/{repo}/git/trees/{ref}?recursive=1');assert not tree.get('truncated')
 sha=gh(f'repos/{repo}/commits/{ref}')['sha'];rows=[]
 for entry in tree['tree']:
  if entry['type']!='blob':continue
  path=entry['path'];row={'source':id,'repo':repo,'revision':sha,'path':path,'local_path':None,'git_blob':entry['sha'],'bytes':entry.get('size',0),'category':category(path),'lines':None,'url':f'https://github.com/{repo}/blob/{sha}/{quote(path)}'}
  if eligible(path,row['bytes']):details(row,base64.b64decode(gh(f'repos/{repo}/git/blobs/{entry["sha"]}')['content']))
  else:row['count_note']='Metadata only: binary/generated/private artifact'
  rows.append(row)
 return {'id':id,'repo':repo,'revision':sha,'ref':ref,'files':rows}

def local_helpers():
 folder=Path(r'D:\abet_ops\sports_teams');rows=[]
 for path in sorted(folder.rglob('*')):
  relative=path.relative_to(folder).as_posix()
  if not path.is_file() or path.suffix not in {'.py','.sql','.yml','.yaml','.toml','.mjs'} or any(x in path.parts for x in ['__pycache__','data','backups','.git']):continue
  row={'source':'teams-operator-helpers','path':relative,'local_path':str(path),'bytes':path.stat().st_size,'category':category(relative),'revision':'local working copy','lines':None}
  details(row,path.read_bytes());rows.append(row)
 return {'id':'teams-operator-helpers','local_root':str(folder),'revision':'local working copy; may include retired operators','files':rows}

def write(sources):
 report={'generated_at':datetime.now(timezone.utc).isoformat(),'scope':'All tracked files in listed source snapshots; source text line counts and symbol locations; operator helper overlay. Generated datasets/binaries/private files are metadata only. Dashboard repository inventory includes unrelated modules but deployment dependency map isolates jobs.','line_definition':'Physical newline-delimited lines and nonblank physical lines, including comments. Python symbols use AST ranges; JavaScript declarations use a text scan, not a complete call graph. No source or credential values are copied.','sources':sources}
 OUT.joinpath('source_inventory.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
 overview=['# Source inventory — November 10, 2026','',report['scope'],'',report['line_definition'],'','Generated by `generate_inventory.py`. Counts are pinned to the revisions below. Local dirty work is separate from deployed source. Branch/runtime copies are separate entries: aggregate counts are not deduplicated unique code.','', '[Live database dictionary](DATABASE.md) · [PostgreSQL catalog](database_catalog.json) · [SQLite catalog](sqlite_catalog.json) · [Full machine inventory](source_inventory.json)','', '| Source | Revision | Files | Counted text files | Physical lines | Detail |','|---|---|---:|---:|---:|---|']
 for source in sources:
  rows=source['files'];counted=[r for r in rows if r.get('lines') is not None];name=source['id']+'.md'
  overview.append(f"| {source['id']} | `{source['revision']}` | {len(rows)} | {len(counted)} | {sum(r['lines'] for r in counted):,} | [Files and symbols]({name}) |")
  lines=[f"# {source['id']} — file and symbol inventory",'',f"Revision: `{source['revision']}`. Root: `{source.get('local_root') or source.get('repo')}`.",'']
  for key in ['inspection_status','versioned_source','configured_cron','limitation']:
   if source.get(key):lines.extend([f"{key}: {source[key]}",''])
  lines += ['| File | Physical lines | Nonblank | Bytes | Category |','|---|---:|---:|---:|---|']
  for r in rows:
   label='['+r['path'].replace('|','\\|')+']('+r['url']+')' if r.get('url') else '`'+r['path']+'`'
   lines.append(f"| {label} | {r.get('lines') if r.get('lines') is not None else '—'} | {r.get('nonblank_lines','—')} | {r['bytes']} | {r['category']} |")
  lines+=['','## Script definitions and dependencies','']
  for r in rows:
   if not r.get('symbols') and not r.get('workflow'):continue
   lines += ['### '+r['path'],'',r['purpose'].replace('\n',' '),'',f"Location: `{r.get('local_path') or r.get('url')}`.",'']
   if r.get('imports'):lines+=['Imports: '+', '.join('`'+str(v)+'`' for v in r['imports'])+'.','']
   if r.get('workflow'):lines+=['Workflow metadata: `'+json.dumps(r['workflow'],ensure_ascii=False)+'`','']
   for s in r.get('symbols',[]):
    loc=f"{s['line']}"+(f"–{s['end_line']}" if s.get('end_line') else '')
    target=r.get('url','')+f"#L{s['line']}" if r.get('url') else ''
    lines.append(f"- `{s['name']}` ({s['kind']}), "+(f'[line {loc}]({target})' if target else f'line {loc}'))
   lines.append('')
  OUT.joinpath(name).write_text('\n'.join(lines)+'\n',encoding='utf-8')
 OUT.joinpath('README.md').write_text('\n'.join(overview)+'\n',encoding='utf-8')
 print('Inventory:',sum(len(s['files']) for s in sources),'files;',sum(r.get('lines') or 0 for s in sources for r in s['files']),'physical lines',flush=True)

def main():
 prior_path=OUT/'source_inventory.json'
 prior=json.loads(prior_path.read_text(encoding='utf-8')) if prior_path.exists() else {}
 sources=[]
 configurations=[('robotics-and-teams','misterplusev/job-radar',r'D:\abet\job-radar','origin/master'),('tech','misterplusev/job-radar-tech',r'D:\abet\job-radar-tech','origin/master'),('sportsbook-runtime','misterplusev/sportsbook-jobs-dashboard',r'D:\abet\sportsbook-jobs-runtime','origin/prod/sportsbook-jobs'),('sportsbook-frontend','misterplusev/sportsbook-jobs-dashboard',r'D:\abet\sportsbook-jobs-runtime','origin/main'),('abet-dashboard','misterplusev/abet-mlb-monitor-widgets',r'D:\abet_ops\abet-dashboard','origin/main')]
 for args in configurations:
  source=git_inventory(*args);sources.append(source);print(source['id'],len(source['files']),flush=True)
 for id,repo in [('robotics-standalone','misterplusev/robotics-jobradar-board'),('tech-standalone','misterplusev/jobradar-tech-board')]:
  source=remote_inventory(id,repo,'main');sources.append(source);print(id,len(source['files']),flush=True)
 sources.append(local_helpers())
 # Preserve separately inspected cloud/runtime snapshots. This local/GitHub
 # generator must not silently discard those entries or imply it refreshed them.
 refreshed={s['id'] for s in sources}
 for source in prior.get('sources',[]):
  if source['id'] not in refreshed:
   source['retained_snapshot_at']=source.get('retained_snapshot_at',prior.get('generated_at'))
   sources.append(source)
   print('Retained separate snapshot:',source['id'],source['retained_snapshot_at'],flush=True)
 write(sources)

if __name__=='__main__':main()
