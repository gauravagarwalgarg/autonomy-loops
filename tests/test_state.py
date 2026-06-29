"""Tests for the agent state machine."""

import pytest

from autonomy_loops.state import AgentState, InvalidTransitionError, StateMachine, StateTransition


class TestStateMachine:
    """Test state machine transitions."""

    def test_initial_state(self):
        sm = StateMachine()
        assert sm.state == AgentState.IDLE
        assert sm.iteration == 0
        assert not sm.is_terminal

    def test_valid_transition(self):
        sm = StateMachine()
        t = sm.transition(AgentState.PLANNING, reason="start")
        assert sm.state == AgentState.PLANNING
        assert t.from_state == AgentState.IDLE
        assert t.to_state == AgentState.PLANNING
        assert t.reason == "start"
        assert sm.iteration == 1

    def test_invalid_transition_raises(self):
        sm = StateMachine()
        with pytest.raises(InvalidTransitionError):
            sm.transition(AgentState.COMPLETED)

    def test_terminal_states(self):
        sm = StateMachine()
        sm.transition(AgentState.PLANNING)
        sm.transition(AgentState.ACTING)
        sm.transition(AgentState.OBSERVING)
        sm.transition(AgentState.REFLECTING)
        sm.transition(AgentState.COMPLETED)
        assert sm.is_terminal

    def test_cancelled_is_terminal(self):
        sm = StateMachine()
        sm.transition(AgentState.CANCELLED)
        assert sm.is_terminal

    def test_history_tracking(self):
        sm = StateMachine()
        sm.transition(AgentState.PLANNING)
        sm.transition(AgentState.ACTING)
        assert len(sm.history) == 2

    def test_iteration_increments_on_planning(self):
        sm = StateMachine()
        sm.transition(AgentState.PLANNING)
        assert sm.iteration == 1
        sm.transition(AgentState.ACTING)
        sm.transition(AgentState.OBSERVING)
        sm.transition(AgentState.REFLECTING)
        sm.transition(AgentState.PLANNING)
        assert sm.iteration == 2

    def test_reset(self):
        sm = StateMachine()
        sm.transition(AgentState.PLANNING)
        sm.transition(AgentState.ACTING)
        sm.reset()
        assert sm.state == AgentState.IDLE
        assert sm.iteration == 0
        assert sm.history == []

    def test_can_transition(self):
        sm = StateMachine()
        assert sm.can_transition(AgentState.PLANNING)
        assert not sm.can_transition(AgentState.ACTING)

    def test_waiting_approval_flow(self):
        sm = StateMachine()
        sm.transition(AgentState.PLANNING)
        sm.transition(AgentState.WAITING_APPROVAL)
        sm.transition(AgentState.ACTING)
        assert sm.state == AgentState.ACTING
