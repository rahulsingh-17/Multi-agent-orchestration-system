# Multi-Agent Orchestration System

A system where several specialized AI agents work together — each with
one clear job — coordinated by an orchestration layer, instead of one
prompt trying to do everything at once.

It includes **two independent pipelines** built on the same engine, to
show the architecture generalizes beyond a single use case:

1. **Research Assistant** — Planner → human approval → Researcher →
   Writer → Critic, with a revise loop
2. **Resume-to-Job-Match** — Extractor → Matcher → Feedback Writer

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
python langgraph_version/resume_match/main.py      # Resume-to-Job-Match
pytest                                              # run the tests
```

Full details (including what each setting does and how to add new
agents) are in `langgraph_version/README.md`.

## How to talk about this project in an interview

A few likely questions, and the honest, short answer to each:

**"Walk me through the architecture."**
A shared state object flows through a graph of agent nodes. The Planner
breaks the task down, a human can review the plan before any real work
happens, the Researcher gathers information, the Writer drafts a result,
and the Critic checks it — looping back to the Writer up to twice if it's
not good enough, then finishing.

**"How do you keep agent outputs reliable?"**
Each agent that needs to make a decision or hand off data (not just
write prose) returns its answer by being forced to call a tool whose
shape matches a Pydantic schema. The result gets validated automatically
— no regex-parsing JSON out of a text response.

**"Why LangGraph instead of building everything yourself?"**
I built a single-agent runtime from scratch first (see `engine/`) to
understand the fundamentals: forced structured output, dependency
injection for testability. Then I used LangGraph for the full
multi-agent system because it already solves checkpointing, pausing/
resuming, and conditional branching well — rebuilding that myself would
have meant reinventing solved problems instead of focusing on the agent
design itself.

**"How do you know it actually works?"**
Tests cover the routing logic (when does the Critic send work back vs.
approve it), the human-review parsing, and that both graphs wire up
correctly — all without spending API calls. Beyond that, every real run
produces a `trace_log.json` showing exactly what each agent did and how
long it took, which is also useful for debugging.

**"What would you add next?"**
A neutral web-search tool (so the Researcher isn't tied to one
provider), a Code Reviewer agent (would need a sandboxed way to actually
run code), and a simple web UI instead of the terminal.
