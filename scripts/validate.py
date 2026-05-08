"""End-to-end validation script.

Exercises the engine, MCP tool dispatcher, HTTP surface, and SDK against the
mock provider with no external dependencies. Used for CI smoke checks and as
a fallback when pytest isn't available.

Run:
  python -m scripts.validate
"""

from __future__ import annotations

import asyncio
import json
import sys
import tempfile
from pathlib import Path

from fastapi.testclient import TestClient

from m3ta_uitars.audit import AuditLogger
from m3ta_uitars.config import Settings
from m3ta_uitars.contracts import TaskStatus
from m3ta_uitars.engine import Engine
from m3ta_uitars.providers.mock import MockProvider
from m3ta_uitars.safety.governor import Governor
from m3ta_uitars.sdk import InProcessClient
from m3ta_uitars.server.http_app import create_app
from m3ta_uitars.server.mcp_server import TOOL_DEFINITIONS, tool_run_task


def _build(tmp: Path) -> tuple[Settings, Engine]:
    settings = Settings(
        provider="mock",
        runtime="hybrid",
        default_dry_run=False,
        action_allowlist=["observe", "screenshot", "wait", "navigate"],
        confirm_required=["type", "click", "key", "scroll"],
        host_allowlist=["example.com"],
        enforce_host_allowlist=True,
        audit_dir=tmp / "audit",
        audit_screenshots=True,
        task_timeout_seconds=10,
    )
    engine = Engine(
        settings=settings,
        provider=MockProvider(),
        governor=Governor(settings),
        audit=AuditLogger(settings.audit_dir),
    )
    return settings, engine


async def _run() -> int:
    failures: list[str] = []

    with tempfile.TemporaryDirectory() as tmp_str:
        tmp = Path(tmp_str)

        # 1. Engine + SDK
        settings, engine = _build(tmp)
        sdk = InProcessClient(engine=engine)
        task = await sdk.run_computer_task(
            instruction="navigate then snapshot",
            agent_id="qubii",
            starting_url="https://example.com",
            dry_run=True,
            confirmation_token="ok",
        )
        if task.status != TaskStatus.SUCCEEDED:
            failures.append(f"sdk dry-run status={task.status}")

        log = await sdk.get_audit_log(task.id)
        if not any(e["event"] == "task_completed" for e in log):
            failures.append("audit log missing task_completed")

        # 2. MCP tool dispatcher
        if {t["name"] for t in TOOL_DEFINITIONS} != {
            "m3ta_uitars_run_task",
            "m3ta_uitars_observe",
            "m3ta_uitars_status",
            "m3ta_uitars_cancel",
            "m3ta_uitars_audit_log",
        }:
            failures.append("MCP tool definitions changed unexpectedly")
        mcp_out = await tool_run_task(
            engine,
            {
                "instruction": "x",
                "agent_id": "hermes",
                "starting_url": "https://example.com",
                "dry_run": True,
                "confirmation_token": "ok",
            },
        )
        if not mcp_out.get("ok"):
            failures.append(f"mcp run_task failed: {mcp_out}")

        # 3. HTTP surface
        settings2, engine2 = _build(tmp)
        client = TestClient(create_app(engine=engine2, settings=settings2))
        resp = client.get("/v1/health")
        if resp.status_code != 200:
            failures.append(f"/v1/health -> {resp.status_code}")

        resp = client.post(
            "/v1/tasks",
            json={
                "instruction": "snapshot",
                "agent_id": "metatron",
                "starting_url": "https://example.com",
                "dry_run": True,
                "confirmation_token": "ok",
            },
        )
        if resp.status_code != 200:
            failures.append(f"POST /v1/tasks -> {resp.status_code} {resp.text}")
        elif resp.json()["task"]["status"] != "succeeded":
            failures.append(f"task did not succeed: {resp.json()}")

        # 4. Safety: blocked host
        resp = client.post(
            "/v1/tasks",
            json={
                "instruction": "x",
                "agent_id": "qubii",
                "starting_url": "https://forbidden.test",
            },
        )
        if resp.status_code != 403:
            failures.append(
                f"expected 403 for blocked host, got {resp.status_code}"
            )

    summary = {
        "checks_run": 4,
        "failures": failures,
        "ok": not failures,
    }
    print(json.dumps(summary, indent=2))
    return 0 if not failures else 1


def main() -> int:
    return asyncio.run(_run())


if __name__ == "__main__":
    sys.exit(main())
