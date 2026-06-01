# SupplyChainOracle

AI Supply Chain Risk Assistant for monitoring weather, news, trade, and historical delivery signals.

The MVP is intentionally practical for a Junior AI Engineer portfolio: React dashboard, FastAPI backend, LangGraph-ready assistant structure, Qdrant-ready RAG layer, Supabase schema, and Dockerized ingestion.

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
* RAG-ready retriever and assistant service

Data:

* Supabase datastore schema in `supabase/schema.sql`
* Qdrant-ready document metadata and retrieval layer
* Mock fallback data for local development without secrets

Ingestion:

* Dockerized scheduler service
* OpenWeather, NewsAPI, UN Comtrade, and Kaggle source placeholders

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

The app runs with mock data even when external API keys are empty.

## Run With Docker

```bash
docker compose up --build
```

Services:

* Frontend: `http://localhost:5173`
* Backend API: `http://localhost:8000`
* API docs: `http://localhost:8000/docs`

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

## Notes

The current implementation is a working scaffold with mock-safe data. The next engineering step is replacing repository methods in `backend/app/services/datastore.py` and retrieval logic in `backend/app/rag/retriever.py` with Supabase and Qdrant clients.
