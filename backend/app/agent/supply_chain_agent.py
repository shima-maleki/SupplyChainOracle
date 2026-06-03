import json
import logging

import httpx
from pydantic import ValidationError

from backend.app.config import get_settings
from backend.app.rag.retriever import retrieve_documents
from backend.app.schemas.chat import ChatRequest, ChatResponse, Citation
from backend.app.schemas.risk import Disruption, Document, Region
from backend.app.services.datastore import datastore

logger = logging.getLogger(__name__)


def answer_question(request: ChatRequest) -> ChatResponse:
    documents = retrieve_documents(request.question, request.region)
    regions = datastore.list_regions()
    disruptions = datastore.list_disruptions()

    openai_response = generate_openai_answer(request, documents, regions, disruptions)
    if openai_response:
        return openai_response

    return fallback_answer(documents, regions, disruptions)


def fallback_answer(
    documents: list[Document],
    regions: list[Region],
    disruptions: list[Disruption],
) -> ChatResponse:
    affected_regions = sorted({doc.region for doc in documents} | {item.region for item in disruptions[:3]})
    highest = max(regions, key=lambda region: region.risk_score)
    drivers = [
        "Weather alerts from OpenWeather signals",
        "Supply chain disruption news retrieved for RAG context",
        "Historical delivery delay patterns from shipment data",
        "Trade activity changes from UN Comtrade metrics",
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


def generate_openai_answer(
    request: ChatRequest,
    documents: list[Document],
    regions: list[Region],
    disruptions: list[Disruption],
) -> ChatResponse | None:
    settings = get_settings()
    if not settings.openai_api_key:
        return None

    citations = [Citation(title=doc.title, source=doc.source, url=doc.url) for doc in documents]
    payload = {
        "model": settings.openai_model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an enterprise supply chain risk analyst. Answer only from the supplied "
                    "risk scores, disruptions, and retrieved documents. Keep the summary concise, "
                    "actionable, and grounded. Return JSON that matches the requested schema."
                ),
            },
            {
                "role": "user",
                "content": build_prompt(request, documents, regions, disruptions),
            },
        ],
        "temperature": 0.2,
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "supply_chain_risk_answer",
                "strict": True,
                "schema": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "summary": {"type": "string"},
                        "risk_level": {"type": "string", "enum": ["Low", "Medium", "High"]},
                        "key_drivers": {
                            "type": "array",
                            "items": {"type": "string"},
                            "minItems": 1,
                            "maxItems": 4,
                        },
                        "affected_regions": {
                            "type": "array",
                            "items": {"type": "string"},
                            "minItems": 1,
                            "maxItems": 6,
                        },
                    },
                    "required": ["summary", "risk_level", "key_drivers", "affected_regions"],
                },
            },
        },
    }

    try:
        response = httpx.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.openai_api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        return ChatResponse.model_validate({**parsed, "citations": citations})
    except (httpx.HTTPError, KeyError, IndexError, json.JSONDecodeError, ValidationError) as exc:
        logger.warning("OpenAI assistant generation failed: %s", exc)
        return None


def build_prompt(
    request: ChatRequest,
    documents: list[Document],
    regions: list[Region],
    disruptions: list[Disruption],
) -> str:
    region_context = [
        {
            "name": region.name,
            "risk_score": region.risk_score,
            "risk_level": region.risk_level.value,
            "last_updated": region.last_updated.isoformat(),
        }
        for region in regions
    ]
    disruption_context = [
        {
            "title": item.title,
            "region": item.region,
            "severity": item.severity.value,
            "source": item.source,
            "created_at": item.created_at.isoformat(),
        }
        for item in disruptions[:6]
    ]
    document_context = [
        {
            "title": document.title,
            "region": document.region,
            "source": document.source,
            "content": document.content[:700],
        }
        for document in documents
    ]

    return json.dumps(
        {
            "question": request.question,
            "requested_region": request.region,
            "risk_scores": region_context,
            "recent_disruptions": disruption_context,
            "retrieved_documents": document_context,
            "output_rules": [
                "Use only supplied context.",
                "Do not invent incidents, sources, or metrics.",
                "Mention uncertainty when context is thin.",
            ],
        },
        default=str,
    )
