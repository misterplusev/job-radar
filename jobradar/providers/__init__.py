"""Ingestion providers. One module per source; each returns List[Job] via the Job contract."""
from typing import List

from .base import Provider
from .greenhouse import GreenhouseProvider
from .lever import LeverProvider
from .ashby import AshbyProvider
from .amazon import AmazonProvider
from .workday import WorkdayProvider

_REGISTRY = {
    "greenhouse": GreenhouseProvider,
    "lever": LeverProvider,
    "ashby": AshbyProvider,
    "amazon": AmazonProvider,
    "workday": WorkdayProvider,
}


def build_providers(targets: dict) -> List[Provider]:
    """Instantiate providers from config/targets.json.

    Target entries are strings ("slug") or objects ({"slug": ..., "content": false}).
    """
    providers: List[Provider] = []
    for source, cls in _REGISTRY.items():
        for entry in targets.get(source, []):
            if isinstance(entry, dict):
                slug = entry.get("slug") or ""
                opts = {k: v for k, v in entry.items() if k != "slug"}
            else:
                slug = entry
                opts = {}
            if not slug:
                continue
            providers.append(cls(slug, **opts) if opts else cls(slug))
    return providers
