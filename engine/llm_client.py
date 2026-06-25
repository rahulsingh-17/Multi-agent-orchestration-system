"""
Thin wrapper around the Anthropic API.

Keeping this as its own class -- rather than calling the SDK directly
inside Agent -- means we can swap in a fake/mock client during tests
without touching any agent logic. This is dependency injection, and it's
the reason the orchestration engine will be unit-testable later without
hitting the live API.
"""

import os
from typing import Any, Optional

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()


class LLMClient:
    """Wraps the Anthropic Messages API behind a small, swappable interface."""

    DEFAULT_MODEL = "claude-sonnet-4-6"

    def __init__(self, api_key: Optional[str] = None):
        resolved_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not resolved_key:
            raise ValueError(
                "No Anthropic API key found. Set ANTHROPIC_API_KEY in your "
                "environment or a .env file, or pass api_key= explicitly."
            )
        self.client = Anthropic(api_key=resolved_key)

    def call(
        self,
        system_prompt: str,
        messages: list[dict[str, Any]],
        tools: Optional[list[dict[str, Any]]] = None,
        tool_choice: Optional[dict[str, Any]] = None,
        model: Optional[str] = None,
        max_tokens: int = 1024,
    ):
        """Make a single call to the Claude Messages API and return the raw response."""
        kwargs: dict[str, Any] = {
            "model": model or self.DEFAULT_MODEL,
            "max_tokens": max_tokens,
            "system": system_prompt,
            "messages": messages,
        }
        if tools:
            kwargs["tools"] = tools
        if tool_choice:
            kwargs["tool_choice"] = tool_choice

        return self.client.messages.create(**kwargs)
