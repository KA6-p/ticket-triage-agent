# Ticket Triage Agent

[![CI](https://github.com/YOUR_USERNAME/ticket-triage-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/ticket-triage-agent/actions)

LLM-powered support-ticket triage. Each incoming ticket is **classified**, **prioritised**, scored for **sentiment and confidence**, checked for **semantic duplicates**, **routed** to a team, and given a **draft reply**. Deterministic guardrails stop the model from under-rating emergencies, low-confidence results go to a human, and agent corrections are stored as feedback.

**Live demo:** _add your Streamlit/Render URL_ · **API docs:** _your-api-url_/docs

## Architecture

```text
Ticket (UI / API / CSV)
        |
     FastAPI ──► Gemini (structured JSON output, schema-validated, retries)
        |             └─ invalid / failed ─► safe fallback + status "triage_failed"
        ├────► Priority guardrails (rules can only RAISE priority)
        ├────► Embeddings ─► ChromaDB (cosine) ─► duplicate detection
        ▼
  SQLAlchemy (SQLite locally / Postgres in prod)
        ├────► Streamlit dashboard (queue, filters, human review form)
        └────► Offline evaluation (precision / recall / F1, confusion matrix)
```

Design decisions worth talking about:

- **Structured output + validation.** Gemini is asked for a JSON schema (`response_schema`), and the reply is re-validated with Pydantic. Any failure becomes an explicit `triage_failed` state, never a silent wrong answer.
- **Guardrails over trust.** Regex rules (outage, data loss, breach, lockout…) can raise priority but never lower it. The pre-override LLM priority and the rule that fired are stored for auditability.
- **Human-in-the-loop.** Confidence below `CONFIDENCE_THRESHOLD` routes to `needs_human_review`. Agents correct tickets in the UI; corrections feed a *human agreement rate* metric.
- **Cosine similarity, correctly.** Chroma collections are created with `hnsw:space=cosine` (its default is L2, which silently breaks `1 - distance` thresholds). Covered by a test.
- **Self-healing vector index.** On startup, tickets missing from the vector store are re-embedded from the database, so ephemeral disks on free hosts don't lose duplicate detection.
- **Prompt-injection aware.** Ticket text is wrapped as untrusted data; the UI HTML-escapes model and customer text.
- **Public-demo safety.** Optional `X-API-Key`, per-IP rate limiting, input length caps, batch row limit.

## Stack

FastAPI · Google Gemini (`google-genai`) · ChromaDB · SQLAlchemy · SQLite/PostgreSQL · Streamlit · Docker · GitHub Actions · pytest · Ruff

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env               # Windows: copy .env.example .env
# edit .env: set GEMINI_API_KEY (free key: https://aistudio.google.com/apikey)

cd backend && uvicorn app.main:app --reload            # http://localhost:8000/docs
# new terminal, from the project root:
pip install -r frontend/requirements.txt
streamlit run frontend/streamlit_app.py                # http://localhost:8501
python scripts/seed_database.py                        # optional demo data
```

Or with Docker: `cp .env.example .env && docker compose up --build`.

Want fully local embeddings (no API call)? `pip install -r requirements-local-embeddings.txt` and set `EMBEDDING_PROVIDER=local`.

## API

| Method | Path | Purpose |
|---|---|---|
| POST | `/tickets` | ingest + triage one ticket |
| GET | `/tickets` | list, filter (`category`, `priority`, `status`), paginate (`limit`, `offset`) |
| GET | `/tickets/{id}` | ticket detail |
| POST | `/tickets/{id}/feedback` | human correction / confirmation |
| POST | `/tickets/batch` | CSV upload (`subject`,`body`; max 50 rows) |
| GET | `/stats` | counts, guardrail overrides, latency, human agreement rate |
| GET | `/health` | health check |

## Tests and evaluation

```bash
pytest -q                                   # 32 tests, no network needed (LLM is faked)
python evaluation/evaluate.py --delay 1.5   # runs the REAL model on 60 labeled tickets
```

`evaluate.py` writes `evaluation/results/latest.md` + `.json` (accuracy, per-class P/R/F1, confusion matrix, priority accuracy with and without guardrails, critical-ticket recall, latency, misclassified tickets).

### Results

_Run the evaluation and paste the table from `evaluation/results/latest.md` here. Only quote numbers you actually measured._

> Caveat to state honestly: the 60-ticket set is small and hand-written, so treat results as a sanity check, not a production benchmark.

## Deploy (free tier)

1. **Database** - create a free Postgres on [Neon](https://neon.tech); copy the connection string.
2. **API** - push to GitHub, then on [Render](https://render.com): *New > Blueprint* (uses `render.yaml`). Set `GEMINI_API_KEY` and `DATABASE_URL`; `API_KEY` is auto-generated. Keep `EMBEDDING_PROVIDER=gemini` (no PyTorch, fits 512 MB).
3. **UI** - either the second service in the blueprint, or [Streamlit Community Cloud](https://share.streamlit.io): main file `frontend/streamlit_app.py`, requirements `frontend/requirements.txt`, secrets:
   ```toml
   API_URL = "https://<your-api>.onrender.com"
   API_KEY = "<same value as the API's API_KEY>"
   ```
4. Open `<api>/health` (`llm_configured` should be `true`), then run `python scripts/seed_database.py --api <url> --api-key <key>`.

Free Render services sleep after inactivity; the first request can take ~30-60 s.

## Project layout

```text
backend/app/{api,services,models,schemas,prompts}   FastAPI app
backend/tests                                       pytest suite
frontend/streamlit_app.py                           dashboard + review UI
evaluation/                                         labeled data + evaluator
scripts/seed_database.py                            demo data loader
```
