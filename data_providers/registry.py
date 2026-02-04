from __future__ import annotations

from data_providers.base import ProviderBundle
from data_providers.demo_provider import load_demo_bundle


def build_provider_bundle() -> ProviderBundle:
    return load_demo_bundle()
