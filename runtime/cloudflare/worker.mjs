// Owner: ABET. Cloudflare owns dispatch for ALL FOUR job scrapers; GitHub Actions
// and the Hugging Face Space only execute jobs. No scraper has a timer of its own.
// One serialized Durable Object alarm; no account cron slots or local processes.
//
// Cadence: each module runs every `everyHours` hours, on UTC hours where
// (hour - hourOffset) % everyHours === 0. The offsets give each of the four
// modules its own hour, so at most one of them writes to the shared free
// database in any hour. The 2026-11-11 outage followed three of them being
// dispatched every hour. `everyHours` must divide 24.
//
// Two ways to start a run, same slot/retry/health rules for both:
//   default        GitHub Actions workflow_dispatch (public repositories)
//   kind: 'space'  POST /api/run?slot=… on a Hugging Face Space. Its address is
//                  read from the environment variable named by `urlEnv`.
export const MODULES = [
  { id: 'robotics', repo: 'misterplusev/job-radar', workflow: 'pipeline.yml', prefix: 'job-radar', minute: 9, everyHours: 4, hourOffset: 0 },
  { id: 'tech', repo: 'misterplusev/job-radar-tech', workflow: 'pipeline.yml', prefix: 'job-radar', minute: 37, everyHours: 4, hourOffset: 1 },
  { id: 'sports_teams', repo: 'misterplusev/job-radar', workflow: 'sports-teams.yml', prefix: 'sports-teams', minute: 23, everyHours: 4, hourOffset: 2 },
  { id: 'sportsbook', kind: 'space', urlEnv: 'SPORTSBOOK_SPACE_URL', minute: 0, everyHours: 4, hourOffset: 3 },
];

export function dueSlot(now, minute, everyHours = 1, hourOffset = 0) {
  const slot = new Date(now);
  slot.setUTCMinutes(minute, 0, 0);
  if (slot.getTime() > now) slot.setUTCHours(slot.getUTCHours() - 1);
  // Step back to the module's most recent scheduled hour.
  while ((((slot.getUTCHours() - hourOffset) % everyHours) + everyHours) % everyHours !== 0)
    slot.setUTCHours(slot.getUTCHours() - 1);
  return slot.toISOString();
}

const slotFor = (now, module) => dueSlot(now, module.minute, module.everyHours || 1, module.hourOffset || 0);
const periodMs = module => (module.everyHours || 1) * 3600000;

export function nextWake(now) {
  const candidates = [Math.floor(now / 300000) * 300000 + 300000];
  for (const module of MODULES) candidates.push(Date.parse(slotFor(now, module)) + periodMs(module));
  return Math.min(...candidates);
}

const json = (value, status = 200) => Response.json(value, { status });

export class JobsScheduler {
  constructor(state, env) { this.state = state; this.env = env; }

  async github(path, body) {
    const response = await fetch(`https://api.github.com/${path}`, {
      method: body ? 'POST' : 'GET',
      headers: { Authorization: `Bearer ${this.env.GITHUB_TOKEN}`,
        Accept: 'application/vnd.github+json', 'User-Agent': 'ABET-Jobs-Scheduler',
        'X-GitHub-Api-Version': '2022-11-28', 'Content-Type': 'application/json' },
      body: body ? JSON.stringify(body) : undefined,
      signal: AbortSignal.timeout(6000),
    });
    if (!response.ok) throw new Error(`GitHub ${response.status} ${path.split('/').slice(-1)[0]}`);
    return response.status === 204 ? null : response.json();
  }

