from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    sentences: Mapped[list["Sentence"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
        order_by="Sentence.position",
    )


class Sentence(Base):
    __tablename__ = "sentences"
    __table_args__ = (UniqueConstraint("document_id", "position", name="uq_sentence_document_position"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)

    document: Mapped[Document] = relationship(back_populates="sentences")
    label: Mapped["ClauseLabel | None"] = relationship(
        back_populates="sentence",
        cascade="all, delete-orphan",
        uselist=False,
    )


class ClauseLabel(Base):
    __tablename__ = "clause_labels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sentence_id: Mapped[int] = mapped_column(ForeignKey("sentences.id", ondelete="CASCADE"), unique=True, nullable=False)
    clause_type: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    sentence: Mapped[Sentence] = relationship(back_populates="label")
