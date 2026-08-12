"""Validator — fully implemented, pre-built for you.

Validates tool calls before execution: checks the tool exists,
required arguments are present, and flags dangerous tools.
"""

from core.tool_registry import ToolRegistry


class Validator:
    """Validates tool calls before the harness executes them."""

    def __init__(self, registry: ToolRegistry, dangerous_tools: list[str] | None = None):
        """Initialize the validator.

        Args:
            registry: The ToolRegistry used to look up tools and their schemas.
            dangerous_tools: Names of tools that require approval before running
                (e.g. ["create_ticket"]). Defaults to an empty list.
        """
        self._registry = registry
        self._dangerous_tools: list[str] = dangerous_tools or []

    def validate_tool_call(self, tool_call: dict) -> dict:
        """Validate a proposed tool call from the LLM.

        Args:
            tool_call: The LLM's tool-call response, of shape:
                {"type": "tool_call", "tool_name": str, "arguments": dict}

        Returns:
            {
                "valid": bool,              # True if the call may be executed
                "error": str | None,        # reason when invalid, else None
                "requires_approval": bool,  # True if the tool is dangerous
            }
        """
        tool_name = tool_call.get("tool_name")
        if not tool_name:
            return {"valid": False, "error": "Missing 'tool_name' in tool_call", "requires_approval": False}

        tool = self._registry.get_tool(tool_name)
        if not tool:
            return {"valid": False, "error": f"Tool '{tool_name}' not found in registry", "requires_approval": False}

        args = tool_call.get("arguments", {})
        required = tool.get("input_schema", {}).get("required", [])

        missing = [req for req in required if req not in args]
        if missing:
            return {"valid": False, "error": f"Missing required arguments: {missing}", "requires_approval": False}

        is_dangerous = self.is_dangerous(tool_name)

        return {"valid": True, "error": None, "requires_approval": is_dangerous}

    def is_dangerous(self, tool_name: str) -> bool:
        """Check if a tool requires approval before execution.

        Args:
            tool_name: The name of the tool to check.

        Returns:
            True if `tool_name` is in the configured dangerous-tools list.
        """
        return tool_name in self._dangerous_tools

