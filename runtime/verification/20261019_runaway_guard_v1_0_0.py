"""Runaway guard for PYTHON scripts that start AI agents or browsers (2026-10-19, Claude; same rules as the Node guard
D:/opencode-sessions-dashboard/scripts/lib/20261019_runaway_guard_v1_0_0.mjs). Operator rulings 2026-10-19:
"STOP ITSELF WITH MORE THAN 3" browsers; Discord alerts; fix the whole system.

Use (copy these lines into any script that runs `opencode run`, `hermes -z`, `codex exec`, Playwright, Puppeteer, agent-browser):
    import sys; sys.path.insert(0, r"D:/abet_ops/machine_watchdog")
    guard = __import__("20261019_runaway_guard_v1_0_0")
    g = guard.guard_before_agent("my-script-name")     # may sys.exit(3): "stop itself"
    if not g["ok"]:
        ...skip this agent run (g["reason"]) and wait / move on...
    ...run ONE agent...
    guard.cleanup_after_agent(g["t0"], "my-script-name")

Rules: machine-wide switch D:/abet_ops/STOP_ALL_AGENTS_MACHINE -> exit 3 | more than 3 automation browsers -> write that
switch + Discord CRIT + exit 3 | 2 one-shot agents already running -> skip | memory commit >= 85 % -> skip |
snapshot failure -> skip (fail closed) | after a run: Hermes browsers started during it are closed + alerted.
Self-test: python -X utf8 -I 20261019_runaway_guard_v1_0_0.py --selftest"""
import datetime as dt
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SNAPSHOT_PS1 = os.path.join(HERE, "20261019_process_snapshot_v1_0_0.ps1")
# Machine-wide emergency switch ONLY. Idea City's park switch (D:/opencode-sessions-dashboard/data/STOP_ALL_AGENTS) is
# deliberately NOT honoured here, so parking Idea City does not block unrelated, guarded scripts.
STOP_FILE = "D:/abet_ops/STOP_ALL_AGENTS_MACHINE"
GUARD_LOG = os.path.join(HERE, "logs", "runaway_guard_python.log")
MAX_BROWSERS, MAX_AGENTS, MAX_COMMIT_PCT = 3, 2, 85
NO_WINDOW = 0x08000000


def _log(line):
    try:
        os.makedirs(os.path.dirname(GUARD_LOG), exist_ok=True)
        with open(GUARD_LOG, "a", encoding="utf-8") as f:
            f.write(f"{dt.datetime.now().astimezone().isoformat(timespec='seconds')} pid {os.getpid()} {line}\n")
    except OSError:
        pass


def _alert(level, title, body):
    try:
        sys.path.insert(0, HERE)
        __import__("20261019_discord_alert_v1_0_0").send_alert(level, title, body)
    except Exception:
        pass


def snapshot():
    try:
        r = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", SNAPSHOT_PS1],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=90, creationflags=NO_WINDOW)
        return json.loads(r.stdout.strip().lstrip("\ufeff"))
    except Exception:
        return None


def decide_before(snap, stop_file_exists):
    if stop_file_exists:
        return {"verdict": "exit", "reason": "STOP_ALL_AGENTS kill switch is set"}
    if not snap:
        return {"verdict": "skip", "reason": "process snapshot failed (fail closed)"}
    procs = snap.get("procs", [])
    browsers = [p for p in procs if p["kind"] == "cft" and p.get("top")]
    if len(browsers) > MAX_BROWSERS:
        return {"verdict": "stop", "reason": f"{len(browsers)} automation browsers running (limit {MAX_BROWSERS})"}
    agents = sum(1 for p in procs if p["kind"] in ("hermesOneShot", "opencodeRun"))
    if agents >= MAX_AGENTS:
        return {"verdict": "skip", "reason": f"{agents} one-shot agents already running (limit {MAX_AGENTS})"}
    commit = 100.0 * (1 - snap["commitFreeKB"] / snap["commitLimitKB"]) if snap.get("commitLimitKB") else 0.0
    if commit >= MAX_COMMIT_PCT:
        return {"verdict": "skip", "reason": f"memory commit {commit:.1f}% (limit {MAX_COMMIT_PCT}%)"}
    return {"verdict": "ok", "reason": "ok", "browsers": len(browsers), "agents": agents, "commit": round(commit, 1)}


