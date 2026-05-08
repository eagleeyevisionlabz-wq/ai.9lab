"""Deterministic in-memory provider used for tests, dry-runs, and CI.

Generates plausible plans/observations without touching any real UI.
"""

from __future__ import annotations

from m3ta_uitars.contracts import (
    Action,
    ActionType,
    Observation,
    Plan,
    Surface,
    TaskRequest,
)
from m3ta_uitars.providers.base import Provider


class MockProvider(Provider):
    name = "mock"

    def __init__(self) -> None:
        self._step = 0

    async def observe(self, request: TaskRequest) -> Observation:
        return Observation(
            surface=request.surface,
            url=request.starting_url,
            title="MockSurface",
            text_summary=f"[mock] step={self._step} agent={request.agent_id}",
            screenshot_ref=f"mock://screenshot/{self._step}",
            elements=[
                {"role": "button", "name": "Submit", "id": "submit"},
                {"role": "textbox", "name": "Search", "id": "q"},
            ],
        )

    async def plan(self, request: TaskRequest, observation: Observation) -> Plan:
        steps: list[Action] = [Action(type=ActionType.OBSERVE, note="initial look")]
        if request.starting_url and request.surface == Surface.BROWSER:
            steps.append(
                Action(
                    type=ActionType.NAVIGATE,
                    target=request.starting_url,
                    note="open starting url",
                )
            )
        steps.append(
            Action(
                type=ActionType.SCREENSHOT,
                note="capture state for audit",
            )
        )
        return Plan(
            rationale=f"[mock] plan for: {request.instruction}",
            steps=steps,
            requires_confirmation=any(s.type == ActionType.NAVIGATE for s in steps),
            risky_actions=[
                s.type for s in steps if s.type in {ActionType.NAVIGATE, ActionType.TYPE}
            ],
        )

    async def act(
        self, action: Action, request: TaskRequest, observation: Observation
    ) -> Observation:
        self._step += 1
        return Observation(
            surface=request.surface,
            url=action.target if action.type == ActionType.NAVIGATE else observation.url,
            title=f"MockSurface (after {action.type.value})",
            text_summary=f"[mock] executed {action.type.value} step={self._step}",
            screenshot_ref=f"mock://screenshot/{self._step}",
        )
