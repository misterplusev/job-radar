"""Validate the repair against the production table definition in disposable cloud PostgreSQL."""
import base64
import json
import os
from pathlib import Path
import subprocess

if os.environ.get('GITHUB_ACTIONS') != 'true':
    raise SystemExit('GitHub-hosted development only')
root = Path(__file__).resolve().parents[3]
def execute(sql):
    return subprocess.check_output(['psql', '-XqAt', '-h', '127.0.0.1', '-U', 'proof', '-d', 'proof',
                                    '-v', 'ON_ERROR_STOP=1', '-c', sql], text=True).splitlines()

def encode(rows):
    return base64.b64encode(json.dumps(rows).encode()).decode()

rows = json.loads((Path(__file__).with_name('input.json')).read_text())
assert len(rows) == 34
controls = [{**rows[0], 'id': -n, 'url': 'https://fixture.invalid/'+str(n)} for n in range(1,5)]
batch = rows + controls
recordset = "jsonb_to_recordset(convert_from(decode('"+encode(batch)+"','base64'),'UTF8')::jsonb)"
execute("insert into team_jobs(id,url,title,team,company,description,detail_status,detail_checked_at,league,platform) "
        "select x.id,x.url,x.title,x.team,x.company,x.description,x.detail_status,x.detail_checked_at,'test','teamworkonline' from "+recordset+
        " as x(id bigint,url text,title text,team text,company text,description text,detail_status text,detail_checked_at timestamptz)")
execute("update team_jobs set description='An independently verified employer description that arrived after the snapshot.' where id=-1")
execute("update team_jobs set is_active=false where id=-2")
execute("update team_jobs set platform='workday' where id=-3")
execute("update team_jobs set title='Another job title' where id=-4")
execute("insert into team_job_notifications(url,status,delivered_at) select url,'delivered',now() from team_jobs limit 1")
def state():
    rows=execute("select json_build_object('id',id,'data',to_jsonb(t)) from team_jobs t order by id")
    return {x['id']:x['data'] for x in map(json.loads,rows)}
before=state()
ledger=execute("select row_to_json(t) from team_job_notifications t")
sql=(root/'sports_teams/db/repair_teamwork_labels.sql').read_text().replace('__REVIEWED_ROWS_BASE64__',encode(batch))
changed=execute(sql)
after=state()
ids={v['id'] for v in rows}
assert {int(x.split('|',1)[0]) for x in changed}==ids
for key,row in before.items():
    expected={**row,'description':''} if key in ids else row
    assert after[key]==expected,key
assert execute(sql)==[] and state()==after
assert execute("select row_to_json(t) from team_job_notifications t")==ledger
proof={'target_rows':len(ids),'changed':len(changed),'other_columns_identical':True,
       'closed_changed_title_changed_body_other_platform_preserved':True,'replay_changes':0,'ledger_unchanged':True}
out=Path('proof');out.mkdir(exist_ok=True)
(out/'labels.json').write_text(json.dumps(proof,indent=2)+'\n')
print(json.dumps(proof))
