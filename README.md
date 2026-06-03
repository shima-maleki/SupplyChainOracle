# SupplyChainOracle

AI Supply Chain Risk Assistant for monitoring weather, news, trade, and historical delivery signals.

The MVP is intentionally practical for a Junior AI Engineer portfolio: React dashboard, FastAPI backend, live ingestion, Supabase persistence, Qdrant-backed RAG, OpenAI grounded assistant responses, explainable risk scoring, and Dockerized ingestion.

## Stack

Frontend:

* React
* TypeScript
* Recharts
* Tailwind-ready CSS structure

Backend:

* FastAPI
* Python service modules
* Risk scoring engine
* OpenAI-backed assistant service with deterministic fallback

Data:

* Supabase datastore schema in `supabase/schema.sql`
* Supabase REST persistence for regions, disruptions, documents, trade metrics, and historical shipments
* Qdrant vector retrieval using OpenAI embeddings
* Mock fallback data for local development without secrets

Ingestion:

* Dockerized scheduler service
* Live OpenWeather, NewsAPI, and UN Comtrade fetchers
* Seeded historical shipment fallback data

## Project Structure

```text
frontend/          React dashboard and assistant UI
backend/           FastAPI API, risk scoring, RAG, agent services
ingestion/         Scheduler service for hourly ingestion
supabase/          Supabase schema
docs/              PRD and architecture documentation
AGENT.md           Build instructions and engineering rules
```

## Environment Setup

Create a local `.env` from the example:

```bash
cp .env.example .env
```

The app runs with mock data when external API keys are empty. With the full `.env`, it uses live ingestion, Supabase, OpenAI, and Qdrant.

Required for the live demo:

```text
OPENAI_API_KEY=
SUPABASE_URL=https://PROJECT_REF.supabase.co
SUPABASE_SERVICE_ROLE_KEY=
QDRANT_URL=
QDRANT_API_KEY=
NEWS_API_KEY=
OPENWEATHER_API_KEY=
UN_COMTRADE_API_KEY=
```

Optional defaults:

```text
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
QDRANT_COLLECTION=supply_chain_documents
INGEST_INTERVAL_SECONDS=3600
```

For first-time Supabase setup, run `supabase/schema.sql` in the Supabase SQL editor or apply it using `SUPABASE_DB_URL`.

## Run With Docker

```bash
docker compose up --build
```

Services:

* Frontend: `http://localhost:5173`
* Backend API: `http://localhost:8000`
* API docs: `http://localhost:8000/docs`

The ingestion container calls `POST /ingest/run` every hour. To trigger ingestion manually:

```bash
curl -X POST http://localhost:8000/ingest/run
```

## Run Backend Locally

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.app.main:app --reload
```

From the repository root, use:

```bash
uvicorn backend.app.main:app --reload
```

## Run Frontend Locally

```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

```text
GET  /health
GET  /dashboard
GET  /regions
GET  /disruptions
GET  /documents
GET  /system/status
GET  /risk/scores
POST /risk/recalculate
POST /assistant/chat
POST /ingest/run
```

## MVP Data Sources

* OpenWeather API for weather risk signals
* NewsAPI for RAG knowledge base articles
* UN Comtrade API for import and export analytics
* Kaggle supply chain data for historical shipment trends

## Demo Checklist

1. Confirm `.env` has Supabase, OpenAI, Qdrant, NewsAPI, OpenWeather, and UN Comtrade values.
2. Run `docker compose up --build`.
3. Open `http://localhost:5173`.
4. Confirm the Live Systems panel shows connected services.
5. Run `POST /ingest/run` from API docs or curl.
6. Confirm `/dashboard` shows updated disruption counts, trade metrics, and recalculated risk scores.
7. Ask the assistant: `What risks are affecting Europe today?`
8. Confirm the assistant returns grounded citations from retrieved documents.

## Notes

The current implementation is a working live-data MVP with mock-safe fallback. The next engineering step is adding deployment-specific infrastructure such as managed hosting, CI checks, scheduled ingestion, and observability.
