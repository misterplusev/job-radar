"""Exercise the actual BoundedSession dispatch with mocked HTTP."""
import unittest
from unittest.mock import patch
import requests
import live_refresh
from jobradar import workday_http as http

class WorkdayTeamRetry(unittest.TestCase):
    def test_workday_post_enters_policy_other_posts_do_not(self):
        with patch.object(live_refresh, "WorkdayHTTP") as factory:
            with live_refresh.BoundedSession("wd:test") as client:
                client.workday.request.return_value = "workday"
                got = client.post("https://example.wd1.myworkdayjobs.com/wday/cxs/example/External/jobs", json={})
                self.assertEqual(got, "workday")
                client.workday.request.assert_called_once()
                with patch.object(client, "_request_once", return_value=requests.Response()) as other:
                    client.post("https://example.com/write", json={})
                    other.assert_called_once()
                    self.assertEqual(client.workday.request.call_count, 1)
    def test_policy_timeout_tuple_is_accepted_by_bounded_transport(self):
        with live_refresh.BoundedSession("wd:test") as client, patch.object(requests.Session, "request") as send:
            client._request_once("POST", "https://example.wd1.myworkdayjobs.com/wday/cxs/example/External/jobs",
                                 timeout=(10,25))
            self.assertEqual(send.call_args.kwargs["timeout"], (10,25))
