"""Only a complete reading of a source may close the jobs it does not list (Codex review 2026-11-19, RAD-02, RAD-13)."""
import unittest
from unittest.mock import Mock, patch

from providers import teamwork, ultipro


def ukg_reply(rows, total):
    response = Mock()
    response.json.return_value = {'opportunities': rows, 'totalCount': total}
    return response


def opp(n):
    return {'Id': f'id-{n}', 'Title': f'Role {n}', 'Locations': [], 'BriefDescription': '', 'PostedDate': None}


class CompleteReading(unittest.TestCase):
    def test_ukg_board_that_returns_fewer_rows_than_asked_is_read_to_the_end(self):
        session = Mock()
        pages = {0: [opp(n) for n in range(25)], 25: [opp(n) for n in range(25, 40)]}
        session.post.side_effect = lambda url, json, **kw: ukg_reply(pages.get(json['opportunitySearch']['Skip'], []), 40)
        jobs = ultipro.scrape('NBA', 'Team', 'C', 'G', session=session)
        self.assertEqual(len(jobs), 40)

    def test_ukg_25_of_100_is_refused(self):
        session = Mock()
        session.post.side_effect = lambda url, json, **kw: ukg_reply(
            [opp(n) for n in range(25)] if json['opportunitySearch']['Skip'] == 0 else [], 100)
        with self.assertRaises(ValueError):
            ultipro.scrape('NBA', 'Team', 'C', 'G', session=session)

    def test_teamwork_markup_change_is_not_read_as_no_jobs(self):
        changed = ('<div class="organization-portal__job-title" data-x="1"><span><a data-new="1" class="t" '
                   'href="/jobs/1">Role</a></span></div>')
        org = teamwork.TeamWorkOrg.__new__(teamwork.TeamWorkOrg)
        with patch.object(teamwork, 'pages', return_value=[changed]), patch.object(teamwork, 'org_url', return_value='u'):
            for name in ('league', 'team', 'org_id'):
                try:
                    object.__setattr__(org, name, 'x')
                except Exception:
                    pass
            with self.assertRaises(ValueError) as ctx:
                teamwork.scrape_org(org, session=Mock())
        self.assertIn('not fully read', str(ctx.exception))


if __name__ == '__main__':
    unittest.main()
