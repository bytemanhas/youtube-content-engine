from datetime import datetime
from enum import StrEnum
from typing import Any

from sqlalchemy import DateTime, Float, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from pgvector.sqlalchemy import Vector


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""


class VideoStatus(StrEnum):
    """Lifecycle states for generated YouTube videos."""

    GENERATED = "generated"
    QA_PASSED = "qa_passed"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"
    UPLOADING = "uploading"
    PUBLISHED = "published"
    FAILED = "failed"


class Video(Base):
    """Store generated video metadata and lifecycle state."""

    __tablename__ = "videos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    content_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="short",
    )

    status: Mapped[VideoStatus] = mapped_column(
        String(40),
        nullable=False,
        default=VideoStatus.GENERATED,
    )

    topic: Mapped[str] = mapped_column(String(500), nullable=False)

    script: Mapped[str | None] = mapped_column(Text, nullable=True)

    video_path: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    youtube_video_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    youtube_url: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class Analytics(Base):
    """Store YouTube performance metrics for generated videos."""

    __tablename__ = "analytics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    video_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    views: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    likes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    comments: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    watch_time_minutes: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    average_view_duration_seconds: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    raw_data: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    collected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class PromptEmbedding(Base):
    """Store embeddings used by the engine's learning and retrieval layer."""

    __tablename__ = "prompt_embeddings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    embedding: Mapped[list[float]] = mapped_column(
        Vector(768),
        nullable=False,
    )

    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )