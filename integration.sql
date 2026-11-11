-- Transactional integration proof. Never persists fixture rows or sends alerts.
begin;
do $$
declare first_id bigint; token1 uuid:=gen_random_uuid(); token2 uuid:=gen_random_uuid(); claimed integer;
begin
  if exists(select 1 from public.sportsbook_job_notifications) then
    raise exception 'Initial migration integration test requires an empty outbox';
  end if;
  insert into public.sportsbook_job_notifications(company,job_url,payload)
    values('__transactional_outbox_test__','https://example.invalid/outbox-test','{}') returning id into first_id;
  select count(*) into claimed from public.claim_sportsbook_notifications(token1,5);
  if claimed<>1 then raise exception 'First claim did not acquire the fixture'; end if;
  select count(*) into claimed from public.claim_sportsbook_notifications(token1,5);
  if claimed<>1 then raise exception 'Repeated claim lost its idempotency'; end if;
  select count(*) into claimed from public.claim_sportsbook_notifications(token2,5);
  if claimed<>0 then raise exception 'A second worker claimed an active lease'; end if;
  update public.sportsbook_job_notifications set lease_until=now()-interval '1 second' where id=first_id;
  select count(*) into claimed from public.claim_sportsbook_notifications(token2,5);
  if claimed<>1 then raise exception 'Expired claim was not recoverable'; end if;
  update public.sportsbook_job_notifications set state='delivered' where id=first_id;
  select count(*) into claimed from public.claim_sportsbook_notifications(gen_random_uuid(),5);
  if claimed<>0 then raise exception 'Delivered row was claimed again'; end if;
  if has_table_privilege('anon','public.sportsbook_job_notifications','SELECT')
     or has_function_privilege('authenticated','public.claim_sportsbook_notifications(uuid,integer)','EXECUTE') then
    raise exception 'Queue is accessible to a browser role';
  end if;
end $$;
select 'claim_idempotency, concurrent_claim_exclusion, expired_lease_recovery, no_repeat_delivery, restricted_access: passed' as proof;
rollback;
