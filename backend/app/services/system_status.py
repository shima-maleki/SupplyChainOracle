from backend.app.config import get_settings
from backend.app.services.datastore import datastore


def system_status() -> dict:
    settings = get_settings()
    documents = datastore.list_documents()
    disruptions = datastore.list_disruptions()
    trade_metrics = datastore.list_trade_metrics()

    return {
        "services": {
            "supabase": bool(settings.supabase_url and (settings.supabase_service_role_key or settings.supabase_anon_key)),
            "qdrant": bool(settings.qdrant_url and settings.qdrant_api_key),
            "openai": bool(settings.openai_api_key),
            "newsapi": bool(settings.news_api_key),
            "openweather": bool(settings.openweather_api_key),
            "un_comtrade": bool(settings.un_comtrade_api_key),
        },
        "models": {
            "chat": settings.openai_model,
            "embedding": settings.openai_embedding_model,
        },
        "rag": {
            "collection": settings.qdrant_collection,
            "documents": len(documents),
            "indexed": bool(settings.qdrant_url and settings.qdrant_api_key and documents),
        },
        "data": {
            "disruptions": len(disruptions),
            "trade_metrics": len(trade_metrics),
        },
    }
