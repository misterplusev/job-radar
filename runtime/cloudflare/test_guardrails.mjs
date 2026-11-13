// Database circuit breaker and incident alert. Run: node --test runtime/cloudflare/
import test from 'node:test';
import assert from 'node:assert/strict';
import { MODULES, JobsScheduler, ALERT_AFTER_TICKS, ALERT_REMINDER_MS } from './worker.mjs';

const NOW = Date.parse('2026-11-11T06:40:00Z');
function fixture(initial = { paused: false, modules: {} }, env = {}) {
  let stored = structuredClone(initial);
  const state = { storage: { get: async () => structuredClone(stored), put: async (_, value) => { stored = structuredClone(value); }, getAlarm: async () => null, setAlarm: async () => {}, deleteAlarm: async () => {} },
    blockConcurrencyWhile: callback => callback() };
  const instance = new JobsScheduler(state, { GITHUB_TOKEN: 'fake', ...env });
  const calls = { github: [], space: [], sent: [] };
  instance.github = async (path, body) => { calls.github.push({ path, body }); return body ? null : { workflow_runs: [] }; };
  instance.space = async (config, path, run = false) => { calls.space.push({ path, run }); return run ? { started: true } : { scrape_running: false, scheduler_slot: null }; };
  instance.notify = async text => { calls.sent.push(text); return true; };
  return { instance, calls, value: () => stored };
}

test('while the database is down no scraper is started, polled or retried', async () => {
  const { instance, calls } = fixture();
  instance.databaseCheck = async () => ({ ok: false, note: 'HTTP 503' });
  const result = await instance.tick('alarm', NOW);
  assert.equal(calls.github.length, 0);
  assert.equal(calls.space.length, 0);
  for (const m of MODULES) assert.equal(result.modules[m.id].status, 'held_database_down');
  assert.equal(result.database.ok, false);
  assert.equal(result.database.down_since, new Date(NOW).toISOString());
  const health = instance.health(result, NOW);
  assert.equal(health.status, 'degraded');
  assert.ok(health.overdue.some(item => item.startsWith('database not answering')));
});

test('held slots start as soon as the database answers again, once', async () => {
  const { instance, calls } = fixture();
  let up = false;
  instance.databaseCheck = async () => ({ ok: up, note: up ? null : 'timeout' });
  await instance.tick('alarm', NOW); await instance.tick('alarm', NOW + 300000);
  assert.equal(calls.github.filter(c => c.body).length, 0);
  up = true;
  const result = await instance.tick('alarm', NOW + 600000);
  assert.equal(calls.github.filter(c => c.body).length, 3);
  assert.equal(calls.space.filter(c => c.run).length, 1);
  assert.equal(result.database.down_since, null);
  await instance.tick('alarm', NOW + 900000);
  assert.equal(calls.github.filter(c => c.body).length, 3);
});

test('down_since is kept across ticks of the same outage', async () => {
  const { instance } = fixture();
  instance.databaseCheck = async () => ({ ok: false, note: 'timeout' });
  await instance.tick('alarm', NOW);
  const result = await instance.tick('alarm', NOW + 300000);
  assert.equal(result.database.down_since, new Date(NOW).toISOString());
});

test('the breaker is off, and never blocks, when it is not configured', async () => {
  const { instance, calls } = fixture();
  assert.deepEqual(await instance.databaseCheck(), { ok: true, note: 'not configured' });
  await instance.tick('alarm', NOW);
  assert.equal(calls.github.filter(c => c.body).length, 3);
});

test('the database check reads one row with the public key and treats errors as down', async () => {
  const { instance } = fixture({ paused: false, modules: {} }, { SUPABASE_URL: 'https://db.example/', SUPABASE_ANON_KEY: 'public-key' });
  const seen = []; const original = globalThis.fetch;
  globalThis.fetch = async (url, init) => { seen.push({ url, init }); if (seen.length === 2) throw new Error('timed out'); return new Response('[]', { status: seen.length === 1 ? 200 : 503 }); };
  try {
    assert.deepEqual(await instance.databaseCheck(), { ok: true, note: null });
    assert.equal((await instance.databaseCheck()).ok, false);
    assert.deepEqual(await instance.databaseCheck(), { ok: false, note: 'HTTP 503' });
  } finally { globalThis.fetch = original; }
  assert.equal(seen[0].url, 'https://db.example/rest/v1/job_scrape_runs?select=id&limit=1');
  assert.equal(seen[0].init.headers.apikey, 'public-key');
});

test('one alert after 15 minutes of trouble, reminders every 6 hours, one recovery message', async () => {
  const { instance, calls } = fixture();
  let up = false;
  instance.databaseCheck = async () => ({ ok: up, note: up ? null : 'HTTP 503' });
  for (let i = 0; i < ALERT_AFTER_TICKS - 1; i++) await instance.tick('alarm', NOW + i * 300000);
  assert.equal(calls.sent.length, 0);
  await instance.tick('alarm', NOW + (ALERT_AFTER_TICKS - 1) * 300000);
  assert.equal(calls.sent.length, 1);
  assert.match(calls.sent[0], /need attention/);
  assert.match(calls.sent[0], /database not answering/);
  for (let i = 0; i < 20; i++) await instance.tick('alarm', NOW + (ALERT_AFTER_TICKS + i) * 300000);
  assert.equal(calls.sent.length, 1);
  await instance.tick('alarm', NOW + (ALERT_AFTER_TICKS - 1) * 300000 + ALERT_REMINDER_MS);
  assert.equal(calls.sent.length, 2);
  // Recovery: database back and every module has a recent success.
  up = true;
  const later = NOW + ALERT_REMINDER_MS + 3600000;
  const done = new Date(later).toISOString();
  instance.github = async (path, body) => body ? null : { workflow_runs: [{ id: 1, display_title: 'x', status: 'completed', conclusion: 'success', updated_at: done }] };
  instance.space = async (config, path, run = false) => run ? { started: true } : { scrape_running: true, current_slot: null, scheduler_slot: { slot: 'earlier', status: 'healthy', ended_at: done } };
  await instance.tick('alarm', later);
  assert.equal(calls.sent.length, 3);
  assert.match(calls.sent[2], /recovered/);
  await instance.tick('alarm', later + 300000);
  assert.equal(calls.sent.length, 3);
});

test('no alert is sent for manual ticks or when no webhook is configured', async () => {
  const { instance, calls } = fixture();
  instance.databaseCheck = async () => ({ ok: false, note: 'HTTP 503' });
  for (let i = 0; i < 6; i++) await instance.tick('operator', NOW + i * 300000);
  assert.equal(calls.sent.length, 0);
  const bare = fixture();
  delete bare.instance.notify;                       // real notify(): no ALERT_WEBHOOK in env
  assert.equal(await bare.instance.notify('x'), false);
});
