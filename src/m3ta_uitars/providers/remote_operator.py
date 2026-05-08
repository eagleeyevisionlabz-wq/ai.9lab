"""Remote operator provider — generic adapter for hosted UI-TARS-style backends.

Targets a remote service that speaks a small REST contract:

  POST {base_url}/observe
  POST {base_url}/plan
  POST {base_url}/act

This is the same contract as `local_uitars`, but pointed at a hosted endpoint
(VolcEngine Doubao UI-TARS, Hugging Face UI-TARS-1.5 inference server, or a
self-hosted browser-operator service).
"""

from __future__ import annotations

import httpx

from m3ta_uitars.contracts import Action, Observation, Plan, TaskRequest
from m3ta_uitars.providers.base import Provider


class RemoteOperatorProvider(Provider):
    name = "remote_operator"

    def __init__(
        self,
        base_url: str,
        api_key: str = "",
        model: str = "ui-tars-1.5",
        timeout: float = 60.0,
    ) -> None:
        if not base_url:
            raise ValueError("RemoteOperatorProvider requires base_url")
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None

    def _headers(self) -> dict[str, str]:
        h = {"Content-Type": "application/json"}
        if self.api_key:
            h["Authorization"] = f"Bearer {self.api_key}"
        return h

    async def _http(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client

    async def _post(self, path: str, payload: dict) -> dict:
        client = await self._http()
        payload = {"model": self.model, **payload}
        resp = await client.post(
            f"{self.base_url}{path}", json=payload, headers=self._headers()
        )
        if resp.status_code >= 400:
            raise RuntimeError(
                f"remote_operator {path} failed: {resp.status_code} {resp.text}"
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
