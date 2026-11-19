"""A job from an owner's careers site is shown under the club(s) that site belongs to, and stored once.

2026-11-19: 541 of 1,422 active jobs were stored under an owner or venue name ("Groupe CH", "Maple Leaf Sports &
Entertainment") with no logo, and seven clubs whose owner runs the careers site showed 0 jobs.
"""
import json
import sqlite3
import unittest
from types import SimpleNamespace

import cloud_storage
import live_refresh
import pipeline_local
import publish_teams as pt

CANADIENS = [{'league': 'NHL', 'team': 'Montreal Canadiens'}]
MLSE = [{'league': 'NBA', 'team': 'Toronto Raptors'}, {'league': 'NHL', 'team': 'Toronto Maple Leafs'}]


def row(n, team, league='NHL', registered=None, site='jobs.example.com'):
    return dict(league=league, team=team, title=f'Role {n}', url=f'https://{site}/jobs/{n}', registered_teams=registered or [])


class ShownUnder(unittest.TestCase):
    def test_owner_of_one_club(self):
        team, league, logo, company, teams = pipeline_local.shown_under(pt, row(1, 'Groupe CH', registered=CANADIENS))
        self.assertEqual((team, league, company, teams), ('Montreal Canadiens', 'NHL', 'Groupe CH', None))
        self.assertEqual(logo, pt.LOGO_MAP['NHL:Montreal Canadiens']['logo'])

    def test_owner_of_two_clubs_in_two_leagues(self):
        team, league, logo, company, teams = pipeline_local.shown_under(pt, row(1, 'Maple Leaf Sports & Entertainment', registered=MLSE))
        self.assertEqual((team, league, company), ('Toronto Raptors', 'NBA', 'Maple Leaf Sports & Entertainment'))
        self.assertEqual([(t['league'], t['team']) for t in teams], [('NBA', 'Toronto Raptors'), ('NHL', 'Toronto Maple Leafs')])
        self.assertEqual([t['logo'] for t in teams], [pt.LOGO_MAP['NBA:Toronto Raptors']['logo'], pt.LOGO_MAP['NHL:Toronto Maple Leafs']['logo']])

    def test_site_that_names_the_club_is_unchanged(self):
        team, league, logo, company, teams = pipeline_local.shown_under(pt, row(1, 'Seattle Kraken', registered=[{'league': 'NHL', 'team': 'Seattle Kraken'}]))
        self.assertEqual((team, league, company, teams), ('Seattle Kraken', 'NHL', 'Seattle Kraken', None))
        self.assertTrue(logo)

    def test_a_known_club_on_another_clubs_site_keeps_its_own_name(self):
        # a league or shared portal that names the real employer: the employer wins over the registry
        team, league, _logo, company, teams = pipeline_local.shown_under(pt, row(1, 'Buffalo Bills', league='NFL', registered=[{'league': 'NHL', 'team': 'Buffalo Sabres'}]))
        self.assertEqual((team, league, company, teams), ('Buffalo Bills', 'NFL', 'Buffalo Bills', None))

    def test_a_club_named_in_full_wins_over_the_site_it_is_listed_on(self):
        # the Devils' jobs are on the careers site registered for the 76ers (same owner)
        sixers = [{'league': 'NBA', 'team': 'Philadelphia 76ers'}]
        team, league, logo, company, teams = pipeline_local.shown_under(pt, row(1, 'New Jersey Devils & Prudential Center', league='NBA', registered=sixers))
        self.assertEqual((team, league, company, teams), ('New Jersey Devils', 'NHL', 'New Jersey Devils & Prudential Center', None))
        self.assertEqual(logo, pt.LOGO_MAP['NHL:New Jersey Devils']['logo'])
        team, league, *_ = pipeline_local.shown_under(pt, row(2, 'Miami Dolphins & Hard Rock Stadium', league='NFL', registered=[{'league': 'NFL', 'team': 'Miami Dolphins'}]))
        self.assertEqual((team, league), ('Miami Dolphins', 'NFL'))

    def test_a_site_registered_for_two_clubs_keeps_both_when_its_name_spells_out_only_one(self):
        both = [{'league': 'NBA', 'team': 'New Orleans Pelicans'}, {'league': 'NFL', 'team': 'New Orleans Saints'}]
        _team, _league, _logo, _company, teams = pipeline_local.shown_under(pt, row(1, 'New Orleans Saints & Pelicans', league='NFL', registered=both))
        self.assertEqual([t['team'] for t in teams], ['New Orleans Pelicans', 'New Orleans Saints'])

    def test_an_affiliate_is_shown_under_the_club_whose_site_lists_it(self):
        team, _league, _logo, company, teams = pipeline_local.shown_under(pt, row(1, 'Bakersfield Condors', registered=[{'league': 'NHL', 'team': 'Edmonton Oilers'}]))
        self.assertEqual((team, company, teams), ('Edmonton Oilers', 'Bakersfield Condors', None))

    def test_unknown_name_without_a_registered_club_is_left_as_it_is(self):
        team, _league, logo, company, teams = pipeline_local.shown_under(pt, row(1, 'Some Venue'))
        self.assertEqual((team, logo, company, teams), ('Some Venue', None, 'Some Venue', None))


