"""LLMOps tracing hooks for Langfuse and Arize Phoenix."""

from typing import Any, Dict


class TracingClient:
    """Provides unified observability tracing for LangGraph agent executions."""

    def __init__(self, service_name: str = "ClauseIQ"):
        self.service_name = service_name

    def log_agent_step(self, agent_name: str, input_data: Dict[str, Any], output_data: Dict[str, Any]) -> None:
        """Record input, output, latency, and token cost for an agent step."""
        pass
