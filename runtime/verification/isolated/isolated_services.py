"""PostgREST gateway and Discord-compatible receiver on the hosted runner only."""
import base64
import hashlib
import hmac
import json
import os
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
import time
from urllib.parse import urlsplit

import requests

ROOT = Path.cwd()
BASE = "http://127.0.0.1:8187"
PGRST = "http://127.0.0.1:3100"
messages = []


def enc(raw):
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def token():
    data = enc(b'{"alg":"HS256","typ":"JWT"}') + "." + enc(b'{"role":"service_role"}')
    signature = hmac.digest(b"isolated-development-proof-key-0123456789abcdef", data.encode(), "sha256")
    return data + "." + enc(signature)


class Gateway(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def relay(self):
        body = self.rfile.read(int(self.headers.get("Content-Length") or 0))
        if self.path.startswith("/rest/v1/"):
            res = requests.request(self.command, PGRST + self.path[len("/rest/v1"):], data=body or None,
                  headers={k:v for k,v in self.headers.items() if k.lower() in {"authorization","prefer","content-type","range"}}, timeout=15)
            self.send_response(res.status_code)
            for k in ("Content-Type","Content-Range"):
                if k in res.headers: self.send_header(k, res.headers[k])
            data = res.content
        elif self.command == "POST" and self.path == "/test-webhook?wait=true":
            payload = json.loads(body)
            assert 1 <= len(payload["embeds"]) <= 5
            receipt = {"id": str(9000+len(messages)), "channel_id":"8100", "webhook_id":"8200"}
            messages.append({"receipt":receipt, "urls":[e["url"] for e in payload["embeds"]]})
            self.send_response(200)
            self.send_header("Content-Type","application/json")
            data = json.dumps(receipt).encode()
        else:
            self.send_error(404)
            return
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    do_GET = do_PATCH = do_POST = relay


def rest(method, table, **options):
    headers = {"Authorization":"Bearer "+token(), **options.pop("headers",{})}
    response = requests.request(method, BASE+"/rest/v1/"+table, headers=headers, timeout=20, **options)
    response.raise_for_status()
    return response.json() if response.content else None


@contextmanager
def services():
    if os.environ.get("GITHUB_ACTIONS") != "true" or not os.environ.get("GITHUB_REF_NAME","").startswith("codex/isolated-"):
        raise RuntimeError("This harness requires the hosted development branch")
    for key in ("SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY", "DISCORD_WEBHOOK_JOBS"):
        if os.environ.get(key): raise RuntimeError("Unexpected preconfigured service "+key)
    os.environ.update(SUPABASE_URL=BASE, SUPABASE_SERVICE_ROLE_KEY=token(), SPORTSBOOK_OUTBOX="1",
                      DISCORD_WEBHOOK_JOBS=BASE+"/test-webhook", JOBRADAR_MODULE="sportsbook")
    (ROOT/"proof").mkdir(exist_ok=True)
    with ThreadingHTTPServer(("127.0.0.1",8187), Gateway) as httpd:
        t = Thread(target=httpd.serve_forever, daemon=True)
        t.start()
        try:
            for i in range(20):
                try:
                    rest("GET","jobs",params={"select":"id","limit":1}); break
                except requests.RequestException:
                    if i == 19: raise
                    time.sleep(1)
            yield
        finally:
            httpd.shutdown()
            t.join(3)
