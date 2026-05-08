"""HTTP surface for n8n / OpenClaw / generic webhook callers.

Endpoints:
  POST /v1/tasks                    -> submit & run task (sync)
  POST /v1/tasks/submit             -> submit only, returns task immediately
  POST /v1/tasks/{task_id}/run      -> drive a previously submitted task
  GET  /v1/tasks/{task_id}          -> status
  POST /v1/tasks/{task_id}/cancel   -> cancel
  GET  /v1/tasks/{task_id}/audit    -> audit log entries
  POST /v1/observe                  -> single observation
  POST /v1/events                   -> event callback sink (for n8n/OpenClaw)
  GET  /v1/health                   -> health check

Auth:
  When `M3TA_UITARS_API_TOKEN` is set, every non-/health request must present
  it via `Authorization: Bearer <token>` or `X-M3TA-Token: <token>`.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from m3ta_uitars.config import Settings, get_settings
from m3ta_uitars.contracts import CancelRequest, TaskRequest
from m3ta_uitars.engine import Engine, TaskNotFound
from m3ta_uitars.safety.governor import SafetyError

log = logging.getLogger(__name__)


class EventPayload(BaseModel):
    source: str
    kind: str
    data: dict[str, Any] = {}


def _check_token(settings: Settings, authorization: Optional[str], x_token: Optional[str]) -> None:
    if not settings.api_token:
        return
    candidate = ""
    if authorization and authorization.lower().startswith("bearer "):
        candidate = authorization.split(" ", 1)[1].strip()
    elif x_token:
        candidate = x_token.strip()
    if candidate != settings.api_token:
        raise HTTPException(status_code=401, detail="invalid or missing token")


def create_app(engine: Optional[Engine] = None, settings: Optional[Settings] = None) -> FastAPI:
    settings = settings or get_settings()
    engine = engine or Engine(settings=settings)

    app = FastAPI(
        title="M3ta-0S UI-TARS Webhook Surface",
        version="0.1.0",
        description="n8n / OpenClaw compatible HTTP surface for UI-TARS tasks.",
    )

    if settings.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    app.state.engine = engine
    app.state.settings = settings

    async def _auth(
        request: Request,
        authorization: Optional[str] = Header(default=None),
        x_m3ta_token: Optional[str] = Header(default=None, alias="X-M3TA-Token"),
    ) -> None:
        if request.url.path == "/v1/health":
            return
        _check_token(settings, authorization, x_m3ta_token)

    @app.get("/v1/health")
    async def health() -> dict[str, Any]:
        return {
            "ok": True,
            "provider": settings.provider,
            "runtime": settings.runtime,
            "default_dry_run": settings.default_dry_run,
        }

    @app.post("/v1/tasks", dependencies=[Depends(_auth)])
    async def submit_and_run(payload: TaskRequest) -> dict[str, Any]:
        try:
            task = await engine.submit_task(payload)
        except SafetyError as exc:
            raise HTTPException(status_code=403, detail=f"safety: {exc}") from exc
        task = await engine.run_task(task.id)
        return {"ok": True, "task": task.model_dump(mode="json")}

    @app.post("/v1/tasks/submit", dependencies=[Depends(_auth)])
    async def submit_only(payload: TaskRequest) -> dict[str, Any]:
        try:
            task = await engine.submit_task(payload)
        except SafetyError as exc:
            raise HTTPException(status_code=403, detail=f"safety: {exc}") from exc
        return {"ok": True, "task": task.model_dump(mode="json")}

    @app.post("/v1/tasks/{task_id}/run", dependencies=[Depends(_auth)])
    async def run_task(task_id: str) -> dict[str, Any]:
        try:
            task = await engine.run_task(task_id)
        except TaskNotFound:
            raise HTTPException(status_code=404, detail="task not found")
        return {"ok": True, "task": task.model_dump(mode="json")}

    @app.get("/v1/tasks/{task_id}", dependencies=[Depends(_auth)])
    async def status(task_id: str) -> dict[str, Any]:
        try:
            task = engine.status(task_id)
        except TaskNotFound:
            raise HTTPException(status_code=404, detail="task not found")
        return {"ok": True, "task": task.model_dump(mode="json")}

    @app.post("/v1/tasks/{task_id}/cancel", dependencies=[Depends(_auth)])
    async def cancel(task_id: str, payload: Optional[CancelRequest] = None) -> dict[str, Any]:
        try:
            task = await engine.cancel_task(
                task_id, payload.reason if payload else None
            )
        except TaskNotFound:
            raise HTTPException(status_code=404, detail="task not found")
        return {"ok": True, "task": task.model_dump(mode="json")}

    @app.get("/v1/tasks/{task_id}/audit", dependencies=[Depends(_auth)])
    async def audit(task_id: str) -> dict[str, Any]:
        return {"ok": True, "entries": engine.audit_log(task_id)}

    @app.post("/v1/observe", dependencies=[Depends(_auth)])
    async def observe(payload: TaskRequest) -> dict[str, Any]:
        obs = await engine.observe(payload)
        return {"ok": True, "observation": obs.model_dump(mode="json")}

    @app.post("/v1/events", dependencies=[Depends(_auth)])
    async def events(payload: EventPayload) -> dict[str, Any]:
        # Sink endpoint for n8n / OpenClaw to deliver upstream events.
        # The engine doesn't act on these directly yet — we log them so workflow
        # designers can prove a path before wiring policy.
        log.info(
            "event received source=%s kind=%s", payload.source, payload.kind
        )
        return {"ok": True, "received": True}

    return app


app = create_app()


def main() -> None:  # pragma: no cover - thin uvicorn launcher
    import uvicorn

    settings = get_settings()
    logging.basicConfig(level=settings.log_level.upper())
    uvicorn.run(
        "m3ta_uitars.server.http_app:app",
        host=settings.http_host,
        port=settings.http_port,
        reload=False,
    )


if __name__ == "__main__":  # pragma: no cover
    main()
