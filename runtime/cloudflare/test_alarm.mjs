import test from 'node:test';
import assert from 'node:assert/strict';
import { JobsScheduler } from './worker.mjs';

test('real Discord acknowledgement is required for incidents and recovery', async () => {
 const scheduler = Object.create(JobsScheduler.prototype);
 scheduler.env = { ALERT_WEBHOOK: 'https://isolated.invalid/sink' };
 let status = 'degraded';
 scheduler.health = () => ({status, overdue: ['test robotics receipt']});
 const original = globalThis.fetch, calls = [], state = {};
 const replies = [new Response(null, {status: 503}), Response.json({}),
    Response.json({id:'123456789000000001',channel_id:'123456789000001111'}),
    new Response(null,{status:429}), Response.json({id:'123456789000000002',channel_id:'123456789000001111'})];
 globalThis.fetch = async (url, options) => {
    assert.equal(String(url), 'https://isolated.invalid/sink?wait=true');
    calls.push(JSON.parse(options.body).content); return replies.shift();
 };
 try {
   const tick = i => scheduler.alert(state, Date.UTC(2026, 10, 17) + i * 300000);
   for (const i of [0,1,2,3]) await tick(i);
   assert.equal(calls.length,2); assert.equal(state.alert.notified_at,null);
   await tick(4); await tick(5);
   assert.equal(calls.length,3); assert.ok(state.alert.notified_at);
   assert.equal(state.last_alert_delivery.message_id,'123456789000000001');
   status='healthy'; await tick(6); assert.ok(state.alert.notified_at);
   await tick(7); assert.equal(state.alert.notified_at,null);
   assert.equal(state.last_alert_delivery.kind,'recovery');
   assert.equal(state.last_alert_delivery.message_id,'123456789000000002');
   await tick(8); assert.equal(calls.length,5);
 } finally { globalThis.fetch = original; }
});
