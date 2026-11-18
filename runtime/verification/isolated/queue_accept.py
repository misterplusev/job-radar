"""Exercise the real PostgREST queue with aged, closed, eligible and protected rows."""
import datetime as dt
import json
import os
import sys
from pathlib import Path
from unittest.mock import patch
from isolated_services import ROOT, BASE, services, rest, messages

def main():
    with services():
        sys.path.insert(0,str(ROOT/'sports_teams'))
        from cloud_storage import CloudStorage
        import notification_queue as policy
        from publish_teams import POSTED_DAYS_MAX
        with patch.dict(os.environ, {'SUPABASE_URL':'https://isolated.invalid'}):
            store=CloudStorage()
        store.url=BASE
        now=dt.datetime.now(dt.timezone.utc)
        old=(now-dt.timedelta(days=30)).isoformat()
        new=(now-dt.timedelta(days=1)).isoformat()
        rows=[];ledger=[]
        def add(key, active, date, state='pending', receipt=None, present=True):
            url='https://example.org/job/'+key
            if present:
                rows.append({'url':url,'league':'NBA','team':'Proof','company':'Proof','title':key,'is_active':active,'first_seen_at':new,'posted_at':date})
            ledger.append({'url':url,'status':state,'discord_message_id':receipt})
        for i in range(635):add('old'+str(i),True,old)
        for i in range(138):add('closed'+str(i),False,new)
        add('ready',True,new);add('was_closed',True,new,'closed')
        add('already_delivered',False,old,'delivered','123')
        add('existing_receipt',False,old,'pending','456')
        add('seeded',False,old,'seeded');add('unpublished',True,new,present=False)
        add('date_unknown',True,'date not supplied');add('use_discovery',True,None)
        store.upsert('team_jobs',rows,'url');store.upsert('team_job_notifications',ledger,'url')
        expected={'pending_to_expired':635,'pending_to_closed':138,'closed_to_pending':1}
        preview=policy.reconcile(store,POSTED_DAYS_MAX,as_of=now)
        assert preview['transitions']==expected and not preview['changed_ids'],preview
        applied=policy.reconcile(store,POSTED_DAYS_MAX,apply=True,as_of=now)
        assert {k:len(v) for k,v in applied['changed_ids'].items()}==expected,applied
        assert not policy.reconcile(store,POSTED_DAYS_MAX,apply=True,as_of=now)['transitions']
        state={r['url'].rsplit('/',1)[-1]:r for r in store.rows('team_job_notifications')}
        assert state['already_delivered']['discord_message_id']=='123' and state['already_delivered']['status']=='delivered'
        assert state['existing_receipt']['discord_message_id']=='456' and state['seeded']['status']=='seeded'
        assert all(state[k]['status']=='pending' for k in ('ready','was_closed','unpublished','date_unknown','use_discovery','existing_receipt'))
        assert len(state)==len(ledger) and not messages
        receipt={'before_rows':len(ledger),'after_rows':len(state),'changes':expected,'replay_changes':0,'orphan_retained':True,'existing_receipts_preserved':True,'sends':0,'production_writes':0}
        print(receipt);(ROOT/'proof'/'queue.json').write_text(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
