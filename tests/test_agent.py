"""Tests for the Agent class."""

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from autonomy_loops.agent import Agent, AgentResult
from autonomy_loops.config import Config
from autonomy_loops.providers.base import LLMMessage, LLMProvider, LLMResponse
from autonomy_loops.state import AgentState


class MockProvider(LLMProvider):
    """Mock LLM provider for testing."""

    def __init__(self, responses: list[LLMResponse] | None = None):
        self._responses = responses or [
            LLMResponse(content="Task completed successfully.", usage={"prompt_tokens": 100, "completion_tokens": 50})
        ]
        self._call_count = 0

    @property
    def name(self) -> str:
        return "mock"

    async def complete(self, messages, **kwargs) -> LLMResponse:
        idx = min(self._call_count, len(self._responses) - 1)
        self._call_count += 1
        return self._responses[idx]

    async def stream(self, messages, **kwargs):
        yield LLMResponse(content="streamed", model="mock")


@pytest.fixture
def config():
    return Config()


@pytest.fixture
def provider():
    return MockProvider()


class TestAgent:
    """Test agent lifecycle and execution."""

    def test_agent_initial_state(self, provider, config):
        agent = Agent(role="developer", mode="code", provider=provider, config=config)
        assert agent.state == AgentState.IDLE

    @pytest.mark.asyncio
    async def test_agent_completes_simple_task(self, provider, config):
        agent = Agent(role="developer", mode="code", provider=provider, config=config)
        result = await agent.run("Write a hello world function")
        assert result.success is True
        assert result.state == AgentState.COMPLETED
        assert result.iterations >= 1
        assert result.total_tokens > 0

    @pytest.mark.asyncio
    async def test_agent_respects_max_iterations(self, config):
        # Provider that always requests tool calls (would loop forever)
        from autonomy_loops.providers.base import ToolCall

        infinite_provider = MockProvider(responses=[
            LLMResponse(
                content="",
                tool_calls=[ToolCall(id="1", name="nonexistent", arguments={})],
                usage={"prompt_tokens": 10, "completion_tokens": 10},
            )
        ])
        config.policy.max_iterations = 3
        agent = Agent(role="developer", mode="code", provider=infinite_provider, config=config)
        result = await agent.run("Do something")
        assert result.success is False
        assert result.state == AgentState.FAILED

    @pytest.mark.asyncio
    async def test_agent_handles_provider_error(self, config):
        from autonomy_loops.providers.base import ProviderError

        class FailingProvider(MockProvider):
            async def complete(self, messages, **kwargs):
                raise ProviderError("API rate limited", provider="mock", retryable=True)

        agent = Agent(role="developer", mode="code", provider=FailingProvider(), config=config)
        result = await agent.run("Do something")
        assert result.success is False
        assert result.state == AgentState.FAILED


class TestAgentResult:
    """Test AgentResult dataclass."""

    def test_result_fields(self):
        result = AgentResult(
            success=True,
            output="Done",
            iterations=3,
            total_tokens=500,
            elapsed_seconds=2.5,
            tool_calls_made=2,
        )
        assert result.success
        assert result.output == "Done"
        assert result.iterations == 3
        assert result.total_tokens == 500
