"""Jobs last seen only by a source that is no longer registered are closed; jobs a registered source lists stay open."""
import sqlite3
import unittest

import live_refresh
import pipeline_local


def row(n):
    return dict(league='NHL', team='Team', title=f'Role {n}', url=f'https://example.com/jobs/{n}')


def result(key, rows, at):
    return dict(source={'kind': 'greenhouse', 'key': key}, rows=rows, status='success', observed_at=at, duration_ms=1, error=None)


class RetiredSources(unittest.TestCase):
    def setUp(self):
        self.con = sqlite3.connect(':memory:')
        self.con.executescript(pipeline_local.SCHEMA)
        self.addCleanup(self.con.close)
        # day 1: an old source lists jobs 1 and 2, a current source lists jobs 2 and 3
        live_refresh.apply_results(self.con, [result('tw:old', [row(1), row(2)], '2026-11-10T13:30:00+00:00'),
                                              result('gh:current', [row(2), row(3)], '2026-11-10T13:31:00+00:00')], pipeline_local)

    def active(self):
        return {r[0].rsplit('/', 1)[1] for r in self.con.execute('select url from team_jobs where is_active=1')}

    def test_without_the_registry_nothing_changes(self):
        live_refresh.apply_results(self.con, [result('gh:current', [row(2), row(3)], '2026-11-18T10:00:00+00:00')], pipeline_local)
        self.assertEqual(self.active(), {'1', '2', '3'})

    def test_job_seen_only_by_an_unregistered_source_closes(self):
        live_refresh.apply_results(self.con, [result('gh:current', [row(2), row(3)], '2026-11-18T10:00:00+00:00')], pipeline_local,
                                   registered_sources={'gh:current'})
        self.assertEqual(self.active(), {'2', '3'})
        closed = self.con.execute("select is_active, closed_at from team_jobs where url like '%/1'").fetchone()
        self.assertEqual(closed[0], 0)
        self.assertTrue(closed[1])

    def test_registered_source_that_failed_keeps_its_jobs_open(self):
        failed = dict(source={'kind': 'greenhouse', 'key': 'gh:current'}, rows=[], status='error', observed_at='2026-11-18T10:00:00+00:00', duration_ms=1, error='timeout')
        live_refresh.apply_results(self.con, [failed], pipeline_local, registered_sources={'gh:current'})
        self.assertEqual(self.active(), {'2', '3'})


if __name__ == '__main__':
    unittest.main()
