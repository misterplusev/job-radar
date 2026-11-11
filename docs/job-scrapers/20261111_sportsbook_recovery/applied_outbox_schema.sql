-- Additive; no historical job backfill and no application-table changes.
create table if not exists public.sportsbook_job_notifications (
  id bigint generated always as identity primary key,
  company text not null,
  job_url text not null,
  payload jsonb not null,
  kind text not null default 'job' check (kind in ('job','verification')),
  state text not null default 'pending'
    check (state in ('pending','sending','delivered','expired','inactive')),
  created_at timestamptz not null default now(),
  available_at timestamptz not null default now(),
  lease_token uuid,
  lease_until timestamptz,
  attempts integer not null default 0,
  last_error text,
  delivered_at timestamptz,
  discord_message_id text,
  discord_channel_id text,
  discord_webhook_id text,
  unique(company,job_url)
);
alter table public.sportsbook_job_notifications enable row level security;
revoke all on public.sportsbook_job_notifications from public,anon,authenticated;
grant select,insert,update on public.sportsbook_job_notifications to service_role;
grant usage,select on sequence public.sportsbook_job_notifications_id_seq to service_role;
create index if not exists sportsbook_notifications_ready_idx
  on public.sportsbook_job_notifications(available_at,id) where state in ('pending','sending');
create index if not exists sportsbook_notifications_lease_idx
  on public.sportsbook_job_notifications(lease_token) where state='sending';
create index if not exists sportsbook_notifications_delivered_idx
  on public.sportsbook_job_notifications(delivered_at desc) where state='delivered';

create or replace function public.claim_sportsbook_notifications(p_token uuid,p_limit integer default 5)
returns setof public.sportsbook_job_notifications
language plpgsql security invoker set search_path=public as $$
begin
  -- Repeating an RPC whose response was lost returns its original claim.
  if exists(select 1 from public.sportsbook_job_notifications where lease_token=p_token and state='sending') then
    return query select * from public.sportsbook_job_notifications
      where lease_token=p_token and state='sending' order by id;
    return;
  end if;
  return query
    with picked as (
      select id from public.sportsbook_job_notifications
      where ((state='pending' and available_at<=now()) or (state='sending' and lease_until<now()))
      order by id for update skip locked limit greatest(1,least(p_limit,5))
    )
    update public.sportsbook_job_notifications q
      set state='sending',lease_token=p_token,lease_until=now()+interval '15 minutes',attempts=q.attempts+1
    from picked where q.id=picked.id returning q.*;
end $$;
revoke all on function public.claim_sportsbook_notifications(uuid,integer) from public,anon,authenticated;
grant execute on function public.claim_sportsbook_notifications(uuid,integer) to service_role;

create or replace function public.sportsbook_notification_status()
returns jsonb language sql security invoker set search_path=public as $$
 select jsonb_build_object(
  'pending',count(*) filter(where state='pending'),
  'sending',count(*) filter(where state='sending'),
  'delivered',count(*) filter(where state='delivered'),
  'expired',count(*) filter(where state='expired'),
  'inactive',count(*) filter(where state='inactive'),
  'retry_pending',count(*) filter(where state in ('pending','sending') and last_error is not null),
  'oldest_pending_at',min(created_at) filter(where state in ('pending','sending')),
  'last_delivered_at',max(delivered_at),
  'latest_delivery',(select jsonb_build_object('message_id',n.discord_message_id,
    'channel_id',n.discord_channel_id,'webhook_id',n.discord_webhook_id,'delivered_at',n.delivered_at)
    from public.sportsbook_job_notifications n where n.state='delivered'
    order by n.delivered_at desc limit 1)) from public.sportsbook_job_notifications;
$$;
revoke all on function public.sportsbook_notification_status() from public,anon,authenticated;
grant execute on function public.sportsbook_notification_status() to service_role;
notify pgrst,'reload schema';
