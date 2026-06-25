"""
Extractor agent.

Job: read the resume and the job description, and pull out the important
facts in a structured way -- the candidate's skills and experience, and
what the job actually requires. It does NOT judge fit yet -- that's the
Matcher's job, right after this.
"""

from pydantic import BaseModel, Field

from ...llm_provider import get_chat_model


class ExtractedInfo(BaseModel):
    candidate_skills: list[str] = Field(
        description="Specific skills, tools, and technologies found in the resume"
    )
    candidate_experience_summary: str = Field(
        description="2-3 sentence summary of the candidate's relevant experience"
    )
    job_title: str = Field(description="The job title from the job description")
    job_requirements: list[str] = Field(
        description="Specific required skills, tools, or qualifications from the job description"
    )


_extractor_llm = get_chat_model().with_structured_output(ExtractedInfo)

EXTRACTOR_PROMPT = (
    "You read a resume and a job description and pull out specific, "
    "factual details only. Do not judge fit -- just extract what's "
    "actually written in each document."
)


def extractor_node(state):
    user_message = (
        f"RESUME:\n{state['resume_text']}\n\n"
        f"JOB DESCRIPTION:\n{state['job_description_text']}"
    )
    result = _extractor_llm.invoke(
        [
            ("system", EXTRACTOR_PROMPT),
            ("human", user_message),
        ]
    )
    return {
        "candidate_skills": result.candidate_skills,
        "candidate_experience_summary": result.candidate_experience_summary,
        "job_title": result.job_title,
        "job_requirements": result.job_requirements,
    }
