"""
Smoke tests that just check both pipelines wire together correctly --
they don't call any real AI model (compiling a graph doesn't invoke
anything; it just checks the boxes and arrows make sense).

Run with: pytest
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from langgraph_version.graph import build_graph
from langgraph_version.resume_match.graph import build_resume_match_graph


def test_research_assistant_graph_has_expected_nodes():
    app = build_graph()
    nodes = set(app.get_graph().nodes.keys())
    expected = {
        "__start__",
        "planner",
        "human_review",
        "researcher",
        "writer",
        "critic",
        "__end__",
    }
    assert expected.issubset(nodes)


def test_resume_match_graph_has_expected_nodes():
    app = build_resume_match_graph()
    nodes = set(app.get_graph().nodes.keys())
    expected = {"__start__", "extractor", "matcher", "feedback_writer", "__end__"}
    assert expected.issubset(nodes)
