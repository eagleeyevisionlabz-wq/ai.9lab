"""Engine end-to-end tests using the mock provider."""

from __future__ import annotations

import pytest

from m3ta_uitars.contracts import Surface, TaskRequest, TaskStatus
from m3ta_uitars.engine import Engine, TaskNotFound
from m3ta_uitars.safety.governor import SafetyError


@pytest.mark.asyncio
async def test_dry_run_succeeds_without_executing(engine: Engine) -> None:
    request = TaskRequest(
        instruction="search anthropic",
        agent_id="qubii",
        surface=Surface.BROWSER,
        starting_url="https://example.com",
        dry_run=True,
        confirmation_token="user-approved",
    )
    task = await engine.submit_task(request)
    task = await engine.run_task(task.id)
    assert task.status == TaskStatus.SUCCEEDED
    assert task.result is not None
    assert task.result.executed_actions == []
    assert task.plan is not None
    assert "dry_run=true" in (task.result.summary or "")


@pytest.mark.asyncio
async def test_full_run_executes_steps(engine: Engine) -> None:
    request = TaskRequest(
        instruction="navigate and snapshot",
        agent_id="hermes",
        surface=Surface.BROWSER,
        starting_url="https://example.com",
        dry_run=False,
        confirmation_token="user-approved",
    )
    task = await engine.submit_task(request)
    task = await engine.run_task(task.id)
    assert task.status == TaskStatus.SUCCEEDED
    assert task.result is not None
    assert len(task.result.executed_actions) > 0


@pytest.mark.asyncio
async def test_awaits_confirmation_when_risky_and_no_token(settings) -> None:
    # Tighten the allowlist so `navigate` is risky and requires confirmation.
    from m3ta_uitars.audit import AuditLogger
    from m3ta_uitars.providers.mock import MockProvider
    from m3ta_uitars.safety.governor import Governor

    strict = settings.model_copy(
        update={
            "action_allowlist": ["observe", "screenshot", "wait"],
            "confirm_required": ["navigate", "type", "click", "key", "scroll"],
        }
    )
    engine = Engine(
        settings=strict,
        provider=MockProvider(),
        governor=Governor(strict),
        audit=AuditLogger(strict.audit_dir),
    )
    request = TaskRequest(
        instruction="navigate",
        agent_id="metatron",
        starting_url="https://example.com",
        dry_run=False,
    )
    task = await engine.submit_task(request)
    task = await engine.run_task(task.id)
    assert task.status == TaskStatus.AWAITING_CONFIRMATION
    assert task.plan is not None


@pytest.mark.asyncio
async def test_request_blocked_for_disallowed_host(engine: Engine) -> None:
    request = TaskRequest(
        instruction="x",
        agent_id="qubii",
        starting_url="https://blocked.test",
    )
    with pytest.raises(SafetyError):
        await engine.submit_task(request)


@pytest.mark.asyncio
async def test_status_unknown_task_raises(engine: Engine) -> None:
    with pytest.raises(TaskNotFound):
        engine.status("tsk_does_not_exist")


@pytest.mark.asyncio
async def test_cancel_marks_task_cancelled(engine: Engine) -> None:
    request = TaskRequest(
        instruction="x", agent_id="qubii", starting_url="https://example.com"
    )
    task = await engine.submit_task(request)
    cancelled = await engine.cancel_task(task.id, reason="user-aborted")
    assert cancelled.status == TaskStatus.CANCELLED


@pytest.mark.asyncio
async def test_audit_log_written(engine: Engine) -> None:
    request = TaskRequest(
        instruction="x",
        agent_id="qubii",
        starting_url="https://example.com",
        dry_run=True,
        confirmation_token="ok",
    )
    task = await engine.submit_task(request)
    await engine.run_task(task.id)
    entries = engine.audit_log(task.id)
    events = [e["event"] for e in entries]
    assert "task_created" in events
    assert "plan_generated" in events
    assert "task_completed" in events
