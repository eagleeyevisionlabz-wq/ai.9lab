"""Provider factory — selects an implementation from settings."""

from __future__ import annotations

from m3ta_uitars.config import Settings
from m3ta_uitars.providers.base import Provider


def build_provider(settings: Settings) -> Provider:
    name = settings.provider
    if name == "mock":
        from m3ta_uitars.providers.mock import MockProvider

        return MockProvider()
    if name == "local_uitars":
        from m3ta_uitars.providers.local_uitars import LocalUITARSProvider

        return LocalUITARSProvider(
            bridge_url=settings.local_bridge_url,
            bridge_token=settings.local_bridge_token,
        )
    if name == "remote_operator":
        from m3ta_uitars.providers.remote_operator import RemoteOperatorProvider

        return RemoteOperatorProvider(
            base_url=settings.remote_base_url,
            api_key=settings.remote_api_key,
            model=settings.remote_model,
        )
    raise ValueError(f"unknown provider: {name!r}")
