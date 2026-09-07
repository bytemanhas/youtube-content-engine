from __future__ import annotations

import logging

from app.agents.state import WorkflowState
from app.services.ai_provider import AIProvider
from app.services.ollama_provider import OllamaProvider


logger = logging.getLogger(__name__)


def research_agent(
    state: WorkflowState,
    provider: AIProvider | None = None,
) -> WorkflowState:
    """Research the supplied topic using the configured AI provider."""

    topic = state.get("topic", "").strip()

    if not topic:
        logger.error("Research agent received an empty topic.")
        return {
            **state,
            "research_notes": [],
        }

    logger.info("Research agent processing topic: %s", topic)

    prompt = f"""
You are the research agent for an autonomous YouTube content engine.

Research the following topic conceptually:

Topic: {topic}

Provide:
1. The key facts and concepts that should be understood.
2. Important context a YouTube script writer should know.
3. Potential claims that require fact-checking.
4. Interesting angles that could make the topic engaging.
5. Important limitations or uncertainties.

Do not invent statistics, quotes, studies, or sources.

Return the research as clear, concise bullet points.
""".strip()

    if provider is None:
        provider = OllamaProvider()

    try:
        research_text = provider.generate_text(prompt)

        research_notes = [
            line.strip("-• ").strip()
            for line in research_text.splitlines()
            if line.strip()
        ]

        if not research_notes:
            logger.warning(
                "Research provider returned no usable notes | topic=%s",
                topic,
            )
            return {
                **state,
                "research_notes": [],
            }

        logger.info(
            "Research agent completed successfully | topic=%s | notes=%d",
            topic,
            len(research_notes),
        )

        return {
            **state,
            "research_notes": research_notes,
        }

    except Exception:
        logger.exception(
            "Research agent failed | topic=%s",
            topic,
        )
        raise