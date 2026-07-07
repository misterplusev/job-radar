"""Core unit tests — run: python -m unittest discover -s tests

Covers the model, prefilter, heuristic scorer, and SQLite storage roundtrip.
No network, no cloud.
"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from jobradar.models import Job
from jobradar.matcher.prefilter import prefilter
from jobradar.matcher.judge import heuristic_score
from jobradar.matcher.profile import CandidateProfile
from jobradar.storage import SQLiteBackend

PROFILE = CandidateProfile(
    text="ML / predictive modeling candidate",
    metros=["seattle", "remote", "denver", "arizona"],
    keywords=["machine learning", "data scientist", "analytics", "python"],
    negatives=["intern", "seasonal", "part-time"],
)


class TestModel(unittest.TestCase):
    def test_dedup_key_normalizes(self):
        a = Job(company="Airbnb, Inc.", title="ML Engineer", url="u1", location="Remote - USA")
        b = Job(company="airbnb inc", title="ml engineer!", url="u2", location="remote  usa")
        self.assertEqual(a.dedup_key(), b.dedup_key())


class TestPrefilter(unittest.TestCase):
    def test_passes_ml_remote(self):
        ok, pf = prefilter("Machine Learning Engineer", "Remote - USA",
                           "build ML models in python", PROFILE)
        self.assertTrue(ok)
        self.assertTrue(pf["remote"])
        self.assertFalse(pf["offshore"])

    def test_drops_offshore(self):
        ok, pf = prefilter("Data Scientist", "Bogotá, Colombia", "analytics", PROFILE)
        self.assertTrue(pf["offshore"])
        self.assertFalse(ok)

    def test_flags_intern(self):
        _, pf = prefilter("Data Science Intern", "Seattle, WA", "internship", PROFILE)
        self.assertTrue(pf["negative"])


class TestHeuristic(unittest.TestCase):
    def test_ml_remote_beats_retail(self):
        _, pf_ml = prefilter("Machine Learning Engineer", "Remote - USA", "deep learning python", PROFILE)
        ml = heuristic_score("Machine Learning Engineer", "Remote - USA", "deep learning python", pf_ml)
        _, pf_retail = prefilter("Retail Associate", "Phoenix, AZ", "cashier", PROFILE)
        retail = heuristic_score("Retail Associate", "Phoenix, AZ", "cashier", pf_retail)
        self.assertGreater(ml["fit_score"], retail["fit_score"])
        self.assertGreaterEqual(ml["fit_score"], 70)

    def test_offshore_penalized(self):
        _, pf = prefilter("Machine Learning Engineer", "London, UK", "ml", PROFILE)
        s = heuristic_score("Machine Learning Engineer", "London, UK", "ml", pf)
        self.assertLess(s["fit_score"], 70)


class TestStorage(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False)
        self.tmp.close()
        self.store = SQLiteBackend(self.tmp.name)

    def test_roundtrip(self):
        jobs = [Job(company="Anthropic", title="ML Engineer", url="https://x/1",
                    location="Remote - USA", description="ml", source="greenhouse")]
        self.assertEqual(self.store.upsert_jobs(jobs), 1)
        # idempotent
        self.store.upsert_jobs(jobs)
        unscored = self.store.fetch_unscored("heuristic")
        self.assertEqual(len(unscored), 1)
        jid = unscored[0]["id"]
        self.store.save_score(jid, {"fit_score": 88, "archetype": "ML", "matched_strengths": [],
                                    "gaps": [], "lead_with": "x", "rationale": "r", "model": "heuristic"})
        self.assertEqual(self.store.fetch_unscored("heuristic"), [])
        alertable = self.store.fetch_alertable(75, "heuristic")
        self.assertEqual(len(alertable), 1)
        self.store.mark_alerted([alertable[0]["score_id"]])
        self.assertEqual(self.store.fetch_alertable(75, "heuristic"), [])
        self.store.upsert_application({"company": "Anthropic", "job_url": "https://x/1",
                                       "job_title": "ML Engineer", "status": "draft"})


if __name__ == "__main__":
    unittest.main()
