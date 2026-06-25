"""
Phase 1 demo: a single agent, no orchestration yet.

This proves the core Agent abstraction works end-to-end against the real
Claude API before we add any multi-agent coordination on top of it.

Run with:
    python examples/phase1_single_agent.py

Requires ANTHROPIC_API_KEY set in your environment, or in a .env file at
the project root (copy .env.example to .env and fill in your key).
"""

import sys
from pathlib import Path

# Make the project root importable regardless of where this script is run from.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pydantic import BaseModel, Field

from engine.agent import Agent


class SummaryResult(BaseModel):
    summary: str = Field(description="A concise 2-3 sentence summary of the text")
    key_points: list[str] = Field(description="3-5 short bullet-point takeaways")


SAMPLE_TEXT = """
Multi-agent systems coordinate several specialized AI agents -- each with
a narrow role -- to solve tasks that a single general-purpose prompt
struggles with. Instead of one model trying to plan, research, write, and
critique all at once, each step is delegated to an agent built for that
job, and an orchestrator decides what runs next, in what order, and what
each agent is allowed to see.
"""


def main():
    summarizer = Agent(
        name="summarizer",
        role="summarization",
        system_prompt=(
            "You are a precise technical summarizer. Read the provided text "
            "and produce a short summary and a handful of key takeaways. "
            "Be concise -- no filler."
        ),
        output_schema=SummaryResult,
    )

    result = summarizer.run(f"Summarize this text:\n\n{SAMPLE_TEXT}")

    print("Summary:\n", result.summary)
    print("\nKey points:")
    for point in result.key_points:
        print(" -", point)


if __name__ == "__main__":
    main()
