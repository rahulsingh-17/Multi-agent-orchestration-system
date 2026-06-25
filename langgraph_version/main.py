"""
Run this file to try the whole system on one question.

    python langgraph_version/main.py

Needs ANTHROPIC_API_KEY set in your environment or in a .env file at the
project root (copy .env.example to .env and fill in your key). If you set
LLM_PROVIDER=openai in .env, also set OPENAI_API_KEY.

While it runs, you'll see each agent print a line as it finishes. At the
end, a full step-by-step trace is also saved to trace_log.json so you can
look back at exactly what each agent did.
"""

import json
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

load_dotenv()

from langgraph.types import Command

from langgraph_version.graph import build_graph
from langgraph_version.tracing import run_graph_with_trace

SAMPLE_QUESTION = "What is the impact of climate change on coffee farming?"


def handle_human_review(payload):
    """Show the planner's sub-questions and ask the user what to do."""
    print("\n--- The Planner suggests researching these sub-questions ---")
    for i, question in enumerate(payload["sub_questions"], 1):
        print(f"{i}. {question}")
    print(f"\n{payload['instructions']}")
    return input("> ").strip()


def main():
    app = build_graph()

    # Every run needs a unique "thread_id" -- it's how LangGraph remembers
    # which paused conversation to resume when we send back your answer.
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}

    user_input = input(
        "Type your research question (or press Enter to use the sample question):\n> "
    ).strip()
    query = user_input if user_input else SAMPLE_QUESTION
    print(f"\nResearching: {query}\n")

    initial_state = {
        "query": query,
        "sub_questions": [],
        "findings": [],
        "draft_report": "",
        "critic_feedback": "",
        "approved": False,
        "revision_count": 0,
    }

    trace = []
    state = dict(initial_state)

    status, payload = run_graph_with_trace(app, initial_state, config, trace, state)

    # While the graph is paused waiting on a human, keep asking and resuming.
    while status == "interrupt":
        decision = handle_human_review(payload)
        status, payload = run_graph_with_trace(
            app, Command(resume=decision), config, trace, state
        )

    print("\n" + "=" * 60)
    print("FINAL REPORT")
    print("=" * 60)
    print(state["draft_report"])
    print()
    print(f"(approved: {state['approved']}, revisions used: {state['revision_count']})")

    trace_path = Path(__file__).resolve().parent / "trace_log.json"
    trace_path.write_text(json.dumps(trace, indent=2, default=str))
    print(f"\nFull step-by-step trace saved to: {trace_path}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nStopped.")
    except Exception as error:
        print("\n" + "=" * 60)
        print("Something went wrong while running the pipeline.")
        print(f"Error: {error}")
        print("=" * 60)
        print(
            "Common causes: missing/invalid API key in .env, no internet "
            "connection, or a temporary issue with the AI provider. "
            "Check your .env file and try again."
        )
