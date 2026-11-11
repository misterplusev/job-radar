"""Keep a verified flag from substituting for the actual official source chain."""
import json
from pathlib import Path
import unittest
from urllib.parse import urlsplit,parse_qs

ROOT=Path(__file__).resolve().parent

class OfficialCareerProofTests(unittest.TestCase):
    def test_every_team_has_evidence_for_a_configured_source(self):
        teams=json.loads((ROOT/'official_careers_registry.json').read_text())
        self.assertEqual(len(teams),124)
        self.assertEqual(len({t['team'] for t in teams}),124)
        for team in teams:
            with self.subTest(team=team['team']):
                self.assertTrue(team['career_link_verified'])
                evidence=[r['career_link_evidence'] for r in team['routes']
                          if r.get('career_link_evidence') and r.get('source_key') in team['source_keys']]
                direct=team.get('direct_listing_evidence',{})
                self.assertTrue(evidence or direct.get('source_key') in team['source_keys'])

    def test_rendered_nba_evidence_matches_exact_employers(self):
        rows={r['team']:r for r in json.loads((ROOT/'career_link_proof_20261111.json').read_text())}
        self.assertEqual(set(rows),{'Chicago Bulls','LA Clippers','Milwaukee Bucks'})
        for team in ('Chicago Bulls','LA Clippers'):
            proof=rows[team]
            self.assertEqual(proof['matching']['official_job_ids'],proof['matching']['feed_job_ids'])
            self.assertGreater(len(proof['matching']['official_job_ids']),0)
            self.assertEqual(proof['feed_status'],'success')
        self.assertEqual(parse_qs(urlsplit(rows['LA Clippers']['matching']['embedded_job_frame']).query)['for'],['laclippers'])
        bucks=rows['Milwaukee Bucks']
        self.assertEqual(bucks['source_key'],'adp:'+bucks['matching']['cid'])
        query=parse_qs(urlsplit(bucks['visible_links'][0]['url']).query)
        self.assertEqual(query['cid'],[bucks['matching']['cid']])
        self.assertEqual(query['ccId'],[bucks['matching']['ccId']])

if __name__=='__main__':unittest.main()
