import test from 'node:test';
import assert from 'node:assert/strict';
import { JobsScheduler } from './worker.mjs';

test('configured central alarm retries, acknowledges, deduplicates and reports recovery', async () => {
  const scheduler = Object.create(JobsScheduler.prototype);
  scheduler.env = { ALERT_WEBHOOK: 'https://isolated.invalid/system-health' };
  let status = 'degraded', accept = false;
  scheduler.health = () => ({status, overdue: ['live test fixture']});
  const calls = [];
  const original = globalThis.fetch;
  globalThis.fetch = async (url, options) => {
    assert.equal(url, scheduler.env.ALERT_WEBHOOK);
    const msg = JSON.parse(options.body).content;
    calls.push(msg);
    return new Response(null, {status: accept ? 204 : 503});
  };
  try {
    let state = {};
    const t = Date.UTC(2026, 10, 17);
    for (const offset of [0, 300000, 600000]) await scheduler.alert(state, t + offset);
    assert.equal(calls.length, 1);
    assert.equal(state.alert.notified_at, null);
    accept = true;
    await scheduler.alert(state, t + 900000);
    assert.ok(state.alert.notified_at);
    assert.match(calls[1], /ABET job scrapers need attention/);
    await scheduler.alert(state, t + 1200000);
    assert.equal(calls.length, 2);
    status = 'healthy';
    await scheduler.alert(state, t + 1500000);
    assert.equal(calls.length, 3);
    assert.match(calls[2], /recovered/);
    assert.equal(state.alert.notified_at, null);
  } finally { globalThis.fetch = original; }
});
