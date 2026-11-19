"""One posting without a title or job path is skipped and counted; it no longer fails the Workday collection.
The sealed listing carries such a posting over from the previous listing, so no scraper closes a job still listed."""
import gzip
import importlib.util
import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


collector = load("browser_full_collection_under_test", "runtime/verification/browser_full_collection.py")
seal = load("seal_under_test", "runtime/workday/seal.py")
AT = "2026-11-18T22:00:00+00:00"
BOARD = "h0.example/t/s"


def posting(n, title="Role", fields=None):
    row = {"title": title, "externalPath": f"/job/City/Role_{n}"}
    if fields:
        row["bulletFields"] = fields
    return row


def previous(jobs, at="2026-11-18T10:00:00+00:00"):
    return {"schema": 1, "observed_at": at, "boards": {BOARD: {"total": len(jobs), "jobs": jobs}}}


class ListingSkips(unittest.TestCase):
    def test_untitled_posting_is_skipped_and_listing_completes(self):
        listing = collector.Listing()
        listing.accept({"total": 4, "jobPostings": [posting(1), posting(2, title="")]}, 0)
        self.assertFalse(listing.complete)
        listing.accept({"total": 4, "jobPostings": [posting(3), {"title": "No path", "bulletFields": ["R-9"]}]}, 2)
        self.assertTrue(listing.complete)
        self.assertEqual((len(listing.rows), listing.skipped), (2, 2))

    def test_what_identifies_a_skipped_posting_is_kept(self):
        listing = collector.Listing()
        listing.accept({"total": 3, "jobPostings": [posting(1), posting(2, title=""), {"title": "No path", "bulletFields": ["R-9"]}]}, 0)
        self.assertEqual(listing.skipped_rows, [{"externalPath": "/job/City/Role_2", "bulletFields": None},
                                                {"externalPath": None, "bulletFields": ["R-9"]}])

    def test_many_malformed_postings_still_fail(self):
        listing = collector.Listing()
        with self.assertRaises(collector.IncompleteListing):
            listing.accept({"total": 20, "jobPostings": [posting(n, title="") for n in range(4)]}, 0)

    def test_repeated_posting_still_fails(self):
        listing = collector.Listing()
        listing.accept({"total": 4, "jobPostings": [posting(1), posting(2)]}, 0)
        with self.assertRaises(collector.IncompleteListing):
            listing.accept({"total": 4, "jobPostings": [posting(2), posting(3)]}, 2)


