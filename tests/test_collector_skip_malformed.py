"""One posting without a title or job path is skipped and counted; it no longer fails the Workday collection."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


collector = load("browser_full_collection_under_test", "runtime/verification/browser_full_collection.py")
seal = load("seal_under_test", "runtime/workday/seal.py")


def posting(n, title="Role"):
    return {"title": title, "externalPath": f"/job/City/Role_{n}"}


class ListingSkips(unittest.TestCase):
    def test_untitled_posting_is_skipped_and_listing_completes(self):
        listing = collector.Listing()
        listing.accept({"total": 4, "jobPostings": [posting(1), posting(2, title="")]}, 0)
        self.assertFalse(listing.complete)
        listing.accept({"total": 4, "jobPostings": [posting(3), {"title": "No path"}]}, 2)
        self.assertTrue(listing.complete)
        self.assertEqual((len(listing.rows), listing.skipped), (2, 2))

    def test_many_malformed_postings_still_fail(self):
        listing = collector.Listing()
        with self.assertRaises(collector.IncompleteListing):
            listing.accept({"total": 20, "jobPostings": [posting(n, title="") for n in range(4)]}, 0)

    def test_repeated_posting_still_fails(self):
        listing = collector.Listing()
        listing.accept({"total": 4, "jobPostings": [posting(1), posting(2)]}, 0)
        with self.assertRaises(collector.IncompleteListing):
            listing.accept({"total": 4, "jobPostings": [posting(2), posting(3)]}, 2)


class SealAcceptsCountedSkips(unittest.TestCase):
    def build(self, folder, skipped_in_receipt, skipped_in_data):
        catalog = [{"id": f"m:{i}", "host": f"h{i}.example", "tenant": "t", "site": "s"} for i in range(19)]
        sources = []
        for i, src in enumerate(catalog):
            jobs = [posting(n) for n in range(3)]
            skip_r = skipped_in_receipt if i == 0 else 0
            skip_d = skipped_in_data if i == 0 else 0
            sources.append({"id": src["id"], "complete": True, "advertised_total": 3 + skip_r, "collected": 3, "skipped_malformed": skip_r})
            (folder / f"{i:02d}-jobs.json").write_text(json.dumps({"source": src, "advertised_total": 3 + skip_r, "skipped_malformed": skip_d, "jobs": jobs}))
        (folder / "report.json").write_text(json.dumps({"at": "2026-11-18T22:00:00+00:00", "sources": sources, "all_listings_complete": True,
            "cleanup": {"remaining_owned_processes": 0, "passed": True}, "browser_count": 1, "production_writes": 0, "discord_sends": 0}))
        (folder / "catalog.json").write_text(json.dumps(catalog))

    def test_board_with_one_skipped_posting_is_sealed(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            self.build(folder, 1, 1)
            data = seal.seal(folder, folder / "catalog.json")
            self.assertEqual(len(data["boards"]), 19)
            self.assertEqual(data["boards"]["h0.example/t/s"]["total"], 3)

    def test_receipt_and_data_must_agree_on_the_skip_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            self.build(folder, 1, 0)
            with self.assertRaises(AssertionError):
                seal.seal(folder, folder / "catalog.json")


if __name__ == "__main__":
    unittest.main()
