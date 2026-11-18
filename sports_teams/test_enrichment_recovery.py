import sqlite3
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from requests import HTTPError, Response
import enrichment

class EnrichmentRecovery(unittest.TestCase):
    def test_denied_employer_is_deferred_while_others_progress_and_history_is_saved(self):
        db=sqlite3.connect(":memory:")
        db.execute("create table team_jobs(id integer primary key,url text, is_active int,platform text, first_seen_at text,description text,posted_at text)")
        urls=["https://www.teamworkonline.com/a/team/role1","https://www.teamworkonline.com/a/team/role2","https://www.teamworkonline.com/b/club/role3"]
        for i,url in enumerate(urls):
            db.execute("insert into team_jobs values(?,?,1,'teamworkonline',?,'original',null)",(i,url,str(3-i)))
        resp=Response();resp.status_code=403
        def detail(row):
            if '/a/' in row['url']: raise HTTPError("403",response=resp)
            return {"description":"Verified public text "*8,"posted_at":None,"salary":None}
        with patch.object(enrichment,"fetch_detail",side_effect=detail) as fetch:
            a=enrichment.enrich(db,limit=3);self.assertEqual((a['success'],a['error'],a['deferred_this_run'],fetch.call_count),(1,1,1,2))
            b=enrichment.enrich(db,limit=3);self.assertEqual((b['success'],b['error']),(0,1))
            self.assertEqual(enrichment.enrich(db,limit=3)['error'],0)
        self.assertEqual(db.execute("select description from team_jobs where id=0").fetchone()[0],"original")
        self.assertEqual(db.execute("select sum(is_active) from team_jobs").fetchone()[0],3)

    def test_hawks_uses_the_employers_recruiting_tenant(self):
        with patch.object(enrichment,"BoundedSession") as factory:
            client=factory.return_value.__enter__.return_value
            client.get.return_value.json.return_value={"jobPostingInfo":{"jobDescription":"<p>Careers</p>"}}
            enrichment.fetch_detail({"url":"https://wd1.myworkdaysite.com/en-US/recruiting/hawks/External/job/Atlanta/Example_R1"})
            self.assertEqual(client.get.call_args.args[0],"https://wd1.myworkdaysite.com/wday/cxs/hawks/External/job/Atlanta/Example_R1")

    def test_cubs_reads_published_jobposting_in_the_official_page(self):
        with patch.object(enrichment,"BoundedSession") as factory:
            client=factory.return_value.__enter__.return_value
            client.get.return_value.text='<script type="application/ld+json">{"@type":"JobPosting","description":"Verified Cubs description","datePosted":"2026-11-06"}</script>'
            row=enrichment.fetch_detail({"url":"https://my1060wd.wd5.myworkdayjobs.com/Chicago_Cubs_FO/job/Chicago/Example_R2"})
            self.assertEqual(row["description"],"Verified Cubs description")
            self.assertIn("/en-US/Chicago_Cubs_FO/job/",client.get.call_args.args[0])
