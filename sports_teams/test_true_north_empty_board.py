"""True North's page with no jobs is an empty board; a page with neither jobs nor that statement is a failure."""
import unittest

from providers import official_ats

SOURCE = {'url': 'https://www.tnse.com/join-our-team/'}
JOB = '<a href="https://secure3.entertimeonline.com/ta/6146095.careers?ShowJob=123&x=1">Usher</a>'
EMPTY = '<p>There are no opportunities available at this time.\n Please check back soon for future postings.</p>'


class Page:
    def __init__(self, body):
        self.text, self.url = f'<html><body>{body}</body></html>', SOURCE['url']

    def raise_for_status(self):
        pass


class Client:
    def __init__(self, body):
        self.body = body

    def get(self, url):
        return Page(self.body)


class TrueNorth(unittest.TestCase):
    def test_listed_job_is_read(self):
        jobs = official_ats.tnse(SOURCE, Client(JOB + EMPTY))
        self.assertEqual([(j['title'], j['url']) for j in jobs],
                         [('Usher', 'https://secure3.entertimeonline.com/ta/6146095.careers?ShowJob=123')])

    def test_page_that_says_nothing_is_open_is_an_empty_board(self):
        self.assertEqual(official_ats.tnse(SOURCE, Client(EMPTY * 3)), [])

    def test_page_with_neither_jobs_nor_that_statement_fails(self):
        with self.assertRaises(ValueError):
            official_ats.tnse(SOURCE, Client('<p>Join our team</p>'))


if __name__ == '__main__':
    unittest.main()
