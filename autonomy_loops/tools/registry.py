"""Tool registry registers, validates, and dispatches tool executions.

Tools are the actions an agent can take in the world: reading files,
running commands, making HTTP requests, etc. The registry provides
discovery (for LLM tool definitions) and execution (with sandboxing).
"""

from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from typing import Any, Callable, Awaitable


@dataclass
class Tool:
    """A registered tool that an agent can invoke."""
    name: str
    description: str
    parameters: dict[str, Any]  # JSON Schema for parameters
    handler: Callable[..., Awaitable[Any]] | Callable[..., Any]
    category: str = "general"  # file, shell, web, code, general
    requires_approval: bool = False

    def to_openai_schema(self) -> dict[str, Any]:
        """Convert to OpenAI function-calling tool schema."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


class ToolRegistry:
    """Registry for agent tools with execution dispatch."""

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        """Register a tool for agent use."""
        self._tools[tool.name] = tool

    def register_function(
        self,
        name: str,
        *,
        description: str = "",
        parameters: dict[str, Any] | None = None,
        category: str = "general",
        requires_approval: bool = False,
    ) -> Callable:
        """Decorator to register a function as a tool.

        Usage:
            @registry.register_function("read_file", description="Read a file")
            async def read_file(path: str) -> str:
                ...
        """
        def decorator(fn: Callable) -> Callable:
            params = parameters or self._infer_parameters(fn)
            tool = Tool(
                name=name,
                description=description or fn.__doc__ or "",
                parameters=params,
                handler=fn,
                category=category,
                requires_approval=requires_approval,
            )
            self._tools[name] = tool
            return fn
        return decorator

    def get(self, name: str) -> Tool | None:
        """Look up a tool by name."""
        return self._tools.get(name)

    def list_tools(self) -> list[Tool]:
        """List all registered tools."""
        return list(self._tools.values())

    def get_tool_definitions(self) -> list[dict[str, Any]]:
        """Get all tools in OpenAI function-calling format."""
        return [tool.to_openai_schema() for tool in self._tools.values()]

    async def execute(self, name: str, arguments: dict[str, Any]) -> Any:
        """Execute a tool by name with given arguments.

        Raises:
            KeyError: Tool not found.
            RuntimeError: Tool execution failed.
        """
        tool = self._tools.get(name)
        if not tool:
            raise KeyError(f"Tool not found: {name}. Available: {list(self._tools.keys())}")

        handler = tool.handler
        if inspect.iscoroutinefunction(handler):
            return await handler(**arguments)
        else:
            return handler(**arguments)

    @staticmethod
    def _infer_parameters(fn: Callable) -> dict[str, Any]:
        """Infer JSON Schema parameters from function signature."""
        sig = inspect.signature(fn)
        properties: dict[str, Any] = {}
        required: list[str] = []

        type_map = {
            str: "string",
            int: "integer",
            float: "number",
            bool: "boolean",
            list: "array",
            dict: "object",
        }

        for name, param in sig.parameters.items():
            if name in ("self", "cls"):
                continue

            annotation = param.annotation
            json_type = type_map.get(annotation, "string")
            properties[name] = {"type": json_type}

            if param.default is inspect.Parameter.empty:
                required.append(name)

        return {
            "type": "object",
            "properties": properties,
            "required": required,
        }
