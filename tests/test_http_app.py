"""HTTP surface tests (FastAPI TestClient)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from m3ta_uitars.config import Settings
from m3ta_uitars.engine import Engine
from m3ta_uitars.server.http_app import create_app


def _client(engine: Engine, settings: Settings) -> TestClient:
    return TestClient(create_app(engine=engine, settings=settings))


def test_health_does_not_require_auth(engine: Engine, settings: Settings) -> None:
    settings = settings.model_copy(update={"api_token": "secret"})
    client = _client(engine, settings)
    resp = client.get("/v1/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["ok"]
    assert body["provider"] == "mock"


def test_protected_endpoint_requires_token(engine: Engine, settings: Settings) -> None:
    settings = settings.model_copy(update={"api_token": "secret"})
    client = _client(engine, settings)
    resp = client.post(
        "/v1/tasks",
        json={
            "instruction": "x",
            "agent_id": "qubii",
            "starting_url": "https://example.com",
            "dry_run": True,
            "confirmation_token": "ok",
        },
    )
    assert resp.status_code == 401


def test_submit_and_run_task_dry_run(engine: Engine, settings: Settings) -> None:
    client = _client(engine, settings)
    resp = client.post(
        "/v1/tasks",
        json={
            "instruction": "navigate to example",
            "agent_id": "qubii",
            "starting_url": "https://example.com",
            "dry_run": True,
            "confirmation_token": "ok",
        },
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["ok"]
    assert body["task"]["status"] == "succeeded"


def test_status_404_on_missing(engine: Engine, settings: Settings) -> None:
    client = _client(engine, settings)
    resp = client.get("/v1/tasks/tsk_missing")
    assert resp.status_code == 404


def test_safety_violation_returns_403(engine: Engine, settings: Settings) -> None:
    client = _client(engine, settings)
    resp = client.post(
        "/v1/tasks",
        json={
            "instruction": "x",
            "agent_id": "qubii",
            "starting_url": "https://blocked.test",
        },
    )
    assert resp.status_code == 403


def test_events_sink(engine: Engine, settings: Settings) -> None:
    client = _client(engine, settings)
    resp = client.post(
        "/v1/events",
        json={"source": "n8n", "kind": "task.completed", "data": {"x": 1}},
    )
    assert resp.status_code == 200
    assert resp.json() == {"ok": True, "received": True}
