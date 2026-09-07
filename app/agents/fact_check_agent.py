from __future__ import annotations

import logging
from typing import Literal

from pydantic import BaseModel, Field

from app.agents.state import WorkflowState
from app.services.gemini_client import GeminiClient


logger = logging.getLogger(__name__)


FactCheckStatus = Literal[
    "supported",
    "unsupported",
    "uncertain",
]


class FactCheckClaim(BaseModel):
    """A single factual claim extracted from a script."""

    claim: str = Field(min_length=1)
    status: FactCheckStatus
    reason: str = Field(min_length=1)


class FactCheckResponse(BaseModel):
    """Structured response returned by the fact-checking model."""

    claims: list[FactCheckClaim]


def fact_check_agent(state: WorkflowState) -> WorkflowState:
    """Extract and assess factual claims from the generated script."""

    topic = state.get("topic", "").strip()
    script = state.get("script", "").strip()

    if not topic:
        logger.error("Fact-check agent received an empty topic.")

        return {
            **state,
            "claims": [],
            "qa_pass": False,
            "qa_errors": [
                "Topic is required for fact-checking."
            ],
        }

    if not script:
        logger.error("Fact-check agent received an empty script.")

        return {
            **state,
            "claims": [],
            "qa_pass": False,
            "qa_errors": [
                "Script is required for fact-checking."
            ],
        }

    prompt = f"""
You are the fact-checking agent for an autonomous YouTube content engine.

Your job is to identify factual claims in the script and assess their
certainty.

Topic:
{topic}

Script:
{script}

For every factual claim, classify it as exactly one of:

- supported
- unsupported
- uncertain

Classification rules:

1. supported
   Use this only when the claim is a generally established fact that can
   be confidently recognized from reliable knowledge.

2. unsupported
   Use this when the claim appears to be false, fabricated, or contradicted
   by established knowledge.

3. uncertain
   Use this when there is not enough reliable information to confidently
   establish whether the claim is true.

Additional rules:

- Do not invent evidence.
- Do not invent sources.
- Do not invent statistics.
- Do not invent quotations.
- Opinions are not factual claims.
- Rhetorical questions are not factual claims.
- Creative language is not a factual claim.
- Keep each claim concise.
- Provide a short explanation for every classification.
- Do not rewrite the script.
- Extract only meaningful factual claims.

Return only the structured response requested by the schema.
""".strip()

    logger.info(
        "Fact-check agent analyzing script | topic=%s",
        topic,
    )

    try:
        client = GeminiClient()

        structured_response = client.generate_structured(
            prompt,
            FactCheckResponse,
        )

        claims = [
            {
                "claim": claim.claim.strip(),
                "status": claim.status,
                "reason": claim.reason.strip(),
            }
            for claim in structured_response.claims
        ]

        unsupported_claims = [
            claim
            for claim in claims
            if claim["status"] == "unsupported"
        ]

        uncertain_claims = [
            claim
            for claim in claims
            if claim["status"] == "uncertain"
        ]

        qa_errors = [
            f"Unsupported factual claim: {claim['claim']}"
            for claim in unsupported_claims
        ]

        qa_errors.extend(
            f"Uncertain factual claim: {claim['claim']}"
            for claim in uncertain_claims
        )

        qa_pass = not unsupported_claims and not uncertain_claims

        logger.info(
            "Fact-check completed | claims=%d | unsupported=%d | "
            "uncertain=%d | qa_pass=%s",
            len(claims),
            len(unsupported_claims),
            len(uncertain_claims),
            qa_pass,
        )

        return {
            **state,
            "claims": claims,
            "qa_pass": qa_pass,
            "qa_errors": qa_errors,
        }

    except Exception:
        logger.exception(
            "Fact-check agent failed | topic=%s",
            topic,
        )

        return {
            **state,
            "claims": [],
            "qa_pass": False,
            "qa_errors": [
                "Fact-check agent failed."
            ],
        }