"""
Unit test for Agent that never touches the real API.

Because LLMClient is injected rather than hardcoded inside Agent, we can
swap in a fake one here. This is what makes the orchestration engine
testable in CI -- a property worth mentioning if asked about it later.

Run with:
    pytest
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pydantic import BaseModel

from engine.agent import Agent


class DummyResult(BaseModel):
    answer: str


def test_agent_run_parses_tool_use_into_pydantic_model():
    fake_tool_use_block = MagicMock()
    fake_tool_use_block.type = "tool_use"
    fake_tool_use_block.input = {"answer": "42"}

    fake_response = MagicMock()
    fake_response.content = [fake_tool_use_block]

    fake_llm_client = MagicMock()
    fake_llm_client.call.return_value = fake_response

    agent = Agent(
        name="dummy",
        role="testing",
        system_prompt="irrelevant for this test",
        output_schema=DummyResult,
        llm_client=fake_llm_client,
    )

    result = agent.run("What is the answer?")

    assert isinstance(result, DummyResult)
    assert result.answer == "42"
    fake_llm_client.call.assert_called_once()