class Stored(unittest.TestCase):
    def setUp(self):
        self.con = sqlite3.connect(':memory:')
        self.con.executescript(pipeline_local.SCHEMA)
        self.addCleanup(self.con.close)

    def stored(self):
        self.con.row_factory = sqlite3.Row
        return [dict(r) for r in self.con.execute('select * from team_jobs order by url')]

    def test_job_is_stored_once_under_its_club_with_the_owner_kept(self):
        pipeline_local.ingest(self.con, [row(1, 'Groupe CH', registered=CANADIENS), row(2, 'Maple Leaf Sports & Entertainment', registered=MLSE)], record_runs=False)
        one, two = self.stored()
        self.assertEqual((one['team'], one['league'], one['company'], one['teams']), ('Montreal Canadiens', 'NHL', 'Groupe CH', None))
        self.assertEqual((two['team'], two['company']), ('Toronto Raptors', 'Maple Leaf Sports & Entertainment'))
        self.assertEqual([t['team'] for t in json.loads(two['teams'])], ['Toronto Raptors', 'Toronto Maple Leafs'])
        self.assertEqual(len(self.stored()), 2)

    def test_a_job_already_stored_under_the_owner_is_renamed_not_copied(self):
        # the state before the fix: stored under the owner's name, no logo
        pipeline_local.ingest(self.con, [row(1, 'Groupe CH')], record_runs=False)
        self.assertEqual((self.stored()[0]['team'], self.stored()[0]['logo_url']), ('Groupe CH', None))
        new, updated = pipeline_local.ingest(self.con, [row(1, 'Groupe CH', registered=CANADIENS)], record_runs=False)
        rows = self.stored()
        self.assertEqual((new, updated, len(rows)), (0, 1, 1))
        self.assertEqual((rows[0]['team'], rows[0]['company']), ('Montreal Canadiens', 'Groupe CH'))
        self.assertTrue(rows[0]['logo_url'])

    def test_closed_jobs_and_jobs_of_a_failed_source_are_renamed_too(self):
        # stored before the fix under the owner's name; no source lists them in this run
        pipeline_local.ingest(self.con, [row(1, 'Groupe CH'), row(2, 'Maple Leaf Sports & Entertainment'), row(3, 'Seattle Kraken'), row(4, 'Old Venue')], record_runs=False)
        self.con.execute("alter table team_jobs add column source_id text")
        for n, key in ((1, 'canadiens'), (2, 'mlse'), (3, 'kraken'), (4, 'retired')):
            self.con.execute('update team_jobs set source_id=?, is_active=? where url like ?', (key, 0 if n in (1, 4) else 1, f'%/{n}'))
        sources = {'canadiens': {'registered_teams': CANADIENS}, 'mlse': {'registered_teams': MLSE}, 'kraken': {'registered_teams': [{'league': 'NHL', 'team': 'Seattle Kraken'}]}}
        changed = pipeline_local.rename_stored_owner_rows(self.con, pt, sources)
        rows = {r['url'][-1]: r for r in self.stored()}
        self.assertEqual(changed, 2)
        self.assertEqual((rows['1']['team'], rows['1']['company'], rows['1']['is_active']), ('Montreal Canadiens', 'Groupe CH', 0))   # still closed
        self.assertEqual([t['team'] for t in json.loads(rows['2']['teams'])], ['Toronto Raptors', 'Toronto Maple Leafs'])
        self.assertEqual(rows['3']['team'], 'Seattle Kraken')
        self.assertEqual((rows['4']['team'], rows['4']['logo_url']), ('Old Venue', None))                  # its source is no longer registered
        self.assertEqual(pipeline_local.rename_stored_owner_rows(self.con, pt, sources), 0)                 # nothing left to do

    def test_database_copy_carries_owner_and_teams_both_ways(self):
        pipeline_local.ingest(self.con, [row(1, 'Groupe CH', registered=CANADIENS), row(2, 'Maple Leaf Sports & Entertainment', registered=MLSE),
                                         row(3, 'Seattle Kraken')], record_runs=False)
        sent = {}
        self.con.execute('create table team_job_observations (source_id text,url text,is_active integer,observed_at text,primary key(source_id,url))')
        cloud = cloud_storage.CloudStorage.__new__(cloud_storage.CloudStorage)
        cloud.upsert = lambda table, rows, conflict: sent.setdefault(table, []).extend(rows)
        cloud.persist(self.con, [], 'run', 'test')
        by_url = {r['url'][-1]: r for r in sent['team_jobs']}
        self.assertEqual((by_url['1']['team'], by_url['1']['company'], by_url['1']['teams']), ('Montreal Canadiens', 'Groupe CH', None))
        self.assertEqual([t['team'] for t in by_url['2']['teams']], ['Toronto Raptors', 'Toronto Maple Leafs'])     # a list, not text
        self.assertEqual((by_url['3']['team'], by_url['3']['company']), ('Seattle Kraken', 'Seattle Kraken'))
        # and back: a fresh working copy restored from the database holds the same values
        fresh = sqlite3.connect(':memory:')
        self.addCleanup(fresh.close)
        fresh.executescript(pipeline_local.SCHEMA)
        cloud.rows = lambda table, **kw: [dict(r, id=i + 1) for i, r in enumerate(sent['team_jobs'])] if table == 'team_jobs' else []
        cloud.restore(fresh)
        fresh.row_factory = sqlite3.Row
        back = {r['url'][-1]: dict(r) for r in fresh.execute('select * from team_jobs')}
        self.assertEqual((back['1']['team'], back['1']['company']), ('Montreal Canadiens', 'Groupe CH'))
        self.assertEqual([t['team'] for t in json.loads(back['2']['teams'])], ['Toronto Raptors', 'Toronto Maple Leafs'])


