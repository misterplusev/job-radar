"""Disposition of undelivered team notifications under the existing posting-age rule."""
from collections import defaultdict
from datetime import datetime, timedelta, timezone


def posting_time(row):
    value = row.get("posted_at") or row.get("first_seen_at")
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    except (TypeError, ValueError, OverflowError):
        return None


def reconcile(storage, max_age_days, *, apply=False, as_of=None):
    now = as_of or datetime.now(timezone.utc)
    cutoff = now - timedelta(days=max_age_days)
    protected = {"delivered_at": "is.null"}
    if storage.has_message_id_column():
        protected["discord_message_id"] = "is.null"
    ledger = storage.rows("team_job_notifications", select="id,url,status", filters={
        **protected, "status":"in.(pending,expired,closed)"})
    report = {"as_of":now.isoformat(), "window_days":max_age_days, "apply":apply,
              "eligible":0, "awaiting_job":0, "unknown_date":0, "transitions":{}, "changed_ids":{}}
    if not ledger:
        return report
    jobs = {r["url"]: r for r in storage.rows("team_jobs", select="url,is_active,posted_at,first_seen_at")}
    changes = defaultdict(list)
    for row in ledger:
        job = jobs.get(row["url"])
        if job is None or job.get("is_active") is None:
            report["awaiting_job"] += 1
            continue
        stamp = posting_time(job)
        if not job["is_active"]:
            target = "closed"
        elif stamp is None:
            report["unknown_date"] += 1
            continue
        else:
            target = "pending" if stamp >= cutoff else "expired"
            report["eligible"] += target == "pending"
        if row["status"] != target:
            changes[(row["status"], target)].append(row["id"])
    for (previous, target), ids in changes.items():
        transition = previous + "_to_" + target
        report["transitions"][transition] = len(ids)
        if not apply:
            continue
        changed = []
        for start in range(0, len(ids), 100):
            batch = ids[start:start+100]
            response = storage.request("PATCH", "team_job_notifications", returning=True, params={
                "id":"in.(" + ",".join(str(int(i)) for i in batch) + ")",
                "status":"eq." + previous, **protected,
                "select":"id"}, json={"status":target})
            changed.extend(row["id"] for row in response.json())
        report["changed_ids"][transition] = changed
    return report
