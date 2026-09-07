from __future__ import annotations

from typing import Any, TypedDict


class WorkflowState(TypedDict, total=False):
    """Shared state passed between YouTube content generation agents."""

    topic: str
    content_type: str
    research_notes: list[str]
    script: str
    claims: list[dict[str, Any]]
    qa_pass: bool
    qa_errors: list[str]
    video_path: str | None
    analytics_data: dict[str, Any]