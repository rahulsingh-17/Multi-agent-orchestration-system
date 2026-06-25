"""
Tests for the human-review node's decision-parsing logic.

We can't trigger a real pause-and-wait here (that only happens inside a
running graph with a checkpointer) -- so instead we fake out the
interrupt() call to return a canned answer, and just check that the
parsing logic afterward does the right thing with it.

Run with: pytest
"""

import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from langgraph_version.agents.human_review import human_review_node


def test_approve_keeps_existing_sub_questions():
    state = {"sub_questions": ["a", "b", "c"]}
    with patch(
        "langgraph_version.agents.human_review.interrupt", return_value="approve"
    ):
        result = human_review_node(state)
    assert result == {}


def test_custom_list_replaces_sub_questions():
    state = {"sub_questions": ["a", "b", "c"]}
    with patch(
        "langgraph_version.agents.human_review.interrupt",
        return_value="x, y, z",
    ):
        result = human_review_node(state)
    assert result == {"sub_questions": ["x", "y", "z"]}


def test_blank_response_keeps_existing_sub_questions():
    state = {"sub_questions": ["a", "b", "c"]}
    with patch("langgraph_version.agents.human_review.interrupt", return_value="   "):
        result = human_review_node(state)
    assert result == {}
