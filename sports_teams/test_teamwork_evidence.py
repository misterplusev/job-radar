import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from publish_teams import _clean_text
from teamwork_evidence import record_missing

URL='https://www.teamworkonline.com/baseball-jobs/atlanta-braves/atlanta-braves-jobs/event-captain-2194349'
APPLY='https://atlantabravesmlb.wd5.myworkdayjobs.com/AtlantaBraves/job/Atlanta-GA/Event-Captain_R2107'
BODY='Coordinate event staff and guest support before the gates open, then reconcile the event checklist after close.'


class PublicDetailEvidence(unittest.TestCase):
    def setUp(self):
        self.temp=TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.row={'url':URL,'title':'Event Captain','team':'Atlanta Braves'}
        self.env=patch.dict(os.environ,{'TEAMWORK_DETAIL_EVIDENCE_DIR':self.temp.name})
        self.env.start();self.addCleanup(self.env.stop)

    def response(self, html, status=200, challenge=False):
        return SimpleNamespace(url=URL,status_code=status,headers={'cf-mitigated':'challenge'} if challenge else {},
                               text=html,content=html.encode())

    def test_exact_identity_and_public_link_no_secret_or_unrelated_text(self):
        html='<h1>Event Captain</h1><main><div id="job-description">'+BODY+'</div><a href="'+APPLY+'?tracking=private">Apply now</a><form>private-value</form><script>secret-variable</script></main>'
        with patch('requests.sessions.Session.request',side_effect=AssertionError('extra network call')):
            record_missing(self.row,self.response(html),_clean_text)
        output=next(Path(self.temp.name).glob('*.json')).read_text()
        proof=json.loads(output)
        self.assertEqual(proof['candidate_description'],BODY)
        self.assertEqual(proof['official_apply_links'],[APPLY])
        self.assertNotIn('private',output);self.assertNotIn('secret-variable',output)

    def test_denial_wrong_identity_and_form_only_never_supply_body_or_external_link(self):
        page='<h1>Event Captain</h1><form>'+BODY+'</form>'
        for res in (self.response(page,403),self.response(page,200,True),
                    self.response('<h1>Different role</h1>'),self.response('<link rel="canonical" href="'+URL[:-1]+'8">'+page)):
            record_missing(self.row,res,_clean_text)
        self.assertEqual(list(Path(self.temp.name).glob('*.json')),[])
        record_missing(self.row,self.response(page),_clean_text)
        value=json.loads(next(Path(self.temp.name).glob('*.json')).read_text())
        self.assertNotIn('candidate_description',value)
        self.assertEqual(value['official_apply_links'],[])

    def test_normal_fetch_collects_once_and_keeps_missing_detail_visible(self):
        from enrichment import fetch_detail
        res=self.response('<h1>Event Captain</h1><div id="job-description">'+BODY+'</div>')
        res.raise_for_status=lambda: None
        with patch('enrichment.BoundedSession') as factory:
            client=factory.return_value.__enter__.return_value
            client.get.return_value=res
            with self.assertRaisesRegex(ValueError,'structured data missing'):
                fetch_detail(self.row)
            self.assertEqual(client.get.call_count,1)
        proof=json.loads(next(Path(self.temp.name).glob('*.json')).read_text())
        self.assertEqual(proof['candidate_description'],BODY)

    def test_idempotent_and_bounded(self):
        out=Path(self.temp.name)
        for i in range(8):(out/(str(i)+'.json')).write_text('{}')
        record_missing(self.row,self.response('<h1>Event Captain</h1>'),_clean_text)
        self.assertEqual(len(list(out.glob('*.json'))),8)
