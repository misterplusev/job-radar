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
  { id: 'robotics', repo: 'misterplusev/job-radar', workflow: 'pipeline.yml', prefix: 'job-radar', minute: 9, everyHours: 12, hourOffset: 0 },
  { id: 'tech', repo: 'misterplusev/job-radar-tech', workflow: 'pipeline.yml', prefix: 'job-radar', minute: 37, everyHours: 12, hourOffset: 9 },
  { id: 'sports_teams', repo: 'misterplusev/job-radar', workflow: 'sports-teams.yml', prefix: 'sports-teams', minute: 23, everyHours: 12, hourOffset: 10 },
  { id: 'sportsbook', kind: 'space', urlEnv: 'SPORTSBOOK_SPACE_URL', minute: 0, everyHours: 12, hourOffset: 11,
    // Discord delivery for sportsbook runs as a GitHub workflow (the Space cannot reach Discord).
    deliver: { repo: 'misterplusev/job-radar', workflow: 'sportsbook-deliver.yml', prefix: 'sportsbook-deliver' } },
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

// The list comes from this module's production workflow. A new attempt must start
// after the failed slot finished. Keep the original receipt and use only the
// newest qualifying full run, so an intervening failure or running attempt stays visible.
function latestFollowup(runs, failed) {
  let latest;
  let newest = Date.parse(failed.updated_at);
  for (const run of runs) {
    const started = Date.parse(run.run_started_at || run.created_at);
    if (run.id === failed.id || run.workflow_id !== failed.workflow_id || !run.workflow_id ||
        run.head_branch !== 'master' || run.event !== 'workflow_dispatch' || !(started > newest)) continue;
    latest = run;
    newest = started;
  }
  return latest;
}

export function nextWake(now) {
  const candidates = [Math.floor(now / 300000) * 300000 + 300000];
  for (const module of MODULES) candidates.push(Date.parse(slotFor(now, module)) + periodMs(module));
  return Math.min(...candidates);
}

const json = (value, status = 200) => Response.json(value, { status });

// GUARDRAILS (added after the 2026-11-11/12 outage; see docs/job-scrapers/RUNBOOK.md)
// 1. Database circuit breaker: every tick reads one row through the public REST API.
//    While that fails, NO scraper is started. During the outage every scheduled run
//    was still dispatched into a database that could not answer, and their retries
//    kept it down for 36 hours. A held slot is started late if the database returns
//    within the slot's configured period, otherwise it is skipped; runs never pile up.
// 2. Incident alert (optional): if ALERT_WEBHOOK is set, one Discord message when
//    health has been bad for ALERT_AFTER_TICKS ticks in a row, a reminder every
//    ALERT_REMINDER_MS while it stays bad, and one message when it recovers.
export const ALERT_AFTER_TICKS = 3;            // 3 ticks = 15 minutes
export const ALERT_REMINDER_MS = 6 * 3600000;  // at most 4 reminders a day

// 3. Running without storage (added 2026-11-21). This Durable Object's storage is counted against the
//    Cloudflare account's free daily allowance, which every Worker on the account shares. On 2026-11-21
//    other Workers used it up at 18:00 UTC: storage.get and storage.put threw until 00:00 UTC, the alarm
//    handler failed six times, Cloudflare dropped the alarm, and no evening run was started. A dev probe
//    the same day showed that alarms still fire and setAlarm/getAlarm still work in that state.
//    So when storage cannot be read, the alarm keeps itself alive and the tick runs from ground truth
//    alone: a slot is started only if it came due within NO_STORAGE_WINDOW_MS, no run carrying that
//    slot's name exists, and nothing of that module is running. The slot name on the run is the receipt;
//    the normal tick finds it again when storage returns, so nothing is started twice or piled up.
export const NO_STORAGE_WINDOW_MS = 12 * 60000;          // ticks at +0, +5 and +10 minutes may start a slot
export const NO_STORAGE_DELIVERY_WINDOW_MS = 30 * 60000; // delivery follows the end of the sportsbook run
const short = error => String(error?.message || error).slice(0, 200);

