"""
Planner agent.

Job: take the user's big question and split it into a few smaller,
clearer sub-questions. It does NOT answer anything itself -- that's the
Researcher's job. Keeping each agent's job narrow is what makes the whole
system easier to reason about.
"""

from pydantic import BaseModel, Field

from ..llm_provider import get_chat_model


class PlannerOutput(BaseModel):
    sub_questions: list[str] = Field(
        description="3 to 4 focused sub-questions that together fully cover the user's original question"
    )


# .with_structured_output() does, automatically, exactly what we built by
# hand in Phase 1: it forces the model to respond by calling a tool whose
# shape matches our Pydantic model, then validates the result for us.
_planner_llm = get_chat_model().with_structured_output(PlannerOutput)

PLANNER_PROMPT = (
    "You are a research planner. Break the user's question into 3-4 clear, "
    "focused sub-questions that together cover everything needed to answer "
    "it well. Do not answer the question yourself -- only break it down."
)


def planner_node(state):
    result = _planner_llm.invoke(
        [
            ("system", PLANNER_PROMPT),
            ("human", state["query"]),
        ]
    )
    return {"sub_questions": result.sub_questions}
