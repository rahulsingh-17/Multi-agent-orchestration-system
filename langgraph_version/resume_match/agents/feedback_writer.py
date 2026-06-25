"""
Feedback Writer agent.

Job: turn the match results into practical advice the candidate can
actually use -- what to highlight, what's missing, and how to improve
their chances for this specific job.
"""

from pydantic import BaseModel, Field

from ...llm_provider import get_chat_model


class FeedbackResult(BaseModel):
    feedback: str = Field(
        description="Clear, practical, encouraging advice for the candidate "
        "on how to improve their fit for this job, written directly to them"
    )


_feedback_llm = get_chat_model().with_structured_output(FeedbackResult)

FEEDBACK_PROMPT = (
    "You give candidates honest, encouraging, practical advice on how to "
    "improve their fit for a specific job, based on a skills match analysis."
)


def feedback_writer_node(state):
    user_message = (
        f"Job title: {state['job_title']}\n"
        f"Match score: {state['match_score']}/100\n"
        f"Matched skills: {', '.join(state['matched_skills'])}\n"
        f"Missing skills: {', '.join(state['missing_skills'])}"
    )
    result = _feedback_llm.invoke(
        [
            ("system", FEEDBACK_PROMPT),
            ("human", user_message),
        ]
    )
    return {"feedback": result.feedback}
