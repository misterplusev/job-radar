// Guardrail 4: storage can be READ but not WRITTEN (the account's stored-data limit is reached, or the daily
// rows-written allowance is used up). storage.get answers with the last saved record; storage.put throws.
// Run: node --test runtime/cloudflare/test_scheduler.mjs runtime/cloudflare/test_no_storage.mjs runtime/cloudflare/test_write_blocked.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { MODULES, JobsScheduler, WRITE_ALERT_EVERY_MS, writeAlertDue } from './worker.mjs';

const FULL = 'database or disk is full: SQLITE_FULL';
const TECH = MODULES.find(m => m.id === 'tech');
const SB = MODULES.find(m => m.id === 'sportsbook');
const TECH_SLOT = '2026-11-21T21:37:00.000Z';
const SB_SLOT = '2026-11-21T23:00:00.000Z';

// Last record saved before writes stopped: every module succeeded on its morning slot.
const saved = () => ({ paused: false, last_tick: '2026-11-21T17:55:00.000Z', last_scheduler_tick: '2026-11-21T17:55:00.000Z',
  modules: { tech: { slot: '2026-11-21T09:37:00.000Z', status: 'success', attempts: 1, last_success: '2026-11-21T09:38:01Z' } } });

function readOnly(env = {}, { record = saved(), alarm = null, setAlarmFails = false } = {}) {
  const alarms = alarm === null ? [] : [alarm];
  const puts = [];
  const state = { storage: {
      get: async () => (record ? structuredClone(record) : undefined),
      put: async (key, value) => { puts.push(key); throw new Error(FULL); },
      getAlarm: async () => alarms.at(-1) ?? null,
      setAlarm: async at => { if (setAlarmFails) throw new Error(FULL); alarms.push(at); },
      deleteAlarm: async () => { alarms.push(null); } },
    blockConcurrencyWhile: callback => callback() };
  return { instance: new JobsScheduler(state, { GITHUB_TOKEN: 'fake', ...env }), alarms, puts };
}
function fakeGithub(instance, { visible = true } = {}) {
  const runs = {}; const posts = [];
  instance.github = async (path, body) => {
    const workflow = path.match(/repos\/(.+?)\/actions\/workflows\/([^/]+)\//).slice(1, 3).join(' ');
    runs[workflow] = runs[workflow] || [];
    if (!body) return { workflow_runs: runs[workflow] };
    posts.push({ workflow, slot: body.inputs.scheduler_slot });
    if (visible) {
      const target = [...MODULES, ...MODULES.filter(m => m.deliver).map(m => m.deliver)].find(m => `${m.repo} ${m.workflow}` === workflow);
      runs[workflow].unshift({ id: posts.length, display_title: `${target.prefix} ${body.inputs.scheduler_slot}`, status: 'in_progress', conclusion: null });
    }
    return null;
  };
  return { runs, posts };
}
const idleSpace = slot => async (config, path, run) => run ? { started: true }
  : { scrape_running: false, scheduler_slot: { slot, status: 'healthy', ended_at: '2026-11-21T11:02:11.000Z' } };
const at = (instance, now, work) => { const real = Date.now; Date.now = () => now; return work().finally(() => { Date.now = real; }); };

test('writes blocked: a slot that just came due is still started, once, under its slot name', async () => {
  const { instance, alarms } = readOnly();
  const { posts } = fakeGithub(instance);
  instance.space = idleSpace('2026-11-21T11:00:00.000Z');
  const now = Date.parse(TECH_SLOT) + 2000;
  await at(instance, now, () => instance.alarm());
  assert.deepEqual(posts, [{ workflow: `${TECH.repo} ${TECH.workflow}`, slot: TECH_SLOT }]);
  assert.ok(alarms.at(-1) > now, 'the next alarm is armed');
  // The next tick, in a NEW instance with nothing remembered: the run name on GitHub prevents a second start.
  const second = readOnly();
  second.instance.github = instance.github; second.instance.space = instance.space;
  await at(second.instance, now + 300000, () => second.instance.alarm());
  assert.equal(posts.length, 1);
});

test('writes blocked: the alarm never throws and always arms the next one', async () => {
  const { instance, alarms } = readOnly();
  fakeGithub(instance); instance.space = async () => { throw new Error('Space 503 /api/health'); };
  instance.databaseCheck = async () => { throw new Error('network down'); };
  const before = Date.now();
  await instance.alarm();
  assert.ok(alarms.at(-1) > before && alarms.at(-1) <= before + 300000 + 1000);
});

test('writes blocked: sportsbook is asked once and its Discord delivery is started once', async () => {
  const { instance } = readOnly({ SPORTSBOOK_DELIVERY: 'on' });
  const { posts } = fakeGithub(instance);
  let health = { scrape_running: false, scheduler_slot: { slot: '2026-11-21T11:00:00.000Z', status: 'healthy', ended_at: '2026-11-21T11:02:11.000Z' } };
  const asked = [];
  instance.space = async (config, path, run) => { if (run) { asked.push(path); return { started: true }; } return health; };
  const start = Date.parse(SB_SLOT);
  await at(instance, start + 1000, () => instance.alarm());
  health = { scrape_running: false, scheduler_slot: { slot: SB_SLOT, status: 'healthy', ended_at: '2026-11-21T23:03:00.000Z' } };
  for (const minutes of [5, 10]) {
    const fresh = readOnly({ SPORTSBOOK_DELIVERY: 'on' });   // a new instance each tick
    fresh.instance.github = instance.github; fresh.instance.space = instance.space;
    await at(fresh.instance, start + minutes * 60000, () => fresh.instance.alarm());
  }
  assert.deepEqual(asked, [`/api/run?slot=${encodeURIComponent(SB_SLOT)}`]);
  assert.deepEqual(posts, [{ workflow: `${SB.deliver.repo} ${SB.deliver.workflow}`, slot: SB_SLOT }]);
});

test('writes blocked: a paused scheduler stays paused and starts nothing', async () => {
  const { instance, alarms, puts } = readOnly({}, { record: { ...saved(), paused: true } });
  const { posts } = fakeGithub(instance); instance.space = idleSpace('2026-11-21T11:00:00.000Z');
  await at(instance, Date.parse(TECH_SLOT) + 2000, () => instance.alarm());
  assert.equal(posts.length, 0);
  assert.equal(alarms.length, 0);
  assert.equal(puts.length, 0);
});

test('writes blocked: the owner is told at most once every six hours, with no stored memory', async () => {
  assert.equal(WRITE_ALERT_EVERY_MS, 6 * 3600000);
  const day = Date.parse('2026-11-22T00:00:00Z');
  const due = [];
  for (let tick = day; tick < day + 86400000; tick += 300000) if (writeAlertDue(tick + 60)) due.push(new Date(tick).toISOString().slice(11, 16));
  assert.deepEqual(due, ['00:15', '06:15', '12:15', '18:15']);
  const sent = [];
  const { instance } = readOnly({ ALERT_WEBHOOK: 'https://discord.example/api/webhooks/1/x' });
  fakeGithub(instance); instance.space = idleSpace('2026-11-21T11:00:00.000Z');
  instance.notify = async text => { sent.push(text); return { message_id: '1', channel_id: '2' }; };
  await at(instance, Date.parse('2026-11-22T06:15:00.050Z'), () => instance.alarm());
  await at(instance, Date.parse('2026-11-22T06:20:00.050Z'), () => instance.alarm());
  assert.equal(sent.length, 1);
  assert.match(sent[0], /cannot save its state/);
  assert.match(sent[0], /SQLITE_FULL/);
});

test('writes blocked: /health says so instead of only reporting a stale heartbeat', async () => {
  const now = Date.parse('2026-11-21T21:40:00Z');
  const { instance } = readOnly({}, { alarm: now + 240000 });
  const response = await at(instance, now, () => instance.fetch(new Request('https://scheduler/health')));
  const body = await response.json();
  assert.equal(response.status, 503);
  assert.equal(body.status, 'degraded');
  assert.equal(body.storage, 'not being written');
  assert.ok(body.overdue.some(line => /has not been saved since 2026-11-21T17:55:00.000Z/.test(line)));
  assert.ok(!body.overdue.includes('scheduler heartbeat'));
});

test('/health reports an enabled scheduler that has no alarm, and never arms one itself', async () => {
  const now = Date.parse('2026-11-21T21:40:00Z');
  const enabled = readOnly({}, { record: { ...saved(), last_scheduler_tick: '2026-11-21T21:35:00.000Z' } });
  const response = await at(enabled.instance, now, () => enabled.instance.fetch(new Request('https://scheduler/health')));
  const body = await response.json();
  assert.equal(response.status, 503);
  assert.match(body.overdue[0], /enabled in its record but has no alarm/);
  assert.equal(body.next_alarm_at, null);
  assert.equal(enabled.alarms.length, 0);       // a read must not undo a pause made while the record could not be saved
  const paused = readOnly({}, { record: { ...saved(), paused: true } });
  const pausedResponse = await at(paused.instance, now, () => paused.instance.fetch(new Request('https://scheduler/health')));
  assert.equal(pausedResponse.status, 200);
  assert.equal(paused.alarms.length, 0);
});

test('writes blocked: /pause removes the alarm and stays in force; /enable arms it again', async () => {
  const now = Date.parse('2026-11-21T21:40:00Z');
  const { instance, alarms } = readOnly({}, { alarm: now + 240000 });
  const { posts } = fakeGithub(instance); instance.space = idleSpace('2026-11-21T11:00:00.000Z');
  const off = await instance.fetch(new Request('https://scheduler/pause', { method: 'POST' }));
  assert.deepEqual([off.status, (await off.json()).alarm], [202, 'removed']);
  await at(instance, now, () => instance.fetch(new Request('https://scheduler/health')));
  assert.equal(alarms.at(-1), null);
  assert.equal(posts.length, 0);
  const on = await instance.fetch(new Request('https://scheduler/enable', { method: 'POST' }));
  assert.deepEqual([on.status, (await on.json()).alarm], [202, 'armed']);
  assert.ok(alarms.at(-1) > Date.now() - 1000);
});

test('/health still answers when the alarm cannot be read or armed', async () => {
  const { instance } = readOnly({}, { setAlarmFails: true });
  instance.state.storage.getAlarm = async () => { throw new Error(FULL); };
  const response = await instance.fetch(new Request('https://scheduler/health'));
  assert.equal(response.status, 503);
  assert.equal((await response.json()).next_alarm_at, 'unreadable');
});

test('storage healthy: one extra save per tick, and nothing else changes', async () => {
  let stored = { paused: false, modules: {} };
  const puts = [];
  const state = { storage: { get: async () => structuredClone(stored), put: async (key, value) => { puts.push(key); stored = structuredClone(value); },
      getAlarm: async () => null, setAlarm: async () => {}, deleteAlarm: async () => {} }, blockConcurrencyWhile: callback => callback() };
  const instance = new JobsScheduler(state, { GITHUB_TOKEN: 'fake' });
  const { posts } = fakeGithub(instance); instance.space = idleSpace('2026-11-21T11:00:00.000Z');
  await at(instance, Date.parse(TECH_SLOT) + 2000, () => instance.alarm());
  assert.ok(posts.some(post => post.workflow === `${TECH.repo} ${TECH.workflow}` && post.slot === TECH_SLOT));
  assert.equal(puts[0], 'state');
  assert.equal(instance.noStorage, null);
  assert.equal(stored.modules.tech.status, 'awaiting_run');
  assert.ok(stored.last_scheduler_tick);
});

test('writes blocked: /health reports 503 immediately via in-memory this.noStorage before 12 min elapse', async () => {
  const start = Date.parse('2026-11-21T17:55:00.000Z');
  const { instance } = readOnly({}, { record: saved(), alarm: start + 300000 });
  fakeGithub(instance); instance.space = idleSpace('2026-11-21T11:00:00.000Z');
  await at(instance, start + 60000, () => instance.alarm());
  assert.ok(instance.noStorage);
  const response = await at(instance, start + 65000, () => instance.fetch(new Request('https://scheduler/health')));
  const body = await response.json();
  assert.equal(response.status, 503);
  assert.equal(body.status, 'degraded');
  assert.equal(body.storage, 'not being written');
  assert.ok(body.no_storage);
});
