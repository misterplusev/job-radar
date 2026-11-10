"""Offline regressions for discovered coverage gaps and notification history."""
import json,os,sqlite3,unittest,sys,contextlib,io
from unittest.mock import Mock,patch
import live_refresh as live
import publish_teams as pub
import cloud_storage,pipeline_local,coverage_report
from providers import official_ats as ats,adp

def response(data=None,text='',url='https://jobs.dayforcehcm.com/fr-CA/club/CANDIDATEPORTAL'):
    r=Mock(text=text,url=url);r.json.return_value=data;return r

class OfficialRoutes(unittest.TestCase):
    def test_dayforce_language_is_not_silently_changed(self):
        s=live.source_from_row({'url':'https://jobs.dayforcehcm.com/fr-CA/club/CANDIDATEPORTAL/jobs/1'})
        self.assertEqual(s['key'],'dayforce:club/CANDIDATEPORTAL:fr-CA')
        self.assertIn('/fr-CA/',s['url'])

    def test_dayforce_pagination_uses_real_offset_and_rejects_truncation(self):
        c=Mock();c.get.side_effect=[response(),response({'csrfToken':'public-nonce'})]
        c.post.side_effect=[response({'maxCount':2,'jobPostings':[{'jobPostingId':1,'jobTitle':'A','postingLocations':None}]}),response({'maxCount':2,'jobPostings':[{'jobPostingId':2,'jobTitle':'B'}]})]
        self.assertEqual(len(ats.dayforce({'url':'https://jobs.dayforcehcm.com/fr-CA/club/CANDIDATEPORTAL'},c)),2)
        self.assertEqual(c.post.call_args.kwargs['json']['paginationStart'],1)
        self.assertEqual(c.post.call_args.kwargs['json']['cultureCode'],'fr-CA')
        c.get.side_effect=[response(),response({'csrfToken':'public-nonce'})]
        c.post.side_effect=[response({'maxCount':2,'jobPostings':[]})]
        with self.assertRaisesRegex(ValueError,'Incomplete'):ats.dayforce({'url':'https://example.com'},c)

    def test_dayforce_missing_nonce_and_repeated_jobs_are_errors(self):
        c=Mock();c.get.side_effect=[response(),response({})]
        with self.assertRaisesRegex(ValueError,'nonce'):ats.dayforce({'url':'https://example.com'},c)
        c.get.side_effect=[response(),response({'csrfToken':'nonce'})]
        c.post.return_value=response({'maxCount':2,'jobPostings':[{'jobPostingId':1},{'jobPostingId':1}]})
        with self.assertRaisesRegex(ValueError,'repeated'):ats.dayforce({'url':'https://example.com'},c)

    def test_bamboohr_incomplete_payload_does_not_mean_empty(self):
        c=Mock();c.get.return_value=response({'result':[],'meta':{'totalCount':2}})
        with self.assertRaises(ValueError):ats.bamboohr({'url':'https://example.com/careers'},c)

    def test_adp_preserves_celtics_career_center_in_request_and_links(self):
        s=live.source_from_row({'url':'https://workforcenow.adp.com/recruitment.html?cid=test&ccId=9201173610523_2'})
        c=Mock();c.get.return_value=response({'jobRequisitions':[],'meta':{'totalNumber':0}})
        self.assertEqual(adp.scrape('NBA','Celtics',s['cid'],session=c,ccid=s['ccid']),[])
        self.assertIn('ccId=9201173610523_2',c.get.call_args.args[0])
        self.assertIn('9201173610523_2',s['key'])

    def test_teamwork_organization_filter_remains_distinct(self):
        a=live.source_from_row({'url':'https://www.teamworkonline.com/hockey-jobs/hockeyjobs/nhl?employment_opportunity_search[organization_id]=123'})
        b=live.source_from_row({'url':'https://www.teamworkonline.com/hockey-jobs/hockeyjobs/nhl?employment_opportunity_search[organization_id]=456'})
        self.assertNotEqual(a['key'],b['key']);self.assertEqual(a['org_id'],'123')

    def test_adp_truncated_final_page_fails(self):
        c=Mock();c.get.side_effect=[response({'jobRequisitions':[{'requisitionId':'1','requisitionTitle':'Manager'}],'meta':{'totalNumber':2}}),response({'jobRequisitions':[],'meta':{'totalNumber':2}})]
        with self.assertRaisesRegex(ValueError,'Incomplete'):adp.scrape('NBA','Team','test',session=c)

    def test_adp_server_page_cap_does_not_skip_jobs(self):
        c=Mock();c.get.side_effect=[response({'jobRequisitions':[{'requisitionId':'1','requisitionTitle':'A'}],'meta':{'totalNumber':2}}),response({'jobRequisitions':[{'requisitionId':'2','requisitionTitle':'B'}],'meta':{'totalNumber':2}})]
        self.assertEqual(len(adp.scrape('NBA','Team','test',session=c)),2)
        self.assertIn('$skip=2',c.get.call_args.args[0])

    def test_workday_missing_total_cannot_close_jobs(self):
        with patch.object(live.BoundedSession,'post',return_value=response({'jobPostings':[]})):
            r=live.fetch_source({'key':'wd:test','kind':'workday','host':'example.com','tenant':'test','site':'Careers'})
        self.assertEqual(r['status'],'error');self.assertIn('total',r['error'])

    def test_workday_later_page_zero_total_keeps_first_page_total(self):
        first=[{'title':'Role','externalPath':'/job/NY/'+str(i)} for i in range(20)]
        pages=[response({'total':22,'jobPostings':first}),response({'total':0,'jobPostings':[{'title':'Role','externalPath':'/job/NY/20'},{'title':'Role','externalPath':'/job/NY/21'}]})]
        with patch.object(live.BoundedSession,'post',side_effect=pages):
            r=live.fetch_source({'key':'wd:test','kind':'workday','host':'example.com','tenant':'test','site':'Careers','team':'Mets','league':'MLB'})
        self.assertEqual(r['status'],'success');self.assertEqual(len(r['rows']),22)

    def test_jobvite_loading_page_is_error_not_zero_jobs(self):
        c=Mock();c.get.return_value=response(text='<h1>Loading...</h1>')
        with self.assertRaises(ValueError):ats.jobvite({'url':'https://example.com'},c)

    def test_notification_rejects_broken_workday_link(self):
        with self.assertRaisesRegex(ValueError,'Workday'):pub.embed({'url':'https://mets.wd5.myworkdayjobs.com/job/NY/Role_R1'})

    def test_embed_separates_employer_date_from_delivery_timestamp(self):
        with patch.object(pub,'now_iso',return_value='2026-11-10T12:00:00Z'):
            e=pub.embed({'url':'https://example.com/job','posted_at':'2026-11-03'})
        self.assertEqual(e['timestamp'],'2026-11-10T12:00:00Z')
        self.assertTrue(any(f['name']=='Posted' and f['value'].startswith('2026-11-03') for f in e['fields']))
        self.assertIsNone(pub._iso('Posted 3 Days Ago'))

    def test_notification_save_preserves_seeded_status_and_timestamp(self):
        with patch.dict(os.environ,{'SUPABASE_URL':'https://example.com','SUPABASE_SERVICE_ROLE_KEY':'mock'}):s=cloud_storage.CloudStorage()
        with patch.object(s,'rows',return_value=[{'url':'old','status':'seeded'}]),patch.object(s,'upsert') as up:
            s.save_notification_state({'seen':['old','new'],'posted_at':'now'})
        self.assertEqual(up.call_args.args[1],[{'url':'new','status':'delivered','delivered_at':'now'}])

    def test_baseline_rows_are_never_marked_delivered(self):
        with patch.dict(os.environ,{'SUPABASE_URL':'https://example.com','SUPABASE_SERVICE_ROLE_KEY':'mock'}):s=cloud_storage.CloudStorage()
        with patch.object(s,'rows',return_value=[]),patch.object(s,'upsert') as up:
            s.save_notification_state({'seen':['existing','announced'],'baseline_urls':['existing'],'posted_at':'now'})
        self.assertEqual(up.call_args.args[1],[{'url':'existing','status':'seeded','delivered_at':None},{'url':'announced','status':'delivered','delivered_at':'now'}])

    def test_failed_baseline_summary_keeps_existing_queue(self):
        with patch.object(pub,'load_rows',return_value=[{'url':'https://example.com/job'}]),patch.object(pub,'load_state',return_value={'seen':[]}),patch.object(pub,'guard'),patch.object(pub,'webhook',return_value='mock'),patch.object(pub,'notify',return_value=False),patch.object(pub,'save_state') as save,patch.object(sys,'argv',['publish_teams.py','--baseline']):
            self.assertEqual(pub.main(),1);save.assert_not_called()

    def test_zero_limit_delivers_all_and_acknowledges_each_chunk(self):
        rows=[{'url':'https://example.com/'+str(i),'title':'Role','posted_at':pub.now_iso()} for i in range(27)];snapshots=[]
        with patch.object(pub,'load_rows',return_value=rows),patch.object(pub,'load_state',return_value={'seen':[]}),patch.object(pub,'guard'),patch.object(pub,'webhook',return_value='mock'),patch.object(pub,'notify',return_value=True) as send,patch.object(pub,'save_state',side_effect=lambda s:snapshots.append(json.loads(json.dumps(s)))),patch.object(pub.time,'sleep'),patch.object(sys,'argv',['publish_teams.py','--post','--limit','0']),contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(pub.main(),0)
        self.assertEqual(send.call_count,6);self.assertEqual(len(snapshots[0]['seen']),5);self.assertEqual(len(snapshots[-1]['seen']),27)

    def test_alias_restore_drops_only_stale_local_copy(self):
        con=sqlite3.connect(':memory:');con.executescript(pipeline_local.SCHEMA);self.addCleanup(con.close)
        pipeline_local.ingest(con,[{'url':'https://example.com/old','league':'MLB','team':'Mets','title':'Role'}],False)
        row={'url':'https://example.com/new','league':'MLB','team':'Mets','title':'Role','first_seen_at':'2020-01-01','is_active':True}
        with patch.dict(os.environ,{'SUPABASE_URL':'https://example.com','SUPABASE_SERVICE_ROLE_KEY':'mock'}):s=cloud_storage.CloudStorage()
        with patch.object(s,'rows',side_effect=[[row],[],[{'old_url':'https://example.com/old','canonical_url':row['url']}]]):s.restore(con)
        self.assertEqual(con.execute('select url,first_seen_at from team_jobs').fetchall(),[(row['url'],'2020-01-01')])

    def test_coverage_does_not_claim_all_teams_from_source_count(self):
        r=coverage_report.build([])
        self.assertEqual(r['summary']['teams'],124);self.assertEqual(r['summary']['with_verified_source'],0)

if __name__=='__main__':unittest.main()
