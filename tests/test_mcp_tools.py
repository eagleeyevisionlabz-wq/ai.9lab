"""MCP tool dispatcher tests (no MCP runtime required)."""

from __future__ import annotations

import pytest

from m3ta_uitars.engine import Engine
from m3ta_uitars.server.mcp_server import (
    TOOL_DEFINITIONS,
    TOOL_DISPATCH,
    tool_audit_log,
    tool_cancel,
    tool_observe,
    tool_run_task,
    tool_status,
)


def test_tool_definitions_have_expected_shape() -> None:
    names = {t["name"] for t in TOOL_DEFINITIONS}
    assert names == {
        "m3ta_uitars_run_task",
        "m3ta_uitars_observe",
        "m3ta_uitars_status",
        "m3ta_uitars_cancel",
        "m3ta_uitars_audit_log",
    }
    for tool in TOOL_DEFINITIONS:
        assert tool["description"]
        assert tool["inputSchema"]["type"] == "object"


def test_tool_dispatch_covers_all_definitions() -> None:
    names = {t["name"] for t in TOOL_DEFINITIONS}
    assert names == set(TOOL_DISPATCH)


@pytest.mark.asyncio
async def test_run_task_tool_dry_run(engine: Engine) -> None:
    result = await tool_run_task(
        engine,
        {
            "instruction": "search",
            "agent_id": "qubii",
            "starting_url": "https://example.com",
            "dry_run": True,
            "confirmation_token": "ok",
        },
    )
    assert result["ok"]
    assert result["task"]["status"] == "succeeded"


@pytest.mark.asyncio
async def test_observe_tool(engine: Engine) -> None:
    result = await tool_observe(
        engine,
        {"agent_id": "hermes", "starting_url": "https://example.com"},
    )
    assert result["ok"]
    assert "observation" in result


@pytest.mark.asyncio
async def test_status_unknown(engine: Engine) -> None:
    out = await tool_status(engine, {"task_id": "tsk_missing"})
    assert out == {"ok": False, "error": "task_not_found"}


@pytest.mark.asyncio
async def test_cancel_unknown(engine: Engine) -> None:
    out = await tool_cancel(engine, {"task_id": "tsk_missing"})
    assert out == {"ok": False, "error": "task_not_found"}


@pytest.mark.asyncio
async def test_audit_log_empty_for_unknown(engine: Engine) -> None:
    out = await tool_audit_log(engine, {"task_id": "tsk_missing"})
    assert out == {"ok": True, "entries": []}