class SealCarriesSkippedPostings(unittest.TestCase):
    def build(self, folder, skipped_in_receipt, skipped_in_data, skipped_rows=None, jobs=None):
        catalog = [{"id": f"m:{i}", "host": f"h{i}.example", "tenant": "t", "site": "s"} for i in range(19)]
        sources = []
        for i, src in enumerate(catalog):
            listed = (jobs if jobs is not None and i == 0 else [posting(n) for n in range(3)])
            skip_r = skipped_in_receipt if i == 0 else 0
            skip_d = skipped_in_data if i == 0 else 0
            sources.append({"id": src["id"], "complete": True, "advertised_total": len(listed) + skip_r, "collected": len(listed), "skipped_malformed": skip_r})
            data = {"source": src, "advertised_total": len(listed) + skip_r, "skipped_malformed": skip_d, "jobs": listed}
            if skipped_rows is not None and i == 0:
                data["skipped"] = skipped_rows
            (folder / f"{i:02d}-jobs.json").write_text(json.dumps(data))
        (folder / "report.json").write_text(json.dumps({"at": AT, "sources": sources, "all_listings_complete": True,
            "cleanup": {"remaining_owned_processes": 0, "passed": True}, "browser_count": 1, "production_writes": 0, "discord_sends": 0}))
        (folder / "catalog.json").write_text(json.dumps(catalog))

    def sealed(self, before, **build):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            self.build(folder, **build)
            return seal.seal(folder, folder / "catalog.json", before)

    def test_board_with_one_skipped_posting_is_sealed(self):
        data = self.sealed({}, skipped_in_receipt=1, skipped_in_data=1)
        self.assertEqual(len(data["boards"]), 19)
        self.assertEqual(data["boards"][BOARD]["total"], 3)

    def test_receipt_and_data_must_agree_on_the_skip_count(self):
        with self.assertRaises(AssertionError):
            self.sealed({}, skipped_in_receipt=1, skipped_in_data=0)

    def test_posting_that_lost_its_title_is_carried_over_with_its_last_title(self):
        before = previous([posting(0), posting(1), posting(2), posting(7, title="Dealer")])
        data = self.sealed(before, skipped_in_receipt=1, skipped_in_data=1, skipped_rows=[{"externalPath": "/job/City/Role_7", "bulletFields": None}])
        board = data["boards"][BOARD]
        self.assertEqual((board["total"], board["carried"], board["held"], board["unidentified"]), (4, 1, 0, 0))
        self.assertIn({"title": "Dealer", "externalPath": "/job/City/Role_7"}, board["jobs"])
        self.assertEqual(data["previous_observed_at"], before["observed_at"])

    def test_posting_without_a_path_is_found_by_its_requisition_fields(self):
        before = previous([posting(0), posting(1), posting(2), posting(7, title="Dealer", fields=["R-7"]), posting(8, fields=["R-8"])])
        data = self.sealed(before, skipped_in_receipt=1, skipped_in_data=1, skipped_rows=[{"externalPath": None, "bulletFields": ["R-7"]}])
        board = data["boards"][BOARD]
        paths = {j["externalPath"] for j in board["jobs"]}
        self.assertEqual((board["carried"], board["held"]), (1, 0))
        self.assertIn("/job/City/Role_7", paths)
        self.assertNotIn("/job/City/Role_8", paths)   # really gone: it leaves the listing as before

    def test_unidentifiable_posting_holds_the_jobs_that_would_leave_for_a_limited_time(self):
        old = (datetime.fromisoformat(AT) - timedelta(days=8)).isoformat()
        recent = (datetime.fromisoformat(AT) - timedelta(days=2)).isoformat()
        before = previous([posting(0), posting(1), posting(2), posting(7), {**posting(8), "held_since": recent}, {**posting(9), "held_since": old}])
        data = self.sealed(before, skipped_in_receipt=1, skipped_in_data=1, skipped_rows=[{"externalPath": None, "bulletFields": None}])
        board = data["boards"][BOARD]
        held = {j["externalPath"]: j.get("held_since") for j in board["jobs"] if "held_since" in j}
        self.assertEqual(held, {"/job/City/Role_7": AT, "/job/City/Role_8": recent})   # Role_9 was held for 8 days: released
        self.assertEqual((board["total"], board["held"], board["unidentified"]), (5, 2, 1))

    def test_old_collector_file_without_details_counts_as_unidentifiable(self):
        before = previous([posting(0), posting(1), posting(2), posting(7)])
        board = self.sealed(before, skipped_in_receipt=1, skipped_in_data=1)["boards"][BOARD]
        self.assertEqual((board["held"], board["unidentified"]), (1, 1))

    def test_new_untitled_posting_holds_nothing(self):
        before = previous([posting(0), posting(1), posting(2), posting(7)])
        board = self.sealed(before, skipped_in_receipt=1, skipped_in_data=1, skipped_rows=[{"externalPath": "/job/City/Brand_New", "bulletFields": None}])["boards"][BOARD]
        self.assertEqual((board["total"], board["carried"], board["held"], board["new_unreadable"]), (3, 0, 0, 1))

    def test_skipped_posting_with_no_readable_previous_listing_publishes_nothing(self):
        def unavailable():
            raise seal.PreviousListingUnavailable("HTTPError: 503")
        with self.assertRaises(seal.PreviousListingUnavailable):
            self.sealed(unavailable, skipped_in_receipt=1, skipped_in_data=1, skipped_rows=[{"externalPath": "/job/City/Role_7", "bulletFields": None}])

    def test_unreadable_previous_listing_does_not_stop_a_clean_collection(self):
        def unavailable():
            raise seal.PreviousListingUnavailable("HTTPError: 503")
        data = self.sealed(unavailable, skipped_in_receipt=0, skipped_in_data=0)
        self.assertEqual(data["boards"][BOARD], {"total": 3, "jobs": [posting(n) for n in range(3)]})
        self.assertNotIn("previous_observed_at", data)

    def test_the_scrapers_reader_accepts_a_listing_with_carried_and_held_jobs(self):
        before = previous([posting(0), posting(1), posting(2), posting(7, title="Dealer"), posting(8)])
        rows = [{"externalPath": "/job/City/Role_7", "bulletFields": None}, {"externalPath": None, "bulletFields": None}]
        now = datetime.now(timezone.utc).isoformat()
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            self.build(folder, 2, 2, skipped_rows=rows)
            report = json.loads((folder / "report.json").read_text())
            report["at"] = now
            (folder / "report.json").write_text(json.dumps(report))
            data = seal.seal(folder, folder / "catalog.json", before)
            (folder / "listing.json.gz").write_bytes(gzip.compress(json.dumps(data).encode()))
            reader = load("workday_snapshot_under_test", "jobradar/workday_snapshot.py")
            with patch.dict(os.environ, {"WORKDAY_LISTINGS_FILE": str(folder / "listing.json.gz")}):
                observed, jobs = reader.board("h0.example", "t", "s")
        self.assertEqual(observed, now)
        self.assertEqual(sorted(j["externalPath"] for j in jobs), [f"/job/City/Role_{n}" for n in (0, 1, 2, 7, 8)])


if __name__ == "__main__":
    unittest.main()
