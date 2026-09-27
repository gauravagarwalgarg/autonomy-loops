"""Policy evaluation engine.

Evaluates declarative policy rules against agent actions to determine
whether to allow, block, or require approval for operations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from autonomy_loops.telemetry.logger import get_logger

logger = get_logger(__name__)


class PolicyDecision(StrEnum):
    """Result of a policy evaluation."""

    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"
    WARN = "warn"


@dataclass
class PolicyRule:
    """A single policy rule."""

    name: str
    trigger: str  # tool_call | llm_call | state_transition
    condition: str  # Simple expression (evaluated safely)
    action: PolicyDecision
    message: str = ""
    approvers: list[str] = field(default_factory=list)


@dataclass
class PolicyEvaluation:
    """Result of evaluating all policies against an action."""

    decision: PolicyDecision
    triggered_rules: list[PolicyRule]
    messages: list[str]


class PolicyEngine:
    """Evaluates policy rules against agent actions.

    Rules are loaded from YAML configuration and evaluated
    at each agent action boundary (tool calls, LLM requests, etc.).
    """

    def __init__(self, rules: list[PolicyRule] | None = None) -> None:
        self._rules = rules or []

    @classmethod
    def from_config(cls, policy_config: dict[str, Any]) -> PolicyEngine:
        """Create engine from policy config dict."""
        rules = []
        for rule_def in policy_config.get("rules", []):
            rules.append(
                PolicyRule(
                    name=rule_def["name"],
                    trigger=rule_def.get("trigger", "tool_call"),
                    condition=rule_def.get("condition", ""),
                    action=PolicyDecision(rule_def.get("action", "allow")),
                    message=rule_def.get("message", ""),
                    approvers=rule_def.get("approvers", []),
                )
            )
        return cls(rules=rules)

    def evaluate(
        self,
        trigger: str,
        context: dict[str, Any],
    ) -> PolicyEvaluation:
        """Evaluate all rules for a given trigger and context.

        Args:
            trigger: Type of action ("tool_call", "llm_call", "state_transition").
            context: Action context (tool name, arguments, etc.).

        Returns:
            PolicyEvaluation with the final decision.
        """
        triggered: list[PolicyRule] = []
        messages: list[str] = []

        for rule in self._rules:
            if rule.trigger != trigger:
                continue

            if self._evaluate_condition(rule.condition, context):
                triggered.append(rule)
                if rule.message:
                    messages.append(f"[{rule.name}] {rule.message}")
                logger.info(
                    "policy_triggered",
                    rule=rule.name,
                    action=rule.action.value,
                )

        if not triggered:
            return PolicyEvaluation(
                decision=PolicyDecision.ALLOW,
                triggered_rules=[],
                messages=[],
            )

        # Most restrictive decision wins
        if any(r.action == PolicyDecision.DENY for r in triggered):
            decision = PolicyDecision.DENY
        elif any(r.action == PolicyDecision.REQUIRE_APPROVAL for r in triggered):
            decision = PolicyDecision.REQUIRE_APPROVAL
        elif any(r.action == PolicyDecision.WARN for r in triggered):
            decision = PolicyDecision.WARN
        else:
            decision = PolicyDecision.ALLOW

        return PolicyEvaluation(
            decision=decision,
            triggered_rules=triggered,
            messages=messages,
        )

    @staticmethod
    def _evaluate_condition(condition: str, context: dict[str, Any]) -> bool:
        """Safely evaluate a condition expression against context.

        Supports simple expressions like:
        - "tool.name == 'shell'"
        - "'prod' in tool.args"
        - "estimated_tokens > 100000"
        """
        if not condition:
            return True

        # Build safe evaluation namespace from context
        namespace = {}
        for key, value in context.items():
            namespace[key] = value

        try:
            # Limited eval with no builtins
            return bool(eval(condition, {"__builtins__": {}}, namespace))  # noqa: S307
        except Exception:
            # If condition can't be evaluated, don't trigger
            return False
