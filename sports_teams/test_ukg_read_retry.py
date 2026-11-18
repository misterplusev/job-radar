"""The read-only UKG job-search POST is retried on a dropped connection; other POSTs are not."""
import unittest
from unittest.mock import patch
import requests
import live_refresh

UKG = "https://recruiting2.ultipro.com/CLI1008CLDG/JobBoard/6ac22da3-de36-4665-9aa7-6aa44b68601e/JobBoardView/LoadSearchResults"


class UkgReadRetry(unittest.TestCase):
    def test_ukg_search_post_is_retried_after_connection_errors(self):
        ok = requests.Response()
        ok.status_code = 200
        with patch.object(live_refresh.time, "sleep"), live_refresh.BoundedSession("ukg:test") as client:
            with patch.object(client, "_request_once", side_effect=[requests.ConnectionError("reset"), requests.ReadTimeout("slow"), ok]) as once:
                self.assertIs(client.post(UKG, json={}), ok)
                self.assertEqual(once.call_count, 3)

    def test_ukg_search_post_still_fails_after_three_attempts(self):
        with patch.object(live_refresh.time, "sleep"), live_refresh.BoundedSession("ukg:test") as client:
            with patch.object(client, "_request_once", side_effect=requests.ConnectionError("reset")) as once:
                with self.assertRaises(requests.ConnectionError):
                    client.post(UKG, json={})
                self.assertEqual(once.call_count, 3)

    def test_other_posts_are_not_retried(self):
        with patch.object(live_refresh.time, "sleep"), live_refresh.BoundedSession("other:test") as client:
            with patch.object(client, "_request_once", side_effect=requests.ConnectionError("reset")) as once:
                with self.assertRaises(requests.ConnectionError):
                    client.post("https://example.com/write", json={})
                self.assertEqual(once.call_count, 1)


if __name__ == "__main__":
    unittest.main()
