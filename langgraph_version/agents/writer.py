"""
Writer (Synthesizer) agent.

Job: take all the research findings and turn them into one clear report
that answers the original question. If the Critic sent back feedback,
this agent also sees that feedback and tries to fix the report.
"""

from pydantic import BaseModel, Field

from ..llm_provider import get_chat_model


class DraftReport(BaseModel):
    report: str = Field(
        description="A clear, well-organized report that answers the original "
        "question, written in plain prose using the research findings provided"
    )


_writer_llm = get_chat_model().with_structured_output(DraftReport)

WRITER_PROMPT = (
    "You are a report writer. Combine the research findings below into one "
    "clear, well-organized report that fully answers the original question. "
    "If revision feedback is provided, address it directly."
)


def writer_node(state):
    findings_text = "\n\n".join(state["findings"])
    feedback = state.get("critic_feedback", "")

    user_message = (
        f"Original question: {state['query']}\n\n"
        f"Research findings:\n{findings_text}"
    )
    if feedback:
        user_message += f"\n\nRevision feedback from the previous review (address this):\n{feedback}"

    result = _writer_llm.invoke(
        [
            ("system", WRITER_PROMPT),
            ("human", user_message),
        ]
    )
    return {"draft_report": result.report}
