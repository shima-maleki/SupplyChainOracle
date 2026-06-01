from fastapi import APIRouter

from backend.app.agent.supply_chain_agent import answer_question
from backend.app.risk.scoring import calculate_risk_score
from backend.app.schemas.chat import ChatRequest, ChatResponse
from backend.app.schemas.risk import DashboardSummary, Disruption, Document, Region, RiskScoreResult
from backend.app.services.datastore import datastore
from backend.app.services.ingestion import run_ingestion
from backend.app.services.mock_data import RISK_INPUTS

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "supply-chain-risk-backend"}


@router.get("/dashboard", response_model=DashboardSummary)
def dashboard() -> DashboardSummary:
    return datastore.dashboard_summary()


@router.get("/regions", response_model=list[Region])
def regions() -> list[Region]:
    return datastore.list_regions()


@router.get("/disruptions", response_model=list[Disruption])
def disruptions() -> list[Disruption]:
    return datastore.list_disruptions()


@router.get("/documents", response_model=list[Document])
def documents() -> list[Document]:
    return datastore.list_documents()


@router.get("/risk/scores", response_model=list[RiskScoreResult])
def risk_scores() -> list[RiskScoreResult]:
    return [calculate_risk_score(region, inputs) for region, inputs in RISK_INPUTS.items()]


@router.post("/risk/recalculate", response_model=list[RiskScoreResult])
def recalculate_risk() -> list[RiskScoreResult]:
    return risk_scores()


@router.post("/assistant/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    return answer_question(request)


@router.post("/ingest/run")
def ingest() -> dict:
    return run_ingestion()
