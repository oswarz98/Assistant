from __future__ import annotations

from data.api_base import MarketDataClient
from data.demo_client import DemoDataClient


def build_client() -> MarketDataClient:
    return DemoDataClient()
