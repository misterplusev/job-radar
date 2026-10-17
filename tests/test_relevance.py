"""Robotics relevance gate tests — run: python -m unittest discover -s tests

No network, no cloud. Guards the #robotics-jobs announce filter against the
regression that let ~4k pure-tech postings through from the big-tech boards.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from jobradar import relevance
from jobradar.publish import _split_relevant

ROBO_DESC = (
    "You will build and ship perception and motion-planning components for our "
    "self-driving stack. Work with lidar and camera sensor fusion, state estimation, "
    "and the local planner on a fleet of autonomous vehicles. Strong C++ and Python "
    "required, ROS2 experience a plus. You will collaborate with the robotics team "
    "on trajectory optimization and closed-loop control of the drive-by-wire actuators."
) * 3


def row(title, description="", company="Acme", posted_at="2099-01-01T00:00:00+00:00"):
    return {"company": company, "title": title, "description": description,
            "url": "https://example.invalid/1", "posted_at": posted_at}


class TestRejectsNoise(unittest.TestCase):
    """Titles that actually showed up in #robotics-jobs from the tech boards."""

    def test_rejects_pure_tech_and_business_roles(self):
        noise = [
            ("Stripe", "Software Engineer, Payments Infrastructure"),
            ("Stripe", "Product Manager, Billing"),
            ("Coinbase", "Financial Analyst, FP&A"),
            ("Coinbase", "Senior Accountant"),
            ("Anthropic", "Research Scientist, Econometrics"),
            ("Anthropic", "Legal Counsel, Commercial"),
            ("Airbnb", "Marketing Manager, Brand"),
            ("Airbnb", "Customer Support Specialist"),
            ("Figma", "Product Designer, Growth"),
            ("Figma", "Technical Writer"),
            ("Databricks", "Recruiter, Technical"),
            ("Databricks", "Staff Software Engineer, Streaming"),
            ("Robinhood", "Compliance Officer"),
            ("Ramp", "FP&A Analyst"),
            ("OpenAI", "Human Resources Business Partner"),
            ("Amazon", "Delivery Driver"),
            ("Amazon", "Warehouse Associate"),
        ]
        for company, title in noise:
            with self.subTest(company=company, title=title):
                self.assertFalse(
                    relevance.is_relevant(title, ROBO_DESC),
                    f"{company}: {title} must not reach #robotics-jobs",
                )

    def test_rejects_weak_title_without_corroboration(self):
        self.assertFalse(relevance.is_relevant("Controls Engineer", ""))
        self.assertFalse(relevance.is_relevant("Controls Engineer", "short blurb"))

    def test_rejects_weak_title_with_uncorroborating_prose(self):
        prose = ("We are looking for a controls engineer to own our internal tooling. "
                 "You will partner with product teams, run quarterly planning, and build "
                 "dashboards. Great communication skills and experience in a fast moving "
                 "environment are what matter most here.") * 3
        self.assertFalse(relevance.is_relevant("Controls Engineer", prose))

    def test_rejects_internships_even_when_robotics_title(self):
        self.assertFalse(relevance.is_relevant("Robotics Engineering Intern", ROBO_DESC))
        self.assertFalse(relevance.is_relevant("Autonomy Intern", ROBO_DESC))

    def test_no_signal_at_all(self):
        self.assertFalse(relevance.is_relevant("Software Engineer", ROBO_DESC))


class TestKeepsRobotics(unittest.TestCase):
    def test_accepts_unambiguous_robotics_titles_without_description(self):
        for title in [
            "Robotics Engineer",
            "Senior Robotics Software Engineer",
            "Autonomy Software Engineer",
            "Autonomous Vehicle Perception Lead",
            "Drone Systems Engineer",
            "Senior Controls Engineer, Motion Planning",
            "SLAM Engineer",
            "Actuator Design Engineer",
            "Humanoid Robotics, Head of Controls",
            "Lidar Perception Engineer",
            "Vehicle Dynamics Engineer",
            "Fleet Autonomy Engineer",
        ]:
            with self.subTest(title=title):
                self.assertTrue(
                    relevance.is_relevant(title, ""),
                    f"{title} must reach #robotics-jobs even with no description",
                )

    def test_accepts_weak_title_backed_by_robotics_description(self):
        for title in [
            "Controls Engineer",
            "Embedded Software Engineer",
            "Firmware Engineer",
            "Computer Vision Engineer",
            "Simulation Engineer",
            "Calibration Engineer",
            "Navigation Engineer",
            "Product Manager, Autonomy",
        ]:
            with self.subTest(title=title):
                self.assertTrue(
                    relevance.is_relevant(title, ROBO_DESC),
                    f"{title} with robotics description must be announced",
                )

    def test_generic_job_families_need_robotics_in_the_title(self):
        """A robotics-flavoured description must not rescue a generic title."""
        for title in [
            "Product Manager, Billing",
            "Research Scientist, Econometrics",
            "Systems Engineer",
            "Solutions Engineer",
            "Staff Software Engineer",
            "Technical Program Manager",
        ]:
            with self.subTest(title=title):
                self.assertFalse(relevance.is_relevant(title, ROBO_DESC))

    def test_deny_beats_allow(self):
        # Robotics words in the description must not rescue a negative title.
        self.assertFalse(relevance.is_relevant("Senior Sales Manager, Robotics", ROBO_DESC))
        self.assertFalse(relevance.is_relevant("Marketing Lead, Autonomy", ROBO_DESC))


