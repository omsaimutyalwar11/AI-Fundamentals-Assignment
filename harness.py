"""Agent Harness — YOU IMPLEMENT THIS.

The harness orchestrates the agentic loop:
  user input → LLM → tool call → validate → execute → feed result back → repeat
"""

from core.llm_client import MockLLMClient
from core.tool_registry import ToolRegistry
from core.validator import Validator
from core.logger import StepLogger


class AgentHarness:
    """The agent harness — ties LLM, tools, validator, and logger into the agentic loop."""

    def __init__(self, llm_client: MockLLMClient, tool_registry: ToolRegistry,
                 validator: Validator, logger: StepLogger, max_steps: int = 5):
        """Initialize the harness.

        Args:
            llm_client: The (mocked) LLM client
            tool_registry: Registry of available tools
            validator: Validates tool calls before execution
            logger: Logs each step
            max_steps: Maximum loop iterations before forced stop
        """
        self._llm = llm_client
        self._registry = tool_registry
        self._validator = validator
        self._logger = logger
        self._max_steps = max_steps

    def run(self, user_input: str) -> dict:
        """Run the agent loop for a given user input.

        Args:
            user_input: The user's natural language request

        Returns:
            {
                "final_answer": str,       # The agent's final text response
                "steps_taken": int,        # How many loop iterations ran
                "stop_reason": str,        # Why the loop stopped:
                                           #   "final_answer" - LLM gave text response
                                           #   "max_steps" - hit step limit
                                           #   "validation_error" - tool call invalid
                                           #   "approval_denied" - user rejected dangerous tool
                "log": list[dict]          # Full step log from logger
            }

        Loop logic:
            1. Build messages list starting with user input
            2. For each step (up to max_steps):
               a. Send messages to LLM client → llm_client.chat(messages)
               b. Log the LLM response
               c. If LLM returns "text" type → that's the final answer, stop
               d. If LLM returns "tool_call" type:
                  i.   Validate using validator.validate_tool_call(...)
                  ii.  Log validation result
                  iii. If invalid → stop with "validation_error"
                  iv.  If requires_approval → auto-approve for now (just log it)
                  v.   Execute the tool via registry.execute_tool(...)
                  vi.  Log the tool result
                  vii. Add tool result to messages and continue loop
            3. If loop exits without final answer → return "max_steps" stop reason
        """
        # TODO: Implement the agentic loop. Methods you will need to call:
        #   - self._llm.chat(messages)                          -> the LLM's next response (a dict)
        #   - self._validator.validate_tool_call(response)      -> {"valid", "error", "requires_approval"}
        #   - self._registry.execute_tool(tool_name, arguments) -> the tool's result (a dict)
        #   - self._logger.log_step(step, action, detail)       -> record one step
        #   - self._logger.get_log()                            -> the full log (for the return value)
        #
        # For each step (up to self._max_steps):
        #   1. Call self._llm.chat(messages) to get the next response, then record
        #      it with self._logger.log_step(step, "llm_response", response).
        #   2. If the response type is "text": it is the final answer — log it and
        #      return with stop_reason "final_answer".
        #   3. If the response type is "tool_call": read its "tool_name" and
        #      "arguments", then:
        #        a. Call self._validator.validate_tool_call(response) and log the result.
        #        b. If it is not valid, return with stop_reason "validation_error".
        #        c. Otherwise call self._registry.execute_tool(tool_name, arguments),
        #           log the result, and append it to messages as a
        #           {"role": "tool_result", ...} entry.
        # If no final answer is produced within self._max_steps, return with
        # stop_reason "max_steps".
        #
        # Return a dict with: "final_answer", "steps_taken", "stop_reason", and
        # "log" (from self._logger.get_log()).
        pass

