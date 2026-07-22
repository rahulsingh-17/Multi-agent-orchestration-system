# Multi-Agent Orchestration System

A system where several specialized AI agents work together — each with
one clear job — coordinated by an orchestration layer, instead of one
prompt trying to do everything at once.

It includes **two independent pipelines** built on the same engine, to
show the architecture generalizes beyond a single use case:

1. **Research Assistant** — Planner → human approval → Researcher →
   Writer → Critic, with a revise loop
2. **Resume-to-Job-Matcher** — Extractor → Matcher → Feedback Writer

## What this project demonstrates

- **Multi-agent coordination** — task decomposition (Planner), delegated
  execution (Researcher), synthesis (Writer), and quality control (Critic)
- **Human-in-the-loop** — the graph genuinely pauses mid-run and waits for
  a real decision before continuing, using LangGraph's `interrupt()` /
  `Command(resume=...)` pattern
- **Reliable structured output** — agents respond via a forced tool call
  matching a Pydantic schema, not by asking the model to "output JSON" and
  hoping the formatting holds up
- **Swappable LLM backends** — Planner/Writer/Critic/Extractor/Matcher can
  run on Claude or OpenAI via one config value, with no code changes
- **Observability** — every run streams a step-by-step trace (which agent
  ran, how long it took, what it returned) to `trace_log.json`
- **Tested** — routing logic, human-review parsing, and graph wiring are
  covered by fast tests that make zero real API calls
- **Built from scratch first, then on LangGraph** — `engine/` is a small
  hand-built single-agent runtime (forced tool-call structured output,
  dependency-injected LLM client) used to learn the fundamentals before
  building the full system in LangGraph

## Architecture

```
                     +-------------------------------+
                     |      Orchestration layer       |
                     |          (LangGraph)           |
                     +---------------+-----------------+
                                     |
              +----------------------+----------------------+
              |                                              |
   Research Assistant pipeline               Resume-to-Job-Match pipeline
              |                                              |
  Planner -> Human review -> Researcher       Extractor -> Matcher
       -> Writer -> Critic --+                     -> Feedback Writer
              ^              | not approved
              +--------------+ (max 2 tries)
```

## Project layout

```
engine/                  Phase 1: hand-built single-agent runtime
  agent.py, llm_client.py
examples/, tests/         Phase 1 demo + unit tests

langgraph_version/        The main system
  llm_provider.py          swappable LLM backend (Claude / OpenAI)
  tracing.py               step-by-step trace logging
  state.py, graph.py, main.py          Research Assistant pipeline
  agents/                  planner, human_review, researcher, writer, critic
  resume_match/            Resume-to-Job-Match pipeline (own state/graph/main)
    agents/                extractor, matcher, feedback_writer

tests/                     Tests covering both pipelines (no real API calls)
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env           # then add your real ANTHROPIC_API_KEY
```

## Run it

```bash
python langgraph_version/main.py                  # Research Assistant
python langgraph_version/resume_match/main.py      # Resume-to-Job-Matcher
pytest                                              # run the tests
```

Full details (including what each setting does and how to add new
agents) are in `langgraph_version/README.md`.
