import hashlib
from pathlib import Path

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from app.models import ClauseLabel, Document, Sentence
from app.parser import CLAUSE_TYPES, extract_title, normalize_clause_type, parse_contract
from app.schemas import DocumentSummary, SentenceOut


def create_document(db: Session, filename: str, content: str) -> Document:
    content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    existing = db.scalar(select(Document).where(Document.content_hash == content_hash))
    if existing:
        return existing

    parsed = parse_contract(content)
    document = Document(
        filename=filename,
        title=extract_title(filename, content),
        content_hash=content_hash,
    )
    for index, parsed_sentence in enumerate(parsed, start=1):
        sentence = Sentence(position=index, text=parsed_sentence.text)
        if parsed_sentence.clause_type:
            sentence.label = ClauseLabel(clause_type=parsed_sentence.clause_type)
        document.sentences.append(sentence)

    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def seed_example_contracts(db: Session, examples_dir: Path) -> list[Document]:
    documents: list[Document] = []
    for path in sorted(examples_dir.glob("*.md")):
        documents.append(create_document(db, path.name, path.read_text(encoding="utf-8")))
    return documents


def set_sentence_label(db: Session, sentence_id: int, clause_type: str | None) -> Sentence | None:
    sentence = db.get(Sentence, sentence_id)
    if not sentence:
        return None

    normalized = normalize_clause_type(clause_type)
    if clause_type and not normalized:
        raise ValueError("Unknown clause type")

    if normalized is None:
        if sentence.label:
            db.delete(sentence.label)
    elif sentence.label:
        sentence.label.clause_type = normalized
    else:
        sentence.label = ClauseLabel(clause_type=normalized)

    db.commit()
    db.refresh(sentence)
    return sentence


def list_documents(db: Session, search: str | None = None, clause_type: str | None = None) -> list[Document]:
    stmt = select(Document).options(joinedload(Document.sentences).joinedload(Sentence.label))

    if search:
        term = f"%{search.strip()}%"
        matching_document_ids = select(Sentence.document_id).where(Sentence.text.ilike(term))
        stmt = stmt.where(or_(Document.title.ilike(term), Document.filename.ilike(term), Document.id.in_(matching_document_ids)))

    normalized = normalize_clause_type(clause_type)
    if clause_type and not normalized:
        return []
    if normalized:
        matching_label_ids = (
            select(Sentence.document_id)
            .join(ClauseLabel)
            .where(ClauseLabel.clause_type == normalized)
        )
        stmt = stmt.where(Document.id.in_(matching_label_ids))

    stmt = stmt.order_by(Document.created_at.desc(), Document.id.desc())
    return list(db.scalars(stmt).unique())


def serialize_sentence(sentence: Sentence) -> SentenceOut:
    return SentenceOut(
        id=sentence.id,
        position=sentence.position,
        text=sentence.text,
        clause_type=sentence.label.clause_type if sentence.label else None,
    )


def summarize_document(document: Document) -> DocumentSummary:
    counts = {clause_type: 0 for clause_type in CLAUSE_TYPES}
    labeled_count = 0
    for sentence in document.sentences:
        if sentence.label:
            labeled_count += 1
            counts[sentence.label.clause_type] = counts.get(sentence.label.clause_type, 0) + 1

    return DocumentSummary(
        id=document.id,
        filename=document.filename,
        title=document.title,
        created_at=document.created_at,
        updated_at=document.updated_at,
        sentence_count=len(document.sentences),
        labeled_count=labeled_count,
        clause_counts=counts,
    )


def clause_group(documents: list[Document]) -> dict[str, list[DocumentSummary]]:
    grouped: dict[str, list[DocumentSummary]] = {clause_type: [] for clause_type in CLAUSE_TYPES}
    grouped["Unlabeled"] = []

    for document in documents:
        summary = summarize_document(document)
        labels = {sentence.label.clause_type for sentence in document.sentences if sentence.label}
        if not labels:
            grouped["Unlabeled"].append(summary)
        for label in labels:
            grouped[label].append(summary)

    return {key: value for key, value in grouped.items() if value}
