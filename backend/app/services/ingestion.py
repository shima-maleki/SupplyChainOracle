from backend.app.integrations.newsapi import NEWS_KEYWORDS
from backend.app.services.datastore import datastore


def run_ingestion() -> dict:
    """Placeholder ingestion orchestration.

    Live API clients can be added behind this function. The current result
    documents what would run and keeps local development deterministic.
    """
    seeded = datastore.seed_mock_data()
    return {
        "status": "ok",
        "mode": "mock-seed" if seeded.get("configured") else "mock",
        "sources": {
            "openweather": "ready",
            "newsapi": {"ready": True, "keywords": NEWS_KEYWORDS},
            "un_comtrade": "ready",
            "kaggle": "seed-data",
        },
        "seeded": seeded,
        "message": "Ingestion seeded MVP data. Live fetchers can replace mock sources next.",
    }
