"""
Run this file to try the Resume-to-Job-Match pipeline.

    python langgraph_version/resume_match/main.py

Needs the same .env setup as the research assistant (same project-root
.env file, same API key).

While it runs, you'll see each agent print a line as it finishes. At the
end, a full step-by-step trace is also saved to trace_log.json.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from dotenv import load_dotenv

load_dotenv()

from langgraph_version.resume_match.graph import build_resume_match_graph
from langgraph_version.tracing import run_graph_with_trace


def _read_multiline(prompt):
    print(prompt)
    print("(paste the text, then type END on its own line and press Enter)")
    lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        lines.append(line)
    return "\n".join(lines)


def main():
    app = build_resume_match_graph()

    resume_text = _read_multiline("\nPaste the RESUME text:")
    job_description_text = _read_multiline("\nPaste the JOB DESCRIPTION text:")

    if not resume_text.strip() or not job_description_text.strip():
        print(
            "\nBoth the resume and the job description need some text. "
            "Please run again and paste something in both."
        )
        return

    initial_state = {
        "resume_text": resume_text,
        "job_description_text": job_description_text,
        "candidate_skills": [],
        "candidate_experience_summary": "",
        "job_title": "",
        "job_requirements": [],
        "matched_skills": [],
        "missing_skills": [],
        "match_score": 0,
        "feedback": "",
    }

    trace = []
    state = dict(initial_state)
    config = {"configurable": {"thread_id": "resume-match-run"}}

    print()
    run_graph_with_trace(app, initial_state, config, trace, state)
    result = state

    print("\n" + "=" * 60)
    print(f"MATCH RESULT for: {result['job_title']}")
    print("=" * 60)
    print(f"Match score: {result['match_score']}/100\n")

    print("Matched skills:")
    for skill in result["matched_skills"]:
        print(f" - {skill}")

    print("\nMissing skills:")
    for skill in result["missing_skills"]:
        print(f" - {skill}")

    print("\nFeedback:")
    print(result["feedback"])

    trace_path = Path(__file__).resolve().parent / "trace_log.json"
    trace_path.write_text(json.dumps(trace, indent=2, default=str))
    print(f"\nFull step-by-step trace saved to: {trace_path}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nStopped.")
    except Exception as error:
        print("\n" + "=" * 60)
        print("Something went wrong while running the pipeline.")
        print(f"Error: {error}")
        print("=" * 60)
        print(
            "Common causes: missing/invalid API key in .env, no internet "
            "connection, or a temporary issue with the AI provider. "
            "Check your .env file and try again."
        )
