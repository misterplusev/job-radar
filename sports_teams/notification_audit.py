"""Read-only notification queue and destination inspection; never sends a message."""
import json
import os
from pathlib import Path
import requests
from cloud_storage import CloudStorage
from publish_teams import _is_recent,embed

store=CloudStorage()
rows=[r for r in store.rows('team_jobs') if r['is_active']]
state=store.rows('team_job_notifications')
seen={r['url'] for r in state if r['status'] in ('delivered','seeded')}
eligible=[r for r in rows if r['url'] not in seen and (_is_recent(r.get('posted_at')) or (not r.get('posted_at') and _is_recent(r.get('first_seen_at'))))]
eligible.sort(key=lambda r:(str(r.get('posted_at') or r.get('first_seen_at') or ''),r['url']),reverse=True)
hook=requests.get(os.environ['DISCORD_WEBHOOK_TEAMS'],timeout=30)
hook.raise_for_status()
report={'active_jobs':len(rows),'recorded_notification_urls':len(seen),
        'seeded':sum(r['status']=='seeded' for r in state),'delivered':sum(r['status']=='delivered' for r in state),
        'last_confirmed_delivery':max((r.get('delivered_at') or '' for r in state if r['status']=='delivered'),default=None),
        'eligible_unannounced':len(eligible),'expected_channel_confirmed':hook.json().get('channel_id')=='1569043665345708344',
        'preview':[{'team':r['team'],'title':r['title'],'url':r['url'],'posted_at':r.get('posted_at')} for r in eligible[:20]],
        'first_message':{'content':'New team jobs discovered: '+str(min(5,len(eligible))),'embeds':[embed(r) for r in eligible[:5]]}}
Path('notification_audit.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k not in ('preview','first_message')}))
