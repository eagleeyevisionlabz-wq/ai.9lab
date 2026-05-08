"""Capability contract for visual computer-use tasks.

Stable, provider-agnostic schemas. All providers and surfaces (MCP, HTTP, SDK)
exchange these types so swapping providers is reversible and auditable.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


class ActionType(str, Enum):
    OBSERVE = "observe"
    SCREENSHOT = "screenshot"
    CLICK = "click"
    TYPE = "type"
    KEY = "key"
    SCROLL = "scroll"
    NAVIGATE = "navigate"
    WAIT = "wait"


class TaskStatus(str, Enum):
    PENDING = "pending"
    PLANNING = "planning"
    AWAITING_CONFIRMATION = "awaiting_confirmation"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMED_OUT = "timed_out"


class Surface(str, Enum):
    BROWSER = "browser"
    DESKTOP = "desktop"
    MOBILE = "mobile"


class Action(BaseModel):
    """A single primitive action a provider can execute."""

    type: ActionType
    target: Optional[str] = Field(
        default=None,
        description="Selector / coordinates / URL — semantics depend on action type.",
    )
    value: Optional[str] = Field(
        default=None, description="Text to type, key chord, scroll delta, etc."
    )
    note: Optional[str] = None


class Observation(BaseModel):
    """The agent's view of the environment at a moment in time."""

    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    surface: Surface = Surface.BROWSER
    url: Optional[str] = None
    title: Optional[str] = None
    text_summary: Optional[str] = None
    screenshot_ref: Optional[str] = Field(
        default=None,
        description="Opaque ref/path to a stored screenshot. Never inline base64 in audit.",
    )
    elements: list[dict[str, Any]] = Field(default_factory=list)


class Plan(BaseModel):
    """A planned sequence of actions before execution."""

    rationale: str = ""
    steps: list[Action] = Field(default_factory=list)
    requires_confirmation: bool = False
    risky_actions: list[ActionType] = Field(default_factory=list)


class TaskRequest(BaseModel):
    """Input to `run_task`."""

    instruction: str = Field(..., min_length=1)
    surface: Surface = Surface.BROWSER
    starting_url: Optional[str] = None
    agent_id: str = Field(
        ..., description="Identifier of the calling agent (qubii, hermes, metatron, ...)."
    )
    dry_run: Optional[bool] = Field(
        default=None,
        description="If None, defaults to settings.default_dry_run.",
    )
    confirmation_token: Optional[str] = Field(
        default=None,
        description="Required when plan contains actions in confirm_required list.",
    )
    metadata: dict[str, Any] = Field(default_factory=dict)
    timeout_seconds: Optional[int] = None

    @field_validator("agent_id")
    @classmethod
    def _agent_id_nonblank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("agent_id is required")
        return v.strip()


class TaskResult(BaseModel):
    """Terminal outcome of a task."""

    ok: bool
    final_observation: Optional[Observation] = None
    executed_actions: list[Action] = Field(default_factory=list)
    error: Optional[str] = None
    summary: Optional[str] = None


class Task(BaseModel):
    """A persistent task record. Returned by `status` / `run_task`."""

    id: str = Field(default_factory=lambda: f"tsk_{uuid4().hex[:16]}")
    request: TaskRequest
    status: TaskStatus = TaskStatus.PENDING
    plan: Optional[Plan] = None
    result: Optional[TaskResult] = None
    audit_log_path: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc)


class CancelRequest(BaseModel):
    task_id: str
    reason: Optional[str] = None


class StatusResponse(BaseModel):
    task: Task


class AuditEntry(BaseModel):
    """A single audit-log line. Persisted as JSONL."""

    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    task_id: str
    agent_id: str
    event: Literal[
        "task_created",
        "plan_generated",
        "action_attempted",
        "action_completed",
        "action_blocked",
        "screenshot_captured",
        "task_completed",
        "task_failed",
        "task_cancelled",
        "confirmation_required",
    ]
    detail: dict[str, Any] = Field(default_factory=dict)
