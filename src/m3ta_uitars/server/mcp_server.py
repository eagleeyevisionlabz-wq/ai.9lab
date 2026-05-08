"""MCP server surface for M3ta-0S UI-TARS integration.

Exposes the capability contract as MCP tools:
  - m3ta_uitars_run_task
  - m3ta_uitars_observe
  - m3ta_uitars_status
  - m3ta_uitars_cancel
  - m3ta_uitars_audit_log

Run:
  python -m m3ta_uitars.server.mcp_server

The MCP package (`mcp>=1.0`) is an optional dependency. When it isn't
installed, importing this module is still safe — `main()` raises with a clear
message. The tool handlers are exported as plain async functions so they can
be unit-tested without the MCP runtime.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from m3ta_uitars.contracts import Surface, TaskRequest
from m3ta_uitars.engine import Engine, TaskNotFound
from m3ta_uitars.safety.governor import SafetyError

log = logging.getLogger(__name__)

TOOL_DEFINITIONS: list[dict[str, Any]] = [
    {
        "name": "m3ta_uitars_run_task",
        "description": (
            "Submit a visual computer-use task to a UI-TARS-style operator and drive it to "
            "completion. Honors dry-run, allowlists, and confirmation gates. Returns the "
            "final Task record (status, plan, result, audit_log_path)."
        ),
        "inputSchema": {
            "type": "object",
            "required": ["instruction", "agent_id"],
            "properties": {
                "instruction": {"type": "string", "minLength": 1},
                "agent_id": {
                    "type": "string",
                    "description": "Calling agent: qubii | hermes | metatron | m3ta-os | ...",
                },
                "surface": {
                    "type": "string",
                    "enum": ["browser", "desktop", "mobile"],
                    "default": "browser",
                },
                "starting_url": {"type": "string"},
                "dry_run": {"type": "boolean"},
                "confirmation_token": {
                    "type": "string",
                    "description": "Required when plan contains risky actions.",
                },
                "metadata": {"type": "object", "additionalProperties": True},
                "timeout_seconds": {"type": "integer", "minimum": 1},
            },
        },
    },
    {
        "name": "m3ta_uitars_observe",
        "description": (
            "Capture a single observation from the current operator surface without "
            "executing any actions."
        ),
        "inputSchema": {
            "type": "object",
            "required": ["agent_id"],
            "properties": {
                "agent_id": {"type": "string"},
                "surface": {
                    "type": "string",
                    "enum": ["browser", "desktop", "mobile"],
                    "default": "browser",
                },
                "starting_url": {"type": "string"},
                "instruction": {
                    "type": "string",
                    "default": "observe",
                },
            },
        },
    },
    {
        "name": "m3ta_uitars_status",
        "description": "Return the current Task record for a given task_id.",
        "inputSchema": {
            "type": "object",
            "required": ["task_id"],
            "properties": {"task_id": {"type": "string"}},
        },
    },
    {
        "name": "m3ta_uitars_cancel",
        "description": "Cancel a running task. Idempotent.",
        "inputSchema": {
            "type": "object",
            "required": ["task_id"],
            "properties": {
                "task_id": {"type": "string"},
                "reason": {"type": "string"},
            },
        },
    },
    {
        "name": "m3ta_uitars_audit_log",
        "description": "Return the JSONL audit entries for a given task_id.",
        "inputSchema": {
            "type": "object",
            "required": ["task_id"],
            "properties": {"task_id": {"type": "string"}},
        },
    },
]


# ---------- thin adapters used by both MCP runtime and tests ----------------


async def tool_run_task(engine: Engine, args: dict[str, Any]) -> dict[str, Any]:
    request = TaskRequest(
        instruction=args["instruction"],
        agent_id=args["agent_id"],
        surface=Surface(args.get("surface", "browser")),
        starting_url=args.get("starting_url"),
        dry_run=args.get("dry_run"),
        confirmation_token=args.get("confirmation_token"),
        metadata=args.get("metadata") or {},
        timeout_seconds=args.get("timeout_seconds"),
    )
    try:
        task = await engine.submit_task(request)
    except SafetyError as exc:
        return {"ok": False, "error": f"safety: {exc}"}
    task = await engine.run_task(task.id)
    return {"ok": True, "task": task.model_dump(mode="json")}


async def tool_observe(engine: Engine, args: dict[str, Any]) -> dict[str, Any]:
    request = TaskRequest(
        instruction=args.get("instruction", "observe"),
        agent_id=args["agent_id"],
        surface=Surface(args.get("surface", "browser")),
        starting_url=args.get("starting_url"),
    )
    obs = await engine.observe(request)
    return {"ok": True, "observation": obs.model_dump(mode="json")}


async def tool_status(engine: Engine, args: dict[str, Any]) -> dict[str, Any]:
    try:
        task = engine.status(args["task_id"])
    except TaskNotFound:
        return {"ok": False, "error": "task_not_found"}
    return {"ok": True, "task": task.model_dump(mode="json")}


async def tool_cancel(engine: Engine, args: dict[str, Any]) -> dict[str, Any]:
    try:
        task = await engine.cancel_task(args["task_id"], args.get("reason"))
    except TaskNotFound:
        return {"ok": False, "error": "task_not_found"}
    return {"ok": True, "task": task.model_dump(mode="json")}


async def tool_audit_log(engine: Engine, args: dict[str, Any]) -> dict[str, Any]:
    entries = engine.audit_log(args["task_id"])
    return {"ok": True, "entries": entries}


TOOL_DISPATCH = {
    "m3ta_uitars_run_task": tool_run_task,
    "m3ta_uitars_observe": tool_observe,
    "m3ta_uitars_status": tool_status,
    "m3ta_uitars_cancel": tool_cancel,
    "m3ta_uitars_audit_log": tool_audit_log,
}


# ---------- MCP runtime entry point -----------------------------------------


def main() -> None:  # pragma: no cover - requires mcp runtime
    try:
        from mcp.server import Server  # type: ignore
        from mcp.server.stdio import stdio_server  # type: ignore
        from mcp.types import TextContent, Tool  # type: ignore
    except ImportError as exc:  # pragma: no cover
        raise SystemExit(
            "MCP server requires the optional `mcp` extra: pip install m3ta-uitars[mcp]"
        ) from exc

    logging.basicConfig(level=logging.INFO)
    engine = Engine()
    server = Server("m3ta-uitars")

    @server.list_tools()  # type: ignore[misc]
    async def _list_tools() -> list[Any]:
        return [
            Tool(
                name=t["name"],
                description=t["description"],
                inputSchema=t["inputSchema"],
            )
            for t in TOOL_DEFINITIONS
        ]

    @server.call_tool()  # type: ignore[misc]
    async def _call_tool(name: str, arguments: dict[str, Any]) -> list[Any]:
        handler = TOOL_DISPATCH.get(name)
        if handler is None:
            payload = {"ok": False, "error": f"unknown tool: {name}"}
        else:
            payload = await handler(engine, arguments or {})
        return [TextContent(type="text", text=json.dumps(payload, default=str))]

    async def _run() -> None:
        async with stdio_server() as (read, write):
            await server.run(read, write, server.create_initialization_options())

    asyncio.run(_run())


if __name__ == "__main__":  # pragma: no cover
    main()
