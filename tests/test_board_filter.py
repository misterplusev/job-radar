"""Drift guard for the static board template.

The published board is a single HTML file that reads Supabase directly with the
anon key. Its off-topic deny-list is necessarily duplicated in JavaScript, so it
can silently drift away from the Python source of truth. These tests fail the
build the moment that happens.

Run: python -m unittest discover -s tests
"""
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from jobradar.relevance import _CORP_SUFFIXES, STRICT_TITLE_ONLY_COMPANIES

BOARD = Path(__file__).resolve().parent.parent / "dashboard" / "board_template.html"


def _read_board() -> str:
    return BOARD.read_text(encoding="utf-8")


def _js_array(html: str, name: str):
    m = re.search(re.escape(name) + r"=\[(.*?)\];", html, re.S)
    assert m, f"{name} not found in board template"
    return [x.strip().strip('"') for x in m.group(1).split(",") if x.strip()]


def _js_set(html: str, name: str):
    m = re.search(re.escape(name) + r"=new Set\(\[(.*?)\]\);", html, re.S)
    assert m, f"{name} not found in board template"
    return {x.strip().strip('"') for x in m.group(1).split(",") if x.strip()}


class TestBoardTemplateConsistency(unittest.TestCase):
    def setUp(self):
        self.html = _read_board()

    def test_offtopic_companies_matches_python_source_of_truth(self):
        js = _js_set(self.html, "OFFTOPIC_COMPANIES")
        self.assertEqual(
            js,
            set(STRICT_TITLE_ONLY_COMPANIES),
            "board OFFTOPIC_COMPANIES drifted from relevance.STRICT_TITLE_ONLY_COMPANIES",
        )

    def test_corp_suffixes_matches_python_source_of_truth(self):
        js = _js_array(self.html, "CORP_SUFFIXES")
        self.assertEqual(
            js,
            list(_CORP_SUFFIXES),
            "board CORP_SUFFIXES drifted from relevance._CORP_SUFFIXES",
        )

    def test_offtopic_toggle_exists_and_defaults_on(self):
        self.assertIn('id=offtopic', self.html)
        m = re.search(r"<input type=checkbox id=offtopic([^>]*)>", self.html)
        self.assertTrue(m, "offtopic checkbox markup not found")
        self.assertIn("checked", m.group(1), "off-topic filter must default to ON")

    def test_toggle_is_wired_to_render(self):
        self.assertIn("isOffTopic(d)", self.html)
        m = re.search(r"\[q,loc,src,st,rem([^\]]*)\]\.forEach\(el=>el\.addEventListener\(\"input\",render\)\)", self.html)
        self.assertTrue(m, "input listener registration not found")
        self.assertIn("ofc", m.group(1), "off-topic checkbox not wired to render()")

    def test_figure_regex_separates_lending_from_figure_ai(self):
        m = re.search(r"OFFTOPIC_URL=/(.*)/i;", self.html)
        self.assertTrue(m, "OFFTOPIC_URL regex not found")
        rx = re.compile(m.group(1), re.I)
        self.assertTrue(rx.search("https://job-boards.greenhouse.io/figure/jobs/123"),
                        "mortgage board must be flagged off-topic")
        self.assertFalse(rx.search("https://job-boards.greenhouse.io/figureai/jobs/123"),
                         "Figure AI board must NOT be flagged off-topic")

    def test_board_uses_namespaced_applications_table(self):
        """Both boards used to share legacy public.applications, which comingled
        the robotics and tech modules and defeated the 'fully independent' build."""
        self.assertIn("/rest/v1/robotics_applications", self.html)
        self.assertNotIn('/rest/v1/applications', self.html)

    def test_board_reads_robotics_jobs(self):
        self.assertIn("/rest/v1/robotics_jobs", self.html)


if __name__ == "__main__":
    unittest.main()
