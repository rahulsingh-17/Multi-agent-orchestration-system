"""
Core Agent abstraction.

An Agent is: a role (system prompt) + an expected output shape (a Pydantic
model) + an LLM client to talk to. It does NOT know about other agents,
orchestration, or control flow -- that's the graph executor's job, coming
in Phase 2. Keeping Agent "dumb" like this is deliberate: it's the unit
the orchestrator will later schedule, run in parallel, and route between.

Structured output is enforced via Claude's tool-use feature: we hand the
model exactly one tool whose input_schema mirrors our Pydantic model, and
force tool_choice so the model MUST respond by calling it. We then
validate the tool's input straight into the Pydantic model. This avoids
fragile "ask the model for JSON and regex it out of a code block" parsing.
"""

from typing import Any, Optional, Type

from pydantic import BaseModel

from .llm_client import LLMClient


class Agent:
    def __init__(
        self,
        name: str,
        role: str,
        system_prompt: str,
        output_schema: Type[BaseModel],
        model: Optional[str] = None,
        llm_client: Optional[LLMClient] = None,
    ):
        self.name = name
        self.role = role
        self.system_prompt = system_prompt
        self.output_schema = output_schema
        self.model = model
        self.llm_client = llm_client or LLMClient()

    def _build_tool_definition(self) -> dict[str, Any]:
        schema = self.output_schema.model_json_schema()
        schema.pop("title", None)  # Pydantic metadata Claude doesn't need
        return {
            "name": "submit_result",
            "description": (
                f"Submit the final structured result for the '{self.name}' agent. "
                "Call this exactly once with your complete answer."
            ),
            "input_schema": schema,
        }

    def run(self, task: str) -> BaseModel:
        """Run this agent on a single task and return a validated Pydantic object."""
        tool = self._build_tool_definition()

        response = self.llm_client.call(
            system_prompt=self.system_prompt,
            messages=[{"role": "user", "content": task}],
            tools=[tool],
            tool_choice={"type": "tool", "name": "submit_result"},
            model=self.model,
        )

        tool_use_block = next(
            block for block in response.content if block.type == "tool_use"
        )
        return self.output_schema.model_validate(tool_use_block.input)
