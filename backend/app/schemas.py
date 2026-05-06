from datetime import datetime

from pydantic import BaseModel


class LabelUpdate(BaseModel):
    clause_type: str | None = None


class SentenceOut(BaseModel):
    id: int
    position: int
    text: str
    clause_type: str | None


class DocumentSummary(BaseModel):
    id: int
    filename: str
    title: str
    created_at: datetime
    updated_at: datetime
    sentence_count: int
    labeled_count: int
    clause_counts: dict[str, int]


class DocumentDetail(DocumentSummary):
    sentences: list[SentenceOut]


class GroupSummary(BaseModel):
    group: str
    documents: list[DocumentSummary]


class DocumentListResponse(BaseModel):
    documents: list[DocumentSummary]
    groups: list[GroupSummary] | None = None
