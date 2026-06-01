from backend.app.rag.retriever import retrieve_documents
from backend.app.schemas.chat import ChatRequest, ChatResponse, Citation
from backend.app.services.datastore import datastore


def answer_question(request: ChatRequest) -> ChatResponse:
    """MVP agent response with grounded mock retrieval.

    This keeps the behavior deterministic until OpenAI and LangGraph are wired
    into the service.
    """
    documents = retrieve_documents(request.question, request.region)
    regions = datastore.list_regions()
    disruptions = datastore.list_disruptions()

    affected_regions = sorted({doc.region for doc in documents} | {item.region for item in disruptions[:3]})
    highest = max(regions, key=lambda region: region.risk_score)
    drivers = [
        "Weather alerts from OpenWeather-style signals",
        "Supply chain disruption news retrieved for RAG context",
        "Historical delivery delay patterns from seeded shipment data",
        "Trade activity changes from UN Comtrade-style metrics",
    ]

    if documents:
        summary = (
            f"Current risk is concentrated around {', '.join(affected_regions[:3])}. "
            f"{highest.name} has the highest score at {highest.risk_score}, classified as {highest.risk_level.value}. "
            "The answer is based on retrieved disruption documents and current risk scores."
        )
    else:
        summary = "Available data is limited for this question. Review the dashboard risk scores and recent disruptions."

    citations = [
        Citation(title=doc.title, source=doc.source, url=doc.url)
        for doc in documents
    ]

    return ChatResponse(
        summary=summary,
        risk_level=highest.risk_level.value,
        key_drivers=drivers,
        affected_regions=affected_regions,
        citations=citations,
    )
