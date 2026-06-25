"""
This is the one place that decides which LLM brain the Planner, Writer,
and Critic use. Change ONE setting (LLM_PROVIDER in your .env file) and
all three switch over automatically -- no code changes needed elsewhere.

The Researcher agent does NOT use this -- it always talks to Claude
directly, because its web search only works on Anthropic's API.

How to use:
    LLM_PROVIDER=anthropic   (default) -> uses Claude
    LLM_PROVIDER=openai      -> uses OpenAI (needs OPENAI_API_KEY in .env)

Want to add Gemini or another provider later? Add one more "if" block
below -- everything else in the project stays the same.
"""

import os


def get_chat_model():
    provider = os.environ.get("LLM_PROVIDER", "anthropic").lower()

    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic

        model_name = os.environ.get("LLM_MODEL", "claude-sonnet-4-6")
        return ChatAnthropic(model=model_name)

    if provider == "openai":
        from langchain_openai import ChatOpenAI

        model_name = os.environ.get("LLM_MODEL", "gpt-4o")
        return ChatOpenAI(model=model_name)

    raise ValueError(
        f"Unknown LLM_PROVIDER '{provider}'. Use 'anthropic' or 'openai' "
        "(or add support for your provider in llm_provider.py)."
    )
