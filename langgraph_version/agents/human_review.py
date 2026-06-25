"""
Human-in-the-loop checkpoint.

Job: after the Planner makes its sub-questions, STOP and show them to you
before any web searching happens. You can type "approve" to continue as-is,
or type your own comma-separated list to replace the plan.

This uses LangGraph's interrupt() function, which actually pauses the
whole program and waits -- it's not a fake pause, the code really stops
here until you respond (handled in main.py).
"""

from langgraph.types import interrupt


def human_review_node(state):
    decision = interrupt(
        {
            "sub_questions": state["sub_questions"],
            "instructions": (
                "Type 'approve' to continue with this plan, or type your own "
                "comma-separated list of sub-questions to replace it."
            ),
        }
    )

    if isinstance(decision, str) and decision.strip().lower() != "approve":
        new_questions = [q.strip() for q in decision.split(",") if q.strip()]
        if new_questions:
            return {"sub_questions": new_questions}

    return {}
