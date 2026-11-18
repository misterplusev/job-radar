"""Verify the authorized browser artifact through the actual team and robotics adapters and cloud stores."""
import json, os, sqlite3, sys
from pathlib import Path
from unittest.mock import patch
from isolated_services import services,rest,ROOT
os.environ["WORKDAY_LISTINGS_FILE"]=str(ROOT/"proof/listings.json.gz")

def main():
    with services():
        os.environ["JOBRADAR_MODULE"]="robotics"
        import run
        from jobradar.providers.workday import WorkdayProvider
        from jobradar import workday_snapshot as snapshot
        names=("bostondynamics","autostore","rockwellautomation")
        with patch.object(run,"build_providers",return_value=[WorkdayProvider(n) for n in names]):
            assert run._ingest_supabase()==0
        raw=json.loads((ROOT/"data/runtime/latest_manifest.json").read_text())
        assert all(r["complete"] for r in raw["providers"])
        reports={r["provider"]:r["job_count"] for r in raw["providers"]}
        bundle=snapshot._unpack(Path(os.environ["WORKDAY_LISTINGS_FILE"]).read_bytes())
        catalog=json.loads((ROOT/"runtime/workday/catalog.json").read_text())
        for board in (b for b in catalog if b["module"]=="robotics"):
            rows=bundle["boards"]["/".join(board[k] for k in ("host","tenant","site"))]["jobs"]
            urls={f'https://{board["host"]}/{board["site"]}'+j["externalPath"] for j in rows}
            actual=rest("GET","robotics_jobs",params={"select":"url","company":"eq."+board["company"],"is_active":"eq.true","limit":1000})
            assert urls=={r["url"] for r in actual}
        sys.path.insert(0,str(ROOT/"sports_teams"))
        import live_refresh, pipeline_local as teams, cloud_storage
        registry=live_refresh.build_sources(teams.pt)
        sources=[registry[b["id"]] for b in catalog if b["module"]=="sports_teams"]
        with patch.object(live_refresh.BoundedSession,"post",side_effect=AssertionError("unexpected second collection")):
            readings=[live_refresh.fetch_source(p) for p in sources]
        assert all(r["status"]=="success" for r in readings),readings
        con=sqlite3.connect(":memory:");con.executescript(teams.SCHEMA)
        with patch.dict(os.environ, {"SUPABASE_URL":"https://isolated.invalid"}):
            service=cloud_storage.CloudStorage()
        from isolated_services import BASE
        service.url=BASE
        service.restore(con)
        new,_,closed=live_refresh.apply_results(con,readings,teams)
        urls={j["url"] for r in readings for j in r["rows"]}
        service.queue_notifications(urls)
        service.persist(con,readings,"2e18e8ff-5fb4-47e7-91a7-a222932dbf94","isolated-workday")
        actual=rest("GET","team_jobs",params={"select":"url","is_active":"eq.true"})
        assert new==len(urls)==len(actual) and {r["url"] for r in actual}==urls
        n2,_,c2=live_refresh.apply_results(con,readings,teams)
        service.queue_notifications(urls)
        assert n2==c2==closed==0
        pending=rest("GET","team_job_notifications",params={"select":"url","status":"eq.pending"})
        assert {r['url'] for r in pending}==urls
        outcome={"robotics_sources":len(reports),"robotics_rows":raw["publish"]["upserted"],"robotics_by_board":reports,
                 "team_sources":len(readings),"team_rows":len(urls),"verified_empty_team_boards":sum(not r["rows"] for r in readings),
                 "team_queue_matches":len(pending),"duplicate_team_rows_on_replay":n2,"date":bundle["observed_at"],"production_writes":0}
        (ROOT/"proof/robotics-teams.json").write_text(json.dumps(outcome,indent=2));print(outcome)
if __name__=="__main__": main()
