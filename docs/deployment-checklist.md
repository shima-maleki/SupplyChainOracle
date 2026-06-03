# Deployment Checklist

Use this checklist before a portfolio demo or production-style deployment.

## Environment

Required live services:

* `OPENAI_API_KEY`
* `SUPABASE_URL`
* `SUPABASE_SERVICE_ROLE_KEY`
* `QDRANT_URL`
* `QDRANT_API_KEY`
* `NEWS_API_KEY`
* `OPENWEATHER_API_KEY`
* `UN_COMTRADE_API_KEY`

Recommended defaults:

* `OPENAI_MODEL=gpt-4o-mini`
* `OPENAI_EMBEDDING_MODEL=text-embedding-3-small`
* `QDRANT_COLLECTION=supply_chain_documents`
* `INGEST_INTERVAL_SECONDS=3600`

Never expose server-side keys to the frontend. `SUPABASE_SERVICE_ROLE_KEY`, `OPENAI_API_KEY`, and `QDRANT_API_KEY` must stay server-side.

## Database

1. Create the Supabase project.
2. Run `supabase/schema.sql`.
3. Confirm these tables exist:
   * `regions`
   * `disruptions`
   * `documents`
   * `trade_metrics`
   * `historical_shipments`

## Vector Store

1. Create a Qdrant Cloud cluster.
2. Set `QDRANT_URL` and `QDRANT_API_KEY`.
3. The backend creates/updates the `QDRANT_COLLECTION` collection during ingestion.
4. Confirm `/ingest/run` returns `rag_index.indexed` greater than `0`.

## Smoke Tests

Run locally:

```bash
python -m pytest backend/tests
cd frontend
npm run build
```

Run with Docker:

```bash
docker compose up --build
```

Verify:

* `GET /health` returns `ok`.
* `GET /system/status` shows connected live services.
* `POST /ingest/run` fetches live sources and recalculates risk scores.
* `GET /dashboard` shows updated regions, disruptions, trade metrics, and RAG document counts.
* `POST /assistant/chat` returns a grounded answer with citations.

## Demo Flow

1. Open `http://localhost:5173`.
2. Show Global Risk Index and High Risk Regions.
3. Show Live Systems panel.
4. Trigger ingestion from API docs at `http://localhost:8000/docs`.
5. Refresh the dashboard.
6. Ask the assistant: `What risks are affecting Europe today?`
7. Point out cited sources and live service status.
