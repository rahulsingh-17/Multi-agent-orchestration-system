"""
The shared "notebook" passed between the 3 agents in this pipeline.
"""

from typing import List, TypedDict


class ResumeMatchState(TypedDict):
    resume_text: str                       # raw resume text you paste in
    job_description_text: str              # raw job description you paste in
    candidate_skills: List[str]            # skills the Extractor found in the resume
    candidate_experience_summary: str      # short summary of the candidate's experience
    job_title: str                         # job title the Extractor found
    job_requirements: List[str]            # requirements the Extractor found in the job post
    matched_skills: List[str]              # requirements the candidate already covers
    missing_skills: List[str]              # requirements the candidate doesn't clearly cover
    match_score: int                       # 0-100 fit score from the Matcher
    feedback: str                          # practical advice from the Feedback Writer
