"""Provider base class + shared HTTP helper."""
from __future__ import annotations

import time
from typing import List

import requests

from ..models import Job

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/122 Safari/537.36")


def http_get(url: str, timeout: int = 30, retries: int = 2, **kw) -> requests.Response:
    last = None
    for attempt in range(retries + 1):
        try:
            r = requests.get(url, headers={"User-Agent": UA, **kw.pop("headers", {})}, timeout=timeout, **kw)
            r.raise_for_status()
            return r
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(1.5 * (attempt + 1))
    raise last  # type: ignore[misc]


class Provider:
    source: str = "base"

    def __init__(self, slug: str):
        self.slug = slug

    @property
    def provider_slug(self) -> str:
        return self.slug

    def fetch(self, run_id: str) -> List[Job]:  # pragma: no cover - abstract
        raise NotImplementedError