// 4. Storage that can be read but not written (added 2026-11-22). The account's free stored-data limit
//    (5 GB, shared by every Worker; 4.6 GB was in use on 2026-11-22, almost none of it this scheduler's)
//    and its daily rows-written allowance stop storage.put while storage.get keeps answering. The normal
//    tick saves its intent before every start, so with writes failing it started nothing and, because
//    its failure count was never saved, never alerted. Each alarm therefore saves the record once before
//    trusting it. If that save fails the tick runs exactly as in guardrail 3, from run names alone.
//    No memory can be kept between ticks in that state, so the owner is told on fixed clock marks:
//    the tick at 00:15, 06:15, 12:15 and 18:15 UTC.
export const WRITE_ALERT_EVERY_MS = 6 * 3600000;
export const writeAlertDue = now => Math.floor(now / 300000) % (WRITE_ALERT_EVERY_MS / 300000) === 3;

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

  // SINGLE-SENDER SWITCH. The delivery workflow is started only when the Worker secret
  // SPORTSBOOK_DELIVERY is exactly 'on'. Deploying this code therefore cannot create a second
  // sportsbook sender while the previous one (abet-jobs-watchdog) is still announcing; the switch
  // is turned on in the same cutover step that turns the previous sender off. At most one
  // dispatch per slot, with one retry if GitHub refuses the request.
  async dispatchDelivery(config, record, slot, state, origin) {
    if (!config.deliver || this.env.SPORTSBOOK_DELIVERY !== 'on') return;
    const path = `repos/${config.deliver.repo}/actions/workflows/${config.deliver.workflow}`;
    try {
      if (record.delivery_dispatched_at) {
        if (['success', 'failure', 'cancelled', 'timed_out'].includes(record.delivery_status)) {
          // tickSpace clears record.error on every tick. A delivery that ended badly used to show as an
          // error for one tick only, and the alert needs three, so it never fired (found 2026-11-19).
          if (record.delivery_status !== 'success')
            record.error = `Delivery run ${record.delivery_run_id} completed ${record.delivery_status}`;
          return;
        }
        const data = await this.github(`${path}/runs?branch=master&per_page=20`);
        const match = data.workflow_runs.find(run => run.display_title === `${config.deliver.prefix} ${slot}`);
        if (!match) {
          // A delivery that was started but never shows up must not wait for ever without a word.
          if (Date.parse(state.last_tick) - Date.parse(record.delivery_dispatched_at) > 15 * 60000)
            record.error = 'Delivery workflow was started but no matching run was found after 15 minutes';
          return;
        }
        record.delivery_run_id = match.id;
        record.delivery_status = match.status === 'completed' ? match.conclusion : match.status;
        if (match.status === 'completed' && match.conclusion !== 'success')
          record.error = `Delivery run ${match.id} completed ${match.conclusion}`;
        return;
      }
      // A delivery run with this slot's name may already exist: started while storage was unavailable,
      // or by an operator standing in for the scheduler. Adopt it instead of starting a second one.
      const existing = (await this.github(`${path}/runs?branch=master&per_page=20`)).workflow_runs
        .find(run => run.display_title === `${config.deliver.prefix} ${slot}`);
      if (existing) {
        record.delivery_dispatched_at = existing.created_at || state.last_tick;
        record.delivery_run_id = existing.id;
        record.delivery_status = existing.status === 'completed' ? existing.conclusion : existing.status;
        if (existing.status === 'completed' && existing.conclusion !== 'success')
          record.error = `Delivery run ${existing.id} completed ${existing.conclusion}`;
        return;
      }
      if ((record.delivery_attempts || 0) >= 2) {
        record.error = 'Delivery workflow could not be started after retries';
        return;
      }
      record.delivery_attempts = (record.delivery_attempts || 0) + 1;
      await this.state.storage.put('state', state);
      await this.github(`${path}/dispatches`, { ref: 'master', inputs: { scheduler_slot: slot, trigger_source: 'cloudflare' } });
      record.delivery_dispatched_at = state.last_tick;
      record.delivery_status = 'awaiting_run';
      console.log(JSON.stringify({ module: config.id, slot, status: 'delivery_dispatched', origin }));
    } catch (error) {
      record.delivery_error = String(error.message).slice(0, 200);
      // Health reads record.error only; a delivery check that keeps failing must be visible there.
      record.error = `Delivery check failed: ${record.delivery_error}`;
    }
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
      // Whatever the scrape's status, anything it queued is delivered now.
      await this.dispatchDelivery(config, record, slot, state, origin);
      return;
    }
    // The Space forgets its slots when it restarts (a deploy, a platform restart).
    // Completed slots remain completed after a runtime rebuild, including degraded runs.
    // Retrying a completed degraded scrape on reboot would bypass the reduced cadence.
    if (['success', 'degraded', 'failed'].includes(record.status)) {
      record.error = record.status === 'success' ? null : `Run for ${slot} ended ${record.status}`;
      await this.dispatchDelivery(config, record, slot, state, origin);
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

  // One cheap read through the same public REST API the scrapers and boards use.
  // Not configured (no SUPABASE_URL / SUPABASE_ANON_KEY) = breaker off, never blocks.
  async databaseCheck() {
    const url = this.env.SUPABASE_URL, key = this.env.SUPABASE_ANON_KEY;
    if (!url || !key) return { ok: true, note: 'not configured' };
    try {
      const response = await fetch(`${url.replace(/\/+$/, '')}/rest/v1/job_scrape_runs?select=id&limit=1`,
        { headers: { apikey: key, Authorization: `Bearer ${key}` }, signal: AbortSignal.timeout(6000) });
      return { ok: response.ok, note: response.ok ? null : `HTTP ${response.status}` };
    } catch (error) {
      return { ok: false, note: String(error.message).slice(0, 80) };
    }
  }

  async notify(text) {
    if (!this.env.ALERT_WEBHOOK) return false;
    try {
      const url = new URL(this.env.ALERT_WEBHOOK);
      url.searchParams.set('wait', 'true');
      const response = await fetch(url, { method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: text.slice(0, 1900) }), signal: AbortSignal.timeout(6000) });
      if (!response.ok) return false;
      const receipt = await response.json();
      if (![receipt?.id, receipt?.channel_id].every(id => typeof id === 'string' && /^\d{17,20}$/.test(id))) return false;
      return { message_id: receipt.id, channel_id: receipt.channel_id };
    } catch { return false; }
  }

  // Called once per alarm tick, after the tick's results are known.
  async alert(state, now) {
    const health = this.health(state, now);
    const alert = state.alert || { bad_ticks: 0, notified_at: null };
    state.alert = alert;
    if (health.status === 'healthy' || health.status === 'paused') {
      if (alert.notified_at && health.status === 'healthy') {
        const recovery = await this.notify(`🟢 **ABET job scrapers recovered.** All four modules and the database are healthy again (problem began ${alert.since}).`);
        if (!recovery) return;
        state.last_alert_delivery = { ...recovery, kind: 'recovery', at: new Date(now).toISOString() };
      }
      state.alert = { bad_ticks: 0, notified_at: null };
      return;
    }
    alert.bad_ticks += 1;
    alert.since = alert.since || new Date(now).toISOString();
    const due = !alert.notified_at ? alert.bad_ticks >= ALERT_AFTER_TICKS
      : now - Date.parse(alert.notified_at) >= ALERT_REMINDER_MS;
    if (!due) return;
    const lines = health.overdue.slice(0, 8).map(item => `• ${item}`);
    const sent = await this.notify([`🔴 **ABET job scrapers need attention** (since ${alert.since})`, ...lines,
      'Status: https://abet-jobs-scheduler.abetscrape.workers.dev/health'].join('\n'));
    if (sent) {
      alert.notified_at = new Date(now).toISOString();
      state.last_alert_delivery = { ...sent, kind: 'incident', at: alert.notified_at };
    }
  }

  async tick(origin, now) {
    const state = await this.state.storage.get('state') || { paused: true, modules: {} };
    state.last_tick = new Date(now).toISOString();
    if (origin === 'alarm') state.last_scheduler_tick = state.last_tick;
    if (state.paused) { await this.state.storage.put('state', state); return state; }
    const database = await this.databaseCheck();
    const wasDown = state.database && state.database.ok === false;
    state.database = { ok: database.ok, note: database.note, checked_at: state.last_tick,
      down_since: database.ok ? null : (wasDown ? state.database.down_since : state.last_tick) };
    for (const config of MODULES) {
      const slot = slotFor(now, config);
      const prior = state.modules[config.id] || {};
      const record = prior.slot === slot ? prior : { slot, attempts: 0, last_success: prior.last_success || null };
      state.modules[config.id] = record;
      if (!database.ok) {
        // Circuit breaker: do not start, retry or even poll runs while the database is down.
        if (!['success', 'in_progress', 'awaiting_run'].includes(record.status)) record.status = 'held_database_down';
        continue;
      }
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
          record.slot_status = record.status;
          delete record.recovery;
          if (match.status === 'completed' && match.conclusion !== 'success') {
            const later = latestFollowup(runs, match);
            if (later?.status === 'completed' && later.conclusion === 'success') {
              record.status = 'success';
              record.recovery = { run_id: later.id, run_url: later.html_url, completed_at: later.updated_at };
            } else {
              record.error = `Run ${match.id} completed ${match.conclusion}`;
            }
          }
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
        if (record.status === 'held_database_down') record.status = 'pending';
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
    if (origin === 'alarm') await this.alert(state, now);
    await this.state.storage.put('state', state);
    return state;
  }

  health(state, now) {
    if (!state) return { status: 'uninitialized', modules: {} };
    const overdue = [];
    if (!state.paused && (!state.last_scheduler_tick || now - Date.parse(state.last_scheduler_tick) > 12 * 60 * 1000))
      overdue.push('scheduler heartbeat');
    if (!state.paused && state.database && state.database.ok === false)
      overdue.push(`database not answering since ${state.database.down_since} (${state.database.note}); scrapers are held`);
    for (const module of MODULES) {
      const record = state.modules[module.id];
      if (state.paused) continue;
      if (!record || !record.last_success || now - Date.parse(record.last_success) > periodMs(module) + 30 * 60 * 1000)
        overdue.push(`${module.id} successful execution`);
      if (record?.error) overdue.push(`${module.id}: ${record.error}`);
    }
    return { ...state, scheduler: 'cloudflare-durable-object-alarm', status: state.paused ? 'paused' : overdue.length ? 'degraded' : 'healthy', overdue };
  }

  // Start one GitHub workflow run for a slot, using only what GitHub itself reports.
  // `stamp` names the field of `record` (in memory only) that remembers this instance already asked.
  async startByName(target, title, slot, record, stamp, now, due) {
    const base = `repos/${target.repo}/actions/workflows/${target.workflow}`;
    const runs = (await this.github(`${base}/runs?branch=master&per_page=30`)).workflow_runs;
    const match = runs.find(run => run.display_title === title);
    if (match) return { status: match.status === 'completed' ? match.conclusion : match.status, run_id: match.id };
    if (runs.some(run => run.status !== 'completed')) return { status: 'deferred_running' };
    if (!due) return { status: 'not_started_no_storage' };
    if (record[stamp] && now - Date.parse(record[stamp]) < 15 * 60000) return { status: 'awaiting_run' };
    record[stamp] = new Date(now).toISOString();
    await this.github(`${base}/dispatches`, { ref: 'master', inputs: { scheduler_slot: slot, trigger_source: 'cloudflare' } });
    console.log(JSON.stringify({ mode: 'no_storage', title, status: 'dispatched' }));
    return { status: 'awaiting_run', started: true };
  }

  // One tick while storage cannot be read (guardrail 3). Nothing is stored; `this.noStorage` lives only
  // as long as this instance and is shown by /health.
  async tickWithoutStorage(now, cause) {
    const memory = this.noStorage = this.noStorage || { since: new Date(now).toISOString(), modules: {} };
    memory.reason = short(cause);
    memory.last_tick = new Date(now).toISOString();
    console.error(JSON.stringify({ mode: 'no_storage', reason: memory.reason }));
    const database = await this.databaseCheck();
    memory.database = { ok: database.ok, note: database.note };
    if (!database.ok) return memory;   // circuit breaker, as in the normal tick
    for (const config of MODULES) {
      const slot = slotFor(now, config);
      const prior = memory.modules[config.id];
      const record = prior?.slot === slot ? prior : { slot };
      memory.modules[config.id] = record;
      const due = now - Date.parse(slot) <= NO_STORAGE_WINDOW_MS;
      try {
        record.error = null;
        if (config.kind !== 'space') {
          Object.assign(record, await this.startByName(config, `${config.prefix} ${slot}`, slot, record, 'dispatched_at', now, due));
          continue;
        }
        const health = await this.space(config, '/api/health');
        const last = health.scheduler_slot || null;
        if (last?.slot === slot) {
          record.status = last.status === 'healthy' ? 'success' : last.status;
          if (config.deliver && this.env.SPORTSBOOK_DELIVERY === 'on') {
            const fresh = now - Date.parse(last.ended_at) <= NO_STORAGE_DELIVERY_WINDOW_MS;
            const delivery = await this.startByName(config.deliver, `${config.deliver.prefix} ${slot}`, slot, record, 'delivery_dispatched_at', now, fresh);
            record.delivery_status = delivery.status;
            record.delivery_run_id = delivery.run_id || null;
          }
        } else if (health.scrape_running) {
          record.status = health.current_slot === slot ? 'in_progress' : 'deferred_running';
        } else if (!due) {
          record.status = 'not_started_no_storage';
        } else if (record.dispatched_at && now - Date.parse(record.dispatched_at) < 15 * 60000) {
          record.status = 'awaiting_run';
        } else {
          record.dispatched_at = new Date(now).toISOString();
          const reply = await this.space(config, `/api/run?slot=${encodeURIComponent(slot)}`, true);
          record.status = reply.started ? 'in_progress' : 'awaiting_run';
          console.log(JSON.stringify({ mode: 'no_storage', module: config.id, slot, status: 'dispatched' }));
        }
      } catch (error) {
        record.status = 'error'; record.error = short(error);
        console.error(JSON.stringify({ mode: 'no_storage', module: config.id, slot, error: record.error }));
      }
    }
    return memory;
  }

  // Guardrails 3 & 4: one Discord message on fixed clock marks while storage cannot be read or saved.
  async alertStorageBlocked(now, cause, readable) {
    const bucket = Math.floor(now / 300000);
    if (!writeAlertDue(now) || this.writeAlertBucket === bucket) return;
    this.writeAlertBucket = bucket;
    const problem = readable
      ? 'cannot save its state (reads work, writes fail)'
      : 'cannot read or save its state (storage unavailable)';
    await this.notify(`🔴 **ABET job scheduler ${problem}** (${short(cause)}). It keeps starting runs ` +
      "from GitHub's and the Space's own records. The Cloudflare account's daily storage allowance or stored-data limit " +
      'is used up; other Workers on the account use almost all of it. Status: https://abet-jobs-scheduler.abetscrape.workers.dev/health');
  }

  async alarm() {
    await this.state.blockConcurrencyWhile(async () => {
      let state, cause = null, readable = true;
      try { state = await this.state.storage.get('state'); }
      catch (error) { cause = error; readable = false; }
      if (readable) {
        if (!state || state.paused) { this.noStorage = null; return; }
        // Guardrail 4: the record must be savable before the normal tick may rely on it.
        try { await this.state.storage.put('state', state); }
        catch (error) { cause = error; }
      }
      if (cause) {
        // Storage cannot be read, or cannot be written. An alarm exists only while the scheduler is enabled
        // (pause deletes it), so this tick may act. Never let the failure escape: Cloudflare drops an alarm
        // after six failed tries. If setAlarm itself throws, that retry is all that is left; /health then
        // reports "enabled but no alarm".
        try {
          await this.tickWithoutStorage(Date.now(), cause);
          await this.alertStorageBlocked(Date.now(), cause, readable);
        }
        catch (failure) { console.error(JSON.stringify({ mode: 'no_storage', error: short(failure) })); }
        finally { await this.state.storage.setAlarm(nextWake(Date.now())); }
        return;
      }
      this.noStorage = null;
      // Arm recovery before network work, so a failed request cannot stop scheduling.
      await this.state.storage.setAlarm(Date.now() + 300000);
      try { await this.tick('alarm', Date.now()); }
      catch (error) {
        // Storage can stop answering in the middle of a tick; the next alarm takes the path above.
        console.error(JSON.stringify({ mode: 'tick_failed', error: short(error) }));
      }
      finally { await this.state.storage.setAlarm(nextWake(Date.now())); }
    });
  }

  async fetch(request) {
    const path = new URL(request.url).pathname;
    if (path === '/health') {
      const now = Date.now();
      let health, stored = null;
      try { stored = await this.state.storage.get('state'); health = this.health(stored, now); }
      catch (error) {
        // Used to answer with an uncaught exception (Cloudflare error 1101), which said nothing.
        health = { scheduler: 'cloudflare-durable-object-alarm', status: 'degraded', storage: 'unavailable', modules: {},
          overdue: [`scheduler storage cannot be read (${short(error)}); running without stored state`],
          no_storage: this.noStorage || null };
      }
      let nextAlarm;
      try { nextAlarm = await this.state.storage.getAlarm(); } catch { nextAlarm = undefined; }
      // Enabled but no alarm: Cloudflare dropped it (six failed tries), or /pause removed it while the record
      // could not be saved. The two cannot be told apart here, so it is reported and never armed from a read:
      // arming it would undo a pause.
      if (stored && stored.paused === false && nextAlarm === null) {
        health.status = 'degraded';
        health.overdue = ['scheduler is enabled in its record but has no alarm, so nothing is being started: POST /enable starts it', ...health.overdue];
      }
      // Guardrail 4: storage writes are failing (detected immediately via in-memory this.noStorage,
      // or after instance restart via a stale saved record while the alarm is still running).
      const staleRecord = stored && !stored.paused && stored.last_scheduler_tick && now - Date.parse(stored.last_scheduler_tick) > 12 * 60000;
      const writeBlocked = stored && !stored.paused && (Boolean(this.noStorage) || (staleRecord && typeof nextAlarm === 'number' && nextAlarm > now - 60000));
      if (writeBlocked) {
        health.status = 'degraded';
        health.storage = 'not being written';
        health.no_storage = this.noStorage || null;
        health.overdue = [`scheduler state has not been saved since ${stored.last_scheduler_tick || 'startup'} although its alarm is running: ` +
          "storage writes are failing; runs are started from GitHub's and the Space's own records, and the module records below are old",
          ...health.overdue.filter(line => line !== 'scheduler heartbeat')];
      }
      health.next_alarm_at = nextAlarm === undefined ? 'unreadable' : nextAlarm === null ? null : new Date(nextAlarm).toISOString();
      return json(health, health.status === 'healthy' || health.status === 'paused' ? 200 : 503);
    }
    return this.state.blockConcurrencyWhile(async () => {
      try {
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
      } catch (error) {
        // Storage unavailable. The alarm is the on/off switch that still works: arm it or remove it.
        if (path === '/enable') await this.state.storage.setAlarm(Date.now() + 1000);
        if (path === '/pause') await this.state.storage.deleteAlarm();
        return json({ stored: false, alarm: path === '/enable' ? 'armed' : path === '/pause' ? 'removed' : 'unchanged',
          error: short(error) }, path === '/tick' ? 503 : 202);
      }
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

