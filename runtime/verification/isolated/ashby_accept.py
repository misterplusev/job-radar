"""Real provider subprocess, real PostgreSQL/PostgREST, isolated sender and exact-history replay."""
import json
import os
from pathlib import Path
import sys
from unittest.mock import patch

from isolated_services import services, rest, messages, ROOT

sys.path.insert(0, str(ROOT))
TARGET="https://jobs.ashbyhq.com/openai/1ae64ddb-505f-4ad2-a731-3a857e94edee"
def main():
    with services():
        os.environ["JOBRADAR_MODULE"]="robotics"
        import run
        from jobradar import publish
        from jobradar.providers.ashby import AshbyProvider
        from jobradar.providers.names import board_company
        source=AshbyProvider("openai")
        unknown="https://isolated.invalid/previous/"
        company=board_company("openai",None)
        base={"company":company,"title":"Known prior job","ats":"ashby","is_active":True,
              "source_payload":{"provider_slug":"openai"}}
        rest("POST","robotics_jobs",json=dict(base,url=unknown))
        with patch.object(run,"build_providers",return_value=[source]):
            try: run._ingest_supabase()
            except RuntimeError as exc: assert "Partial scrape" in str(exc),exc
            else: raise AssertionError("An unknown blank title must produce a partial receipt")
            record=json.loads(Path("data/runtime/latest_manifest.json").read_text())
            first=record["providers"][0]
            assert first["unresolved_rows"]>=1 and first["job_count"]>0 and record["publish"]["deactivated"]==0,record
            assert rest("GET","robotics_jobs",params={"url":"eq."+unknown,"select":"is_active"})[0]["is_active"]
            rest("POST","robotics_jobs",json=dict(base,url=TARGET,title="Growth Marketing, Creative and Ad Operations"))
            assert run._ingest_supabase()==0
        manifest=json.loads(Path("data/runtime/latest_manifest.json").read_text())
        receipt=manifest["providers"][0]
        assert receipt["source_rows"]==receipt["job_count"] and receipt["complete"] and receipt["unresolved_rows"]==0
        assert TARGET in receipt["retained_title_urls"]
        assert rest("GET","robotics_jobs",params={"url":"eq."+TARGET,"select":"is_active,title"})==[
            {"is_active":True,"title":"Growth Marketing, Creative and Ad Operations"}]
        assert not rest("GET","robotics_jobs",params={"url":"eq."+unknown,"select":"is_active"})[0]["is_active"]
        rows=rest("GET","robotics_jobs",params={"select":"url","is_active":"eq.true","company":"eq."+company,"limit":1000})
        assert len(rows)==receipt["job_count"],(len(rows),receipt)
        assert not rest("GET","robotics_job_notifications",params={"job_url":"eq."+TARGET})
        result={"live_rows":len(rows),"fresh_titles":first["job_count"],"known_title_observations":len(receipt["retained_title_urls"]),
                "unresolved":receipt["unresolved_rows"],"unknown_title_test_closed":record["publish"]["deactivated"],
                "confirmed_absence_closed_on_complete_run":manifest["publish"]["deactivated"],
                "cached_title_generated_notifications":0,"sender_deliveries":len(messages),"production_writes":0}
        (ROOT/"proof"/"ashby.json").write_text(json.dumps(result,indent=2))
        print(json.dumps(result))
if __name__=="__main__": main()
