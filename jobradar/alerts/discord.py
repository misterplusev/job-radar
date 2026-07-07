"""Discord alerts: one compact digest of strong new matches, deduped via `alerted` flag.

If no webhook is configured, prints the digest (dry-run) instead of posting — so the
build/test never spams the real channel.
"""
from __future__ import annotations

import json
from typing import List

import requests

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122 Safari/537.36"
MAX_LINES = 15


def _active_model(settings) -> str:
    return settings.ANTHROPIC_MODEL if settings.ANTHROPIC_API_KEY else "heuristic"


def _digest(rows: List[dict]) -> str:
    lines = [f"**Job Radar — {len(rows)} new strong match(es)**", ""]
    for r in rows[:MAX_LINES]:
        loc = (r.get("location") or "").split(";")[0].strip()
        lines.append(f"`{r['fit_score']:>3}` **{r.get('title','?')}** — {r.get('company','?')}"
                     f"{' · ' + loc if loc else ''}\n<{r.get('url','')}>")
    if len(rows) > MAX_LINES:
        lines.append(f"\n…+{len(rows) - MAX_LINES} more in the dashboard")
    text = "\n".join(lines)
    return text[:1990]


def send_alerts(settings, store) -> int:
    model = _active_model(settings)
    rows = store.fetch_alertable(settings.ALERT_MIN_SCORE, model)
    if not rows:
        print("[alert] no new matches at/above threshold")
        return 0

    content = _digest(rows)
    webhook = settings.DISCORD_JOB_RADAR_WEBHOOK

    if not webhook:
        print("[alert] DRY-RUN (no DISCORD_JOB_RADAR_WEBHOOK set):\n" + content)
        return 0

    r = requests.post(webhook, headers={"User-Agent": UA, "Content-Type": "application/json"},
                      data=json.dumps({"username": "Job Radar", "content": content}), timeout=30)
    r.raise_for_status()
    # only the ones we actually showed get marked (rest alert next run)
    store.mark_alerted([row["score_id"] for row in rows[:MAX_LINES]])
    return min(len(rows), MAX_LINES)
