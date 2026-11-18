"""Read a fresh, verified public-careers snapshot. Failure falls back to the normal provider."""
from datetime import datetime, timezone
import gzip
from io import BytesIO
import json
import os
from pathlib import Path
import re
from threading import Lock
import time
from urllib.parse import urlsplit

import requests

TAG = "abet-workday-listings-v1"
RELEASE_URL = "https://api.github.com/repos/misterplusev/job-radar/releases/tags/" + TAG
_lock = Lock()
_cache = (None, 0, None)


def _unpack(raw):
    if len(raw) > 3_000_000:
        raise ValueError("compressed Workday snapshot is over budget")
    with gzip.GzipFile(fileobj=BytesIO(raw)) as stream:
        payload = stream.read(10_000_001)
    if len(payload) > 10_000_000:
        raise ValueError("Workday snapshot is over budget")
    return json.loads(payload)


def _fetch(path):
    if path:
        return _unpack(Path(path).read_bytes())
    with requests.Session() as client:
        res = client.get(RELEASE_URL, timeout=(4, 12))
        res.raise_for_status()
        assets = [a for a in res.json().get("assets", []) if a.get("state") == "uploaded"
                  and re.fullmatch(r"listings-[0-9]+-[0-9]+\.json\.gz", a.get("name", ""))
                  and 0 < a.get("size", 0) <= 3_000_000]
        if not assets:
            raise ValueError("No verified Workday listing asset")
        latest = max(assets, key=lambda a: tuple(map(int, re.findall(r"\d+", a["name"]))))
        url = "https://github.com/misterplusev/job-radar/releases/download/" + TAG + "/" + latest["name"]
        res = client.get(url, timeout=(5, 18), stream=True)
        res.raise_for_status()
        with BytesIO() as body:
            for chunk in res.iter_content(65536):
                body.write(chunk)
                if body.tell() > 3_000_000:
                    raise ValueError("Workday download exceeds budget")
            return _unpack(body.getvalue())


def board(host, tenant, site):
    path = os.environ.get("WORKDAY_LISTINGS_FILE")
    if not path and os.environ.get("WORKDAY_LISTINGS_ENABLED") != "1":
        return None
    global _cache
    key = (path, os.environ.get("GITHUB_RUN_ID"))
    with _lock:
        if _cache[0] != key or time.monotonic() >= _cache[1]:
            try:
                value = _fetch(path)
            except (OSError, ValueError, requests.RequestException) as exc:
                print(f"[WORKDAY_SNAPSHOT] unavailable: {type(exc).__name__}", flush=True)
                value = None
            _cache = (key, time.monotonic() + 120, value)
        bundle = _cache[2]
    if not isinstance(bundle, dict) or bundle.get("schema") != 1:
        return None
    try:
        observed = datetime.fromisoformat(bundle["observed_at"])
        age = (datetime.now(timezone.utc) - observed).total_seconds()
        if age < -60 or age > 3 * 3600:
            return None
        key = host + "/" + tenant + "/" + site
        data = bundle["boards"][key]
        rows = data["jobs"]
        if not isinstance(rows, list) or type(data["total"]) != int or not 0 <= len(rows) == data["total"] <= 5000:
            raise ValueError("count mismatch")
        paths = set()
        for row in rows:
            p = row["externalPath"]
            if (not isinstance(p, str) or not p.startswith("/job/") or "\\" in p
                    or urlsplit(p).query or urlsplit(p).fragment or any(v in (".","..") for v in p.split("/"))
                    or not isinstance(row["title"], str) or not row["title"].strip() or p in paths):
                raise ValueError("invalid listing identity")
            paths.add(p)
    except (KeyError, TypeError, ValueError) as exc:
        print(f"[WORKDAY_SNAPSHOT] {host}/{site} unavailable: {type(exc).__name__}", flush=True)
        return None
    print(f"[WORKDAY_SNAPSHOT] {host}/{site}: {len(rows)} verified URLs observed {observed.isoformat()}", flush=True)
    return bundle["observed_at"], rows
