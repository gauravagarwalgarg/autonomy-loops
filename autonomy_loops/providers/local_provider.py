"""Local model provider (Ollama, vLLM, LM Studio, etc.).

Connects to any OpenAI-compatible local inference server.
"""

from __future__ import annotations

from typing import Any, AsyncIterator

import httpx

from autonomy_loops.config import ProviderConfig
from autonomy_loops.providers.base import (
    LLMMessage,
    LLMProvider,
    LLMResponse,
    ProviderError,
    ToolCall,
)


class LocalProvider(LLMProvider):
    """Provider for local OpenAI-compatible servers (Ollama, vLLM, etc.)."""

    def __init__(self, config: ProviderConfig) -> None:
        self._config = config
        self._base_url = (config.base_url or "http://localhost:11434").rstrip("/")

    @property
    def name(self) -> str:
        return "local"

    def _format_messages(self, messages: list[LLMMessage]) -> list[dict[str, Any]]:
        return [{"role": msg.role, "content": msg.content} for msg in messages]

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
        model_name = model or self._config.default_model or "llama3.1:8b"

        payload: dict[str, Any] = {
            "model": model_name,
            "messages": self._format_messages(messages),
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        if tools:
            payload["tools"] = tools
        if stop:
            payload["stop"] = stop

        try:
            async with httpx.AsyncClient(timeout=self._config.timeout_seconds) as client:
                resp = await client.post(
                    f"{self._base_url}/v1/chat/completions",
                    json=payload,
                )
                resp.raise_for_status()
                data = resp.json()
        except httpx.HTTPError as e:
            raise ProviderError(str(e), provider=self.name, retryable=True) from e

        choice = data["choices"][0]
        tool_calls = []
        if choice.get("message", {}).get("tool_calls"):
            import json
            for tc in choice["message"]["tool_calls"]:
                tool_calls.append(ToolCall(
                    id=tc["id"],
                    name=tc["function"]["name"],
                    arguments=json.loads(tc["function"]["arguments"]),
                ))

        usage = data.get("usage", {})
        return LLMResponse(
            content=choice.get("message", {}).get("content", ""),
            tool_calls=tool_calls,
            model=model_name,
            usage={
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
            },
            finish_reason=choice.get("finish_reason", "stop"),
            raw=data,
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
        model_name = model or self._config.default_model or "llama3.1:8b"

        payload: dict[str, Any] = {
            "model": model_name,
            "messages": self._format_messages(messages),
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }

        try:
            async with httpx.AsyncClient(timeout=self._config.timeout_seconds) as client:
                async with client.stream(
                    "POST",
                    f"{self._base_url}/v1/chat/completions",
                    json=payload,
                ) as resp:
                    async for line in resp.aiter_lines():
                        if line.startswith("data: ") and line != "data: [DONE]":
                            import json
                            chunk = json.loads(line[6:])
                            delta = chunk.get("choices", [{}])[0].get("delta", {})
                            if delta.get("content"):
                                yield LLMResponse(content=delta["content"], model=model_name)
        except httpx.HTTPError as e:
            raise ProviderError(str(e), provider=self.name, retryable=True) from e
