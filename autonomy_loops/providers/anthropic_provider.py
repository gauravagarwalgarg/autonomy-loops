"""Anthropic Claude provider implementation."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from autonomy_loops.config import ProviderConfig
from autonomy_loops.providers.base import (
    LLMMessage,
    LLMProvider,
    LLMResponse,
    ProviderError,
    ToolCall,
)


class AnthropicProvider(LLMProvider):
    """Provider for Anthropic Claude API."""

    def __init__(self, config: ProviderConfig) -> None:
        self._config = config
        self._client: Any = None

    @property
    def name(self) -> str:
        return "anthropic"

    def _get_client(self) -> Any:
        if self._client is None:
            try:
                from anthropic import AsyncAnthropic
            except ImportError as e:
                raise ProviderError(
                    "anthropic package not installed. Run: pip install autonomy-loops[anthropic]",
                    provider=self.name,
                ) from e
            self._client = AsyncAnthropic(api_key=self._config.api_key)
        return self._client

    def _format_messages(self, messages: list[LLMMessage]) -> tuple[str, list[dict[str, Any]]]:
        """Split system message and format conversation for Anthropic API."""
        system_prompt = ""
        conversation: list[dict[str, Any]] = []

        for msg in messages:
            if msg.role == "system":
                system_prompt += msg.content + "\n"
            elif msg.role == "tool":
                conversation.append(
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": msg.tool_call_id,
                                "content": msg.content,
                            }
                        ],
                    }
                )
            else:
                conversation.append({"role": msg.role, "content": msg.content})

        return system_prompt.strip(), conversation

    def _format_tools(self, tools: list[dict[str, Any]] | None) -> list[dict[str, Any]] | None:
        """Convert OpenAI-style tool definitions to Anthropic format."""
        if not tools:
            return None
        anthropic_tools = []
        for tool in tools:
            func = tool.get("function", tool)
            anthropic_tools.append(
                {
                    "name": func["name"],
                    "description": func.get("description", ""),
                    "input_schema": func.get("parameters", {"type": "object", "properties": {}}),
                }
            )
        return anthropic_tools

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
        client = self._get_client()
        model_name = model or self._config.default_model or "claude-sonnet-4-20250514"
        system_prompt, conversation = self._format_messages(messages)

        kwargs: dict[str, Any] = {
            "model": model_name,
            "messages": conversation,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if system_prompt:
            kwargs["system"] = system_prompt
        if tools:
            kwargs["tools"] = self._format_tools(tools)
        if stop:
            kwargs["stop_sequences"] = stop

        try:
            response = await client.messages.create(**kwargs)
        except Exception as e:
            raise ProviderError(str(e), provider=self.name, retryable=True) from e

        # Parse response content blocks
        content_parts: list[str] = []
        tool_calls: list[ToolCall] = []

        for block in response.content:
            if block.type == "text":
                content_parts.append(block.text)
            elif block.type == "tool_use":
                tool_calls.append(
                    ToolCall(
                        id=block.id,
                        name=block.name,
                        arguments=block.input,
                    )
                )

        return LLMResponse(
            content="\n".join(content_parts),
            tool_calls=tool_calls,
            model=response.model,
            usage={
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
            },
            finish_reason=response.stop_reason or "end_turn",
            raw=response,
        )

    async def stream(
        self,
        messages: list[LLMMessage],
        *,
        model: str | None = None,
        temperature: float = 0.0,
        max_tokens: int = 4096,
        tools: list[dict[str, Any]] | None = None,
    ) -> AsyncIterator[LLMResponse]:
        client = self._get_client()
        model_name = model or self._config.default_model or "claude-sonnet-4-20250514"
        system_prompt, conversation = self._format_messages(messages)

        kwargs: dict[str, Any] = {
            "model": model_name,
            "messages": conversation,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if system_prompt:
            kwargs["system"] = system_prompt
        if tools:
            kwargs["tools"] = self._format_tools(tools)

        try:
            async with client.messages.stream(**kwargs) as stream:
                async for text in stream.text_stream:
                    yield LLMResponse(content=text, model=model_name)
        except Exception as e:
            raise ProviderError(str(e), provider=self.name, retryable=True) from e
