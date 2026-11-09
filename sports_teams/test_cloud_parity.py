import json
import os
import sqlite3
import unittest
from datetime import datetime,timezone
from unittest.mock import Mock,patch
from pathlib import Path
import cloud_storage
import enrichment
import live_refresh
import pipeline_local
import publish_teams
from providers import teamwork


class ParityTests(unittest.TestCase):
    def test_complete_description_updates_even_when_shorter(self):
        con=sqlite3.connect(':memory:');con.executescript(pipeline_local.SCHEMA);self.addCleanup(con.close)
        row=dict(league='NFL',team='Team',title='Manager',url='https://example.com/role',platform='greenhouse',description='A'*2000)
        pipeline_local.ingest(con,[row],False);pipeline_local.ingest(con,[dict(row,description='B'*1000)],False)
        self.assertEqual(con.execute('select description from team_jobs').fetchone()[0],'B'*1000)

    def test_league_portal_preserves_actual_employer(self):
        from providers.base import Job
        job=Job(league='NHL',team='Washington Capitals',title='Manager',url='https://example.com/job',location='DC')
        with patch.object(live_refresh.teamwork,'scrape_org',return_value=[job]):
            result=live_refresh.fetch_source(dict(kind='teamworkonline',key='tw:league',path='hockey-jobs/league',league='NHL',team='NHL League Office'))
        self.assertEqual(result['rows'][0]['team'],'Washington Capitals')

    def test_owner_correction_preserves_identity_and_first_seen(self):
        con=sqlite3.connect(':memory:');con.executescript(pipeline_local.SCHEMA);self.addCleanup(con.close)
        row=dict(league='NHL',team='NHL League Office',title='Manager',url='https://example.com/role')
        pipeline_local.ingest(con,[row],False)
        first=con.execute('select first_seen_at from team_jobs').fetchone()[0]
        pipeline_local.ingest(con,[dict(row,team='Washington Capitals')],False)
        self.assertEqual(con.execute('select count(*),team,first_seen_at from team_jobs').fetchone(),(1,'Washington Capitals',first))

    def test_old_unannounced_job_is_not_announced_as_new(self):
        import sys
        rows=[dict(title='Old role',url='https://example.com/old',posted_at='2020-01-01',first_seen_at='2020-01-01')]
        with patch.object(publish_teams,'load_rows',return_value=rows),patch.object(publish_teams,'load_state',return_value={'seen':[]}),patch.object(publish_teams,'notify') as send,patch.object(sys,'argv',['publish_teams.py','--post']):
            self.assertEqual(publish_teams.main(),0);send.assert_not_called()

    def test_verified_empty_source_retires_jobs(self):
        con=sqlite3.connect(':memory:');con.executescript(pipeline_local.SCHEMA);self.addCleanup(con.close)
        row=dict(league='NFL',team='Team',title='Manager',url='https://job-boards.greenhouse.io/test/jobs/1')
        pipeline_local.ingest(con,[row],False)
        result=dict(source={'kind':'greenhouse','key':'gh:test'},rows=[],status='success',observed_at='2026-11-09T00:00:00Z',duration_ms=1,error=None)
        live_refresh.apply_results(con,[result],pipeline_local)
        self.assertEqual(con.execute('select is_active from team_jobs').fetchone()[0],0)

    def test_cloud_source_relay_preserves_canonical_url(self):
        response=Mock(headers={'X-Source-URL':'https://www.teamworkonline.com/final?page=2'})
        with patch.dict(os.environ,{'TEAMS_SOURCE_RELAY_URL':'https://relay.example/source/teamwork','DISCORD_RELAY_TOKEN':'test-only'}),patch('requests.Session.request',return_value=response) as request:
            with live_refresh.BoundedSession() as client:
                result=client.get('https://www.teamworkonline.com/start',params={'page':2})
        self.assertEqual(result.url,'https://www.teamworkonline.com/final?page=2')
        self.assertEqual(request.call_args.args[1],'https://relay.example/source/teamwork')
        self.assertEqual(request.call_args.kwargs['params']['url'],'https://www.teamworkonline.com/start?page=2')

    def page(self,body,url):
        response=Mock(text=body,url=url);response.raise_for_status.return_value=None;return response

    def test_teamwork_follows_next_page_and_deduplicates(self):
        card='<h3 class="organization-portal__job-title"><a href="/football-jobs/test/team/job-1">Manager</a></h3>'
        client=Mock();client.get.side_effect=[self.page(card+'<a rel="next" href="?page=2">Next</a>','https://www.teamworkonline.com/test'),self.page(card.replace('job-1','job-2'),'https://www.teamworkonline.com/test?page=2')]
        jobs=teamwork.scrape_org(teamwork.TeamWorkOrg('NFL','Team','test',''),session=client)
        self.assertEqual(len(jobs),2)
        self.assertEqual(client.get.call_args_list[1].args[0],'https://www.teamworkonline.com/test?page=2')

    def test_malformed_and_cycle_pages_fail_instead_of_closing_jobs(self):
        client=Mock();client.get.return_value=self.page('<h1>Temporarily unavailable</h1>','https://www.teamworkonline.com/test')
        with self.assertRaises(ValueError):list(teamwork.pages('https://www.teamworkonline.com/test',client,25))
        client.get.return_value=self.page('<select name="employment_opportunity_search[organization_id]"></select><a rel="next" href="/test">Next</a>','https://www.teamworkonline.com/test')
        with self.assertRaises(ValueError):list(teamwork.pages('https://www.teamworkonline.com/test',client,25))

    def test_jsonld_extracts_full_description_and_salary_without_guessing(self):
        raw={'@graph':[{'@type':'Organization'},{'@type':'JobPosting','description':'A'*2500,'baseSalary':{'currency':'USD'}}]}
        got=enrichment.jsonld_job('<script type="application/ld+json">'+json.dumps(raw)+'</script>')
        self.assertEqual(len(got['description']),2500);self.assertEqual(got['baseSalary'],{'currency':'USD'})

    def test_supabase_pagination_and_retries_exhaustion_raise(self):
        with patch.dict(os.environ,{'SUPABASE_URL':'https://example.supabase.co','SUPABASE_SERVICE_ROLE_KEY':'test-only'}):store=cloud_storage.CloudStorage()
        first=Mock();first.json.return_value=[{'id':i} for i in range(1000)];last=Mock();last.json.return_value=[{'id':1001}]
        with patch.object(store,'request',side_effect=[first,last]) as req:
            self.assertEqual(len(store.rows('team_jobs')),1001);self.assertEqual(req.call_args.kwargs['params']['offset'],1000)
        response=Mock(status_code=503,ok=False)
        with patch.object(cloud_storage.requests,'request',return_value=response),patch.object(cloud_storage.time,'sleep'):
            with self.assertRaises(RuntimeError):store.request('POST','team_jobs',json=[])

    def test_restoring_cloud_preserves_first_seen_and_inactive_status(self):
        con=sqlite3.connect(':memory:');con.executescript(pipeline_local.SCHEMA)
        self.addCleanup(con.close)
        row=dict(league='NFL',team='Team',title='Manager',url='https://example.com/1',is_active=False,first_seen_at='2020-01-01T00:00:00Z')
        with patch.dict(os.environ,{'SUPABASE_URL':'https://example.supabase.co','SUPABASE_SERVICE_ROLE_KEY':'test-only'}):store=cloud_storage.CloudStorage()
        with patch.object(store,'rows',side_effect=[[row],[]]):store.restore(con)
        self.assertEqual(con.execute('select first_seen_at,is_active from team_jobs').fetchone(),('2020-01-01T00:00:00Z',0))

    def test_cloud_notification_guard_never_posts(self):
        with patch.dict(os.environ,{'NOTIFICATIONS_PAUSED':'1'}),patch.object(publish_teams.urllib.request,'urlopen') as send:
            with self.assertRaises(SystemExit):publish_teams.notify('https://example.com',{})
            send.assert_not_called()

    def test_full_description_survives_long_listing_teaser(self):
        con=sqlite3.connect(':memory:');con.executescript(pipeline_local.SCHEMA)
        self.addCleanup(con.close)
        row=dict(league='NFL',team='Team',title='Manager',url='https://example.com',description='A'*2000)
        pipeline_local.ingest(con,[row],False);pipeline_local.ingest(con,[dict(row,description='B'*100)],False)
        self.assertEqual(len(con.execute('select description from team_jobs').fetchone()[0]),2000)

    def test_runtime_schedule_is_same_each_day_and_dst_aware(self):
        import runtime
        winter=runtime.schedule(datetime(2026,11,9,12,tzinfo=timezone.utc))
        summer=runtime.schedule(datetime(2026,7,6,11,tzinfo=timezone.utc))
        self.assertEqual(winter['previous_due_utc'],'2026-11-09T11:00:00+00:00')
        self.assertEqual(summer['previous_due_utc'],'2026-07-06T10:00:00+00:00')
        self.assertEqual(winter['weekday_hours_et'],winter['weekend_hours_et'])


if __name__=='__main__':unittest.main()
