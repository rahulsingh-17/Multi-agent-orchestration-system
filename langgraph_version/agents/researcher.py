"""
Researcher agent.

Job: for each sub-question, actually search the web and write a short
answer based on what it finds.

Note: this uses Claude's built-in web search tool directly (the raw
Anthropic SDK), not the LangChain wrapper used elsewhere -- because the
web search tool runs on Anthropic's servers and we just want its final
written answer back, no need for the structured-output trick here.

For now this goes through the sub-questions one at a time. Running them
truly in parallel is a nice upgrade for later (LangGraph supports this
with something called "Send"), but one-at-a-time is simpler to follow
while you're still learning the pieces.
"""

import os

import anthropic

MODEL_NAME = "claude-sonnet-4-6"

_client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

RESEARCHER_SYSTEM_PROMPT = (
    "You are a careful researcher. Use the web_search tool to find current, "
    "reliable information that answers the question. Then write a clear "
    "answer in 3-5 sentences based on what you found."
)


def _research_one(question: str) -> str:
    try:
        response = _client.messages.create(
            model=MODEL_NAME,
            max_tokens=1024,
            system=RESEARCHER_SYSTEM_PROMPT,
            tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 3}],
            messages=[{"role": "user", "content": question}],
        )
        # The response can contain several kinds of content blocks (search
        # calls, search results, text). We only want the final written text.
        text_parts = [block.text for block in response.content if block.type == "text"]
        answer = "\n".join(text_parts).strip()
        return answer if answer else "No clear answer was found for this sub-question."
    except Exception as error:
        # If one sub-question fails (rate limit, network blip, etc.), we
        # don't want that to take down the whole pipeline -- the Writer
        # will just have a gap noted here instead of a full answer.
        return f"(Could not research this sub-question due to an error: {error})"


def researcher_node(state):
    findings = []
    for question in state["sub_questions"]:
        answer = _research_one(question)
        findings.append(f"Q: {question}\nA: {answer}")
    return {"findings": findings}
