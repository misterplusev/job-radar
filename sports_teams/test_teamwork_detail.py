import unittest

from teamwork_detail import detail
from publish_teams import _clean_text

URL = 'https://www.teamworkonline.com/baseball-jobs/atlanta-braves/atlanta-braves-jobs/event-captain-2194349'
BODY = 'Coordinate event staff, brief the assigned crew and review operational checklists before each gate opens.'
TITLE = 'Event Captain'


class TeamWorkDetail(unittest.TestCase):
    def read(self, page, final=URL):
        return detail(page, URL, final, TITLE, _clean_text)

    def test_verified_semantic_region_without_json_ld_preserves_only_employer_text(self):
        html = '<h1>Atlanta Braves</h1><main><h1>Event Captain</h1><section aria-labelledby="jd"><h2 id="jd">Job description</h2><p>'+BODY+'</p><form>Apply now</form></section></main>'
        self.assertEqual(self.read(html), {'title': TITLE, 'description': BODY})

    def test_canonical_redirect_unrelated_organization_and_ad_text_are_rejected(self):
        for html, final in [
            ('<h1>Event Captain</h1><p>'+BODY+'</p>', URL),
            ('<h1>Different job</h1><div id="job-description">'+BODY+'</div>',URL),
            ('<h1>Event Captain</h1><div id="job-description">'+BODY+'</div>', URL[:-1]+'8'),
            ('<link rel="canonical" href="'+URL[:-1]+'8"><h1>Event Captain</h1><div id="job-description">'+BODY+'</div>', URL),
            ('<h1>Event Captain</h1><aside><div itemprop="description">'+BODY+'</div></aside>',URL),
            ('<h1>Event Captain</h1><div itemtype="https://schema.org/Organization"><div itemprop="description">'+BODY+'</div></div>',URL),
            ('<h1>Event Captain</h1><div id="job-description">'+BODY+'</div><div data-testid="job-description">Something else. '+BODY+'</div>',URL)]:
            with self.subTest(html=html,final=final), self.assertRaises(ValueError):
                self.read(html,final)

    def test_select_exact_job_from_graph_and_preserve_salary(self):
        import json
        item = {'@type':'JobPosting','title':TITLE,'url':URL,'description':BODY,'baseSalary':{'currency':'USD'}}
        wrong = {**item,'title':'Different job','description':'Unrelated job details '*8}
        html = '<script type="application/ld+json">'+json.dumps({'@graph':[item,wrong]})+'</script>'
        self.assertEqual(self.read(html),item)
