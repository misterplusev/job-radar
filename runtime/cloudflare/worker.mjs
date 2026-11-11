// Owner: ABET. Cloudflare owns hourly dispatch; GitHub Actions only executes jobs.
// One serialized Durable Object alarm; no account cron slots or local processes.
export const MODULES = [
  { id: 'robotics', repo: 'misterplusev/job-radar', minute: 9 },
  { id: 'tech', repo: 'misterplusev/job-radar-tech', minute: 37 },
];

export function dueSlot(now, minute) {
  const slot = new Date(now);
  slot.setUTCMinutes(minute, 0, 0);
  if (slot.getTime() > now) slot.setUTCHours(slot.getUTCHours() - 1);
  return slot.toISOString();
}

export function nextWake(now) {
  const candidates = [Math.floor(now / 300000) * 300000 + 300000];
  for (const module of MODULES) candidates.push(Date.parse(dueSlot(now, module.minute)) + 3600000);
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

  async tick(origin, now) {
    const state = await this.state.storage.get('state') || { paused: true, modules: {} };
    state.last_tick = new Date(now).toISOString();
    if (origin === 'alarm') state.last_scheduler_tick = state.last_tick;
    if (state.paused) { await this.state.storage.put('state', state); return state; }
    for (const config of MODULES) {
      const slot = dueSlot(now, config.minute);
      const prior = state.modules[config.id] || {};
      const record = prior.slot === slot ? prior : { slot, attempts: 0 };
      state.modules[config.id] = record;
      try {
        const data = await this.github(`repos/${config.repo}/actions/workflows/pipeline.yml/runs?per_page=30`);
        const runs = data.workflow_runs;
        const match = runs.find(run => run.display_title === `job-radar ${slot}`);
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
        // Persist intent before the remote action. Retries are bounded per hourly slot.
        record.dispatched_at = state.last_tick;
        await this.state.storage.put('state', state);
        await this.github(`repos/${config.repo}/actions/workflows/pipeline.yml/dispatches`,
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
      if (!record || !record.last_success || now - Date.parse(record.last_success) > 90 * 60 * 1000)
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
