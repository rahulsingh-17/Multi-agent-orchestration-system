"""
Flow for the Resume-to-Job-Match pipeline:

    START -> extractor -> matcher -> feedback_writer -> END

Simple and linear on purpose -- no loops or human pauses needed here,
since there's nothing partway through that needs approval. Just one
straight pipeline from raw text to useful feedback.
"""

from langgraph.graph import StateGraph, START, END

from .state import ResumeMatchState
from .agents.extractor import extractor_node
from .agents.matcher import matcher_node
from .agents.feedback_writer import feedback_writer_node


def build_resume_match_graph():
    graph = StateGraph(ResumeMatchState)

    graph.add_node("extractor", extractor_node)
    graph.add_node("matcher", matcher_node)
    graph.add_node("feedback_writer", feedback_writer_node)

    graph.add_edge(START, "extractor")
    graph.add_edge("extractor", "matcher")
    graph.add_edge("matcher", "feedback_writer")
    graph.add_edge("feedback_writer", END)

    return graph.compile()
