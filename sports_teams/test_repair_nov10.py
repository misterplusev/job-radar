import sqlite3
import types
import unittest
from unittest.mock import Mock

import live_refresh
import pipeline_local
from providers import teamwork


class SourceRepairTests(unittest.TestCase):
    def test_filtered_portal_must_confirm_requested_employer(self):
        client=Mock()
        org=teamwork.TeamWorkOrg('NHL','Detroit Red Wings','hockey-jobs/hockeyjobs/nhl-league-office','28282')
        for selected in ('', '<option value="30003" selected>Capitals</option>'):
            client.get.return_value=Mock(text='<select name="employment_opportunity_search[organization_id]">'+selected+'</select>')
            with self.assertRaisesRegex(ValueError,'organization filter'):
                teamwork.scrape_org(org,session=client)

    def test_confirmed_empty_team_is_valid(self):
        client=Mock()
        client.get.return_value=Mock(text='<select name="employment_opportunity_search[organization_id]"><option value="28277" selected>Boston Bruins</option></select>')
        self.assertEqual(teamwork.scrape_org(teamwork.TeamWorkOrg('NHL','Bruins','hockey-jobs/hockeyjobs/nhl-league-office','28277'),session=client),[])

    def fixture(self):
        con=sqlite3.connect(':memory:');self.addCleanup(con.close)
        con.executescript(pipeline_local.SCHEMA)
        con.execute('create table team_job_observations(source_id text,url text,is_active integer,observed_at text,primary key(source_id,url))')
        con.execute("insert into team_jobs(league,team,title,url,first_seen_at,is_active) values('NHL','Team','Role','https://example.com/job','2020-01-01',1)")
        pipe=types.SimpleNamespace(ingest=lambda *a,**kw:(0,0),now=lambda:'2026-11-11T08:00:00Z')
        return con,pipe

    def result(self,key,status='success'):
        return {'source':{'key':key,'kind':'test'},'status':status,'rows':[],
                'duration_ms':1,'error':None,'observed_at':'2026-11-11T08:00:00Z'}

    def test_phantom_inferred_observation_cannot_keep_absent_job_active(self):
        con,pipe=self.fixture()
        con.executemany('insert into team_job_observations values(?,?,?,?)',[
            ('inferred','https://example.com/job',1,None),('actual','https://example.com/job',1,'2026-11-10')])
        live_refresh.apply_results(con,[self.result('actual')],pipe)
        self.assertEqual(con.execute('select is_active from team_jobs').fetchone()[0],0)
        live_refresh.apply_results(con,[self.result('actual')],pipe)
        self.assertEqual(con.execute('select sum(is_active) from team_job_observations').fetchone()[0],0)

    def test_failed_cross_listing_preserves_job(self):
        con,pipe=self.fixture()
        con.executemany('insert into team_job_observations values(?,?,?,?)',[
            ('a','https://example.com/job',1,'2026-11-10'),('b','https://example.com/job',1,'2026-11-10')])
        live_refresh.apply_results(con,[self.result('a'),self.result('b','error')],pipe)
        self.assertEqual(con.execute('select is_active from team_jobs').fetchone()[0],1)

    def test_retired_route_waits_for_successful_replacement(self):
        con,pipe=self.fixture()
        con.execute('insert into team_job_observations values(?,?,?,?)',('old','https://example.com/job',1,'2026-11-10'))
        live_refresh.apply_results(con,[self.result('replacement','error')],pipe,{'old':'replacement'})
        self.assertEqual(con.execute('select is_active from team_jobs').fetchone()[0],1)
        live_refresh.apply_results(con,[self.result('replacement')],pipe,{'old':'replacement'})
        self.assertEqual(con.execute('select is_active from team_jobs').fetchone()[0],0)


if __name__=='__main__':unittest.main()
