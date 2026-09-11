from fastapi.testclient import TestClient

from fin_research.api.app import create_app


def test_research_endpoint() -> None:
    with TestClient(create_app()) as client:
        response = client.post("/research", json={"ticker": "meta"})
    assert response.status_code == 200
    assert response.json()["ticker"] == "META"
