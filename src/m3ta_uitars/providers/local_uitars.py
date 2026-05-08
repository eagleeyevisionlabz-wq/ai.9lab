"""Local UI-TARS Desktop provider — placeholder bridge.

UI-TARS Desktop does not currently ship with a documented public HTTP API for
external orchestration. This adapter defines the *contract* a future bridge
must satisfy:

  POST {bridge_url}/observe   -> Observation JSON
  POST {bridge_url}/plan      -> Plan JSON
  POST {bridge_url}/act       -> Observation JSON

Until such a bridge is available, this provider raises NotImplementedError on
calls so misconfiguration is obvious. Use `MockProvider` for development and
`RemoteOperatorProvider` for a hosted backend.

TODO(uitars-bridge): replace this with the real UI-TARS Desktop bridge once
ByteDance ships an external automation API or once we publish our own helper
app that exposes one.
"""

from __future__ import annotations

import httpx

from m3ta_uitars.contracts import Action, Observation, Plan, TaskRequest
from m3ta_uitars.providers.base import Provider


class LocalUITARSProvider(Provider):
    name = "local_uitars"

    def __init__(self, bridge_url: str, bridge_token: str = "", timeout: float = 30.0) -> None:
        self.bridge_url = bridge_url.rstrip("/")
        self.bridge_token = bridge_token
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None

    def _headers(self) -> dict[str, str]:
        h = {"Content-Type": "application/json"}
        if self.bridge_token:
            h["Authorization"] = f"Bearer {self.bridge_token}"
        return h

    async def _http(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client

    async def _post(self, path: str, payload: dict) -> dict:
        client = await self._http()
        try:
            resp = await client.post(
                f"{self.bridge_url}{path}", json=payload, headers=self._headers()
            )
        except httpx.HTTPError as exc:
            raise NotImplementedError(
                f"Local UI-TARS Desktop bridge not reachable at {self.bridge_url}{path}: {exc}. "
                "See providers/local_uitars.py TODO(uitars-bridge)."
            ) from exc
        if resp.status_code >= 400:
            raise RuntimeError(
                f"local_uitars bridge {path} failed: {resp.status_code} {resp.text}"
            )
        return resp.json()

    async def observe(self, request: TaskRequest) -> Observation:
        data = await self._post("/observe", {"request": request.model_dump(mode="json")})
        return Observation.model_validate(data)

    async def plan(self, request: TaskRequest, observation: Observation) -> Plan:
        data = await self._post(
            "/plan",
            {
                "request": request.model_dump(mode="json"),
                "observation": observation.model_dump(mode="json"),
            },
        )
        return Plan.model_validate(data)

    async def act(
        self, action: Action, request: TaskRequest, observation: Observation
    ) -> Observation:
        data = await self._post(
            "/act",
            {
                "action": action.model_dump(mode="json"),
                "request": request.model_dump(mode="json"),
                "observation": observation.model_dump(mode="json"),
            },
        )
        return Observation.model_validate(data)

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None
