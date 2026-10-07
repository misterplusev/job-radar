"""Ingestion providers. One module per source; each returns List[Job] via the Job contract."""
from typing import List

from .base import Provider
from .greenhouse import GreenhouseProvider
from .lever import LeverProvider
from .ashby import AshbyProvider
from .amazon import AmazonProvider

_REGISTRY = {
    "greenhouse": GreenhouseProvider,
    "lever": LeverProvider,
    "ashby": AshbyProvider,
    "amazon": AmazonProvider,
}


def build_providers(targets: dict) -> List[Provider]:
    """Instantiate providers from config/targets.json: {"greenhouse": [slugs], "lever": [...], ...}."""
    providers: List[Provider] = []
    for source, cls in _REGISTRY.items():
        for slug in targets.get(source, []):
            providers.append(cls(slug))
    return providers
