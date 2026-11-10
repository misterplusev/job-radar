"""Supabase persistence matching the other jobs modules; SQLite is a working cache.

No credentials enter logs, snapshots or the public board. Cloud mode fails closed
when persistence fails. URL identity and first observations survive rebuilds.
"""
import json
import os
import sqlite3
import time
import requests

JOB_FIELDS = ('league','team','title','url','location','description','platform','posted_at',
              'first_seen_at','last_seen_at','is_active','closed_at','logo_url','source_id',
              'salary','detail_status','detail_checked_at')


class CloudStorage:
    def __init__(self):
        self.url = os.environ['SUPABASE_URL'].rstrip('/')
        self.key = os.environ['SUPABASE_SERVICE_ROLE_KEY']
        if not self.url.startswith('https://') or not self.key:
            raise ValueError('Supabase configuration missing')

    def request(self, method, table, **kwargs):
        headers = {'apikey':self.key,'Authorization':'Bearer '+self.key,
                   'Prefer':'resolution=merge-duplicates,return=minimal'}
        for attempt in range(3):
            try:
                r = requests.request(method,self.url+'/rest/v1/'+table,headers=headers,timeout=45,**kwargs)
            except requests.RequestException:
                if attempt == 2: raise RuntimeError('Supabase connection failed') from None
                time.sleep(attempt + 1); continue
            if r.status_code in (429,500,502,503,504) and attempt < 2:
                time.sleep(attempt + 1); continue
            if not r.ok:
                raise RuntimeError(f'Supabase {method} {table.split("?")[0]} HTTP {r.status_code}')
            return r

    def rows(self, table):
        result=[]
        for offset in range(0,100000,1000):
            r=self.request('GET',table,params={'select':'*','order':'id.asc','limit':1000,'offset':offset})
            page=r.json()
            if not isinstance(page,list): raise ValueError('Invalid database result')
            result.extend(page)
            if len(page)<1000:return result
        raise ValueError('Database pagination limit reached')

    def upsert(self, table, rows, conflict):
        for pos in range(0,len(rows),100):
            self.request('POST',table,params={'on_conflict':conflict},json=rows[pos:pos+100])

    def restore(self, con):
        rows=self.rows('team_jobs')
        cols={r[1] for r in con.execute('pragma table_info(team_jobs)')}
        for name in ('source_id','salary','detail_status','detail_checked_at'):
            if name not in cols:con.execute(f'alter table team_jobs add column {name} text')
        con.execute('create table if not exists team_job_observations (source_id text,url text,is_active integer,observed_at text,primary key(source_id,url))')
        for row in rows:
            hit=con.execute('select id from team_jobs where url=?',(row['url'],)).fetchone()
            if hit:
                con.execute('update team_jobs set '+','.join(f'{k}=?' for k in JOB_FIELDS)+' where id=?',
                            [row.get(k) for k in JOB_FIELDS]+[hit[0]])
                continue
            fields=','.join(JOB_FIELDS);marks=','.join('?' for _ in JOB_FIELDS)
            updates=','.join(f'{k}=excluded.{k}' for k in JOB_FIELDS if k not in ('url','team'))
            con.execute(f'insert into team_jobs ({fields}) values ({marks}) on conflict(team,url) do update set {updates}',[row.get(k) for k in JOB_FIELDS])
        for row in self.rows('team_job_observations'):
            con.execute('insert or replace into team_job_observations values(?,?,?,?)',[row.get(k) for k in ('source_id','url','is_active','observed_at')])
        # Retire stale local copies only after their canonical cloud row was restored.
        for alias in self.rows('team_job_url_aliases'):
            if con.execute('select 1 from team_jobs where url=?',(alias['canonical_url'],)).fetchone():
                con.execute('delete from team_jobs where url=?',(alias['old_url'],))
                con.execute('delete from team_job_observations where url=?',(alias['old_url'],))
        con.commit()
        # Seed only confirmed historical delivery records, never every scraped URL.
        from pathlib import Path
        seed=Path(__file__).resolve().parent/'data/notification_seed.json'
        if seed.exists() and not self.rows('team_job_notifications'):
            prior=json.loads(seed.read_text(encoding='utf-8'))
            self.upsert('team_job_notifications',[{'url':u,'status':'seeded','delivered_at':prior.get('posted_at')} for u in prior.get('seen',[])],'url')
        return len(rows)

    def persist(self, con, results, run_id, trigger):
        con.row_factory=sqlite3.Row
        rows=[]
        for r in con.execute('select * from team_jobs'):
            d=dict(r);row={k:d.get(k) for k in JOB_FIELDS}
            row.update(company=d['team'],ats=d.get('platform'),scraped_at=d.get('last_seen_at'),is_active=bool(d['is_active']))
            rows.append(row)
        self.upsert('team_jobs',rows,'url')
        obs=[dict(r) for r in con.execute('select * from team_job_observations')]
        for o in obs:o['is_active']=bool(o['is_active'])
        self.upsert('team_job_observations',obs,'source_id,url')
        runs=[dict(run_id=run_id,provider=r['source']['key'],source=r['source']['key'],platform=r['source']['kind'],
             status=r['status'],job_count=len(r['rows']),duration_ms=r['duration_ms'],error_summary=r.get('error'),
             created_at=r['observed_at'],trigger_source=trigger) for r in results]
        self.upsert('team_job_scrape_runs',runs,'run_id,provider')
        return len(rows)

    def notification_state(self):
        rows=self.rows('team_job_notifications')
        return {'schema':'abet.teams.posted.v1','seen':[r['url'] for r in rows if r['status'] in ('delivered','seeded')], 'posts':0}

    def save_notification_state(self,state):
        prior={r['url'] for r in self.rows('team_job_notifications') if r['status'] in ('seeded','delivered')}
        self.upsert('team_job_notifications',[{'url':u,'status':'delivered','delivered_at':state.get('posted_at')} for u in state['seen'] if u not in prior], 'url')
