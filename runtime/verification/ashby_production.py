"""Recover just the OpenAI board and do not retire jobs from other acquisition routes."""
import json
from pathlib import Path
from unittest.mock import patch
import run
from jobradar import publish
from jobradar.providers.ashby import AshbyProvider

original=publish.publish
def positive(jobs, **opts):
    opts["allow_deactivate"]=False
    return original(jobs, **opts)
with patch.object(run,"build_providers",return_value=[AshbyProvider("openai")]),patch.object(publish,"publish",positive):
    assert run._ingest_supabase()==0
m=json.loads(Path("data/runtime/latest_manifest.json").read_text())
receipt=m["providers"][0]
assert m["module"]=="robotics" and m["status"]=="healthy" and receipt["complete"] and not receipt.get("unresolved_rows")
assert m["publish"]["upserted"]==receipt["job_count"]>0 and m["publish"]["deactivated"]==0
print(json.dumps({"provider":receipt,"publish":m["publish"]}))
