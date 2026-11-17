import unittest,time,sys
from unittest.mock import patch
import requests
from network_guard import NetworkBudget,BudgetExceeded
class GuardTests(unittest.TestCase):
 def test_production_and_unapproved_methods_are_blocked(self):
  b=NetworkBudget({'example.myworkdayjobs.com'})
  for method,url in [('POST','https://discord.com/api/webhooks/x'),('GET','https://project.supabase.co/rest/v1/jobs'),('POST','https://example.myworkdayjobs.com/apply'),('GET','http://example.myworkdayjobs.com/')]:
   with self.subTest(url=url),self.assertRaises(BudgetExceeded):b.validate(method,url)
  b.validate('POST','https://example.myworkdayjobs.com/wday/cxs/x/y/jobs')
 def test_request_limit_and_deadline_are_hard(self):
  b=NetworkBudget({'example.myworkdayjobs.com'},max_requests=1);b.count=1
  with self.assertRaises(BudgetExceeded):b.validate('GET','https://example.myworkdayjobs.com/a')
  b.count=0;b.deadline=time.monotonic()-1
  with self.assertRaises(BudgetExceeded):b.validate('GET','https://example.myworkdayjobs.com/a')
 def test_guard_records_status_and_swallowed_budget_violation(self):
  def fake(session,req,**kw):
   r=requests.Response();r.status_code=429;r._content=b'<title>Rate limited</title>';r._content_consumed=True;r.headers={'Retry-After':'900'};return r
  with patch.object(requests.Session,'send',fake):
   b=NetworkBudget({'careers.example'},max_requests=1).install()
   try:
    requests.get('https://careers.example/jobs')
    with self.assertRaises(BudgetExceeded):requests.get('https://careers.example/jobs')
   finally:b.close()
  self.assertEqual(b.count,1);self.assertEqual(b.events[0]['status'],429);self.assertEqual(b.events[0]['retry_after'],'900');self.assertTrue(b.violation)
if __name__=='__main__':unittest.main()
