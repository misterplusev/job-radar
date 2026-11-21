// Guardrail 3: the Cloudflare account's free Durable Object allowance is used up (2026-11-21).
// storage.get and storage.put throw; setAlarm, getAlarm and deleteAlarm still work.
// Run: node --test runtime/cloudflare/test_scheduler.mjs runtime/cloudflare/test_no_storage.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { MODULES, JobsScheduler, dueSlot, NO_STORAGE_WINDOW_MS } from './worker.mjs';

const LIMIT = 'Exceeded allowed rows read in Durable Objects free tier.';
function blocked(env = {}, storage = {}) {
  const alarms = [];
  const fail = async () => { throw new Error(LIMIT); };
  const state = { storage: { get: fail, put: fail, getAlarm: async () => alarms.at(-1) ?? null,
      setAlarm: async at => { alarms.push(at); }, deleteAlarm: async () => { alarms.push(null); }, ...storage },
    blockConcurrencyWhile: callback => callback() };
  return { instance: new JobsScheduler(state, { GITHUB_TOKEN: 'fake', ...env }), alarms };
}
// A fake GitHub: remembers runs per workflow; a dispatch is recorded and (optionally) becomes a visible run.
function fakeGithub(instance, { visible = true } = {}) {
  const runs = {}; const posts = [];
  instance.github = async (path, body) => {
    const workflow = path.match(/repos\/(.+?)\/actions\/workflows\/([^/]+)\//).slice(1, 3).join(' ');
    runs[workflow] = runs[workflow] || [];
    if (!body) return { workflow_runs: runs[workflow] };
    posts.push({ workflow, slot: body.inputs.scheduler_slot });
    if (visible) {
      const target = [...MODULES, ...MODULES.filter(m => m.deliver).map(m => m.deliver)]
        .find(m => `${m.repo} ${m.workflow}` === workflow);
      runs[workflow].unshift({ id: posts.length, display_title: `${target.prefix} ${body.inputs.scheduler_slot}`, status: 'in_progress', conclusion: null });
    }
    return null;
  };
  return { runs, posts };
}
const TECH = MODULES.find(m => m.id === 'tech');
const SB = MODULES.find(m => m.id === 'sportsbook');
const TECH_SLOT = '2026-11-21T21:37:00.000Z';
const SB_SLOT = '2026-11-21T23:00:00.000Z';
const idleSpace = slot => async (config, path, run) => run ? { started: true }
  : { scrape_running: false, scheduler_slot: { slot, status: 'healthy', ended_at: '2026-11-21T11:02:11.000Z' } };

test('the alarm survives storage that cannot be read and arms the next one', async () => {
  const { instance, alarms } = blocked();
  fakeGithub(instance); instance.space = idleSpace('2026-11-21T11:00:00.000Z');
  const before = Date.now();
  await instance.alarm();                       // must not throw: six throws and Cloudflare drops the alarm
  assert.equal(alarms.length, 1);
  assert.ok(alarms[0] > before && alarms[0] <= before + 300000 + 1000);
  assert.equal(instance.noStorage.reason, LIMIT);
});

test('a tick that fails midway does not end the alarm chain', async () => {
  const alarms = [];
  const state = { storage: { get: async () => ({ paused: false, modules: {} }), put: async () => { throw new Error(LIMIT); },
      getAlarm: async () => null, setAlarm: async at => { alarms.push(at); }, deleteAlarm: async () => {} },
    blockConcurrencyWhile: callback => callback() };
  const instance = new JobsScheduler(state, { GITHUB_TOKEN: 'fake' });
  fakeGithub(instance); instance.space = idleSpace('2026-11-21T11:00:00.000Z');
  await instance.alarm();
  assert.equal(alarms.length, 2);               // the recovery alarm, then the next wake
});

test('without storage a slot that just came due is started once, under its slot name', async () => {
  const { instance } = blocked();
  const { posts } = fakeGithub(instance, { visible: false });   // GitHub accepts but does not list the run yet
  instance.space = idleSpace('2026-11-21T11:00:00.000Z');
  const now = Date.parse(TECH_SLOT) + 1000;
  const memory = await instance.tickWithoutStorage(now, new Error(LIMIT));
  await instance.tickWithoutStorage(now + 179000, new Error(LIMIT));   // 21:40 tick, same instance
  assert.deepEqual(posts, [{ workflow: `${TECH.repo} ${TECH.workflow}`, slot: TECH_SLOT }]);
  assert.equal(memory.modules.tech.status, 'awaiting_run');
  // The other three are hours past their slots: nothing is started for them.
  assert.equal(memory.modules.robotics.status, 'not_started_no_storage');
  assert.equal(memory.modules.sports_teams.status, 'not_started_no_storage');
  assert.equal(memory.modules.sportsbook.status, 'success');
});

test('without storage and without memory, the run name on GitHub prevents a second start', async () => {
  const first = blocked(); const github = fakeGithub(first.instance);
  first.instance.space = idleSpace('2026-11-21T11:00:00.000Z');
  await first.instance.tickWithoutStorage(Date.parse(TECH_SLOT) + 1000, new Error(LIMIT));
  const second = blocked();                     // a new instance: nothing remembered
  second.instance.github = first.instance.github; second.instance.space = first.instance.space;
  const memory = await second.instance.tickWithoutStorage(Date.parse(TECH_SLOT) + 180000, new Error(LIMIT));
  assert.equal(github.posts.length, 1);
  assert.equal(memory.modules.tech.status, 'in_progress');
});

test('without storage a slot older than the window is not started', async () => {
  const { instance } = blocked(); const { posts } = fakeGithub(instance);
  instance.space = idleSpace('2026-11-21T11:00:00.000Z');
  const memory = await instance.tickWithoutStorage(Date.parse(TECH_SLOT) + NO_STORAGE_WINDOW_MS + 1000, new Error(LIMIT));
  assert.equal(posts.length, 0);
  assert.equal(memory.modules.tech.status, 'not_started_no_storage');
});

test('without storage a workflow that is already running defers the slot', async () => {
  const { instance } = blocked(); const { runs, posts } = fakeGithub(instance);
  runs[`${TECH.repo} ${TECH.workflow}`] = [{ id: 9, display_title: 'job-radar workflow_dispatch', status: 'in_progress' }];
  instance.space = idleSpace('2026-11-21T11:00:00.000Z');
  const memory = await instance.tickWithoutStorage(Date.parse(TECH_SLOT) + 1000, new Error(LIMIT));
  assert.equal(posts.length, 0);
  assert.equal(memory.modules.tech.status, 'deferred_running');
});

test('without storage the database circuit breaker still holds every run', async () => {
  const { instance } = blocked(); const { posts } = fakeGithub(instance);
  instance.space = async () => { throw new Error('must not be called'); };
  instance.databaseCheck = async () => ({ ok: false, note: 'HTTP 503' });
  const memory = await instance.tickWithoutStorage(Date.parse(TECH_SLOT) + 1000, new Error(LIMIT));
  assert.equal(posts.length, 0);
  assert.deepEqual(memory.modules, {});
});

test('without storage sportsbook is asked once, then its delivery is started once', async () => {
  const { instance } = blocked({ SPORTSBOOK_DELIVERY: 'on' }); const { posts } = fakeGithub(instance);
  let health = { scrape_running: false, scheduler_slot: { slot: '2026-11-21T11:00:00.000Z', status: 'healthy', ended_at: '2026-11-21T11:02:11.000Z' } };
  const asked = [];
  instance.space = async (config, path, run) => { if (run) { asked.push(path); return { started: true }; } return health; };
  const start = Date.parse(SB_SLOT);
  await instance.tickWithoutStorage(start + 1000, new Error(LIMIT));
  health = { scrape_running: true, current_slot: SB_SLOT, scheduler_slot: health.scheduler_slot };
  let memory = await instance.tickWithoutStorage(start + 60000, new Error(LIMIT));
  assert.equal(memory.modules.sportsbook.status, 'in_progress');
  health = { scrape_running: false, scheduler_slot: { slot: SB_SLOT, status: 'healthy', ended_at: '2026-11-21T23:03:00.000Z' } };
  await instance.tickWithoutStorage(start + 300000, new Error(LIMIT));
  memory = await instance.tickWithoutStorage(start + 600000, new Error(LIMIT));
  assert.deepEqual(asked, [`/api/run?slot=${encodeURIComponent(SB_SLOT)}`]);
  const deliveries = posts.filter(p => p.workflow === `${SB.deliver.repo} ${SB.deliver.workflow}`);
  assert.deepEqual(deliveries, [{ workflow: `${SB.deliver.repo} ${SB.deliver.workflow}`, slot: SB_SLOT }]);
  assert.equal(memory.modules.sportsbook.status, 'success');
  assert.equal(memory.modules.sportsbook.delivery_status, 'in_progress');
  // Tech, robotics and sports teams were not due at 23:00: only the delivery was posted to GitHub.
  assert.equal(posts.length, 1);
});

test('one module failing without storage does not stop the others', async () => {
  const { instance } = blocked(); const { posts } = fakeGithub(instance);
  instance.space = async () => { throw new Error('Space 503 /api/health'); };
  const memory = await instance.tickWithoutStorage(Date.parse(TECH_SLOT) + 1000, new Error(LIMIT));
  assert.equal(posts.length, 1);
  assert.equal(memory.modules.sportsbook.status, 'error');
});

test('/health answers with the reason instead of an uncaught exception', async () => {
  const { instance } = blocked();
  const response = await instance.fetch(new Request('https://scheduler/health'));
  const body = await response.json();
  assert.equal(response.status, 503);
  assert.equal(body.status, 'degraded');
  assert.equal(body.storage, 'unavailable');
  assert.match(body.overdue[0], /Exceeded allowed rows read/);
  assert.equal(body.next_alarm_at, null);
});

test('/enable and /pause still switch the alarm when storage cannot be written', async () => {
  const { instance, alarms } = blocked();
  const on = await instance.fetch(new Request('https://scheduler/enable', { method: 'POST' }));
  assert.equal(on.status, 202);
  assert.equal((await on.json()).alarm, 'armed');
  assert.ok(alarms[0] > Date.now() - 1000);
  const off = await instance.fetch(new Request('https://scheduler/pause', { method: 'POST' }));
  assert.equal((await off.json()).alarm, 'removed');
  assert.equal(alarms.at(-1), null);
});

test('when storage returns, the normal tick finds the runs started without it and starts nothing', async () => {
  let stored = { paused: false, modules: {} };
  const state = { storage: { get: async () => structuredClone(stored), put: async (_, value) => { stored = structuredClone(value); },
      getAlarm: async () => null, setAlarm: async () => {}, deleteAlarm: async () => {} }, blockConcurrencyWhile: callback => callback() };
  const instance = new JobsScheduler(state, { GITHUB_TOKEN: 'fake', SPORTSBOOK_DELIVERY: 'on' });
  const { runs, posts } = fakeGithub(instance);
  const now = Date.parse('2026-11-22T00:05:00Z');
  for (const m of MODULES.filter(m => !m.kind))
    runs[`${m.repo} ${m.workflow}`] = [{ id: 1, display_title: `${m.prefix} ${dueSlot(now, m.minute, m.everyHours, m.hourOffset)}`, status: 'completed', conclusion: 'success', updated_at: '2026-11-21T22:30:00Z' }];
  // job-radar's pipeline.yml list must hold robotics' own slot; sports teams has its own workflow.
  runs[`${SB.deliver.repo} ${SB.deliver.workflow}`] = [{ id: 7, display_title: `${SB.deliver.prefix} ${SB_SLOT}`, status: 'completed', conclusion: 'success', created_at: '2026-11-21T23:05:00Z' }];
  instance.space = async (config, path, run) => { assert.ok(!run); return { scrape_running: false, scheduler_slot: { slot: SB_SLOT, status: 'healthy', ended_at: '2026-11-21T23:03:00.000Z' } }; };
  const result = await instance.tick('alarm', now);
  assert.equal(posts.length, 0);
  assert.equal(result.modules.tech.status, 'success');
  assert.equal(result.modules.sports_teams.status, 'success');
  assert.equal(result.modules.sportsbook.status, 'success');
  assert.equal(result.modules.sportsbook.delivery_status, 'success');
  assert.equal(result.modules.sportsbook.delivery_run_id, 7);
});
