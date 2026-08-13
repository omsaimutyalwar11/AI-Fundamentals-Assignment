"""Step Logger — fully implemented, pre-built for you.

Logs each step of the agent loop for observability.
"""


class StepLogger:
    """Records and prints each step of the agentic loop."""

    def __init__(self):
        """Create an empty logger.

        Each recorded step is stored as a dict of shape:
            {"step_number": int, "action": str, "detail": dict}
        """
        self._steps: list[dict] = []

    def log_step(self, step_number: int, action: str, detail: dict) -> None:
        """Record a step and print it.

        Args:
            step_number: 1-based index of the loop iteration.
            action: The kind of step. One of "llm_response", "validation",
                "tool_call", "tool_result", "final_answer".
            detail: Payload for the step; its shape depends on `action`:
                "llm_response" -> the LLM response dict, either
                    {"type": "tool_call", "tool_name": str, "arguments": dict}
                    or {"type": "text", "content": str}
                "validation"   -> {"valid": bool, "error": str | None, "requires_approval": bool}
                "tool_call"    -> {"tool_name": str, "arguments": dict}
                "tool_result"  -> {"result": dict}
                "final_answer" -> {"content": str, "stop_reason": str}

        Returns:
            None. The record is appended to the internal log and printed.
        """
        record = {"step_number": step_number, "action": action, "detail": detail}
        self._steps.append(record)
        self.print_step(step_number, action, detail)

    def get_log(self) -> list[dict]:
        """Return all logged steps.

        Returns:
            A list (copy) of step records, each of shape:
                {"step_number": int, "action": str, "detail": dict}
        """
        return list(self._steps)

    def print_step(self, step_number: int, action: str, detail: dict) -> None:
        """Print a formatted step to the console.

        Args:
            step_number: 1-based index of the loop iteration.
            action: The step kind (see `log_step` for the full list).
            detail: The step payload (see `log_step` for the per-action shape).

        Returns:
            None.
        """
        prefix = f"[Step {step_number}]"

        if action == "llm_response":
            if detail.get("type") == "tool_call":
                print(f'{prefix} LLM suggests: call tool "{detail.get("tool_name", "?")}" with {detail.get("arguments", {})}')
            else:
                print(f'{prefix} LLM responds: "{detail.get("content", "")}"')
        elif action == "validation":
            if detail.get("valid"):
                extra = " [WARNING] requires approval" if detail.get("requires_approval") else ""
                print(f"{prefix} Validating: [OK] tool exists, [OK] required args present{extra}")
            else:
                print(f'{prefix} Validating: [FAIL] {detail.get("error", "unknown error")}')
        elif action == "tool_call":
            args_str = ", ".join(f'{k}="{v}"' for k, v in detail.get("arguments", {}).items())
            print(f'{prefix} Executing: {detail.get("tool_name", "?")}({args_str})')
        elif action == "tool_result":
            print(f'{prefix} Tool result: {detail.get("result", {})}')
        elif action == "final_answer":
            print(f'\n[DONE] ({step_number} steps, stop reason: {detail.get("stop_reason", "done")})')
            print(f'   Answer: {detail.get("content", "")}')
        else:
            print(f"{prefix} {action}: {detail}")