  // The Space is private: SPACE_READ_TOKEN gets the request through Hugging Face,
  // SPACE_RUN_TOKEN is the launcher's own RUN_TOKEN. Neither is ever logged.
  async space(config, path, run = false) {
    const base = this.env[config.urlEnv];
    if (!base) throw new Error(`${config.urlEnv} is not configured`);
    const headers = { 'User-Agent': 'ABET-Jobs-Scheduler' };
    if (this.env.SPACE_READ_TOKEN) headers.Authorization = `Bearer ${this.env.SPACE_READ_TOKEN}`;
    if (run) headers['X-Run-Token'] = this.env.SPACE_RUN_TOKEN || '';
    const response = await fetch(`${base.replace(/\/+$/, '')}${path}`,
      { method: run ? 'POST' : 'GET', headers, signal: AbortSignal.timeout(8000) });
    // 409 = a scrape is already running there; that is an answer, not a failure.
    if (!response.ok && response.status !== 409) throw new Error(`Space ${response.status} ${path.split('?')[0]}`);
    return response.json();
  }

  async tickSpace(config, record, prior, state, slot, origin, now) {
    const health = await this.space(config, '/api/health');
    const last = health.scheduler_slot || null;
    record.last_checked = state.last_tick;
    record.error = null;
    record.last_success = last?.status === 'healthy' ? last.ended_at : (prior.last_success || null);
    if (last?.slot === slot) {
      record.status = last.status === 'healthy' ? 'success' : last.status;
      if (last.status !== 'healthy') record.error = `Run for ${slot} ended ${last.status}`;
      return;
    }
    if (health.scrape_running) {
      record.status = health.current_slot === slot ? 'in_progress' : 'deferred_running';
      return;
    }
    if (record.dispatched_at && now - Date.parse(record.dispatched_at) < 15 * 60 * 1000) {
      record.status = 'awaiting_run';
      return;
    }
    if (record.attempts >= 2) {
      record.status = 'failed'; record.error = 'Run requested but the Space did not run it after retries';
      return;
    }
    record.attempts += 1;
    record.status = 'dispatching';
    record.dispatched_at = state.last_tick;
    await this.state.storage.put('state', state);
    const reply = await this.space(config, `/api/run?slot=${encodeURIComponent(slot)}`, true);
    record.status = reply.started ? 'in_progress' : 'awaiting_run';
    record.dispatch_origin = origin;
    console.log(JSON.stringify({ module: config.id, slot, status: 'dispatched', origin }));
  }

  async tick(origin, now) {
    const state = await this.state.storage.get('state') || { paused: true, modules: {} };
    state.last_tick = new Date(now).toISOString();
    if (origin === 'alarm') state.last_scheduler_tick = state.last_tick;
    if (state.paused) { await this.state.storage.put('state', state); return state; }
    for (const config of MODULES) {
      const slot = slotFor(now, config);
      const prior = state.modules[config.id] || {};
      const record = prior.slot === slot ? prior : { slot, attempts: 0 };
      state.modules[config.id] = record;
      try {
        if (config.kind === 'space') {
          await this.tickSpace(config, record, prior, state, slot, origin, now);
          continue;
        }
        const data = await this.github(`repos/${config.repo}/actions/workflows/${config.workflow}/runs?branch=master&per_page=30`);
        const runs = data.workflow_runs;
        const match = runs.find(run => run.display_title === `${config.prefix} ${slot}`);
        const latestSuccess = runs.find(run => run.conclusion === 'success');
        record.last_success = latestSuccess?.updated_at || null;
        record.last_checked = state.last_tick;
        record.error = null;
        if (match) {
          record.run_id = match.id;
          record.run_url = match.html_url;
          record.status = match.status === 'completed' ? match.conclusion : match.status;
          if (match.status === 'completed' && match.conclusion !== 'success')
            record.error = `Run ${match.id} completed ${match.conclusion}`;
          continue;
        }
        // A persisted acceptance receipt and run-name lookup prevent duplicate dispatch.
        if (record.dispatched_at && now - Date.parse(record.dispatched_at) < 15 * 60 * 1000) {
          record.status = 'awaiting_run';
          continue;
        }
        if (runs.some(run => run.status !== 'completed')) {
          record.status = 'deferred_running';
          continue;
        }
        if (record.attempts >= 2) {
          record.status = 'failed'; record.error = 'Dispatch accepted but no run appeared after retries';
          continue;
        }
        record.attempts += 1;
        record.status = 'dispatching';
        // Persist intent before the remote action. Retries are bounded per slot.
        record.dispatched_at = state.last_tick;
        await this.state.storage.put('state', state);
        await this.github(`repos/${config.repo}/actions/workflows/${config.workflow}/dispatches`,
          { ref: 'master', inputs: { scheduler_slot: slot, trigger_source: 'cloudflare' } });
        record.status = 'awaiting_run';
        record.dispatch_origin = origin;
        console.log(JSON.stringify({ module: config.id, slot, status: 'dispatched', origin }));
      } catch (error) {
        record.status = 'error'; record.error = String(error.message).slice(0, 200);
        console.error(JSON.stringify({ module: config.id, slot, error: record.error }));
      }
    }
    await this.state.storage.put('state', state);
    return state;
  }