class Registry(unittest.TestCase):
    def test_every_source_carries_the_clubs_it_is_registered_for(self):
        sources = live_refresh.build_sources(pt)
        self.assertEqual([(t['league'], t['team']) for t in sources['wd:mlse.wd3.myworkdayjobs.com/MLSE']['registered_teams']],
                         [('NBA', 'Toronto Raptors'), ('NHL', 'Toronto Maple Leafs')])
        self.assertEqual([t['team'] for t in sources['dayforce:groupech/CANDIDATEPORTAL']['registered_teams']], ['Montreal Canadiens'])
        shared = {k for k, s in sources.items() if len(s['registered_teams']) > 1}
        self.assertEqual(len(shared), 4)
        self.assertTrue(all(s['registered_teams'] for s in sources.values()))
        # every registered club has a logo, so no remapped job can end up without one
        for source in sources.values():
            for club in source['registered_teams']:
                self.assertTrue(pt.logo_for(club), club)


class DiscordLine(unittest.TestCase):
    def test_company_field_names_team_and_owner(self):
        base = dict(url='https://jobs.example.com/jobs/1', title='Role', league='NHL')
        self.assertEqual(pt._team_and_owner(dict(base, team='Montreal Canadiens', company='Groupe CH')), 'Montreal Canadiens · Groupe CH')
        self.assertEqual(pt._team_and_owner(dict(base, team='Seattle Kraken', company='Seattle Kraken')), 'Seattle Kraken')
        two = json.dumps([{'league': 'NBA', 'team': 'Toronto Raptors'}, {'league': 'NHL', 'team': 'Toronto Maple Leafs'}])
        self.assertEqual(pt._team_and_owner(dict(base, team='Toronto Raptors', company='Maple Leaf Sports & Entertainment', teams=two)),
                         'Toronto Raptors / Toronto Maple Leafs · Maple Leaf Sports & Entertainment')
        self.assertEqual(pt.embed(dict(base, team='Montreal Canadiens', company='Groupe CH'))['fields'][0]['value'], 'Montreal Canadiens · Groupe CH')


if __name__ == '__main__':
    unittest.main()
