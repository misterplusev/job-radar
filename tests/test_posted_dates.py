"""Every provider must give the publisher a posted date it can read.

The publisher announces a new job in Discord only when its posted date is within the last 14 days and is in
ISO form. Lever, Ashby and Workday jobs carried no date and Amazon's was text ("April  2, 2026"), so between
2026-11-11 and 2026-11-19 none of 1,544 new robotics jobs from those four sources was announced.
"""
import os
import unittest
from datetime import datetime, timedelta, timezone
from unittest import mock

os.environ.setdefault("JOBRADAR_MODULE", "robotics")

from jobradar import publish
from jobradar.providers import amazon, ashby, lever, workday


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


class PostedDates(unittest.TestCase):
    def test_lever_uses_created_time(self):
        self.assertEqual(lever.posted_from_ms(1792604051949), "2026-10-21T17:34:11+00:00")
        self.assertIsNone(lever.posted_from_ms(None))
        self.assertIsNone(lever.posted_from_ms("not a number"))
        payload = [{"text": "Engineer", "hostedUrl": "https://jobs.lever.co/x/1", "createdAt": 1792604051949,
                    "categories": {"location": "Remote"}}]
        with mock.patch.object(lever, "http_get", return_value=FakeResponse(payload)):
            jobs = lever.LeverProvider("x").fetch("run")
        self.assertEqual(jobs[0].posted_at, "2026-10-21T17:34:11+00:00")
        self.assertTrue(publish._is_recently_posted(
            lever.posted_from_ms(int(datetime.now(timezone.utc).timestamp() * 1000))))

    def test_ashby_uses_published_time(self):
        payload = {"name": "X", "jobs": [{"title": "Engineer", "jobUrl": "https://jobs.ashbyhq.com/x/1",
                                           "publishedAt": "2026-04-07T17:12:35.753+00:00", "location": "NYC"}]}
        with mock.patch.object(ashby, "http_get", return_value=FakeResponse(payload)):
            jobs = ashby.AshbyProvider("x").fetch("run")
        self.assertEqual(jobs[0].posted_at, "2026-04-07T17:12:35.753+00:00")
        datetime.fromisoformat(jobs[0].posted_at)

    def test_amazon_text_date_becomes_iso(self):
        self.assertEqual(amazon.iso_date("April  2, 2026"), "2026-04-02")
        self.assertEqual(amazon.iso_date("November 19, 2026"), "2026-11-19")
        self.assertEqual(amazon.iso_date("2026-04-02"), "2026-04-02")
        self.assertIsNone(amazon.iso_date(""))
        self.assertIsNone(amazon.iso_date("soon"))
        recent = (datetime.now(timezone.utc) - timedelta(days=3)).strftime("%B %d, %Y")
        self.assertTrue(publish._is_recently_posted(amazon.iso_date(recent)))
        self.assertFalse(publish._is_recently_posted(recent))

    def test_workday_relative_text_becomes_a_date(self):
        seen = "2026-11-19T09:30:00+00:00"
        self.assertEqual(workday.posted_from_relative("Posted Today", seen), "2026-11-19")
        self.assertEqual(workday.posted_from_relative("Posted Yesterday", seen), "2026-11-18")
        self.assertEqual(workday.posted_from_relative("Posted 3 Days Ago", seen), "2026-11-16")
        self.assertEqual(workday.posted_from_relative("Posted 30 Days Ago", seen), "2026-10-20")
        self.assertIsNone(workday.posted_from_relative("Posted 30+ Days Ago", seen))
        self.assertIsNone(workday.posted_from_relative(None, seen))
        self.assertIsNone(workday.posted_from_relative("Posted recently", seen))

    def test_stored_date_is_never_blanked_and_workday_date_never_moves(self):
        row = publish.keep_stored_posted_at({"ats": "workday", "posted_at": None}, {"posted_at": "2026-10-20"})
        self.assertEqual(row["posted_at"], "2026-10-20")
        row = publish.keep_stored_posted_at({"ats": "workday", "posted_at": "2026-10-21"}, {"posted_at": "2026-10-20"})
        self.assertEqual(row["posted_at"], "2026-10-20")
        row = publish.keep_stored_posted_at({"ats": "lever", "posted_at": None}, {"posted_at": "2026-10-20"})
        self.assertEqual(row["posted_at"], "2026-10-20")
        # A source with its own exact date still corrects a stored one (Amazon text to ISO, Greenhouse).
        row = publish.keep_stored_posted_at({"ats": "amazon", "posted_at": "2026-04-02"}, {"posted_at": "April  2, 2026"})
        self.assertEqual(row["posted_at"], "2026-04-02")
        row = publish.keep_stored_posted_at({"ats": "ashby", "posted_at": "2026-04-07"}, None)
        self.assertEqual(row["posted_at"], "2026-04-07")
        row = publish.keep_stored_posted_at({"ats": "ashby", "posted_at": None}, {"posted_at": None})
        self.assertIsNone(row["posted_at"])


if __name__ == "__main__":
    unittest.main()
