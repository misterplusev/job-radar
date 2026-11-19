"""One UKG job listed on two job boards of the same employer is stored once, not once per board."""
import sqlite3
import unittest
from unittest import mock

import live_refresh
import pipeline_local

ACCOUNT = 'recruiting.ultipro.com/HOC10001BFLO'
A = '21121b32-5e02-47fe-b087-ed7f2f363892'
B = '4d61dcfa-1b56-4c81-b31a-0e36b69a57fa'
OTHER = 'recruiting2.ultipro.com/HOU1000'


def job_id(n):
    return f'00000000-0000-0000-0000-{n:012d}'


def row(board, n, account=ACCOUNT):
    return dict(league='NHL', team='Buffalo Sabres', title=f'Role {n}',
                url=f'https://{account}/JobBoard/{board}/OpportunityDetail?opportunityId={job_id(n)}')


def result(board, rows, at, status='success', account=ACCOUNT):
    return dict(source={'kind': 'ukg', 'key': f'ukg:{account}/JobBoard/{board}'}, rows=rows if status == 'success' else [],
                status=status, observed_at=at, duration_ms=1, error=None if status == 'success' else 'timeout')


class OneRowPerUkgJob(unittest.TestCase):
    def setUp(self):
        self.con = sqlite3.connect(':memory:')
        self.con.executescript(pipeline_local.SCHEMA)
        self.addCleanup(self.con.close)

    def run_boards(self, *results):
        return live_refresh.apply_results(self.con, list(results), pipeline_local)

    def active(self):
        return sorted((url.split('/JobBoard/')[1][:8], int(url[-12:])) for (url,) in
                      self.con.execute('select url from team_jobs where is_active=1'))

    def test_job_on_two_boards_is_stored_once(self):
        new, _, _ = self.run_boards(result(B, [row(B, 1), row(B, 2)], '2026-11-19T10:00:00+00:00'),
                                    result(A, [row(A, 1), row(A, 3)], '2026-11-19T10:00:01+00:00'))
        self.assertEqual(self.active(), [(A[:8], 1), (A[:8], 3), (B[:8], 2)])   # job 1 once, under the first board in key order
        self.assertEqual(new, 3)

    def test_copies_already_stored_twice_are_reduced_to_one(self):
        # the state measured on 2026-11-19: job 1 stored under both boards
        with mock.patch.object(live_refresh, 'one_row_per_ukg_job', return_value=0):
            self.run_boards(result(A, [row(A, 1)], '2026-11-18T10:00:00+00:00'), result(B, [row(B, 1), row(B, 2)], '2026-11-18T10:00:01+00:00'))
        self.assertEqual(self.active(), [(A[:8], 1), (B[:8], 1), (B[:8], 2)])
        _, _, closed = self.run_boards(result(A, [row(A, 1)], '2026-11-19T10:00:00+00:00'), result(B, [row(B, 1), row(B, 2)], '2026-11-19T10:00:01+00:00'))
        self.assertEqual(self.active(), [(A[:8], 1), (B[:8], 2)])
        self.assertEqual(closed, 1)

    def test_job_stays_with_the_board_that_holds_it_when_that_board_fails(self):
        self.run_boards(result(B, [row(B, 1)], '2026-11-18T10:00:00+00:00'))
        new, _, closed = self.run_boards(result(B, [], '2026-11-19T10:00:00+00:00', status='error'),
                                         result(A, [row(A, 1)], '2026-11-19T10:00:01+00:00'))
        self.assertEqual(self.active(), [(B[:8], 1)])          # no second copy under board A, nothing announced as new
        self.assertEqual((new, closed), (0, 0))

    def test_job_moves_when_its_board_stops_listing_it(self):
        self.run_boards(result(B, [row(B, 1)], '2026-11-18T10:00:00+00:00'))
        self.run_boards(result(B, [], '2026-11-19T10:00:00+00:00'), result(A, [row(A, 1)], '2026-11-19T10:00:01+00:00'))
        self.assertEqual(self.active(), [(A[:8], 1)])

    def test_same_job_number_at_another_employer_is_a_different_job(self):
        self.run_boards(result(A, [row(A, 1)], '2026-11-19T10:00:00+00:00'),
                        result(A, [row(A, 1, account=OTHER)], '2026-11-19T10:00:01+00:00', account=OTHER))
        self.assertEqual(len(self.active()), 2)

    def test_links_of_other_job_systems_are_untouched(self):
        other = dict(league='NHL', team='Team', title='Role', url='https://example.com/jobs/1')
        dropped = live_refresh.one_row_per_ukg_job(self.con, [dict(source={'kind': 'greenhouse', 'key': 'gh:a'}, rows=[other], status='success'),
                                                              dict(source={'kind': 'greenhouse', 'key': 'gh:b'}, rows=[dict(other)], status='success')])
        self.assertEqual(dropped, 0)


if __name__ == '__main__':
    unittest.main()
