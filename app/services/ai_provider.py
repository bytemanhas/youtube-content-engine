from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, TypeVar

from pydantic import BaseModel


T = TypeVar("T", bound=BaseModel)


class AIProvider(ABC):
    """Abstract interface for AI providers used by the engine."""

    @abstractmethod
    def generate_text(self, prompt: str) -> str:
        """Generate text from a prompt."""
        raise NotImplementedError

    @abstractmethod
    def generate_structured(
        self,
        prompt: str,
        response_model: type[T],
    ) -> T:
        """Generate and validate structured output."""
        raise NotImplementedError