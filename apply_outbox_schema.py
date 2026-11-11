import hashlib,json,os
from pathlib import Path
import requests
assert os.environ['SUPABASE_PROJECT_REF']=='alxgteasytezekyunyjk'
base='https://api.supabase.com/v1/projects/alxgteasytezekyunyjk/database/query'
headers={'Authorization':'Bearer '+os.environ['SUPABASE_ACCESS_TOKEN']}
receipt=[]
for file in ['migration.sql','integration.sql']:
    sql=Path(file).read_text()
    if file=='migration.sql':sql='begin;\n'+sql+'\ncommit;'
    response=requests.post(base,headers=headers,json={'query':sql},timeout=90)
    if not response.ok:
        print('SQL request failed:',response.status_code,response.text[:1000]);raise SystemExit(1)
    receipt.append({'file':file,'sha256':hashlib.sha256(Path(file).read_bytes()).hexdigest(),'http':response.status_code,'result':response.json()})
Path('migration-receipt.json').write_text(json.dumps(receipt,indent=2))
print(json.dumps(receipt,indent=2))
