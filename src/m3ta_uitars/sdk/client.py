"""Agent SDK clients."""

from __future__ import annotations

from typing import Any, Optional, Protocol

import httpx

from m3ta_uitars.contracts import (
    Observation,
    Surface,
    Task,
    TaskRequest,
)
from m3ta_uitars.engine import Engine


class M3taUITARSClient(Protocol):
    async def run_computer_task(
        self,
        instruction: str,
        agent_id: str,
        *,
        surface: Surface = Surface.BROWSER,
        starting_url: Optional[str] = None,
        dry_run: Optional[bool] = None,
        confirmation_token: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
        timeout_seconds: Optional[int] = None,
    ) -> Task: ...

    async def observe_screen(
        self,
        agent_id: str,
        *,
        surface: Surface = Surface.BROWSER,
        starting_url: Optional[str] = None,
    ) -> Observation: ...

    async def get_task_status(self, task_id: str) -> Task: ...

    async def cancel_task(self, task_id: str, reason: Optional[str] = None) -> Task: ...

    async def get_audit_log(self, task_id: str) -> list[dict[str, Any]]: ...


# ---------------------------------------------------------------------------
# In-process client — direct engine access
# ---------------------------------------------------------------------------


class InProcessClient:
    """Thin wrapper around `Engine`. Use when the agent runs in the same
    process as the engine (e.g. embedded inside Hermes)."""

    def __init__(self, engine: Optional[Engine] = None) -> None:
        self.engine = engine or Engine()

    async def run_computer_task(
        self,
        instruction: str,
        agent_id: str,
        *,
        surface: Surface = Surface.BROWSER,
        starting_url: Optional[str] = None,
        dry_run: Optional[bool] = None,
        confirmation_token: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
        timeout_seconds: Optional[int] = None,
    ) -> Task:
        request = TaskRequest(
            instruction=instruction,
            agent_id=agent_id,
            surface=surface,
            starting_url=starting_url,
            dry_run=dry_run,
            confirmation_token=confirmation_token,
            metadata=metadata or {},
            timeout_seconds=timeout_seconds,
        )
        task = await self.engine.submit_task(request)
        return await self.engine.run_task(task.id)

    async def observe_screen(
        self,
        agent_id: str,
        *,
        surface: Surface = Surface.BROWSER,
        starting_url: Optional[str] = None,
    ) -> Observation:
        request = TaskRequest(
            instruction="observe",
            agent_id=agent_id,
            surface=surface,
            starting_url=starting_url,
        )
        return await self.engine.observe(request)

    async def get_task_status(self, task_id: str) -> Task:
        return self.engine.status(task_id)

    async def cancel_task(self, task_id: str, reason: Optional[str] = None) -> Task:
        return await self.engine.cancel_task(task_id, reason)

    async def get_audit_log(self, task_id: str) -> list[dict[str, Any]]:
        return self.engine.audit_log(task_id)

    async def aclose(self) -> None:
        await self.engine.aclose()


# ---------------------------------------------------------------------------
# HTTP client — talks to the FastAPI surface
# ---------------------------------------------------------------------------


class HTTPClient:
    """HTTP client for agents that talk to the running webhook server."""

    def __init__(
        self,
        base_url: str,
        api_token: str = "",
        timeout: float = 60.0,
        client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        if not base_url:
            raise ValueError("HTTPClient requires base_url")
        self.base_url = base_url.rstrip("/")
        self.api_token = api_token
        self.timeout = timeout
        self._client = client
        self._owns_client = client is None

    def _headers(self) -> dict[str, str]:
        h = {"Content-Type": "application/json"}
        if self.api_token:
            h["Authorization"] = f"Bearer {self.api_token}"
        return h

    async def _http(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client

    async def _request(self, method: str, path: str, **kw: Any) -> dict[str, Any]:
        client = await self._http()
        resp = await client.request(
            method, f"{self.base_url}{path}", headers=self._headers(), **kw
        )
        if resp.status_code >= 400:
            raise RuntimeError(f"{method} {path} failed: {resp.status_code} {resp.text}")
        return resp.json()

    async def run_computer_task(
        self,
        instruction: str,
        agent_id: str,
        *,
        surface: Surface = Surface.BROWSER,
        starting_url: Optional[str] = None,
        dry_run: Optional[bool] = None,
        confirmation_token: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
        timeout_seconds: Optional[int] = None,
    ) -> Task:
        body = TaskRequest(
            instruction=instruction,
            agent_id=agent_id,
            surface=surface,
            starting_url=starting_url,
            dry_run=dry_run,
            confirmation_token=confirmation_token,
            metadata=metadata or {},
            timeout_seconds=timeout_seconds,
        ).model_dump(mode="json")
        data = await self._request("POST", "/v1/tasks", json=body)
        return Task.model_validate(data["task"])

    async def observe_screen(
        self,
        agent_id: str,
        *,
        surface: Surface = Surface.BROWSER,
        starting_url: Optional[str] = None,
    ) -> Observation:
        body = TaskRequest(
            instruction="observe",
            agent_id=agent_id,
            surface=surface,
            starting_url=starting_url,
        ).model_dump(mode="json")
        data = await self._request("POST", "/v1/observe", json=body)
        return Observation.model_validate(data["observation"])

    async def get_task_status(self, task_id: str) -> Task:
        data = await self._request("GET", f"/v1/tasks/{task_id}")
        return Task.model_validate(data["task"])

    async def cancel_task(self, task_id: str, reason: Optional[str] = None) -> Task:
        body = {"task_id": task_id, "reason": reason} if reason else {"task_id": task_id}
        data = await self._request("POST", f"/v1/tasks/{task_id}/cancel", json=body)
        return Task.model_validate(data["task"])

    async def get_audit_log(self, task_id: str) -> list[dict[str, Any]]:
        data = await self._request("GET", f"/v1/tasks/{task_id}/audit")
        return data["entries"]

    async def aclose(self) -> None:
        if self._client is not None and self._owns_client:
            await self._client.aclose()
            self._client = None
