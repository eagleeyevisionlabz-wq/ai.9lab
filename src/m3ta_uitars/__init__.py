"""M3ta-0S UI-TARS integration layer.

Surfaces:
  - MCP server (`m3ta_uitars.server.mcp_server`)
  - HTTP webhooks for n8n / OpenClaw (`m3ta_uitars.server.http_app`)
  - Agent SDK (`m3ta_uitars.sdk`)
"""

from m3ta_uitars.contracts import (
    Action,
    ActionType,
    Observation,
    Plan,
    Task,
    TaskRequest,
    TaskResult,
    TaskStatus,
)
from m3ta_uitars.engine import Engine
from m3ta_uitars.config import Settings, get_settings

__all__ = [
    "Action",
    "ActionType",
    "Observation",
    "Plan",
    "Task",
    "TaskRequest",
    "TaskResult",
    "TaskStatus",
    "Engine",
    "Settings",
    "get_settings",
]

__version__ = "0.1.0"
