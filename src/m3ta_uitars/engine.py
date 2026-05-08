"""Engine — the orchestrator implementing the capability contract.

Public interface:
  - submit_task(request) -> Task
  - run_task(task_id) -> Task   (drives the task to terminal state)
  - cancel_task(task_id, reason=None) -> Task
  - status(task_id) -> Task
  - observe(request) -> Observation
  - plan(request, observation) -> Plan
  - audit_log(task_id) -> list[dict]
"""

from __future__ import annotations

import asyncio
import logging
from typing import Optional

from m3ta_uitars.audit import AuditLogger
from m3ta_uitars.config import Settings, get_settings
from m3ta_uitars.contracts import (
    Action,
    AuditEntry,
    Observation,
    Plan,
    Task,
    TaskRequest,
    TaskResult,
    TaskStatus,
)
from m3ta_uitars.providers.base import Provider
from m3ta_uitars.providers.factory import build_provider
from m3ta_uitars.safety.governor import Governor, SafetyError

log = logging.getLogger(__name__)


class TaskNotFound(KeyError):
    pass


class Engine:
    def __init__(
        self,
        settings: Optional[Settings] = None,
        provider: Optional[Provider] = None,
        governor: Optional[Governor] = None,
        audit: Optional[AuditLogger] = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.provider = provider or build_provider(self.settings)
        self.governor = governor or Governor(self.settings)
        self.audit = audit or AuditLogger(self.settings.audit_dir)
        self._tasks: dict[str, Task] = {}
        self._cancel_flags: dict[str, asyncio.Event] = {}
        self._lock = asyncio.Lock()

    # --------------------------------------------------------------- contract

    async def observe(self, request: TaskRequest) -> Observation:
        return await self.provider.observe(request)

    async def plan(self, request: TaskRequest, observation: Observation) -> Plan:
        return await self.provider.plan(request, observation)

    async def submit_task(self, request: TaskRequest) -> Task:
        decision = self.governor.evaluate_request(request)
        if decision.blocked:
            raise SafetyError("; ".join(decision.blocked_reasons))

        task = Task(request=request)
        async with self._lock:
            self._tasks[task.id] = task
            self._cancel_flags[task.id] = asyncio.Event()
        task.audit_log_path = str(self.audit._path(task.id))
        self._audit(task, "task_created", {"instruction": request.instruction})
        return task

    async def run_task(self, task_id: str) -> Task:
        task = self._get(task_id)
        cancel = self._cancel_flags[task_id]
        timeout = task.request.timeout_seconds or self.settings.task_timeout_seconds
        try:
            return await asyncio.wait_for(self._drive(task, cancel), timeout=timeout)
        except asyncio.TimeoutError:
            task.status = TaskStatus.TIMED_OUT
            task.result = TaskResult(ok=False, error="timeout")
            task.touch()
            self._audit(task, "task_failed", {"reason": "timeout"})
            return task

    async def cancel_task(self, task_id: str, reason: Optional[str] = None) -> Task:
        task = self._get(task_id)
        flag = self._cancel_flags.get(task_id)
        if flag:
            flag.set()
        if task.status not in {
            TaskStatus.SUCCEEDED,
            TaskStatus.FAILED,
            TaskStatus.CANCELLED,
            TaskStatus.TIMED_OUT,
        }:
            task.status = TaskStatus.CANCELLED
            task.result = TaskResult(ok=False, error=f"cancelled: {reason or ''}".strip(": "))
            task.touch()
            self._audit(task, "task_cancelled", {"reason": reason})
        return task

    def status(self, task_id: str) -> Task:
        return self._get(task_id)

    def audit_log(self, task_id: str) -> list[dict]:
        return self.audit.read(task_id)

    # ---------------------------------------------------------------- driver

    async def _drive(self, task: Task, cancel: asyncio.Event) -> Task:
        request = task.request
        dry_run = self.governor.effective_dry_run(request)

        # 1. Observe
        task.status = TaskStatus.PLANNING
        task.touch()
        observation = await self.provider.observe(request)
        if observation.screenshot_ref and self.settings.audit_screenshots:
            self._audit(
                task, "screenshot_captured", {"ref": observation.screenshot_ref}
            )

        # 2. Plan
        plan = await self.provider.plan(request, observation)
        task.plan = plan
        plan_decision = self.governor.evaluate_plan(plan, request)
        self._audit(
            task,
            "plan_generated",
            {
                "rationale": plan.rationale,
                "steps": [s.model_dump(mode="json") for s in plan.steps],
                "blocked_reasons": plan_decision.blocked_reasons,
                "requires_confirmation": plan_decision.requires_confirmation,
                "risky_actions": [a.value for a in plan_decision.risky_actions],
            },
        )
        if plan_decision.blocked:
            task.status = TaskStatus.FAILED
            task.result = TaskResult(
                ok=False,
                error="plan blocked by governor: " + "; ".join(plan_decision.blocked_reasons),
            )
            task.touch()
            self._audit(task, "task_failed", {"reason": "plan_blocked"})
            return task

        if plan_decision.requires_confirmation:
            task.status = TaskStatus.AWAITING_CONFIRMATION
            task.touch()
            self._audit(
                task,
                "confirmation_required",
                {"risky_actions": [a.value for a in plan_decision.risky_actions]},
            )
            return task

        if dry_run:
            task.status = TaskStatus.SUCCEEDED
            task.result = TaskResult(
                ok=True,
                final_observation=observation,
                executed_actions=[],
                summary=f"dry_run=true; {len(plan.steps)} step(s) planned",
            )
            task.touch()
            self._audit(task, "task_completed", {"dry_run": True})
            return task

        # 3. Act
        task.status = TaskStatus.RUNNING
        task.touch()
        executed: list[Action] = []
        last_obs = observation
        for step in plan.steps:
            if cancel.is_set():
                task.status = TaskStatus.CANCELLED
                task.result = TaskResult(
                    ok=False,
                    final_observation=last_obs,
                    executed_actions=executed,
                    error="cancelled mid-task",
                )
                task.touch()
                return task

            step_decision = self.governor.evaluate_action(step, request, plan)
            if step_decision.blocked:
                self._audit(
                    task,
                    "action_blocked",
                    {
                        "action": step.model_dump(mode="json"),
                        "reasons": step_decision.blocked_reasons,
                    },
                )
                task.status = TaskStatus.FAILED
                task.result = TaskResult(
                    ok=False,
                    final_observation=last_obs,
                    executed_actions=executed,
                    error="action blocked: " + "; ".join(step_decision.blocked_reasons),
                )
                task.touch()
                self._audit(task, "task_failed", {"reason": "action_blocked"})
                return task

            self._audit(
                task, "action_attempted", {"action": step.model_dump(mode="json")}
            )
            try:
                last_obs = await self.provider.act(step, request, last_obs)
            except Exception as exc:  # noqa: BLE001 - provider boundary
                log.exception("provider.act failed")
                task.status = TaskStatus.FAILED
                task.result = TaskResult(
                    ok=False,
                    final_observation=last_obs,
                    executed_actions=executed,
                    error=f"provider error: {exc}",
                )
                task.touch()
                self._audit(task, "task_failed", {"reason": str(exc)})
                return task
            executed.append(step)
            self._audit(
                task,
                "action_completed",
                {"action": step.model_dump(mode="json")},
            )
            if last_obs.screenshot_ref and self.settings.audit_screenshots:
                self._audit(
                    task, "screenshot_captured", {"ref": last_obs.screenshot_ref}
                )

        task.status = TaskStatus.SUCCEEDED
        task.result = TaskResult(
            ok=True,
            final_observation=last_obs,
            executed_actions=executed,
            summary=f"executed {len(executed)} step(s)",
        )
        task.touch()
        self._audit(task, "task_completed", {"steps": len(executed)})
        return task

    # ---------------------------------------------------------------- helpers

    def _get(self, task_id: str) -> Task:
        task = self._tasks.get(task_id)
        if task is None:
            raise TaskNotFound(task_id)
        return task

    def _audit(self, task: Task, event: str, detail: dict) -> None:
        self.audit.log(
            AuditEntry(
                task_id=task.id,
                agent_id=task.request.agent_id,
                event=event,  # type: ignore[arg-type]
                detail=detail,
            )
        )

    async def aclose(self) -> None:
        await self.provider.close()
