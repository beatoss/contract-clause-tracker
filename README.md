# Contract Clause Tracker

Note: The engineer has only 1 month of professional Python experience, using Python to steer a microscope in robotics, not to build APIs.

A small full-stack coding-challenge app for tracking clause types across uploaded contracts.

## Run

```bash
docker-compose up --build
```

Open `http://localhost:4200/dashboard`. Use **Seed examples** to import the included example contracts, or upload a UTF-8 `.txt`, `.md`, or `.markdown` file.

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

## Design decisions

- Server side searching / filtering
- Opens document labeling at `/document/:id/label`. Could have also gone for a modal menu.
- Updates labels immediately. Could have also gone for a Save button.

## Architecture

- **Backend:** FastAPI, SQLAlchemy, SQLite.
- **Frontend:** Angular standalone app. (could have gone for Angular 21)
- **Database:** SQLite.
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

Backend tests cover the critical API paths. From a fresh checkout, install the backend dependencies once:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Then run the tests from the `backend` directory:

```bash
pytest
```

The tests use a temporary SQLite database, so they do not modify your local development database or Docker volume.

## Extension Notes

- **AI labeling:** add a button or background service that proposes labels for unlabeled sentences, store suggestions separately from accepted labels, and let reviewers approve or reject them.
- **Scaling:** move from SQLite to PostgreSQL. Decide between id or uuid as the primary key. Add pagination. searching: only after 2 characters and with a delay.
- **Technical:** upgrade to Angular 21 with singals, node 24 LTS, add AGENTS.md / copilot-instructions.md with more guidelines about technical decisions.
- **Auditability:** add label history with user, timestamp, previous label, and confidence/source.
- **UX/DESIGN**: Make better UX and a nicer design:-). Decide for a primary component library. Use icons. More and better error messages. Example: if you oploaded a document already.
