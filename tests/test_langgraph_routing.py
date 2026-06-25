"""
Tests for the routing logic in the research assistant graph -- the part
that decides what happens after the Critic checks the report. This is
plain Python logic with no AI calls in it, so these tests are instant
and free to run.

Run with: pytest
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from langgraph_version.graph import route_after_critic, MAX_REVISIONS


def test_routes_to_end_when_approved():
    state = {"approved": True, "revision_count": 0}
    assert route_after_critic(state) == "end"


def test_routes_to_revise_when_not_approved_and_tries_left():
    state = {"approved": False, "revision_count": 0}
    assert route_after_critic(state) == "revise"


def test_routes_to_end_when_out_of_revisions_even_if_not_approved():
    state = {"approved": False, "revision_count": MAX_REVISIONS}
    assert route_after_critic(state) == "end"