  health(state, now) {
    if (!state) return { status: 'uninitialized', modules: {} };
    const overdue = [];
    if (!state.paused && (!state.last_scheduler_tick || now - Date.parse(state.last_scheduler_tick) > 12 * 60 * 1000))
      overdue.push('scheduler heartbeat');
    for (const module of MODULES) {
      const record = state.modules[module.id];
      if (state.paused) continue;
      if (!record || !record.last_success || now - Date.parse(record.last_success) > periodMs(module) + 30 * 60 * 1000)
        overdue.push(`${module.id} successful execution`);
      if (record?.error) overdue.push(`${module.id}: ${record.error}`);
    }
    return { ...state, scheduler: 'cloudflare-durable-object-alarm', status: state.paused ? 'paused' : overdue.length ? 'degraded' : 'healthy', overdue };
  }

  async alarm() {
    await this.state.blockConcurrencyWhile(async () => {
      const state = await this.state.storage.get('state');
      if (!state || state.paused) return;
      // Arm recovery before network work, so a failed request cannot stop scheduling.
      await this.state.storage.setAlarm(Date.now() + 300000);
      try { await this.tick('alarm', Date.now()); }
      finally { await this.state.storage.setAlarm(nextWake(Date.now())); }
    });
  }

  async fetch(request) {
    const path = new URL(request.url).pathname;
    if (path === '/health') {
      const health = this.health(await this.state.storage.get('state'), Date.now());
      const nextAlarm = await this.state.storage.getAlarm();
      health.next_alarm_at = nextAlarm === null ? null : new Date(nextAlarm).toISOString();
      return json(health, health.status === 'healthy' || health.status === 'paused' ? 200 : 503);
    }
    return this.state.blockConcurrencyWhile(async () => {
      if (path === '/tick') return json(await this.tick(request.headers.get('X-Origin') || 'manual', Date.now()));
      if (path === '/enable' || path === '/pause') {
        const state = await this.state.storage.get('state') || { modules: {} };
        state.paused = path === '/pause';
        state.changed_at = new Date().toISOString();
        await this.state.storage.put('state', state);
        if (state.paused) await this.state.storage.deleteAlarm();
        else await this.state.storage.setAlarm(Date.now() + 1000);
        return json({ paused: state.paused });
      }
      return json({ error: 'not found' }, 404);
    });
  }
}

function scheduler(env) { return env.SCHEDULER.get(env.SCHEDULER.idFromName('production')); }

export default {
  async fetch(request, env) {
    const path = new URL(request.url).pathname;
    if (path === '/health' && request.method === 'GET')
      return scheduler(env).fetch('https://scheduler/health');
    if (request.method !== 'POST' || !['/enable', '/pause', '/tick'].includes(path))
      return json({ error: 'not found' }, 404);
    if (!env.CONTROL_TOKEN || request.headers.get('Authorization') !== `Bearer ${env.CONTROL_TOKEN}`)
      return json({ error: 'unauthorized' }, 401);
    return scheduler(env).fetch(`https://scheduler${path}`, { method: 'POST', headers: { 'X-Origin': 'operator' } });
  },
};
