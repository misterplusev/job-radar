import test from 'node:test';
import assert from 'node:assert/strict';
import worker, { MODULES, JobsScheduler, dueSlot, nextWake } from './worker.mjs';

function fixture(initial = { paused: false, modules: {} }) {
  let stored = structuredClone(initial);
  const state = { storage: { get: async () => structuredClone(stored), put: async (_, value) => { stored = structuredClone(value); }, getAlarm: async () => null, setAlarm: async () => {}, deleteAlarm: async () => {} },
    blockConcurrencyWhile: callback => callback() };
  return { instance: new JobsScheduler(state, { GITHUB_TOKEN: 'fake' }), value: () => stored };
}
const NOW = Date.parse('2026-11-11T06:40:00Z');
test('hourly slots roll back before the scheduled minute', () => {
  assert.equal(dueSlot(Date.parse('2026-11-11T06:08:00Z'), 9), '2026-11-11T05:09:00.000Z');
  assert.equal(dueSlot(NOW, 37), '2026-11-11T06:37:00.000Z');
});
test('slots honour the per-module cadence and stagger', () => {
  // robotics: every 3h on hours 0,3,6...; tech: 1,4,7...; sports_teams: 2,5,8...
  assert.equal(dueSlot(NOW, 9, 3, 0), '2026-11-11T06:09:00.000Z');
  assert.equal(dueSlot(NOW, 37, 3, 1), '2026-11-11T04:37:00.000Z');
  assert.equal(dueSlot(NOW, 23, 3, 2), '2026-11-11T05:23:00.000Z');
  assert.equal(dueSlot(Date.parse('2026-11-11T00:05:00Z'), 9, 3, 0), '2026-11-10T21:09:00.000Z');
  const hours = MODULES.map(m => new Date(dueSlot(NOW, m.minute, m.everyHours, m.hourOffset)).getUTCHours() % 3);
  assert.deepEqual(hours.sort(), [0, 1, 2]);
  for (const m of MODULES) assert.equal(24 % m.everyHours, 0);
});
test('alarm wake includes exact module slots and bounded recovery checks', () => {
  assert.equal(nextWake(Date.parse('2026-11-11T06:08:00Z')), Date.parse('2026-11-11T06:09:00Z'));
  assert.equal(nextWake(Date.parse('2026-11-11T07:36:00Z')), Date.parse('2026-11-11T07:37:00Z'));
  assert.equal(nextWake(Date.parse('2026-11-11T08:22:00Z')), Date.parse('2026-11-11T08:23:00Z'));
  assert.equal(nextWake(Date.parse('2026-11-11T06:36:00Z')), Date.parse('2026-11-11T06:40:00Z'));
  assert.equal(nextWake(NOW), NOW + 300000);
});
test('repeated ticks dispatch once and preserve accepted receipts', async () => {
  const { instance, value } = fixture(); const calls = [];
  instance.github = async (path, body) => { if (body) { calls.push(body); return null; } return { workflow_runs: [] }; };
  await instance.tick('cron', NOW); await instance.tick('cron', NOW + 300000);
  assert.equal(calls.length, 3); assert.equal(value().modules.tech.attempts, 1);
  assert.equal(value().modules.robotics.dispatch_origin, 'cron');
});
test('run title recovery prevents redispatch after lost local acknowledgement', async () => {
  const { instance } = fixture();
  instance.github = async (path, body) => {
    assert.equal(body, undefined);
    const config = MODULES.find(m => path.includes(`repos/${m.repo}/actions/workflows/${m.workflow}/`));
    assert.ok(config);
    return { workflow_runs: [{ id: 1, display_title: `${config.prefix} ${dueSlot(NOW, config.minute, config.everyHours, config.hourOffset)}`, status: 'completed', conclusion: 'success', updated_at: new Date(NOW).toISOString() }] };
  };
  const result = await instance.tick('cron', NOW);
  assert.equal(result.modules.tech.status, 'success');
});
test('an existing running workflow defers dispatch', async () => {
  const { instance } = fixture();
  instance.github = async (path, body) => { assert.equal(body, undefined); return { workflow_runs: [{ status: 'in_progress' }] }; };
  assert.equal((await instance.tick('cron', NOW)).modules.tech.status, 'deferred_running');
});
test('pause performs no GitHub operations', async () => {
  const { instance } = fixture({ paused: true, modules: {} });
  instance.github = async () => { throw new Error('must not call'); };
  assert.equal((await instance.tick('cron', NOW)).paused, true);
});
test('dispatch attempts are bounded and stale health is exposed', async () => {
  const { instance } = fixture(); let calls = 0;
  instance.github = async (path, body) => { if (body) calls++; return body ? null : { workflow_runs: [] }; };
  await instance.tick('cron', NOW); await instance.tick('cron', NOW + 16 * 60000);
  const result = await instance.tick('cron', NOW + 17 * 60000);
  assert.equal(calls, 6);
  assert.equal(instance.health(result, NOW + 3600000).status, 'degraded');
});
test('health allows one full period plus grace before calling a module overdue', () => {
  const { instance } = fixture();
  const modules = Object.fromEntries(MODULES.map(m => [m.id, { last_success: new Date(NOW).toISOString(), error: null }]));
  const state = { paused: false, last_scheduler_tick: new Date(NOW + 3 * 3600000).toISOString(), modules };
  assert.equal(instance.health(state, NOW + 3 * 3600000 + 60000).status, 'healthy');
  state.last_scheduler_tick = new Date(NOW + 4 * 3600000).toISOString();
  assert.equal(instance.health(state, NOW + 4 * 3600000).status, 'degraded');
});
test('sports teams dispatches its own workflow without blocking robotics', async () => {
  const { instance } = fixture(); const writes=[];
  instance.github = async(path, body) => {
    if(body){writes.push({path,body});return null;}
    return { workflow_runs: path.includes('sports-teams.yml') ? [{status:'in_progress'}] : [] };
  };
  const result=await instance.tick('alarm',NOW);
  assert.equal(result.modules.sports_teams.status,'deferred_running');
  assert.equal(writes.length,2);
  assert.ok(writes.every(w=>w.path.includes('pipeline.yml')));
});
test('public mutating endpoints require a control token', async () => {
  const response = await worker.fetch(new Request('https://example/enable', { method: 'POST' }), { CONTROL_TOKEN: 'fake' });
  assert.equal(response.status, 401);
});
