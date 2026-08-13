"""Mock LLM Client — fully implemented, pre-built for you.

Instead of calling a real LLM API, this client uses simple keyword
matching to decide which tool to call based on user input.
"""


class MockLLMClient:
    """Simulates an LLM that maps user input to tool calls via keyword matching."""

    def __init__(self, tool_schemas: list[dict]):
        """Initialize with available tool schemas.

        Args:
            tool_schemas: List of tool schema dicts from ToolRegistry.list_tool_schemas()
        """
        self._tool_schemas = tool_schemas

    def chat(self, messages: list[dict]) -> dict:
        """Process messages and return either a tool call or text response.

        Args:
            messages: List of dicts with "role" and "content" keys.

        Returns:
            {"type": "tool_call", "tool_name": str, "arguments": dict}
            or {"type": "text", "content": str}
        """
        if not messages:
            return {"type": "text", "content": "No input provided."}

        last = messages[-1]
        role = last.get("role", "")
        content = last.get("content", "")

        # If the last message is a tool result, summarise it
        if role == "tool_result":
            return {"type": "text", "content": f"Based on the tool result: {content}"}

        # If the last message is from the user, match keywords to tools
        text = content.lower()

        # Weather
        weather_keywords = ["weather", "temperature", "climate", "forecast"]
        if any(kw in text for kw in weather_keywords):
            city = self._extract_city(text)
            return {"type": "tool_call", "tool_name": "get_weather", "arguments": {"city": city}}

        # Build / CI
        build_keywords = ["build", "ci", "pipeline", "deploy"]
        if any(kw in text for kw in build_keywords):
            repo, branch = self._extract_repo_branch(text)
            return {"type": "tool_call", "tool_name": "get_build_status", "arguments": {"repo": repo, "branch": branch}}

        # Documentation search
        docs_keywords = ["docs", "documentation", "search", "how to", "guide"]
        if any(kw in text for kw in docs_keywords):
            query = self._extract_query(text)
            return {"type": "tool_call", "tool_name": "search_docs", "arguments": {"query": query}}

        # Ticket / issue creation
        ticket_keywords = ["ticket", "issue", "bug", "create"]
        if any(kw in text for kw in ticket_keywords):
            title, description = self._extract_ticket_info(content)
            return {"type": "tool_call", "tool_name": "create_ticket", "arguments": {"title": title, "description": description, "priority": "medium"}}

        # No match
        return {"type": "text", "content": "I don't have a suitable tool for that request."}

    # ── helpers ──

    @staticmethod
    def _extract_city(text: str) -> str:
        known = ["mumbai", "pune", "bangalore", "delhi", "chennai", "hyderabad", "kolkata"]
        for city in known:
            if city in text:
                return city.capitalize()
        for marker in ["in ", "for ", "at "]:
            if marker in text:
                after = text.split(marker, 1)[1].strip()
                return after.split()[0].capitalize() if after else "Unknown"
        return "Unknown"

    @staticmethod
    def _extract_repo_branch(text: str) -> tuple[str, str]:
        repo, branch = "unknown-repo", "main"
        for r in ["backend-api", "frontend-app", "backend", "frontend"]:
            if r in text:
                repo = r
                break
        for b in ["main", "dev", "develop", "staging", "master"]:
            if f" {b}" in text or text.endswith(b):
                branch = b
                break
        return repo, branch

    @staticmethod
    def _extract_query(text: str) -> str:
        for prefix in ["search docs for ", "search documentation for ", "search for ", "docs ", "documentation ", "how to ", "search ", "guide "]:
            if text.startswith(prefix):
                return text[len(prefix):].strip() or text
        return text

    @staticmethod
    def _extract_ticket_info(original: str) -> tuple[str, str]:
        text = original.strip()
        for prefix in ["create a ticket for ", "create ticket for ", "open a ticket for ", "file a bug for ", "create a ticket ", "create ticket "]:
            if text.lower().startswith(prefix):
                text = text[len(prefix):]
                break
        title = text.strip() or "Untitled ticket"
        return title, f"Auto-created from user request: {original.strip()}"
