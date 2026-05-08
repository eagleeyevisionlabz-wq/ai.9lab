"""Provider interface — the boundary between the engine and a concrete backend."""

from __future__ import annotations

from abc import ABC, abstractmethod

from m3ta_uitars.contracts import Action, Observation, Plan, TaskRequest


class Provider(ABC):
    """Abstract provider for visual computer-use.

    Implementations may be:
      - local UI-TARS Desktop bridge
      - remote browser/computer operator
      - mock/simulated for tests
    """

    name: str = "abstract"

    @abstractmethod
    async def observe(self, request: TaskRequest) -> Observation:
        """Capture current screen / page state."""

    @abstractmethod
    async def plan(self, request: TaskRequest, observation: Observation) -> Plan:
        """Produce a plan of actions for the request."""

    @abstractmethod
    async def act(
        self, action: Action, request: TaskRequest, observation: Observation
    ) -> Observation:
        """Execute one action and return the resulting observation."""

    async def close(self) -> None:
        """Release any resources. Default no-op."""
        return None