class TestStrictTechBoards(unittest.TestCase):
    """The pure-tech boards are in targets.json only for their autonomy teams."""

    def test_weak_title_rejected_on_tech_boards_even_with_robotics_prose(self):
        for company in ["Stripe", "Anthropic", "Coinbase", "Figma", "Airbnb",
                        "Robinhood", "Ramp", "OpenAI", "Databricks"]:
            for title in ["Firmware Engineer", "Controls Engineer",
                          "Embedded Software Engineer", "Computer Vision Engineer"]:
                with self.subTest(company=company, title=title):
                    self.assertFalse(
                        relevance.is_relevant(title, ROBO_DESC, company),
                        f"{company}: {title} must not reach #robotics-jobs",
                    )

    def test_strong_title_still_accepted_on_tech_boards(self):
        for company in ["Stripe", "Anthropic", "OpenAI"]:
            with self.subTest(company=company):
                self.assertTrue(relevance.is_relevant("Robotics Engineer", "", company))
                self.assertTrue(relevance.is_relevant("Autonomy Engineer", "", company))
                self.assertTrue(relevance.is_relevant("Perception Engineer", "", company))

    def test_strict_policy_does_not_apply_to_robotics_boards(self):
        for company in ["Waymo", "Figure AI", "Apptronik", "Boston Dynamics"]:
            with self.subTest(company=company):
                self.assertTrue(relevance.is_relevant("Controls Engineer", ROBO_DESC, company))

    def test_company_matching_tolerates_suffixes_and_case(self):
        for company in ["anthropic", "ANTHROPIC", "Stripe, Inc.", "stripe inc"]:
            with self.subTest(company=company):
                self.assertFalse(relevance.is_relevant("Firmware Engineer", ROBO_DESC, company))


class TestExplain(unittest.TestCase):
    def test_reason_is_actionable(self):
        ok, reason = relevance.explain("Robotics Engineer", "")
        self.assertTrue(ok)
        self.assertTrue(reason.startswith("strong-title:"), reason)

        ok, reason = relevance.explain("Accountant", "")
        self.assertFalse(ok)
        self.assertTrue(reason.startswith("negative:"), reason)

        ok, reason = relevance.explain("Controls Engineer", ROBO_DESC)
        self.assertTrue(ok)
        self.assertIn("weak-title+corroboration:", reason)


class TestSplitRelevant(unittest.TestCase):
    def test_partitions_without_mutating(self):
        rows = [
            row("Robotics Engineer"),
            row("Financial Analyst", company="Coinbase"),
            row("Autonomy Engineer"),
            row("Product Designer", company="Figma"),
        ]
        keep, drop = _split_relevant(rows)
        self.assertEqual([r["title"] for r in keep], ["Robotics Engineer", "Autonomy Engineer"])
        self.assertEqual([r["title"] for r in drop], ["Financial Analyst", "Product Designer"])
        self.assertEqual(len(rows), 4, "input must not be mutated")

    def test_kill_switch_restores_legacy_behaviour(self):
        from jobradar import publish
        original = publish.RELEVANCE_ON
        try:
            publish.RELEVANCE_ON = False
            rows = [row("Financial Analyst"), row("Product Designer")]
            keep, drop = _split_relevant(rows)
            self.assertEqual(len(keep), 2)
            self.assertEqual(drop, [])
        finally:
            publish.RELEVANCE_ON = original


if __name__ == "__main__":
    unittest.main()