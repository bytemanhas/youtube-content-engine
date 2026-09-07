from __future__ import annotations

import json
import logging
from typing import TypeVar

from ollama import Client
from pydantic import BaseModel

from app.services.ai_provider import AIProvider


logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class OllamaProvider(AIProvider):
    """Local AI provider powered by Ollama."""

    def __init__(
        self,
        *,
        host: str = "http://127.0.0.1:11434",
        model: str = "llama3.2:3b",
    ) -> None:
        self._client = Client(host=host)
        self._model = model

    def generate_text(self, prompt: str) -> str:
        """Generate plain text using the configured Ollama model."""

        if not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        try:
            response = self._client.generate(
                model=self._model,
                prompt=prompt,
            )

            text = response.response.strip()

            if not text:
                raise RuntimeError(
                    "Ollama returned an empty response."
                )

            logger.info(
                "Ollama generation successful | model=%s | characters=%d",
                self._model,
                len(text),
            )

            return text

        except Exception:
            logger.exception(
                "Ollama generation failed | model=%s",
                self._model,
            )
            raise

    def generate_structured(
        self,
        prompt: str,
        response_model: type[T],
    ) -> T:
        """Generate JSON and validate it against a Pydantic model."""

        if not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        schema = response_model.model_json_schema()

        try:
            response = self._client.generate(
                model=self._model,
                prompt=prompt,
                format=schema,
            )

            raw_response = response.response.strip()

            if not raw_response:
                raise RuntimeError(
                    "Ollama returned an empty structured response."
                )

            parsed_response = json.loads(raw_response)

            validated_response = response_model.model_validate(
                parsed_response
            )

            logger.info(
                "Ollama structured generation successful | "
                "model=%s | schema=%s",
                self._model,
                response_model.__name__,
            )

            return validated_response

        except json.JSONDecodeError as exc:
            logger.exception(
                "Ollama returned invalid JSON | model=%s",
                self._model,
            )
            raise RuntimeError(
                "Ollama returned invalid JSON."
            ) from exc

        except Exception:
            logger.exception(
                "Ollama structured generation failed | "
                "model=%s | schema=%s",
                self._model,
                response_model.__name__,
            )
            raise