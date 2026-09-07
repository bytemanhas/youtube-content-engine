from __future__ import annotations

import logging
from typing import TypeVar

from google import genai
from pydantic import BaseModel

from app.config import get_settings


logger = logging.getLogger(__name__)

ResponseModelT = TypeVar("ResponseModelT", bound=BaseModel)


class GeminiClient:
    """Application-level client for Google Gemini."""

    def __init__(self) -> None:
        settings = get_settings()

        if not settings.gemini_api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured."
            )

        self._client = genai.Client(
            api_key=settings.gemini_api_key,
            http_options={
                "timeout": 90_000,
            },
        )

        logger.info(
            "Gemini client initialized successfully."
        )

    def generate_text(
        self,
        prompt: str,
        *,
        model: str = "gemini-3.6-flash",
    ) -> str:
        """Generate a text response from Gemini."""

        if not prompt.strip():
            raise ValueError(
                "Prompt cannot be empty."
            )

        try:
            response = self._client.models.generate_content(
                model=model,
                contents=prompt,
                config={
                    "automatic_function_calling": {
                        "disable": True,
                    },
                },
            )

            text = response.text

            if not text:
                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            return text.strip()

        except Exception:
            logger.exception(
                "Gemini text generation failed."
            )
            raise

    def generate_structured(
        self,
        prompt: str,
        response_model: type[ResponseModelT],
        *,
        model: str = "gemini-3.6-flash",
    ) -> ResponseModelT:
        """Generate and validate a structured Gemini response."""

        if not prompt.strip():
            raise ValueError(
                "Prompt cannot be empty."
            )

        try:
            response = self._client.models.generate_content(
                model=model,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": response_model,
                    "automatic_function_calling": {
                        "disable": True,
                    },
                },
            )

            if not response.text:
                raise RuntimeError(
                    "Gemini returned an empty structured response."
                )

            return response_model.model_validate_json(
                response.text
            )

        except Exception:
            logger.exception(
                "Gemini structured generation failed."
            )
            raise