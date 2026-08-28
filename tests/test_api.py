from fastapi.testclient import TestClient

from backend.api.main import app, store
from backend.models.geography import GeographicIdentity

client = TestClient(app)


def test_required_endpoints_and_insufficient_evidence_contract():
    response = client.get("/health")
    assert response.status_code == 200
    assert client.get("/ui/").status_code == 200

    store.put_geography(
        GeographicIdentity(
            geo_id="WB:TEST:LOCALITY",
            district="North 24 Parganas",
            locality="Controlled Locality",
            locality_type="TEST_FIXTURE",
            quality_flags=["SYNTHETIC_TEST_ONLY"],
        )
    )
    search = client.get("/localities/search", params={"q": "Controlled"})
    assert search.status_code == 200
    assert search.json()[0]["geo_id"] == "WB:TEST:LOCALITY"

    request = {
        "geo_id": "WB:TEST:LOCALITY",
        "entrepreneur": {
            "geo_id": "WB:TEST:LOCALITY",
            "available_capital": 1000,
            "business_category": "milk",
        },
    }
    decision = client.post("/analyze", json=request)
    assert decision.status_code == 200
    payload = decision.json()
    assert payload["status"] == "INSUFFICIENT_EVIDENCE"
    assert payload["selected_venture"] is None
    assert payload["evidence_gaps"]
    stored = client.get(f"/analysis/{payload['analysis_id']}")
    assert stored.status_code == 200


def test_unknown_analysis_returns_404():
    assert client.get("/analysis/does-not-exist").status_code == 404


def test_ordinary_user_request_resolves_location_and_returns_granular_gates():
    response = client.post(
        "/analyze",
        json={
            "state": "West Bengal",
            "district": "North 24 Parganas",
            "locality": "Controlled Locality",
            "capital": 100000,
            "business_category": "dairy",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "INSUFFICIENT_EVIDENCE"
    codes = {gate["code"] for gate in payload["evidence_gates"]}
    assert "NO_DEMAND_EVIDENCE" in codes
    assert "NO_PRICE_EVIDENCE" in codes
    assert "NO_CURRENT_FINANCE_RULE" in codes
    assert payload["geo_resolution"]["resolved_geo_id"] == "WB:TEST:LOCALITY"
