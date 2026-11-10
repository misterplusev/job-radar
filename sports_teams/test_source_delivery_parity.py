import contextlib,io,json,os,sys,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import live_refresh as live
import publish_teams as pub
from cloud_storage import CloudStorage

class Parity(unittest.TestCase):
    def test_only_explicit_team_sources_can_enter_production(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/'sources.json').write_text(json.dumps([{'key':'team'},{'key':'unrelated-league-search'}]))
            (root/'official_careers_registry.json').write_text(json.dumps([{'source_keys':['team']}]))
            self.assertEqual(set(live.build_sources(SimpleNamespace(ROOT=root))),{'team'})
            (root/'official_careers_registry.json').write_text(json.dumps([{'source_keys':['missing']}]))
            with self.assertRaisesRegex(ValueError,'missing'):live.build_sources(SimpleNamespace(ROOT=root))

    def test_no_generic_league_discovery(self):
        with patch.object(live,'build_sources',return_value={}),patch.object(live.teamwork_vertical,'discover') as discover:
            live.collect(None)
        discover.assert_not_called()

    def test_queued_new_job_only_and_failed_delivery_stays_pending(self):
        rows=[{'url':'https://example.com/'+x,'title':x,'posted_at':pub.now_iso()} for x in ('old','new')]
        state={'seen':[],'pending':[rows[1]['url']]}
        with patch.object(pub,'load_rows',return_value=rows),patch.object(pub,'load_state',return_value=state),patch.object(pub,'guard'),patch.object(pub,'webhook',return_value='mock'),patch.object(pub,'notify',return_value=False) as send,patch.object(pub,'save_state') as save,patch.object(pub.time,'sleep'),patch.object(sys,'argv',['publish_teams.py','--post']),contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(pub.main(),1)
        self.assertEqual([e['url'] for e in send.call_args.args[1]['embeds']],[rows[1]['url']])
        self.assertEqual(state['pending'],[rows[1]['url']]);save.assert_not_called()

    def test_queue_creation_never_resets_delivered_history(self):
        with patch.dict(os.environ,{'SUPABASE_URL':'https://example.com','SUPABASE_SERVICE_ROLE_KEY':'mock'}):cloud=CloudStorage()
        with patch.object(cloud,'request') as req:cloud.queue_notifications(['new','new'])
        self.assertTrue(req.call_args.kwargs['ignore_duplicates'])
        self.assertEqual(req.call_args.kwargs['json'],[{'url':'new','status':'pending','delivered_at':None}])

if __name__=='__main__':unittest.main()
