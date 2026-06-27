"""Human-in-the-loop (HITL) gate implementation.

Provides approval workflows that pause agent execution and wait for
human review before proceeding with sensitive operations.
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Awaitable


class ApprovalStatus(str, Enum):
    """Status of an approval request."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    TIMED_OUT = "timed_out"


@dataclass
class ApprovalRequest:
    """A request for human approval."""
    id: str
    agent_id: str
    action_type: str  # tool_call, state_transition, etc.
    description: str
    context: dict[str, Any] = field(default_factory=dict)
    status: ApprovalStatus = ApprovalStatus.PENDING
    requested_at: float = field(default_factory=time.time)
    resolved_at: float | None = None
    resolved_by: str | None = None
    comment: str = ""


class HITLGate:
    """Human-in-the-loop approval gate.

    Supports multiple approval backends:
    - CLI (interactive terminal prompt)
    - Webhook (POST to external approval system)
    - Queue (Redis/message queue for async workflows)
    """

    def __init__(
        self,
        *,
        timeout_seconds: int = 300,
        approval_handler: Callable[[ApprovalRequest], Awaitable[ApprovalStatus]] | None = None,
    ) -> None:
        self._timeout = timeout_seconds
        self._handler = approval_handler or self._default_cli_handler
        self._pending: dict[str, ApprovalRequest] = {}

    async def request_approval(self, request: ApprovalRequest) -> ApprovalStatus:
        """Submit an approval request and wait for resolution.

        Args:
            request: The approval request to submit.

        Returns:
            Final approval status.
        """
        self._pending[request.id] = request

        try:
            status = await asyncio.wait_for(
                self._handler(request),
                timeout=self._timeout,
            )
        except asyncio.TimeoutError:
            status = ApprovalStatus.TIMED_OUT

        request.status = status
        request.resolved_at = time.time()
        return status

    @staticmethod
    async def _default_cli_handler(request: ApprovalRequest) -> ApprovalStatus:
        """Default handler: prompt on CLI for approval."""
        print(f"\n{'='*60}")
        print(f"  APPROVAL REQUIRED")
        print(f"{'='*60}")
        print(f"  Agent: {request.agent_id}")
        print(f"  Action: {request.action_type}")
        print(f"  Description: {request.description}")
        if request.context:
            print(f"  Context: {request.context}")
        print(f"{'='*60}")

        # Run input in thread to not block event loop
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: input("  Approve? [y/N]: ").strip().lower(),
        )

        if response in ("y", "yes"):
            return ApprovalStatus.APPROVED
        return ApprovalStatus.REJECTED

    @staticmethod
    async def auto_approve(request: ApprovalRequest) -> ApprovalStatus:
        """Auto-approve handler (for testing/CI)."""
        return ApprovalStatus.APPROVED

    @staticmethod
    async def auto_reject(request: ApprovalRequest) -> ApprovalStatus:
        """Auto-reject handler (for testing)."""
        return ApprovalStatus.REJECTED
