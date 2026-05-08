"""Environment-driven settings.

All secrets and endpoints are read from env vars. Never hardcode.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

ProviderName = Literal["local_uitars", "remote_operator", "mock"]
RuntimeName = Literal["macos_local", "docker_server", "hybrid"]


def _csv(name: str, default: str = "") -> list[str]:
    raw = os.getenv(name, default)
    return [item.strip() for item in raw.split(",") if item.strip()]


def _bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


class Settings(BaseModel):
    provider: ProviderName = Field(default="mock")
    runtime: RuntimeName = Field(default="hybrid")
    log_level: str = Field(default="INFO")

    http_host: str = Field(default="127.0.0.1")
    http_port: int = Field(default=8765)
    api_token: str = Field(default="")
    cors_origins: list[str] = Field(default_factory=list)

    local_bridge_url: str = Field(default="http://127.0.0.1:9001")
    local_bridge_token: str = Field(default="")

    remote_base_url: str = Field(default="")
    remote_api_key: str = Field(default="")
    remote_model: str = Field(default="ui-tars-1.5")

    default_dry_run: bool = Field(default=True)
    action_allowlist: list[str] = Field(
        default_factory=lambda: ["observe", "screenshot", "wait"]
    )
    confirm_required: list[str] = Field(
        default_factory=lambda: ["navigate", "type", "click", "key", "scroll"]
    )
    host_allowlist: list[str] = Field(default_factory=list)
    enforce_host_allowlist: bool = Field(default=True)

    audit_dir: Path = Field(default=Path("./.audit"))
    audit_screenshots: bool = Field(default=True)
    task_timeout_seconds: int = Field(default=300)

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            provider=os.getenv("M3TA_UITARS_PROVIDER", "mock"),  # type: ignore[arg-type]
            runtime=os.getenv("M3TA_UITARS_RUNTIME", "hybrid"),  # type: ignore[arg-type]
            log_level=os.getenv("M3TA_UITARS_LOG_LEVEL", "INFO"),
            http_host=os.getenv("M3TA_UITARS_HTTP_HOST", "127.0.0.1"),
            http_port=int(os.getenv("M3TA_UITARS_HTTP_PORT", "8765")),
            api_token=os.getenv("M3TA_UITARS_API_TOKEN", ""),
            cors_origins=_csv("M3TA_UITARS_CORS_ORIGINS"),
            local_bridge_url=os.getenv(
                "M3TA_UITARS_LOCAL_BRIDGE_URL", "http://127.0.0.1:9001"
            ),
            local_bridge_token=os.getenv("M3TA_UITARS_LOCAL_BRIDGE_TOKEN", ""),
            remote_base_url=os.getenv("M3TA_UITARS_REMOTE_BASE_URL", ""),
            remote_api_key=os.getenv("M3TA_UITARS_REMOTE_API_KEY", ""),
            remote_model=os.getenv("M3TA_UITARS_REMOTE_MODEL", "ui-tars-1.5"),
            default_dry_run=_bool("M3TA_UITARS_DEFAULT_DRY_RUN", True),
            action_allowlist=_csv(
                "M3TA_UITARS_ACTION_ALLOWLIST", "observe,screenshot,wait"
            ),
            confirm_required=_csv(
                "M3TA_UITARS_CONFIRM_REQUIRED", "navigate,type,click,key,scroll"
            ),
            host_allowlist=_csv("M3TA_UITARS_HOST_ALLOWLIST"),
            enforce_host_allowlist=_bool("M3TA_UITARS_ENFORCE_HOST_ALLOWLIST", True),
            audit_dir=Path(os.getenv("M3TA_UITARS_AUDIT_DIR", "./.audit")),
            audit_screenshots=_bool("M3TA_UITARS_AUDIT_SCREENSHOTS", True),
            task_timeout_seconds=int(
                os.getenv("M3TA_UITARS_TASK_TIMEOUT_SECONDS", "300")
            ),
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings.from_env()


def reset_settings_cache() -> None:
    """Clear the cached settings — used by tests."""
    get_settings.cache_clear()
