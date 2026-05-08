"""Safety governor unit tests."""

from __future__ import annotations

from m3ta_uitars.config import Settings
from m3ta_uitars.contracts import Action, ActionType, Plan, TaskRequest
from m3ta_uitars.safety.governor import Governor


def _settings(**overrides) -> Settings:
    base = dict(
        action_allowlist=["observe", "screenshot", "wait", "navigate"],
        confirm_required=["type", "click", "key", "scroll", "navigate"],
        host_allowlist=["example.com"],
        enforce_host_allowlist=True,
    )
    base.update(overrides)
    return Settings(**base)


def test_request_blocked_when_starting_url_outside_allowlist() -> None:
    g = Governor(_settings())
    decision = g.evaluate_request(
        TaskRequest(
            instruction="x",
            agent_id="qubii",
            starting_url="https://evil.example",
        )
    )
    assert decision.blocked
    assert "host" in decision.blocked_reasons[0]


def test_request_allowed_for_subdomain_in_allowlist() -> None:
    g = Governor(_settings())
    decision = g.evaluate_request(
        TaskRequest(
            instruction="x",
            agent_id="qubii",
            starting_url="https://www.example.com/path",
        )
    )
    assert decision.allowed


def test_plan_requires_confirmation_for_risky_actions() -> None:
    g = Governor(_settings())
    plan = Plan(
        rationale="x",
        steps=[
            Action(type=ActionType.OBSERVE),
            Action(type=ActionType.NAVIGATE, target="https://example.com"),
            Action(type=ActionType.CLICK, target="#submit"),
        ],
    )
    request = TaskRequest(instruction="x", agent_id="hermes")
    decision = g.evaluate_plan(plan, request)
    assert decision.allowed
    assert decision.requires_confirmation
    assert ActionType.NAVIGATE in decision.risky_actions
    assert ActionType.CLICK in decision.risky_actions


def test_plan_confirmed_when_token_provided() -> None:
    g = Governor(_settings())
    plan = Plan(steps=[Action(type=ActionType.CLICK, target="#x")])
    request = TaskRequest(
        instruction="x", agent_id="hermes", confirmation_token="ok-by-user"
    )
    decision = g.evaluate_plan(plan, request)
    assert decision.allowed
    assert not decision.requires_confirmation


def test_action_outside_allowlist_blocked() -> None:
    g = Governor(
        _settings(action_allowlist=["observe"], confirm_required=[])
    )
    decision = g.evaluate_action(
        Action(type=ActionType.CLICK, target="#x"),
        TaskRequest(instruction="x", agent_id="qubii"),
    )
    assert decision.blocked


def test_dry_run_default_used_when_request_unset() -> None:
    g = Governor(_settings(default_dry_run=True))
    request = TaskRequest(instruction="x", agent_id="qubii")
    assert g.effective_dry_run(request) is True

    request = TaskRequest(instruction="x", agent_id="qubii", dry_run=False)
    assert g.effective_dry_run(request) is False
