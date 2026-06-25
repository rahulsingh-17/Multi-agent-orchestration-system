# LangGraph Version (current focus)

This folder now has **two separate agent pipelines**, built on the same
LangGraph engine and the same swappable-LLM setup:

1. **Research assistant** (`main.py`) — answers a research question
2. **Resume-to-Job-Match** (`resume_match/main.py`) — compares a resume
   against a job description and gives feedback

## 1. Research assistant

```
Your question
     |
     v
  Planner  (breaks it into sub-questions)
     |
     v
 Human review  <-- PROGRAM PAUSES HERE, waits for you to approve/edit
     |
     v
 Researcher  (searches the web for each sub-question)
     |
     v
  Writer  (writes the report)
     |
     v
  Critic  (checks it) --not good enough--> back to Writer (max 2 tries)
     |
   good enough
     |
     v
 Final report
```

Run it:
```bash
python langgraph_version/main.py
```
It'll ask for your question, show you the Planner's sub-questions and
**wait** — type `approve` to continue, or type your own comma-separated
list of sub-questions to use instead.

## 2. Resume-to-Job-Match

```
Resume text + Job description text
            |
            v
       Extractor  (pulls out skills, experience, requirements)
            |
            v
        Matcher  (scores the fit, lists matched/missing skills)
            |
            v
   Feedback Writer  (gives you practical advice)
            |
            v
       Final result
```

Run it:
```bash
python langgraph_version/resume_match/main.py
```
It'll ask you to paste your resume text, then the job description text
(type `END` on its own line when you're done pasting each one).

## Switching the LLM (Planner / Writer / Critic / Extractor / Matcher / Feedback Writer)

These agents read structured text and don't need web search, so they can
run on Claude, OpenAI, or others. Set this in your `.env` file:

```
LLM_PROVIDER=anthropic      # or: openai
LLM_MODEL=claude-sonnet-4-6 # or: gpt-4o, etc.
```

The **Researcher** agent in the research assistant always uses Claude
directly — it needs Claude's built-in web search, which only Anthropic's
API has.

## Files

```
langgraph_version/
  llm_provider.py        # picks which LLM the text-only agents use
  state.py / graph.py / main.py        # research assistant
  agents/
    planner.py, human_review.py, researcher.py, writer.py, critic.py
  resume_match/                         # second pipeline
    state.py / graph.py / main.py
    agents/
      extractor.py, matcher.py, feedback_writer.py
```

## Setup (same for both pipelines)

1. ```bash
   python -m venv .venv
   source .venv/bin/activate      # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. ```bash
   cp .env.example .env
   ```
   Open `.env` and add your real Anthropic API key. If you want to try
   OpenAI for the text-only agents, also set `OPENAI_API_KEY` and change
   `LLM_PROVIDER=openai`.

## If something goes wrong

- **"No Anthropic API key found"** → check your `.env` file has the
  right key in it.
- **Import errors** → make sure `pip install -r requirements.txt` ran
  inside the same virtual environment you're running scripts with.
- **Program seems stuck after showing sub-questions** → that's normal! It's
  the human-review pause — type `approve` (or your edit) and press Enter.
- Anything else → paste the exact error message and we'll fix it together.

## Seeing what each agent actually did (logging)

Both `main.py` files now print a line every time an agent finishes, like:

```
  -> [planner] finished in 2.1s
  -> [researcher] finished in 8.4s
```

And once the run finishes, a full step-by-step trace gets saved to
`trace_log.json` (sitting next to whichever `main.py` you ran). Open that
file and you'll see, for every step: which agent ran, how long it took,
and exactly what it returned. This is the file to screen-record or show
in an interview — it proves what each agent actually did, not just the
final answer.

## Running the tests

```bash
pytest
```

These tests check the *logic* (routing decisions, how the human-review
step parses your input, whether both graphs wire together correctly) —
none of them call the real AI model, so they run instantly and don't cost
anything. They won't catch every possible bug, but they will catch you
accidentally breaking the wiring while adding new agents later.

## How to add a new agent later

1. New file in the right `agents/` folder, with a function like the
   others: `def my_agent_node(state): ...`
2. In that pipeline's `graph.py`: `graph.add_node("my_agent", my_agent_node)`
   and connect it with `add_edge` (or `add_conditional_edges` if it needs
   to make a decision) wherever you want it to run.
3. If it needs extra data, add a field for it in that pipeline's `state.py`.
