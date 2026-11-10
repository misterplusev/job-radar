"""Offline regression checks. All notification and HTTP calls are mocked."""
import contextlib
import io
import json
import sqlite3
import sys
import unittest
from unittest.mock import patch

import live_refresh as live
import pipeline_local as pipeline
import publish_teams as publisher
from providers import teamwork, teamwork_vertical


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.con = sqlite3.connect(':memory:')
        self.con.executescript(pipeline.SCHEMA)

    def tearDown(self):
        self.con.close()

    def row(self, ident='1', **kw):
        return dict(league='NFL', team='NFL League Office', title='Program Manager',
                    url='https://job-boards.greenhouse.io/nflcareers/jobs/' + ident,
                    platform='greenhouse', scraped_at='2026-11-09T20:00:00+00:00', **kw)

    def result(self, rows, status='success'):
        return dict(source=dict(key='gh:nflcareers', kind='greenhouse'), rows=rows,
                    status=status, observed_at='2026-11-09T20:00:00+00:00', duration_ms=10,
                    error='test failure' if status == 'error' else None)

    def test_failed_source_preserves_jobs_and_last_seen(self):
        pipeline.ingest(self.con, [self.row()], record_runs=False)
        before = self.con.execute('select last_seen_at from team_jobs').fetchone()[0]
        live.apply_results(self.con, [self.result([], 'error')], pipeline)
        self.assertEqual(self.con.execute('select is_active,last_seen_at from team_jobs').fetchone(), (1,before))
        self.assertEqual(self.con.execute('select status from team_job_scrape_runs').fetchone()[0], 'error')

    def test_empty_source_cannot_close_previous_jobs(self):
        pipeline.ingest(self.con, [self.row()], record_runs=False)
        live.apply_results(self.con, [self.result([], 'empty_unverified')], pipeline)
        self.assertEqual(self.con.execute('select is_active from team_jobs').fetchone()[0], 1)

    def test_only_successful_source_can_close_its_missing_job(self):
        pipeline.ingest(self.con, [self.row('1'), self.row('2'), dict(self.row('3'), url='https://job-boards.greenhouse.io/another/jobs/3')], record_runs=False)
        live.apply_results(self.con, [self.result([self.row('1')])], pipeline)
        self.assertEqual([r[0] for r in self.con.execute('select is_active from team_jobs order by id')], [1,0,1])

    def test_first_seen_stable_and_runs_are_per_source(self):
        result = self.result([self.row('1'), self.row('2')])
        live.apply_results(self.con, [result], pipeline)
        first = self.con.execute('select first_seen_at from team_jobs order by id').fetchall()
        live.apply_results(self.con, [result], pipeline)
        self.assertEqual(self.con.execute('select first_seen_at from team_jobs order by id').fetchall(), first)
        self.assertEqual(self.con.execute('select count(*) from team_jobs').fetchone()[0], 2)
        self.assertEqual(self.con.execute('select count(*) from team_job_scrape_runs').fetchone()[0], 2)

    def test_cross_listed_job_survives_other_source_failure(self):
        first=self.result([self.row('1')])
        second=self.result([self.row('1')]);second['source']=dict(key='gh:second',kind='greenhouse')
        live.apply_results(self.con,[first,second],pipeline)
        failed=self.result([], 'error');failed['source']=second['source']
        live.apply_results(self.con,[self.result([self.row('2')]),failed],pipeline)
        self.assertEqual(self.con.execute('select is_active from team_jobs where url=?',(self.row('1')['url'],)).fetchone()[0],1)

    def test_same_url_under_different_team_label_is_not_duplicated(self):
        pipeline.ingest(self.con,[self.row()],record_runs=False)
        pipeline.ingest(self.con,[dict(self.row(),team='Other spelling')],record_runs=False)
        self.assertEqual(self.con.execute('select count(*) from team_jobs').fetchone()[0],1)

    def test_short_listing_does_not_destroy_full_description(self):
        pipeline.ingest(self.con, [self.row(description='Full detailed role description')], record_runs=False)
        pipeline.ingest(self.con, [self.row(description='NFL')], record_runs=False)
        self.assertEqual(self.con.execute('select description from team_jobs').fetchone()[0], 'Full detailed role description')

    def test_workday_url_and_legacy_incomplete_link(self):
        source = live.source_from_row(dict(url='https://nba.wd108.myworkdayjobs.com/en-US/nbacareers/job/NY/A_JR1/apply', team='NBA',league='NBA'))
        self.assertEqual(source['site'], 'nbacareers')
        self.assertIsNone(live.source_from_row(dict(url='https://club.wd1.myworkdayjobs.com/job/NY/Manager_JR1')))

    def test_irregular_teamwork_slug(self):
        match = teamwork_vertical.ORG_SLUG_RE.match('/football-jobs/chiefs/kansas-city-chiefs-29577/manager-2198533')
        self.assertIsNotNone(match)
        self.assertEqual(match.group(3), 'kansas-city-chiefs-29577')
        self.assertNotIn('organization_id', teamwork.org_url(teamwork.TeamWorkOrg('NFL','Chiefs','football-jobs/chiefs/kansas-city-chiefs-29577','')))

    def test_request_budget(self):
        with live.BoundedSession() as client:
            client.calls = live.MAX_REQUESTS
            with self.assertRaises(TimeoutError):
                client.get('https://example.com')

    def test_nba_keeps_workday_as_ats_platform(self):
        from providers.base import Job
        job=Job(league='NBA',team='NBA League Office',title='Manager',url='https://nba.example/job',location='NY',platform='workday')
        with patch.object(live.nba,'scrape',return_value=[job]):
            result=live.fetch_source(dict(kind='nba',key='nba:league',league='NBA',team='NBA League Office'))
        self.assertEqual(result['rows'][0]['platform'],'workday')

    def publishing(self, success, count=12, args=None):
        rows = [dict(self.row(str(i)), posted_at=publisher.now_iso()) for i in range(count)]
        saved = []
        with patch.object(publisher, 'load_rows', return_value=rows), patch.object(publisher,'load_state',return_value={'seen': [],'pending':[r['url'] for r in rows],'posts':0}), patch.object(publisher,'save_state',side_effect=saved.append), patch.object(publisher,'guard'), patch.object(publisher,'webhook',return_value='mock-only'), patch.object(publisher,'notify',side_effect=success), patch.object(publisher.time,'sleep'), patch.object(sys,'argv',['publish_teams.py']+(args or ['--post','--limit','10'])), contextlib.redirect_stdout(io.StringIO()):
            code = publisher.main()
        return saved, code

    def test_limit_does_not_mark_backlog_as_posted(self):
        saved, code = self.publishing([True,True])
        self.assertEqual(code,0)
        self.assertEqual(len(saved[0]['seen']),10)

    def test_failed_chunk_remains_unseen(self):
        saved, code = self.publishing([True,False])
        self.assertEqual(code,1)
        self.assertEqual(len(saved[0]['seen']),5)

    def test_all_failed_does_not_change_state(self):
        saved, code = self.publishing([False,False])
        self.assertEqual(code,1)
        self.assertFalse(saved)

    def test_publish_without_mode_does_not_send(self):
        saved, code = self.publishing([],args=['--limit','10'])
        self.assertEqual(code,0)
        self.assertFalse(saved)

    def test_dry_run_never_sends_or_updates_state(self):
        saved, code = self.publishing([],args=['--dry-run'])
        self.assertEqual(code,0)
        self.assertFalse(saved)


if __name__ == '__main__':
    unittest.main()
