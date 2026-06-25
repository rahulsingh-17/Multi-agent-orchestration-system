"""
This file draws the actual flowchart.

add_node(name, function)  -> "here's a box, and here's the code that runs in it"
add_edge(a, b)            -> "after box a finishes, always go to box b"
add_conditional_edges      -> "after this box, look at the result and DECIDE
                                which box to go to next"

Our flow:

    START -> planner -> human_review -> researcher -> writer -> critic
                              |                            ^         |
                       (you approve/edit                   |         |
                        the plan here)                     |  not approved
                                                             |   (and tries left)
                                                             +---------+
                                                                       |
                                                                approved (or out of tries)
                                                                       v
                                                                      END

human_review is a PAUSE POINT: the program stops there and waits for you
to type something in the terminal, then continues with whatever you typed.
This needs a "checkpointer" -- LangGraph's way of remembering exactly
where it paused, so it can pick back up correctly.

If you want to add a 5th agent later (say, a "fact_checker"), the steps
are: write a new file in agents/ with a `fact_checker_node(state)`
function (same pattern as the others), then add one `add_node(...)` line
and rewire the `add_edge` / `add_conditional_edges` calls below to include
it where you want it to run.
"""

from langgraph.graph import StateGraph, START, END

try:
    from langgraph.checkpoint.memory import InMemorySaver
except ImportError:  # older langgraph versions used this name instead
    from langgraph.checkpoint.memory import MemorySaver as InMemorySaver

from .state import ResearchState
from .agents.planner import planner_node
from .agents.human_review import human_review_node
from .agents.researcher import researcher_node
from .agents.writer import writer_node
from .agents.critic import critic_node

MAX_REVISIONS = 2  # safety cap so the writer/critic loop can't run forever


def route_after_critic(state):
    """Decide what happens after the Critic checks the report."""
    if state["approved"] or state["revision_count"] >= MAX_REVISIONS:
        return "end"
    return "revise"


def build_graph():
    graph = StateGraph(ResearchState)

    graph.add_node("planner", planner_node)
    graph.add_node("human_review", human_review_node)
    graph.add_node("researcher", researcher_node)
    graph.add_node("writer", writer_node)
    graph.add_node("critic", critic_node)

    graph.add_edge(START, "planner")
    graph.add_edge("planner", "human_review")
    graph.add_edge("human_review", "researcher")
    graph.add_edge("researcher", "writer")
    graph.add_edge("writer", "critic")
    graph.add_conditional_edges(
        "critic",
        route_after_critic,
        {"revise": "writer", "end": END},
    )

    checkpointer = InMemorySaver()
    return graph.compile(checkpointer=checkpointer)
