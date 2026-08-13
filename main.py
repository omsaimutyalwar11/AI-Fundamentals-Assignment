"""Entry point — wires all components and runs automated validation.

Run this after completing all TODOs:
    python main.py
"""
from core.tool_registry import ToolRegistry
from core.mock_tools import get_weather, get_build_status, search_docs, create_ticket
from core.validator import Validator
from core.llm_client import MockLLMClient
from core.logger import StepLogger
from harness import AgentHarness


def setup_registry() -> ToolRegistry:
    """Create and populate the tool registry with all mock tools."""
    registry = ToolRegistry()

    registry.register_tool(
        name="get_weather",
        description="Return current weather data for a city.",
        input_schema={
            "type": "object",
            "properties": {"city": {"type": "string", "description": "City name"}},
            "required": ["city"]
        },
        handler=get_weather
    )

    registry.register_tool(
        name="get_build_status",
        description="Return the latest CI build status for a repository and branch.",
        input_schema={
            "type": "object",
            "properties": {
                "repo": {"type": "string", "description": "Repository name"},
                "branch": {"type": "string", "description": "Branch name"}
            },
            "required": ["repo", "branch"]
        },
        handler=get_build_status
    )

    registry.register_tool(
        name="search_docs",
        description="Search internal documentation and return matching results.",
        input_schema={
            "type": "object",
            "properties": {"query": {"type": "string", "description": "Search query"}},
            "required": ["query"]
        },
        handler=search_docs
    )

    registry.register_tool(
        name="create_ticket",
        description="Create a new ticket in the issue tracker. This is a write operation.",
        input_schema={
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Ticket title"},
                "description": {"type": "string", "description": "Ticket description"},
                "priority": {"type": "string", "description": "Priority: low, medium, high, critical"}
            },
            "required": ["title", "description"]
        },
        handler=create_ticket
    )

    return registry


def setup_harness() -> AgentHarness:
    """Create a fully wired harness ready to use."""
    registry = setup_registry()
    validator = Validator(registry, dangerous_tools=["create_ticket"])
    llm_client = MockLLMClient(tool_schemas=registry.list_tool_schemas())
    logger = StepLogger()
    return AgentHarness(llm_client, registry, validator, logger, max_steps=5)


# ─── Harness Tests ─────────────────────────────────────────────────


def test_weather_query():
    """Test: weather query triggers get_weather tool and returns an answer."""
    print("=" * 60)
    print("TEST: Weather Query")
    print("=" * 60)

    harness = setup_harness()
    result = harness.run("What's the weather in Mumbai?")

    assert result is not None, "FAIL: run() returned None"
    assert "final_answer" in result, "FAIL: result missing 'final_answer'"
    assert "steps_taken" in result, "FAIL: result missing 'steps_taken'"
    assert "stop_reason" in result, "FAIL: result missing 'stop_reason'"
    assert "log" in result, "FAIL: result missing 'log'"
    assert len(result["final_answer"]) > 0, "FAIL: final_answer is empty"
    assert result["steps_taken"] >= 1, "FAIL: should take at least 1 step"
    assert result["stop_reason"] in ["final_answer", "max_steps"], "FAIL: unexpected stop_reason"

    print(f"[OK] PASSED - Answer: {result['final_answer'][:80]}...")
    print(f"   Steps: {result['steps_taken']}, Stop reason: {result['stop_reason']}\n")


def test_build_status_query():
    """Test: build status query triggers get_build_status tool."""
    print("=" * 60)
    print("TEST: Build Status Query")
    print("=" * 60)

    harness = setup_harness()
    result = harness.run("Check build status of backend-api on main")

    assert result is not None, "FAIL: run() returned None"
    assert len(result["final_answer"]) > 0, "FAIL: final_answer is empty"
    assert result["steps_taken"] >= 1, "FAIL: should take at least 1 step"

    print(f"[OK] PASSED - Answer: {result['final_answer'][:80]}...")
    print(f"   Steps: {result['steps_taken']}, Stop reason: {result['stop_reason']}\n")


def test_docs_search_query():
    """Test: docs search triggers search_docs tool."""
    print("=" * 60)
    print("TEST: Documentation Search Query")
    print("=" * 60)

    harness = setup_harness()
    result = harness.run("Search docs for authentication")

    assert result is not None, "FAIL: run() returned None"
    assert len(result["final_answer"]) > 0, "FAIL: final_answer is empty"
    assert result["steps_taken"] >= 1, "FAIL: should take at least 1 step"

    print(f"[OK] PASSED - Answer: {result['final_answer'][:80]}...")
    print(f"   Steps: {result['steps_taken']}, Stop reason: {result['stop_reason']}\n")


