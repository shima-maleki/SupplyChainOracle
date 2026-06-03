from backend.app.agent.supply_chain_agent import fallback_answer
from backend.app.services.mock_data import mock_disruptions, mock_documents, mock_regions


def test_fallback_answer_returns_grounded_citations() -> None:
    response = fallback_answer(
        documents=mock_documents(),
        regions=mock_regions(),
        disruptions=mock_disruptions(),
    )

    assert response.risk_level == "High"
    assert response.citations
    assert response.affected_regions
