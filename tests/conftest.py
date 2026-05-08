"""Test fixtures: a fresh Settings/Engine per test, with mock provider and an
isolated audit dir so tests never touch the developer's real audit log.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from m3ta_uitars.audit import AuditLogger
from m3ta_uitars.config import Settings
from m3ta_uitars.engine import Engine
from m3ta_uitars.providers.mock import MockProvider
from m3ta_uitars.safety.governor import Governor


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    return Settings(
        provider="mock",
        runtime="hybrid",
        default_dry_run=False,
        action_allowlist=["observe", "screenshot", "wait", "navigate"],
        confirm_required=["type", "click", "key", "scroll"],
        host_allowlist=["example.com"],
        enforce_host_allowlist=True,
        audit_dir=tmp_path / "audit",
        audit_screenshots=True,
        task_timeout_seconds=10,
    )


@pytest.fixture
def engine(settings: Settings) -> Engine:
    return Engine(
        settings=settings,
        provider=MockProvider(),
        governor=Governor(settings),
        audit=AuditLogger(settings.audit_dir),
    )
