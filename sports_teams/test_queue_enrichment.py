import sqlite3
import unittest
from unittest.mock import patch
from jobradar.workday_http import WorkdayChallenge
import enrichment

class EnrichmentPriority(unittest.TestCase):
    def test_missing_first_challenge_stops_host_and_saved_text_stays_available(self):
        db=sqlite3.connect(":memory:")
        db.execute("create table team_jobs(id integer primary key,url text,is_active int,platform text,first_seen_at text,description text,posted_at text)")
        urls=['https://team.wd5.myworkdayjobs.com/a/job/a','https://team.wd5.myworkdayjobs.com/a/job/b','https://other.wd5.myworkdayjobs.com/a/job/c']
        for i,u in enumerate(urls):
            db.execute("insert into team_jobs values(?,?,1,'workday','2026-11-01',?,null)",(i,u,'verified text '*12 if i==0 else ''))
        seen=[]
        def fetch(row):
            seen.append(row['url'])
            if row['url']==urls[1]:raise WorkdayChallenge('restricted')
            return dict(description='official detail '*10,posted_at=None,salary=None)
        with patch.object(enrichment,'fetch_detail',side_effect=fetch):
            result=enrichment.enrich(db,limit=5)
        self.assertNotIn(urls[0],seen)
        self.assertEqual(result['missing_descriptions'],1)
        self.assertEqual(result['retained_descriptions_pending_refresh'],1)
        self.assertEqual(db.execute("select detail_status from team_jobs where id=1").fetchone()[0],'forbidden')
