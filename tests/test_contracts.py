"""Schema validation."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from m3ta_uitars.contracts import (
    Action,
    ActionType,
    Surface,
    Task,
    TaskRequest,
    TaskStatus,
)


def test_task_request_requires_agent_id() -> None:
    with pytest.raises(ValidationError):
        TaskRequest(instruction="open browser", agent_id="")


def test_task_request_minimal() -> None:
    req = TaskRequest(instruction="search", agent_id="qubii")
    assert req.surface == Surface.BROWSER
    assert req.metadata == {}


def test_task_default_status() -> None:
    task = Task(request=TaskRequest(instruction="i", agent_id="hermes"))
    assert task.status == TaskStatus.PENDING
    assert task.id.startswith("tsk_")


def test_action_type_enum_round_trip() -> None:
    a = Action(type=ActionType.NAVIGATE, target="https://example.com")
    dumped = a.model_dump(mode="json")
    assert dumped["type"] == "navigate"
    rebuilt = Action.model_validate(dumped)
    assert rebuilt.type == ActionType.NAVIGATE
