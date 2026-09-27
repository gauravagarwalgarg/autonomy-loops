"""Tests for the tool registry."""

import pytest

from autonomy_loops.tools.registry import Tool, ToolRegistry


class TestToolRegistry:
    """Test tool registration and execution."""

    def test_register_tool(self):
        registry = ToolRegistry()
        tool = Tool(
            name="read_file",
            description="Read a file",
            parameters={"type": "object", "properties": {"path": {"type": "string"}}},
            handler=lambda path: f"content of {path}",
        )
        registry.register(tool)
        assert registry.get("read_file") is tool

    def test_register_function_decorator(self):
        registry = ToolRegistry()

        @registry.register_function("greet", description="Say hello")
        def greet(name: str) -> str:
            return f"Hello, {name}!"

        tool = registry.get("greet")
        assert tool is not None
        assert tool.name == "greet"
        assert tool.description == "Say hello"

    @pytest.mark.asyncio
    async def test_execute_sync_handler(self):
        registry = ToolRegistry()
        registry.register(
            Tool(
                name="add",
                description="Add two numbers",
                parameters={},
                handler=lambda a, b: a + b,
            )
        )
        result = await registry.execute("add", {"a": 2, "b": 3})
        assert result == 5

    @pytest.mark.asyncio
    async def test_execute_async_handler(self):
        registry = ToolRegistry()

        async def async_fetch(url: str) -> str:
            return f"fetched {url}"

        registry.register(
            Tool(
                name="fetch",
                description="Fetch URL",
                parameters={},
                handler=async_fetch,
            )
        )
        result = await registry.execute("fetch", {"url": "https://example.com"})
        assert result == "fetched https://example.com"

    @pytest.mark.asyncio
    async def test_execute_unknown_tool_raises(self):
        registry = ToolRegistry()
        with pytest.raises(KeyError):
            await registry.execute("nonexistent", {})

    def test_get_tool_definitions(self):
        registry = ToolRegistry()
        registry.register(
            Tool(
                name="test_tool",
                description="A test tool",
                parameters={"type": "object", "properties": {"x": {"type": "string"}}},
                handler=lambda x: x,
            )
        )
        defs = registry.get_tool_definitions()
        assert len(defs) == 1
        assert defs[0]["type"] == "function"
        assert defs[0]["function"]["name"] == "test_tool"

    def test_list_tools(self):
        registry = ToolRegistry()
        registry.register(Tool(name="a", description="", parameters={}, handler=lambda: None))
        registry.register(Tool(name="b", description="", parameters={}, handler=lambda: None))
        assert len(registry.list_tools()) == 2

    def test_infer_parameters(self):
        def my_func(name: str, count: int, flag: bool = False) -> str:
            return ""

        params = ToolRegistry._infer_parameters(my_func)
        assert params["properties"]["name"]["type"] == "string"
        assert params["properties"]["count"]["type"] == "integer"
        assert "name" in params["required"]
        assert "count" in params["required"]
        assert "flag" not in params["required"]
