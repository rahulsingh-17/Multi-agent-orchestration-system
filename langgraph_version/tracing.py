"""
A small helper that turns "run the graph and only see the final answer"
into "see each agent finish, one by one, with how long it took."

How it works, in plain words: instead of asking LangGraph to run
everything and hand back just the end result (what .invoke() does), we
ask it to run one step at a time and tell us after each one (that's what
.stream(..., stream_mode="updates") does). We just print and save what it
tells us. No changes needed inside any agent file -- this works because
LangGraph already knows exactly which agent just ran and what it returned.
"""

import time
from typing import Any


def run_graph_with_trace(app, graph_input, config, trace: list, state: dict):
    """
    Run the graph until it either pauses for human review or finishes.

    - `trace` is a list you provide; one entry gets appended per agent step.
    - `state` is a dict you provide; it gets updated in place with each
      agent's output, so by the end it holds the full, final state.

    Returns:
        ("interrupt", payload)  if the graph paused -- payload is whatever
                                 the human_review step is asking
        ("done", state)         if the graph finished
    """
    step_start = time.monotonic()

    for update in app.stream(graph_input, config=config, stream_mode="updates"):
        step_duration = round(time.monotonic() - step_start, 2)
        step_start = time.monotonic()

        if "__interrupt__" in update:
            return "interrupt", update["__interrupt__"][0].value

        for node_name, node_output in update.items():
            state.update(node_output)
            trace.append(
                {
                    "node": node_name,
                    "duration_seconds": step_duration,
                    "output": node_output,
                }
            )
            print(f"  -> [{node_name}] finished in {step_duration}s")

    return "done", state
