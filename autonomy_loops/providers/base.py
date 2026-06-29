"""Abstract base for LLM providers.

All providers implement this interface, enabling the orchestrator and agents
to work identically regardless of the underlying model backend.
"""

from __future__ import annotations

import abc
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import Any


@dataclass
class LLMMessage:
    """A single message in the conversation."""

    role: str  # system | user | assistant | tool
    content: str
    name: str | None = None
    tool_call_id: str | None = None
    tool_calls: list[ToolCall] = field(default_factory=list)


@dataclass
class ToolCall:
    """A tool invocation requested by the model."""

    id: str
    name: str
    arguments: dict[str, Any]


@dataclass
class LLMResponse:
    """Response from an LLM provider."""

    content: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    model: str = ""
    usage: dict[str, int] = field(default_factory=dict)  # prompt_tokens, completion_tokens
    finish_reason: str = "stop"
    raw: Any = None  # Provider-specific raw response


class ProviderError(Exception):
    """Base error for provider failures."""

    def __init__(self, message: str, provider: str = "", retryable: bool = False) -> None:
        super().__init__(message)
        self.provider = provider
        self.retryable = retryable


class LLMProvider(abc.ABC):
    """Abstract interface for LLM providers.

    Implementations handle authentication, request formatting, rate limiting,
    and response parsing for a specific provider (OpenAI, Anthropic, etc.).
    """

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Provider identifier (e.g., 'openai', 'anthropic')."""
        ...

    @abc.abstractmethod
    async def complete(
        self,
        messages: list[LLMMessage],
        *,
        model: str | None = None,
        temperature: float = 0.0,
        max_tokens: int = 4096,
        tools: list[dict[str, Any]] | None = None,
        stop: list[str] | None = None,
    ) -> LLMResponse:
        """Send a completion request to the provider.

        Args:
            messages: Conversation history.
            model: Override the default model.
            temperature: Sampling temperature (0 = deterministic).
            max_tokens: Maximum response tokens.
            tools: Tool definitions in OpenAI function-calling format.
            stop: Stop sequences.

        Returns:
            LLMResponse with content and/or tool calls.

        Raises:
            ProviderError: On API failures (rate limits, auth, etc.).
        """
        ...

    @abc.abstractmethod
    def stream(
        self,
        messages: list[LLMMessage],
        *,
        model: str | None = None,
        temperature: float = 0.0,
        max_tokens: int = 4096,
        tools: list[dict[str, Any]] | None = None,
    ) -> AsyncIterator[LLMResponse]:
        """Stream a completion response token-by-token.

        Yields partial LLMResponse objects as tokens arrive.
        """
        ...

    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text. Default: ~4 chars per token."""
        return len(text) // 4