def guard_before_agent(role):
    stop = os.path.exists(STOP_FILE)
    d = decide_before(None if stop else snapshot(), stop)
    if d["verdict"] == "exit":
        _log(f"{role}: EXIT - {d['reason']}")
        print(f"[runaway-guard] {role}: {d['reason']} - exiting")
        sys.exit(3)
    if d["verdict"] == "stop":
        _log(f"{role}: STOP - {d['reason']}")
        if not os.path.exists(STOP_FILE):
            with open(STOP_FILE, "w", encoding="utf-8") as f:
                json.dump({"set_by": f"python runaway guard ({role}, pid {os.getpid()})",
                           "at": dt.datetime.now().astimezone().isoformat(timespec="seconds"), "reason": d["reason"],
                           "how_to_clear": "Operator only. Runbook: docs/20261019_*_MACHINE_FREEZE_RUNAWAY_AGENTS_FIX_AND_RUNBOOK_v1_0_0/04_RUNBOOK."},
                          f, indent=1)
        _alert("crit", f"{role} stopped itself", f"{d['reason']}. STOP_ALL_AGENTS written; the machine watchdog closes leaked browsers.")
        print(f"[runaway-guard] {role}: {d['reason']} - STOP_ALL_AGENTS written, exiting")
        sys.exit(3)
    if d["verdict"] == "skip":
        _log(f"{role}: SKIP - {d['reason']}")
        return {"ok": False, "reason": d["reason"], "t0": dt.datetime.now(dt.timezone.utc).timestamp()}
    _log(f"{role}: OK browsers={d['browsers']} agents={d['agents']} commit={d['commit']}")
    return {"ok": True, "reason": "ok", "t0": dt.datetime.now(dt.timezone.utc).timestamp()}


def cleanup_after_agent(t0, role):
    snap = snapshot()
    if not snap:
        return 0
    leaked = []
    for p in snap.get("procs", []):
        if p["kind"] == "cft" and p.get("top") and p.get("cftHermes") and p.get("created"):
            created = dt.datetime.fromisoformat(p["created"].replace("Z", "+00:00")).timestamp()
            if created >= t0 - 5:
                leaked.append(p)
    for p in leaked:
        subprocess.run(["taskkill", "/PID", str(p["id"]), "/T", "/F"], capture_output=True, creationflags=NO_WINDOW, timeout=60)
    if leaked:
        _log(f"{role}: closed {len(leaked)} Hermes browser(s) leaked by the run")
        _alert("warn", f"{role}: browser leak", f"{len(leaked)} Hermes Chrome browser(s) appeared during a {role} run and were closed.")
    return len(leaked)


def _selftest():
    snap = lambda procs, free=50: {"commitLimitKB": 1000, "commitFreeKB": 10 * free, "procs": procs}  # noqa: E731
    br = lambda i, top=True: {"id": i, "kind": "cft", "top": top, "cftHermes": True}  # noqa: E731
    cases = [("kill switch", decide_before(None, True)["verdict"], "exit"),
             ("snapshot failed", decide_before(None, False)["verdict"], "skip"),
             ("3 browsers ok", decide_before(snap([br(1), br(2), br(3)]), False)["verdict"], "ok"),
             ("4 browsers stop", decide_before(snap([br(i) for i in range(4)]), False)["verdict"], "stop"),
             ("children not counted", decide_before(snap([br(1)] + [br(9 + i, False) for i in range(20)]), False)["verdict"], "ok"),
             ("2 agents skip", decide_before(snap([{"id": 1, "kind": "opencodeRun"}, {"id": 2, "kind": "hermesOneShot"}]), False)["verdict"], "skip"),
             ("commit 85 skip", decide_before(snap([], 15), False)["verdict"], "skip")]
    ok = all(g == w for _, g, w in cases)
    for name, g, w in cases:
        print(("PASS " if g == w else "FAIL ") + f"{name} (got {g})")
    print("PY GUARD SELFTEST", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(_selftest() if "--selftest" in sys.argv else 0)