def test_no_matching_tool():
    """Test: unmatched input returns a text response directly (no tool call)."""
    print("=" * 60)
    print("TEST: No Matching Tool")
    print("=" * 60)

    harness = setup_harness()
    result = harness.run("Tell me a joke")

    assert result is not None, "FAIL: run() returned None"
    assert result["stop_reason"] == "final_answer", "FAIL: should stop with 'final_answer'"
    assert result["steps_taken"] >= 1, "FAIL: should take at least 1 step"

    print(f"[OK] PASSED - Answer: {result['final_answer'][:80]}...")
    print(f"   Steps: {result['steps_taken']}, Stop reason: {result['stop_reason']}\n")


def test_max_steps_enforced():
    """Test: harness respects the max_steps limit."""
    print("=" * 60)
    print("TEST: Max Steps Enforced")
    print("=" * 60)

    registry = setup_registry()
    validator = Validator(registry, dangerous_tools=[])
    llm_client = MockLLMClient(tool_schemas=registry.list_tool_schemas())
    logger = StepLogger()
    harness = AgentHarness(llm_client, registry, validator, logger, max_steps=1)

    result = harness.run("What's the weather in Mumbai?")

    assert result is not None, "FAIL: run() returned None"
    assert result["steps_taken"] <= 1, "FAIL: should not exceed max_steps=1"

    print(f"[OK] PASSED - Steps: {result['steps_taken']}, Stop reason: {result['stop_reason']}\n")


def test_log_is_populated():
    """Test: the harness populates the step log."""
    print("=" * 60)
    print("TEST: Log Is Populated")
    print("=" * 60)

    harness = setup_harness()
    result = harness.run("What's the weather in Pune?")

    assert isinstance(result["log"], list), "FAIL: log should be a list"
    assert len(result["log"]) > 0, "FAIL: log should not be empty"

    print(f"[OK] PASSED - Log entries: {len(result['log'])}\n")


def test_dangerous_tool_requires_approval():
    """Test: a dangerous tool (create_ticket) is flagged for approval, then executed."""
    print("=" * 60)
    print("TEST: Dangerous Tool Requires Approval")
    print("=" * 60)

    harness = setup_harness()  # create_ticket is registered as a dangerous tool
    result = harness.run("Create a ticket for the login bug")

    assert result is not None, "FAIL: run() returned None"
    assert result["stop_reason"] == "final_answer", "FAIL: should finish with 'final_answer' after auto-approving"
    assert result["steps_taken"] >= 2, "FAIL: dangerous tool run should take at least 2 steps (call + summary)"

    approval_logged = any(
        entry["action"] == "validation" and entry["detail"].get("requires_approval") is True
        for entry in result["log"]
    )
    assert approval_logged, "FAIL: expected a validation log entry with requires_approval=True"

    print(f"[OK] PASSED - Answer: {result['final_answer'][:80]}...")
    print(f"   Steps: {result['steps_taken']}, Stop reason: {result['stop_reason']}\n")


def test_invalid_tool_call_rejected():
    """Test: an invalid tool call (missing required args) stops with 'validation_error'."""
    print("=" * 60)
    print("TEST: Invalid Tool Call Rejected")
    print("=" * 60)

    class _InvalidCallLLM:
        """Stub LLM that proposes get_weather without the required 'city' argument."""
        def chat(self, messages: list) -> dict:
            return {"type": "tool_call", "tool_name": "get_weather", "arguments": {}}

    registry = setup_registry()
    validator = Validator(registry, dangerous_tools=[])
    logger = StepLogger()
    harness = AgentHarness(_InvalidCallLLM(), registry, validator, logger, max_steps=3)

    result = harness.run("weather?")

    assert result is not None, "FAIL: run() returned None"
    assert result["stop_reason"] == "validation_error", "FAIL: should stop with 'validation_error'"
    assert result["steps_taken"] == 1, "FAIL: should stop on the first (invalid) step"
    assert len(result["final_answer"]) > 0, "FAIL: final_answer should explain the error"

    print(f"[OK] PASSED - Answer: {result['final_answer'][:80]}...")
    print(f"   Steps: {result['steps_taken']}, Stop reason: {result['stop_reason']}\n")


# ─── Main ────────────────────────────────────────────────────────────


def main():
    print()
    print("  AI Agent Harness - Automated Validation")
    print("=" * 60)
    print()

    tests = [
        test_weather_query,
        test_build_status_query,
        test_docs_search_query,
        test_no_matching_tool,
        test_max_steps_enforced,
        test_log_is_populated,
        test_dangerous_tool_requires_approval,
        test_invalid_tool_call_rejected,
    ]

    passed = 0
    failed = 0

    for test_fn in tests:
        try:
            test_fn()
            passed += 1
        except AssertionError as e:
            print(f"\n[FAIL] FAILED: {e}")
            print()
            failed += 1
        except Exception as e:
            print(f"\n[ERROR] ERROR: {type(e).__name__}: {e}")
            print()
            failed += 1

    # Summary
    print("=" * 60)
    print(f"  Results: {passed} passed, {failed} failed, {len(tests)} total")
    if failed == 0:
        print("  [SUCCESS] All tests passed! Your harness is working correctly.")
    else:
        print("  [WARNING] Some tests failed. Check the errors above.")
    print("=" * 60)


if __name__ == "__main__":
    main()
