import unittest
from browser_full_collection import Listing,IncompleteListing,acceptance_ok
def payload(total,start,count):return {'total':total,'jobPostings':[{'title':f'Job{i}','externalPath':f'/job/location/role_{i}'} for i in range(start,start+count)]}
class ListingSafety(unittest.TestCase):
    def test_all_pages_required_and_later_zero_total_allowed(self):
        listing=Listing();listing.accept(payload(23,0,20),0);self.assertFalse(listing.complete)
        listing.accept(payload(0,20,3),20);self.assertTrue(listing.complete);self.assertEqual(len(listing.rows),23)
    def test_premature_empty_cannot_close_jobs(self):
        listing=Listing();listing.accept(payload(23,0,20),0)
        with self.assertRaises(IncompleteListing):listing.accept(payload(0,20,0),20)
        self.assertFalse(listing.complete)
    def test_repeated_page_rejected(self):
        listing=Listing();listing.accept(payload(40,0,20),0)
        with self.assertRaises(IncompleteListing):listing.accept(payload(0,0,20),20)
        self.assertFalse(listing.complete)
    def test_changing_total_rejected(self):
        listing=Listing();listing.accept(payload(25,0,20),0)
        with self.assertRaises(IncompleteListing):listing.accept(payload(26,20,6),20)
    def test_invalid_row_not_counted(self):
        listing=Listing()
        with self.assertRaises(IncompleteListing):listing.accept({'total':1,'jobPostings':[{'title':'Job','externalPath':'https://other.example/job'}]},0)
        self.assertFalse(listing.complete)
    def test_true_empty_can_be_complete(self):
        listing=Listing();listing.accept(payload(0,0,0),0);self.assertTrue(listing.complete)
    def test_unexpected_offset_rejected(self):
        with self.assertRaises(IncompleteListing):Listing().accept(payload(10,0,10),20)
    def test_more_rows_than_total_rejected(self):
        with self.assertRaises(IncompleteListing):Listing().accept(payload(1,0,2),0)
    def test_acceptance_requires_all_sources_and_confirmed_cleanup(self):
        report={'sources':[{'complete':True} for _ in range(19)],'cleanup':{'passed':True,'remaining_owned_processes':0},'browser_count':1,'production_writes':0,'discord_sends':0}
        self.assertTrue(acceptance_ok(report,19))
        report['sources'].pop();self.assertFalse(acceptance_ok(report,19))
        report['sources'].append({'complete':True});report['cleanup']['remaining_owned_processes']=1
        self.assertFalse(acceptance_ok(report,19))
if __name__=='__main__':unittest.main()
