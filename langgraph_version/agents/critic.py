"""
Critic agent.

Job: read the draft report and decide if it's actually good. If yes,
approve it and we're done. If no, write specific feedback and send it
back to the Writer to try again.

This agent's "approved" field is what the graph uses to decide what to
do next -- that's why it needs structured output (a plain text answer
wouldn't let our code make a yes/no decision reliably).
"""

from pydantic import BaseModel, Field

from ..llm_provider import get_chat_model


class CriticReview(BaseModel):
    approved: bool = Field(
        description="True only if the report is clear, accurate, and fully answers the original question"
    )
    feedback: str = Field(
        description="If not approved, specific actionable feedback for the writer. Empty string if approved."
    )


_critic_llm = get_chat_model().with_structured_output(CriticReview)

CRITIC_PROMPT = (
    "You are a strict editor reviewing a research report. Check it against "
    "the original question: is it accurate, complete, and clearly written? "
    "Approve only if it's genuinely good. Otherwise give specific feedback "
    "on what to fix."
)


def critic_node(state):
    user_message = (
        f"Original question: {state['query']}\n\n"
        f"Draft report:\n{state['draft_report']}"
    )
    result = _critic_llm.invoke(
        [
            ("system", CRITIC_PROMPT),
            ("human", user_message),
        ]
    )

    revision_count = state.get("revision_count", 0)
    if not result.approved:
        revision_count += 1

    return {
        "approved": result.approved,
        "critic_feedback": result.feedback,
        "revision_count": revision_count,
    }
