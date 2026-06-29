"""OpenAI / Azure OpenAI provider implementation."""

from __future__ import annotations

from typing import Any, AsyncIterator

from autonomy_loops.config import ProviderConfig
from autonomy_loops.providers.base import (
    LLMMessage,
    LLMProvider,
    LLMResponse,
    ProviderError,
    ToolCall,
)


class OpenAIProvider(LLMProvider):
    """Provider for OpenAI API and Azure OpenAI endpoints."""

    def __init__(self, config: ProviderConfig) -> None:
        self._config = config
        self._client: Any = None

    @property
    def name(self) -> str:
        return "openai"

    def _get_client(self) -> Any:
        if self._client is None:
            try:
                from openai import AsyncOpenAI
            except ImportError as e:
                raise ProviderError(
                    "openai package not installed. Run: pip install autonomy-loops[openai]",
                    provider=self.name,
                ) from e

            kwargs: dict[str, Any] = {"api_key": self._config.api_key}
            if self._config.base_url:
                kwargs["base_url"] = self._config.base_url
            self._client = AsyncOpenAI(**kwargs)
        return self._client

    def _format_messages(self, messages: list[LLMMessage]) -> list[dict[str, Any]]:
        """Convert internal messages to OpenAI format."""
        formatted = []
        for msg in messages:
            entry: dict[str, Any] = {"role": msg.role, "content": msg.content}
            if msg.name:
                entry["name"] = msg.name
            if msg.tool_call_id:
                entry["tool_call_id"] = msg.tool_call_id
            if msg.tool_calls:
                entry["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": tc.name, "arguments": str(tc.arguments)},
                    }
                    for tc in msg.tool_calls
                ]
            formatted.append(entry)
        return formatted

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
        model_name = model or self._config.default_model or "gpt-4o"

        kwargs: dict[str, Any] = {
            "model": model_name,
            "messages": self._format_messages(messages),
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if tools:
            kwargs["tools"] = tools
        if stop:
            kwargs["stop"] = stop

        try:
            response = await client.chat.completions.create(**kwargs)
        except Exception as e:
            raise ProviderError(str(e), provider=self.name, retryable=True) from e

        choice = response.choices[0]
        tool_calls = []
        if choice.message.tool_calls:
            import json
            for tc in choice.message.tool_calls:
                tool_calls.append(ToolCall(
                    id=tc.id,
                    name=tc.function.name,
                    arguments=json.loads(tc.function.arguments),
                ))

        return LLMResponse(
            content=choice.message.content or "",
            tool_calls=tool_calls,
            model=response.model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
            },
            finish_reason=choice.finish_reason or "stop",
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
        model_name = model or self._config.default_model or "gpt-4o"

        kwargs: dict[str, Any] = {
            "model": model_name,
            "messages": self._format_messages(messages),
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }
        if tools:
            kwargs["tools"] = tools

        try:
            stream = await client.chat.completions.create(**kwargs)
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield LLMResponse(
                        content=chunk.choices[0].delta.content,
                        model=model_name,
                    )
        except Exception as e:
            raise ProviderError(str(e), provider=self.name, retryable=True) from e
