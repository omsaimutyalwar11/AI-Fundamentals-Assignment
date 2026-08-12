"""Tool Registry — fully implemented, pre-built for you.

The tool registry stores available tools and their schemas.
It lets the harness look up, list, and execute tools by name.
"""


class ToolRegistry:
    """Registry that manages available tools and their schemas."""

    def __init__(self):
        """Initialize an empty tool registry."""
        self._tools: dict = {}

    def register_tool(self, name: str, description: str, input_schema: dict, handler) -> None:
        """Register a tool with its schema and handler function.

        Args:
            name: Unique tool name.
            description: Human-readable description of what the tool does.
            input_schema: JSON-schema-style dict describing the arguments, e.g.
                {"type": "object",
                 "properties": {"city": {"type": "string"}},
                 "required": ["city"]}
            handler: Callable invoked as handler(**arguments); returns a result dict.

        Returns:
            None.

        Raises:
            ValueError: If a tool with the same name is already registered.
        """
        if name in self._tools:
            raise ValueError(f"Tool '{name}' is already registered.")
        
        self._tools[name] = {
            "name": name,
            "description": description,
            "input_schema": input_schema,
            "handler": handler
        }

    def get_tool(self, name: str) -> dict | None:
        """Look up a tool by name.

        Args:
            name: The tool name to look up.

        Returns:
            The stored tool dict of shape
                {"name": str, "description": str, "input_schema": dict, "handler": callable}
            or None if no tool with that name is registered.
        """
        return self._tools.get(name)

    def has_tool(self, name: str) -> bool:
        """Check if a tool is registered.

        Args:
            name: The tool name to check.

        Returns:
            True if a tool with that name is registered.
        """
        return name in self._tools

    def list_tool_schemas(self) -> list[dict]:
        """Return all tool schemas for LLM context (excludes handler).

        Returns:
            A list of schema dicts, each of shape:
                {"name": str, "description": str, "inputSchema": dict}
        """
        schemas = []
        for name, data in self._tools.items():
            schemas.append({
                "name": data["name"],
                "description": data["description"],
                "inputSchema": data["input_schema"]
            })
        return schemas

    def execute_tool(self, name: str, arguments: dict) -> dict:
        """Execute a registered tool with given arguments.

        Args:
            name: The name of a registered tool.
            arguments: Keyword arguments passed to the tool handler.

        Returns:
            The tool's result dict. On success, tool-specific data of shape
                {"success": True, "data": {...}}; on a handler error,
                {"success": False, "error": str}.

        Raises:
            KeyError: If no tool with `name` is registered.
        """
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' is not registered.")
        
        handler = self._tools[name]["handler"]
        try:
            return handler(**arguments)
        except Exception as e:
            return {"success": False, "error": str(e)}

