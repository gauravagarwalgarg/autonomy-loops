"""Agent state machine for AutonomyLoops.

Defines the lifecycle states an agent transitions through during execution,
with guards, hooks, and audit logging at each transition.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class AgentState(StrEnum):
    """Agent lifecycle states."""

    IDLE = "idle"
    PLANNING = "planning"
    ACTING = "acting"
    OBSERVING = "observing"
    REFLECTING = "reflecting"
    WAITING_APPROVAL = "waiting_approval"
    DELEGATING = "delegating"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# Valid state transitions
_TRANSITIONS: dict[AgentState, set[AgentState]] = {
    AgentState.IDLE: {AgentState.PLANNING, AgentState.CANCELLED},
    AgentState.PLANNING: {
        AgentState.ACTING,
        AgentState.WAITING_APPROVAL,
        AgentState.FAILED,
        AgentState.CANCELLED,
    },
    AgentState.ACTING: {
        AgentState.OBSERVING,
        AgentState.WAITING_APPROVAL,
        AgentState.FAILED,
        AgentState.CANCELLED,
    },
    AgentState.OBSERVING: {AgentState.REFLECTING, AgentState.FAILED, AgentState.CANCELLED},
    AgentState.REFLECTING: {
        AgentState.PLANNING,
        AgentState.DELEGATING,
        AgentState.COMPLETED,
        AgentState.FAILED,
        AgentState.CANCELLED,
    },
    AgentState.WAITING_APPROVAL: {
        AgentState.ACTING,
        AgentState.PLANNING,
        AgentState.CANCELLED,
        AgentState.FAILED,
    },
    AgentState.DELEGATING: {AgentState.OBSERVING, AgentState.FAILED, AgentState.CANCELLED},
    AgentState.COMPLETED: set(),
    AgentState.FAILED: set(),
    AgentState.CANCELLED: set(),
}


@dataclass
class StateTransition:
    """Record of a state transition for audit trail."""

    from_state: AgentState
    to_state: AgentState
    timestamp: float = field(default_factory=time.time)
    reason: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class InvalidTransitionError(Exception):
    """Raised when an invalid state transition is attempted."""


class StateMachine:
    """Manages agent state with transition validation and history."""

    def __init__(self, initial_state: AgentState = AgentState.IDLE) -> None:
        self._state = initial_state
        self._history: list[StateTransition] = []
        self._iteration = 0

    @property
    def state(self) -> AgentState:
        return self._state

    @property
    def history(self) -> list[StateTransition]:
        return self._history.copy()

    @property
    def iteration(self) -> int:
        return self._iteration

    @property
    def is_terminal(self) -> bool:
        return self._state in {AgentState.COMPLETED, AgentState.FAILED, AgentState.CANCELLED}

    def can_transition(self, target: AgentState) -> bool:
        """Check if a transition to the target state is valid."""
        return target in _TRANSITIONS.get(self._state, set())

    def transition(self, target: AgentState, reason: str = "", **metadata: Any) -> StateTransition:
        """Execute a state transition.

        Raises InvalidTransitionError if the transition is not allowed.
        """
        if not self.can_transition(target):
            raise InvalidTransitionError(
                f"Cannot transition from {self._state.value} to {target.value}. "
                f"Valid targets: {[s.value for s in _TRANSITIONS.get(self._state, set())]}"
            )

        transition = StateTransition(
            from_state=self._state,
            to_state=target,
            reason=reason,
            metadata=metadata,
        )
        self._history.append(transition)
        self._state = target

        # Increment iteration counter on each planning phase
        if target == AgentState.PLANNING:
            self._iteration += 1

        return transition

    def reset(self) -> None:
        """Reset to initial state (for re-runs)."""
        self._state = AgentState.IDLE
        self._history.clear()
        self._iteration = 0
