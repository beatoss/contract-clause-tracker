from pathlib import Path

from fastapi import Depends, FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, joinedload

from app.database import get_db, init_db
from app.models import Document, Sentence
from app.parser import CLAUSE_TYPES
from app.schemas import DocumentDetail, DocumentListResponse, GroupSummary, LabelUpdate, SentenceOut
from app.services import clause_group, create_document, list_documents, seed_example_contracts, serialize_sentence, set_sentence_label, summarize_document

app = FastAPI(title="Contract Clause Tracker")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://127.0.0.1:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/clause-types")
def clause_types() -> list[str]:
    return CLAUSE_TYPES


@app.post("/api/documents", response_model=DocumentDetail)
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)) -> DocumentDetail:
    if not file.filename or not file.filename.lower().endswith((".txt", ".md", ".markdown")):
        raise HTTPException(status_code=400, detail="Upload a .txt or .md file")

    raw = await file.read()
    try:
        content = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail="File must be UTF-8 text") from exc

    document = create_document(db, file.filename, content)
    return document_detail(document)


@app.get("/api/documents", response_model=DocumentListResponse)
def documents(
    search: str | None = None,
    clause_type: str | None = Query(default=None),
    group_by: str | None = Query(default=None, pattern="^(clause_type)?$"),
    db: Session = Depends(get_db),
) -> DocumentListResponse:
    results = list_documents(db, search=search, clause_type=clause_type)
    summaries = [summarize_document(document) for document in results]
    groups = None

    if group_by == "clause_type":
        groups = [
            GroupSummary(group=group, documents=documents)
            for group, documents in clause_group(results).items()
        ]

    return DocumentListResponse(documents=summaries, groups=groups)


@app.get("/api/documents/{document_id}", response_model=DocumentDetail)
def get_document(document_id: int, db: Session = Depends(get_db)) -> DocumentDetail:
    document = db.get(
        Document,
        document_id,
        options=[joinedload(Document.sentences).joinedload(Sentence.label)],
    )
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document_detail(document)


@app.patch("/api/sentences/{sentence_id}/label", response_model=SentenceOut)
def update_label(sentence_id: int, payload: LabelUpdate, db: Session = Depends(get_db)) -> SentenceOut:
    try:
        sentence = set_sentence_label(db, sentence_id, payload.clause_type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not sentence:
        raise HTTPException(status_code=404, detail="Sentence not found")
    return serialize_sentence(sentence)


@app.post("/api/dev/seed", response_model=list[DocumentDetail])
def seed(db: Session = Depends(get_db)) -> list[DocumentDetail]:
    candidates = [
        Path(__file__).resolve().parents[1] / "example-contracts",
        Path(__file__).resolve().parents[2] / "example-contracts",
    ]
    examples_dir = next((path for path in candidates if path.exists()), candidates[0])
    if not examples_dir.exists():
        raise HTTPException(status_code=404, detail="example-contracts directory not found")
    return [document_detail(document) for document in seed_example_contracts(db, examples_dir)]


def document_detail(document: Document) -> DocumentDetail:
    summary = summarize_document(document)
    return DocumentDetail(
        **summary.model_dump(),
        sentences=[serialize_sentence(sentence) for sentence in document.sentences],
    )
