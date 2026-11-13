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
  // every 4h: robotics hours 0,4,8...; tech 1,5,9...; sports_teams 2,6,10...; sportsbook 3,7,11...
  assert.equal(dueSlot(NOW, 9, 4, 0), '2026-11-11T04:09:00.000Z');
  assert.equal(dueSlot(NOW, 37, 4, 1), '2026-11-11T05:37:00.000Z');
  assert.equal(dueSlot(NOW, 23, 4, 2), '2026-11-11T06:23:00.000Z');
  assert.equal(dueSlot(NOW, 0, 4, 3), '2026-11-11T03:00:00.000Z');
  assert.equal(dueSlot(Date.parse('2026-11-11T00:05:00Z'), 9, 4, 0), '2026-11-10T20:09:00.000Z');
  assert.deepEqual(MODULES.map(m => m.id), ['robotics', 'tech', 'sports_teams', 'sportsbook']);
  // One scheduler, one cadence, and no two modules share an hour.
  assert.deepEqual(MODULES.map(m => m.everyHours), [4, 4, 4, 4]);
  assert.deepEqual(MODULES.map(m => m.hourOffset).sort(), [0, 1, 2, 3]);
  const used = new Set();
  for (const m of MODULES) for (let h = m.hourOffset; h < 24; h += m.everyHours) { assert.ok(!used.has(h)); used.add(h); }
  assert.equal(used.size, 24);
  for (const m of MODULES) assert.equal(24 % m.everyHours, 0);
});
test('alarm wake includes exact module slots and bounded recovery checks', () => {
  assert.equal(nextWake(Date.parse('2026-11-11T08:08:00Z')), Date.parse('2026-11-11T08:09:00Z'));
  assert.equal(nextWake(Date.parse('2026-11-11T09:36:00Z')), Date.parse('2026-11-11T09:37:00Z'));
  assert.equal(nextWake(Date.parse('2026-11-11T10:22:00Z')), Date.parse('2026-11-11T10:23:00Z'));
  assert.equal(nextWake(Date.parse('2026-11-11T10:58:00Z')), Date.parse('2026-11-11T11:00:00Z'));
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
  const state = { paused: false, last_scheduler_tick: new Date(NOW + 4 * 3600000).toISOString(), modules };
  assert.equal(instance.health(state, NOW + 4 * 3600000 + 60000).status, 'healthy');
  state.last_scheduler_tick = new Date(NOW + 5 * 3600000).toISOString();
  assert.equal(instance.health(state, NOW + 5 * 3600000).status, 'degraded');
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

// ---- sportsbook: same scheduler, started over HTTP on its Hugging Face Space ----
const SB = MODULES.find(m => m.id === 'sportsbook');
const SB_SLOT = dueSlot(NOW, SB.minute, SB.everyHours, SB.hourOffset);
function spaceFixture(health) {
  const made = fixture(); const calls = [];
  made.instance.github = async (path, body) => body ? null : { workflow_runs: [{ status: 'in_progress' }] };
  made.instance.space = async (config, path, run = false) => {
    calls.push({ id: config.id, path, run });
    return run ? { started: true } : health();
  };
  return { ...made, calls };
}
test('sportsbook is asked to run once per slot, with the slot as its receipt', async () => {
  const { instance, calls, value } = spaceFixture(() => ({ scrape_running: false, scheduler_slot: null }));
  await instance.tick('alarm', NOW); await instance.tick('alarm', NOW + 300000);
  const runs = calls.filter(c => c.run);
  assert.equal(runs.length, 1);
  assert.equal(runs[0].path, `/api/run?slot=${encodeURIComponent(SB_SLOT)}`);
  assert.equal(value().modules.sportsbook.attempts, 1);
  assert.equal(value().modules.sportsbook.status, 'awaiting_run');
});
test('sportsbook slot is complete when the Space reports that slot finished', async () => {
  const ended = new Date(NOW - 60000).toISOString();
  const { instance, calls } = spaceFixture(() => ({ scrape_running: false, scheduler_slot: { slot: SB_SLOT, status: 'healthy', ended_at: ended } }));
  const result = await instance.tick('alarm', NOW);
  assert.equal(result.modules.sportsbook.status, 'success');
  assert.equal(result.modules.sportsbook.last_success, ended);
  assert.equal(calls.filter(c => c.run).length, 0);
});
test('a sportsbook run that ended degraded or failed is reported, not retried', async () => {
  const { instance, calls } = spaceFixture(() => ({ scrape_running: false, scheduler_slot: { slot: SB_SLOT, status: 'failed', ended_at: new Date(NOW).toISOString() } }));
  const result = await instance.tick('alarm', NOW);
  assert.equal(result.modules.sportsbook.status, 'failed');
  assert.match(result.modules.sportsbook.error, /ended failed/);
  assert.equal(calls.filter(c => c.run).length, 0);
});
test('a running sportsbook scrape defers the request and keeps the last success', async () => {
  const made = fixture({ paused: false, modules: { sportsbook: { slot: 'older', attempts: 1, last_success: '2026-11-11T03:16:00.000Z' } } });
  made.instance.github = async (path, body) => body ? null : { workflow_runs: [{ status: 'in_progress' }] };
  let ran = 0;
  made.instance.space = async (config, path, run = false) => { if (run) ran++; return { scrape_running: true, current_slot: null, scheduler_slot: null }; };
  const result = await made.instance.tick('alarm', NOW);
  assert.equal(result.modules.sportsbook.status, 'deferred_running');
  assert.equal(result.modules.sportsbook.last_success, '2026-11-11T03:16:00.000Z');
  assert.equal(ran, 0);
});
test('sportsbook requests are bounded at two per slot', async () => {
  const { instance, calls } = spaceFixture(() => ({ scrape_running: false, scheduler_slot: null }));
  const start = Date.parse('2026-11-11T03:00:00Z');  // all three ticks fall in the 03:00 slot
  await instance.tick('alarm', start); await instance.tick('alarm', start + 16 * 60000);
  const result = await instance.tick('alarm', start + 32 * 60000);
  assert.equal(calls.filter(c => c.run).length, 2);
  assert.equal(result.modules.sportsbook.status, 'failed');
});
test('an unconfigured or unreachable Space does not block the other three', async () => {
  const { instance } = fixture(); const writes = [];
  instance.github = async (path, body) => { if (body) { writes.push(path); return null; } return { workflow_runs: [] }; };
  const result = await instance.tick('alarm', NOW);
  assert.equal(writes.length, 3);
  assert.equal(result.modules.sportsbook.status, 'error');
  assert.match(result.modules.sportsbook.error, /SPORTSBOOK_SPACE_URL is not configured/);
});
test('Space requests carry the read token and run token, and never put them in errors', async () => {
  const { instance } = fixture();
  instance.env = { SPORTSBOOK_SPACE_URL: 'https://space.example/', SPACE_READ_TOKEN: 'read-secret', SPACE_RUN_TOKEN: 'run-secret' };
  const seen = []; const original = globalThis.fetch;
  globalThis.fetch = async (url, init) => { seen.push({ url, init }); return new Response('{}', { status: seen.length === 1 ? 200 : 500 }); };
  try {
    await instance.space(SB, '/api/run?slot=x', true);
    await assert.rejects(() => instance.space(SB, '/api/health'), error => !/secret/.test(error.message) && /Space 500 \/api\/health/.test(error.message));
  } finally { globalThis.fetch = original; }
  assert.equal(seen[0].url, 'https://space.example/api/run?slot=x');
  assert.equal(seen[0].init.method, 'POST');
  assert.equal(seen[0].init.headers.Authorization, 'Bearer read-secret');
  assert.equal(seen[0].init.headers['X-Run-Token'], 'run-secret');
  assert.equal(seen[1].init.headers['X-Run-Token'], undefined);
});
