"""
Shared setup for all tests in this folder.

The agent files (planner.py, writer.py, critic.py, etc.) create an LLM
client as soon as they're imported. That client just needs SOME key to
exist to be created -- it doesn't check if the key is real until you
actually make a call. Since none of our tests make real calls, we set a
fake key here so importing those files doesn't crash during testing.
"""

import os

os.environ.setdefault("ANTHROPIC_API_KEY", "sk-ant-test-dummy-key")
