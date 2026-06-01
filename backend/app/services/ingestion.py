from backend.app.integrations.newsapi import NEWS_KEYWORDS


def run_ingestion() -> dict:
    """Placeholder ingestion orchestration.

    Live API clients can be added behind this function. The current result
    documents what would run and keeps local development deterministic.
    """
    return {
        "status": "ok",
        "mode": "mock",
        "sources": {
            "openweather": "ready",
            "newsapi": {"ready": True, "keywords": NEWS_KEYWORDS},
            "un_comtrade": "ready",
            "kaggle": "seed-data",
        },
        "message": "Ingestion pipeline is scaffolded. Configure API keys to enable live fetchers.",
    }
