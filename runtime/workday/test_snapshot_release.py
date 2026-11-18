import gzip, json, os, tempfile, unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch
import publish_workday as publisher


class Reply:
    def __init__(self, data=None, *, content=None, status=200):
        self.data,self.content,self.status_code=data,content,status
    def json(self):return self.data
    def raise_for_status(self):
        if self.status_code>=400:raise AssertionError(self.status_code)


class ReleaseTests(unittest.TestCase):
    def test_round_trip_and_retention_use_only_our_assets(self):
        now=datetime.now(timezone.utc)
        body=gzip.compress(json.dumps({"schema":1,"observed_at":now.isoformat(),"boards":{"x":{}}}).encode())
        marker="Bounded public snapshots of official team and employer career pages. Managed by the ABET Workday collector."
        sess=MagicMock();sess.__enter__.return_value=sess
        sess.get.return_value=Reply({"tag_name":publisher.TAG,"body":marker,"id":12})
        posted=[];removed=[]
        earlier=[{"name":f"listings-{n}-10.json.gz","id":n,"state":"uploaded"} for n in (1,2,3)]
        def request(method,url,**opts):
            if method=="GET":return Reply(earlier+[{"name":"other-asset","id":52,"state":"uploaded"}])
            if method=="POST":
                posted.append(opts["data"]);return Reply({"id":55,"size":len(body),"state":"uploaded","browser_download_url":"https://isolated.invalid/file"})
            if method=="DELETE":removed.append(url);return Reply({})
            raise AssertionError(method)
        sess.request.side_effect=request
        env={"GITHUB_ACTIONS":"true","GITHUB_REPOSITORY":publisher.REPO,"GITHUB_REF_NAME":"master","GITHUB_RUN_ID":"55","GITHUB_SHA":"dummy","GH_TOKEN":"test"}
        with patch.dict(os.environ,env),patch.object(Path,"read_bytes",return_value=body),patch.object(publisher.requests,"Session",return_value=sess),patch.object(publisher.requests,"get",return_value=Reply(content=body)):
            publisher.main()
        self.assertEqual(posted,[body]);self.assertEqual(removed,[publisher.API+"/releases/assets/1"])

    def test_development_branch_has_no_publication_authority(self):
        with patch.dict(os.environ,{"GITHUB_REF_NAME":"dev"}),self.assertRaises(RuntimeError):
            publisher.main()
