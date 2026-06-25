"""
Matcher agent.

Job: compare what the candidate has against what the job needs, and give
a score plus a clear breakdown of what matches and what's missing.
"""

from pydantic import BaseModel, Field

from ...llm_provider import get_chat_model


class MatchResult(BaseModel):
    match_score: int = Field(
        description="A score from 0 to 100 for how well the candidate fits the job requirements"
    )
    matched_skills: list[str] = Field(
        description="Requirements the candidate's skills/experience already cover"
    )
    missing_skills: list[str] = Field(
        description="Requirements not clearly covered by the candidate's skills/experience"
    )


_matcher_llm = get_chat_model().with_structured_output(MatchResult)

MATCHER_PROMPT = (
    "You compare a candidate's skills and experience against a job's "
    "requirements. Be honest and specific -- don't inflate the score, "
    "and back up the score with the matched/missing lists."
)


def matcher_node(state):
    user_message = (
        f"Job title: {state['job_title']}\n"
        f"Job requirements: {', '.join(state['job_requirements'])}\n\n"
        f"Candidate skills: {', '.join(state['candidate_skills'])}\n"
        f"Candidate experience: {state['candidate_experience_summary']}"
    )
    result = _matcher_llm.invoke(
        [
            ("system", MATCHER_PROMPT),
            ("human", user_message),
        ]
    )
    return {
        "match_score": result.match_score,
        "matched_skills": result.matched_skills,
        "missing_skills": result.missing_skills,
    }
