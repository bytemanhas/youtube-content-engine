from __future__ import annotations

import logging

from app.agents.state import WorkflowState
from app.services.gemini_client import GeminiClient


logger = logging.getLogger(__name__)


def script_agent(state: WorkflowState) -> WorkflowState:
    """Generate a YouTube script from the research stage."""

    topic = state.get("topic", "").strip()
    content_type = state.get("content_type", "short").strip().lower()
    research_notes = state.get("research_notes", [])

    if not topic:
        logger.error("Script agent received an empty topic.")
        return {
            **state,
            "script": "",
            "qa_pass": False,
            "qa_errors": ["Topic is required to generate a script."],
        }

    if not research_notes:
        logger.error("Script agent received no research notes.")
        return {
            **state,
            "script": "",
            "qa_pass": False,
            "qa_errors": ["Research notes are required to generate a script."],
        }

    research_text = "\n".join(
        f"- {note}"
        for note in research_notes
        if note.strip()
    )

    if content_type == "long_form":
        format_instructions = """
Create a long-form YouTube script.

Structure:
1. Strong opening hook
2. Introduction
3. Main sections with logical progression
4. Examples and explanations
5. Key takeaway
6. Natural conclusion and call to action

Target approximately 8-12 minutes of spoken content.
"""
    else:
        format_instructions = """
Create a YouTube Shorts script.

Structure:
1. Immediate hook in the first sentence
2. Fast-paced explanation
3. One memorable insight or payoff
4. Short natural call to action

Target approximately 30-60 seconds of spoken content.
Avoid unnecessary introductions and filler.
"""

    prompt = f"""
You are the Script Agent for an autonomous YouTube content engine.

Topic:
{topic}

Content type:
{content_type}

Research notes:
{research_text}

{format_instructions}

Writing requirements:
- Write for spoken delivery, not an academic article.
- Make every sentence useful.
- Keep the pacing engaging.
- Do not invent facts, statistics, quotes, studies, or sources.
- Do not make unsupported claims.
- Use simple, natural language.
- Do not include camera directions.
- Do not include scene descriptions.
- Return only the final spoken script.
""".strip()

    logger.info(
        "Script agent generating script | topic=%s | content_type=%s",
        topic,
        content_type,
    )

    try:
        client = GeminiClient()
        script = client.generate_text(prompt)

        if not script.strip():
            raise RuntimeError("Gemini returned an empty script.")

        logger.info(
            "Script generation completed | topic=%s | characters=%d",
            topic,
            len(script),
        )

        return {
            **state,
            "script": script.strip(),
            "qa_pass": False,
            "qa_errors": [],
        }

    except Exception:
        logger.exception(
            "Script generation failed | topic=%s",
            topic,
        )

        return {
            **state,
            "script": "",
            "qa_pass": False,
            "qa_errors": ["Script generation failed."],
        }