"""SDK tests."""

from __future__ import annotations

import pytest

from m3ta_uitars.contracts import TaskStatus
from m3ta_uitars.engine import Engine
from m3ta_uitars.sdk import InProcessClient


@pytest.mark.asyncio
async def test_in_process_run_computer_task(engine: Engine) -> None:
    client = InProcessClient(engine=engine)
    task = await client.run_computer_task(
        instruction="search example",
        agent_id="hermes",
        starting_url="https://example.com",
        dry_run=True,
        confirmation_token="ok",
    )
    assert task.status == TaskStatus.SUCCEEDED


@pytest.mark.asyncio
async def test_in_process_observe_screen(engine: Engine) -> None:
    client = InProcessClient(engine=engine)
    obs = await client.observe_screen(
        agent_id="metatron", starting_url="https://example.com"
    )
    assert obs.title == "MockSurface"


@pytest.mark.asyncio
async def test_in_process_audit_log(engine: Engine) -> None:
    client = InProcessClient(engine=engine)
    task = await client.run_computer_task(
        instruction="x",
        agent_id="qubii",
        starting_url="https://example.com",
        dry_run=True,
        confirmation_token="ok",
    )
    log = await client.get_audit_log(task.id)
    assert any(entry["event"] == "task_completed" for entry in log)
