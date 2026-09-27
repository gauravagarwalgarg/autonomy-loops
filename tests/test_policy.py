"""Tests for the policy engine."""

from autonomy_loops.policy.engine import PolicyDecision, PolicyEngine, PolicyRule


class TestPolicyEngine:
    """Test policy evaluation."""

    def test_no_rules_allows_all(self):
        engine = PolicyEngine(rules=[])
        result = engine.evaluate("tool_call", {"tool": {"name": "read_file"}})
        assert result.decision == PolicyDecision.ALLOW

    def test_deny_rule_blocks(self):
        rules = [
            PolicyRule(
                name="block-rm",
                trigger="tool_call",
                condition="'rm -rf' in command",
                action=PolicyDecision.DENY,
                message="Destructive command blocked",
            )
        ]
        engine = PolicyEngine(rules=rules)
        result = engine.evaluate("tool_call", {"command": "rm -rf /"})
        assert result.decision == PolicyDecision.DENY
        assert len(result.triggered_rules) == 1

    def test_approval_required_rule(self):
        rules = [
            PolicyRule(
                name="prod-guard",
                trigger="tool_call",
                condition="'prod' in target",
                action=PolicyDecision.REQUIRE_APPROVAL,
            )
        ]
        engine = PolicyEngine(rules=rules)
        result = engine.evaluate("tool_call", {"target": "deploy-to-prod"})
        assert result.decision == PolicyDecision.REQUIRE_APPROVAL

    def test_unmatched_trigger_is_allowed(self):
        rules = [
            PolicyRule(
                name="only-tool-calls",
                trigger="tool_call",
                condition="True",
                action=PolicyDecision.DENY,
            )
        ]
        engine = PolicyEngine(rules=rules)
        result = engine.evaluate("llm_call", {})
        assert result.decision == PolicyDecision.ALLOW

    def test_most_restrictive_wins(self):
        rules = [
            PolicyRule(
                name="warn", trigger="tool_call", condition="True", action=PolicyDecision.WARN
            ),
            PolicyRule(
                name="deny", trigger="tool_call", condition="True", action=PolicyDecision.DENY
            ),
        ]
        engine = PolicyEngine(rules=rules)
        result = engine.evaluate("tool_call", {})
        assert result.decision == PolicyDecision.DENY

    def test_condition_evaluation_failure_does_not_trigger(self):
        rules = [
            PolicyRule(
                name="bad-condition",
                trigger="tool_call",
                condition="undefined_variable == 'x'",
                action=PolicyDecision.DENY,
            )
        ]
        engine = PolicyEngine(rules=rules)
        result = engine.evaluate("tool_call", {})
        assert result.decision == PolicyDecision.ALLOW

    def test_from_config(self):
        config = {
            "rules": [
                {"name": "test", "trigger": "tool_call", "condition": "True", "action": "warn"}
            ]
        }
        engine = PolicyEngine.from_config(config)
        assert len(engine._rules) == 1
