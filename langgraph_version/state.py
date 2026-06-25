"""
This is the "shared notebook" that every agent reads from and writes to.

Think of it like a folder being passed around a team: the Planner writes
the sub-questions into it, the Researcher adds their findings, the Writer
reads those findings and writes a draft, and the Critic reads the draft
and writes feedback. LangGraph handles passing this notebook from one
agent to the next -- we just say what's inside it.
"""

from typing import List, TypedDict


class ResearchState(TypedDict):
    query: str              # the original question from the user
    sub_questions: List[str]  # smaller questions the Planner breaks it into
    findings: List[str]       # what the Researcher(s) found for each sub-question
    draft_report: str         # the report the Writer produced
    critic_feedback: str      # feedback from the Critic, if the report needs work
    approved: bool            # True once the Critic is happy with the report
    revision_count: int       # how many times the Writer has tried so far
