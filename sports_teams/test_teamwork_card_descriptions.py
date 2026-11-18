import sqlite3
import unittest
from unittest.mock import patch

import pipeline_local
from providers import teamwork


class TeamWorkCardDescriptions(unittest.TestCase):
    def test_card_employer_label_is_only_an_employer(self):
        card = '<h3 class="organization-portal__job-title"><a href="/event-captain-2194349">Event Captain</a></h3><p class="organization-portal__job-category">Atlanta Braves</p>'
        org = teamwork.TeamWorkOrg('MLB', 'Portal', 'baseball-jobs/atlanta-braves', '')
        with patch.object(teamwork, 'pages', return_value=[card]):
            job, = teamwork.scrape_org(org)
        self.assertEqual(job.team, 'Atlanta Braves')
        self.assertEqual(job.title, 'Event Captain')
        self.assertFalse(job.description_clean)
        self.assertFalse(job.description_raw)

    def test_normal_ingest_repairs_historical_labels_and_preserves_real_bodies(self):
        db = sqlite3.connect(':memory:')
        self.addCleanup(db.close)
        db.executescript(pipeline_local.SCHEMA)
        team = 'Atlanta Braves'
        row = dict(league='MLB', team=team, title='Event Captain', url='https://www.teamworkonline.com/example-2194349',
                   platform='teamworkonline', description=team)
        def lookup():
            return db.execute('select description from team_jobs').fetchone()[0]
        pipeline_local.ingest(db,[row],False)
        self.assertFalse(lookup())
        db.execute('update team_jobs set description=?', (team,))
        pipeline_local.ingest(db,[row],False)
        self.assertFalse(lookup())
        body = 'Coordinate guests and event staff from the first briefing through venue close. '*3
        db.execute('update team_jobs set description=?', (body,))
        pipeline_local.ingest(db,[row],False)
        self.assertEqual(lookup(),body)
        self.assertEqual(db.execute('select count(*) from team_jobs where is_active=1').fetchone()[0],1)
