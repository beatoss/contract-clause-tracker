# Contract Clause Tracker

A small full-stack coding-challenge app for tracking clause types across uploaded contracts.

## Run

```bash
docker-compose up --build
```

Open `http://localhost:4200`. Use **Seed** to import the included example contracts, or upload a UTF-8 `.txt`, `.md`, or `.markdown` file.

The API is also available at `http://localhost:8000`, with OpenAPI docs at `http://localhost:8000/docs`.

## Run Locally For Debugging

Start the backend:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Start the frontend in another terminal:

```bash
cd frontend
npm install
npm start
```

The local Angular proxy sends `/api` requests to `http://localhost:8000`. Docker uses `proxy.docker.conf.json` so Compose still routes to the `backend` service.

## What It Does

- Uploads plain-text or Markdown contracts.
- Splits contract text into sentence-level clauses.
- Lets a user label each sentence as:
  - Limitation of Liability
  - Termination for Convenience
  - Non-Compete
- Shows a searchable/filterable dashboard of documents.
- Groups documents by clause type.
- Imports labels from comments like `<!-- Clause Type: Limitation of Liability -->` when they appear after a sentence in the sample contracts.

## Architecture

- **Backend:** FastAPI, SQLAlchemy, SQLite.
- **Frontend:** Angular standalone app.
- **Database:** SQLite in a Docker volume.
- **Containerization:** `docker-compose.yml` runs the API and Angular dev server.

The backend is intentionally compact: `documents` store metadata, `sentences` store ordered sentence text, and `clause_labels` stores the single active label for a sentence.

## API Overview

- `POST /api/documents` uploads a `.txt` or `.md` file.
- `GET /api/documents` lists documents with optional `search`, `clause_type`, and `group_by=clause_type`.
- `GET /api/documents/{id}` returns a document with ordered sentences and labels.
- `PATCH /api/sentences/{id}/label` sets or clears a sentence label.
- `GET /api/clause-types` returns the fixed clause type list.
- `POST /api/dev/seed` imports the bundled example contracts.

## Tests

Backend tests cover the critical paths:

```bash
cd backend
pip install -r requirements.txt
pytest
```

## Extension Notes

- **AI labeling:** add a background endpoint that proposes labels for unlabeled sentences, store suggestions separately from accepted labels, and let reviewers approve or reject them.
- **Scaling:** move from SQLite to PostgreSQL, add pagination/search indexes, and run parsing/AI work in a queue.
- **Auditability:** add label history with actor, timestamp, previous label, and confidence/source.
- **Clause taxonomy:** replace the fixed list with a configurable `clause_types` table.
