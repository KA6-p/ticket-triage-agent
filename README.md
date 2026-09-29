# Ticket Triage Agent

A ticket triage system that ingests tickets, classifies them, scores priority, detects sentiment and semantic duplicates, suggests routing, drafts a first response, logs confidence, and supports human feedback and evaluation.

## Architecture

```text
Ticket Source -> FastAPI -> preprocessing
                    |-> Claude classification/priority/draft
                    |-> sentence-transformers -> ChromaDB -> similarity
                    |-> deterministic priority guardrails
                    v
                 SQLite/Postgres
                    |-> Streamlit dashboard
                    |-> evaluation module
```

Claude provides reasoning while embeddings handle retrieval and duplicate detection. Low-confidence classifications are routed to human review. Keyword rules provide deterministic priority overrides.

## Stack

FastAPI, Claude API, sentence-transformers, ChromaDB, PostgreSQL/SQLite, SQLAlchemy, Streamlit, Docker, GitHub Actions, pytest, Ruff.

## Run locally

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env   # Windows
# cp .env.example .env  # Linux/macOS
```

Set `ANTHROPIC_API_KEY` in `.env`.

Backend:

```bash
cd backend
uvicorn app.main:app --reload
```

Open `http://localhost:8000/docs`.

Frontend, in another terminal:

```bash
streamlit run frontend/streamlit_app.py
```

Open `http://localhost:8501`.

## API

- `POST /tickets` ingest and triage a ticket
- `GET /tickets` list/filter tickets
- `GET /tickets/{id}` ticket details
- `POST /tickets/{id}/feedback` human correction
- `POST /tickets/batch` CSV ingestion
- `GET /stats` dashboard statistics
- `GET /health` health check

## CSV format

```csv
subject,body
Refund requested,I was charged twice.
```

## Evaluation

The repository contains a small labeled dataset under `evaluation/dataset/labeled_tickets.csv` and an evaluation runner:

```bash
python evaluation/evaluate.py --file evaluation/dataset/labeled_tickets.csv
```

For a serious portfolio evaluation, expand this to 50-100 labeled tickets and report precision, recall, F1, and a confusion matrix. Do not claim performance numbers until the evaluation has actually been run.

## Docker

```bash
cp .env.example .env
# edit .env with your key
docker compose up --build
```

## Production path

Use managed PostgreSQL, deploy the FastAPI container to Railway/Render, deploy Streamlit separately, store secrets in the platform secret manager, enable GitHub Actions, seed realistic demo tickets, and record a short walkthrough.
