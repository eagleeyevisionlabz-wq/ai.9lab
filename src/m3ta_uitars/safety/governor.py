"""Safety / governance gate.

Enforces:
  - Action allowlist
  - Confirmation requirement for risky actions
  - Host allowlist for navigate actions
  - Dry-run defaults
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse

from m3ta_uitars.config import Settings
from m3ta_uitars.contracts import Action, ActionType, Plan, TaskRequest


class SafetyError(Exception):
    """Raised when a request or action is blocked by the governor."""


@dataclass
class GovernorDecision:
    allowed: bool
    requires_confirmation: bool
    risky_actions: list[ActionType]
    blocked_reasons: list[str]

    @property
    def blocked(self) -> bool:
        return not self.allowed


class Governor:
    """Pure, deterministic policy checker. No I/O."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    # ----- request-level checks -----

    def evaluate_request(self, request: TaskRequest) -> GovernorDecision:
        reasons: list[str] = []
        if request.starting_url:
            host_block = self._check_host(request.starting_url)
            if host_block:
                reasons.append(host_block)

        return GovernorDecision(
            allowed=not reasons,
            requires_confirmation=False,
            risky_actions=[],
            blocked_reasons=reasons,
        )

    # ----- plan-level checks -----

    def evaluate_plan(
        self, plan: Plan, request: TaskRequest
    ) -> GovernorDecision:
        allowlist = {a.lower() for a in self.settings.action_allowlist}
        confirm_required = {a.lower() for a in self.settings.confirm_required}

        risky: list[ActionType] = []
        reasons: list[str] = []

        for step in plan.steps:
            atype = step.type.value.lower()
            if atype not in allowlist and atype not in confirm_required:
                reasons.append(f"action '{atype}' not in allowlist")
                continue
            if atype in confirm_required:
                risky.append(step.type)
            if step.type == ActionType.NAVIGATE and step.target:
                host_block = self._check_host(step.target)
                if host_block:
                    reasons.append(host_block)

        needs_confirm = bool(risky) and not request.confirmation_token
        return GovernorDecision(
            allowed=not reasons,
            requires_confirmation=needs_confirm,
            risky_actions=risky,
            blocked_reasons=reasons,
        )

    # ----- per-action runtime gate -----

    def evaluate_action(
        self, action: Action, request: TaskRequest, plan: Optional[Plan] = None
    ) -> GovernorDecision:
        allowlist = {a.lower() for a in self.settings.action_allowlist}
        confirm_required = {a.lower() for a in self.settings.confirm_required}
        atype = action.type.value.lower()

        reasons: list[str] = []
        if atype not in allowlist and atype not in confirm_required:
            reasons.append(f"action '{atype}' not in allowlist")

        if action.type == ActionType.NAVIGATE and action.target:
            host_block = self._check_host(action.target)
            if host_block:
                reasons.append(host_block)

        risky = [action.type] if atype in confirm_required else []
        needs_confirm = bool(risky) and not request.confirmation_token

        return GovernorDecision(
            allowed=not reasons,
            requires_confirmation=needs_confirm,
            risky_actions=risky,
            blocked_reasons=reasons,
        )

    # ----- helpers -----

    def _check_host(self, url_or_host: str) -> Optional[str]:
        if not self.settings.enforce_host_allowlist:
            return None
        host = self._extract_host(url_or_host)
        if not host:
            return f"could not parse host from '{url_or_host}'"
        allow = {h.lower() for h in self.settings.host_allowlist}
        if not allow:
            return f"host '{host}' blocked: host_allowlist is empty"
        if not any(host == h or host.endswith("." + h) for h in allow):
            return f"host '{host}' not in host_allowlist"
        return None

    @staticmethod
    def _extract_host(value: str) -> str:
        if "://" in value:
            return (urlparse(value).hostname or "").lower()
        # Bare host like "example.com" or "example.com/path"
        return value.split("/", 1)[0].lower()

    def effective_dry_run(self, request: TaskRequest) -> bool:
        if request.dry_run is None:
            return self.settings.default_dry_run
        return bool(request.dry_run)
