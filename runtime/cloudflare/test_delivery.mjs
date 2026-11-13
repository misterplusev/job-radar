// Sportsbook Discord delivery is a GitHub workflow started by the scheduler after each sportsbook slot.
// Run: node --test runtime/cloudflare/test_scheduler.mjs runtime/cloudflare/test_guardrails.mjs runtime/cloudflare/test_delivery.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { MODULES, JobsScheduler, dueSlot } from './worker.mjs';

const NOW = Date.parse('2026-11-11T06:40:00Z');
const SB = MODULES.find(m => m.id === 'sportsbook');
const SLOT = dueSlot(NOW, SB.minute, SB.everyHours, SB.hourOffset);
const DISPATCH = 'repos/misterplusev/job-radar/actions/workflows/sportsbook-deliver.yml/dispatches';

function fixture(env = {}, slotStatus = 'healthy') {
  let stored = { paused: false, modules: {} };
  const state = { storage: { get: async () => structuredClone(stored), put: async (_, value) => { stored = structuredClone(value); }, getAlarm: async () => null, setAlarm: async () => {}, deleteAlarm: async () => {} },
    blockConcurrencyWhile: callback => callback() };
  const instance = new JobsScheduler(state, { GITHUB_TOKEN: 'fake', ...env });
  const calls = { dispatch: [], lookups: 0, runs: [], failDispatch: 0 };
  instance.github = async (path, body) => {
    if (path === DISPATCH) {
      if (calls.failDispatch > 0) { calls.failDispatch--; throw new Error('GitHub 502 dispatches'); }
      calls.dispatch.push(body); return null;
    }
    if (path.includes('sportsbook-deliver.yml/runs')) { calls.lookups++; return { workflow_runs: calls.runs }; }
    return body ? null : { workflow_runs: [{ status: 'in_progress' }] };   // other modules: busy, never dispatched
  };
  instance.space = async (config, path, run = false) => run ? { started: true }
    : { scrape_running: false, scheduler_slot: { slot: SLOT, status: slotStatus, ended_at: new Date(NOW - 60000).toISOString() } };
  return { instance, calls, value: () => stored };
}

test('the module declares one delivery workflow', () => {
  assert.deepEqual(SB.deliver, { repo: 'misterplusev/job-radar', workflow: 'sportsbook-deliver.yml', prefix: 'sportsbook-deliver' });
  assert.equal(MODULES.filter(m => m.deliver).length, 1);
});

test('with the switch off, a finished slot starts no delivery workflow', async () => {
  for (const env of [{}, { SPORTSBOOK_DELIVERY: 'off' }, { SPORTSBOOK_DELIVERY: 'ON' }, { SPORTSBOOK_DELIVERY: 'true' }]) {
    const { instance, calls } = fixture(env);
    await instance.tick('alarm', NOW); await instance.tick('alarm', NOW + 300000);
    assert.equal(calls.dispatch.length, 0);
  }
});

test('with the switch on, a finished slot starts delivery exactly once, labelled with the slot', async () => {
  const { instance, calls, value } = fixture({ SPORTSBOOK_DELIVERY: 'on' });
  for (let i = 0; i < 4; i++) await instance.tick('alarm', NOW + i * 300000);
  assert.equal(calls.dispatch.length, 1);
  assert.deepEqual(calls.dispatch[0], { ref: 'master', inputs: { scheduler_slot: SLOT, trigger_source: 'cloudflare' } });
  assert.equal(value().modules.sportsbook.status, 'success');
  assert.equal(value().modules.sportsbook.delivery_status, 'awaiting_run');
});

test('a degraded or failed scrape still drains what was queued', async () => {
  for (const status of ['degraded', 'failed']) {
    const { instance, calls } = fixture({ SPORTSBOOK_DELIVERY: 'on' }, status);
    await instance.tick('alarm', NOW);
    assert.equal(calls.dispatch.length, 1);
  }
});

test('a refused dispatch is retried once and then reported', async () => {
  const { instance, calls, value } = fixture({ SPORTSBOOK_DELIVERY: 'on' });
  calls.failDispatch = 5;
  for (let i = 0; i < 4; i++) await instance.tick('alarm', NOW + i * 300000);
  assert.equal(calls.dispatch.length, 0);
  assert.equal(value().modules.sportsbook.delivery_attempts, 2);
  assert.match(value().modules.sportsbook.error, /could not be started/);
});

test('the delivery run result is recorded, and a failed delivery is reported as a problem', async () => {
  const { instance, calls, value } = fixture({ SPORTSBOOK_DELIVERY: 'on' });
  await instance.tick('alarm', NOW);
  calls.runs = [{ id: 77, display_title: `sportsbook-deliver ${SLOT}`, status: 'in_progress', conclusion: null }];
  await instance.tick('alarm', NOW + 300000);
  assert.equal(value().modules.sportsbook.delivery_status, 'in_progress');
  calls.runs = [{ id: 77, display_title: `sportsbook-deliver ${SLOT}`, status: 'completed', conclusion: 'failure' }];
  const result = await instance.tick('alarm', NOW + 600000);
  assert.equal(result.modules.sportsbook.delivery_status, 'failure');
  assert.equal(result.modules.sportsbook.error, 'Delivery run 77 completed failure');
  assert.ok(instance.health(result, NOW + 600000).overdue.some(item => item.includes('Delivery run 77')));
  const lookups = calls.lookups;
  await instance.tick('alarm', NOW + 900000);
  assert.equal(calls.lookups, lookups);                 // finished: no more polling
  assert.equal(calls.dispatch.length, 1);               // and never re-sent by the scheduler
});

test('a successful delivery leaves the module healthy', async () => {
  const { instance, calls, value } = fixture({ SPORTSBOOK_DELIVERY: 'on' });
  await instance.tick('alarm', NOW);
  calls.runs = [{ id: 78, display_title: `sportsbook-deliver ${SLOT}`, status: 'completed', conclusion: 'success' }];
  await instance.tick('alarm', NOW + 300000);
  assert.equal(value().modules.sportsbook.delivery_status, 'success');
  assert.equal(value().modules.sportsbook.error, null);
});
