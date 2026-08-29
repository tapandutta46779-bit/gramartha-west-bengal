from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import quote

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import RedirectResponse, Response
from fastapi.staticfiles import StaticFiles

from backend.api.contracts import AnalyzeRequest, CompareRequest, StressRequest
from backend.evidence.store import EvidenceStore
from backend.finance.digital_twin import project_monthly_cashflow
from backend.finance.stress import find_failure_boundary, summarize_stress
from backend.models.decision import VentureDecision
from backend.reporting.customer_pdf import build_customer_pdf
from backend.service import analyze

app = FastAPI(title="GramArtha West Bengal Business Advisor", version="0.7.1")
store = EvidenceStore(os.environ.get("SIH26091_SQLITE_PATH", ":memory:"))
frontend_path = Path(__file__).resolve().parents[2] / "frontend"
if frontend_path.exists():
    app.mount("/ui", StaticFiles(directory=frontend_path, html=True), name="ui")


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/ui/", status_code=307)


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "methodology_version": "decision-v6",
        "presentation_version": "plain-language-summary-v2-full-detail",
    }


@app.get("/localities/search")
def search_localities(
    q: str = Query(min_length=1),
    limit: int = Query(20, ge=1, le=100),
    district: str | None = None,
    locality_type: str | None = None,
):
    return store.search_geographies(q, limit, district, locality_type)


@app.get("/districts")
def districts():
    return {"state": "West Bengal", "districts": store.list_districts()}


@app.get("/evidence/{geo_id}")
def evidence(geo_id: str):
    return {"geo_id": geo_id, "records": store.get_evidence(geo_id)}


@app.get("/geography/{geo_id}/crosswalk")
def geography_crosswalk(geo_id: str):
    geography = store.get_geography(geo_id)
    if geography is None:
        raise HTTPException(404, "geography not found")
    return {
        "geo_id": geo_id,
        "current_geography": geography,
        "historical_crosswalks": store.get_crosswalks(geo_id),
    }


@app.post("/analyze")
def analyze_endpoint(request: AnalyzeRequest):
    return analyze(request, store)


@app.post("/compare")
def compare_endpoint(request: CompareRequest):
    decision = analyze(request, store)
    return {
        "analysis_id": decision.analysis_id,
        "status": decision.status,
        "selected": decision.selected_venture,
        "alternatives": decision.alternatives,
        "rejected": decision.mvv.rejected if decision.mvv else [],
    }


@app.post("/stress")
def stress_endpoint(request: StressRequest):
    decision = store.get_analysis(request.analysis_id)
    if decision is None:
        raise HTTPException(404, "analysis not found")
    if decision.digital_twin is None:
        raise HTTPException(409, "analysis has no digital-twin assumptions")
    assumptions = decision.digital_twin.assumptions

    def survives(demand: float) -> bool:
        twin = project_monthly_cashflow(
            opening_cash=assumptions["opening_cash"],
            monthly_demand=demand,
            capacity=assumptions["capacity"],
            unit_price=assumptions["unit_price"],
            variable_cost_per_unit=assumptions["variable_cost_per_unit"],
            fixed_monthly_cost=assumptions["fixed_monthly_cost"],
            growth_rate=assumptions["growth_rate"],
            ramp_months=int(assumptions["ramp_months"]),
            loan=decision.loan_terms,
        )
        return twin.default_month is None

    boundary = find_failure_boundary(
        "monthly_demand",
        assumptions["monthly_demand"],
        "DOWN",
        request.demand_step,
        survives,
        request.maximum_points,
    )
    decision.stress = summarize_stress(
        "demand-downside-v1",
        decision.digital_twin.minimum_cash,
        decision.digital_twin.default_month,
        [boundary],
    )
    store.put_analysis(decision)
    return {"analysis_id": request.analysis_id, "stress": decision.stress}


@app.get("/analysis/{analysis_id}")
def get_analysis(analysis_id: str):
    decision = store.get_analysis(analysis_id)
    if decision is None:
        raise HTTPException(404, "analysis not found")
    return decision


@app.get("/analysis/{analysis_id}/pdf")
def get_analysis_pdf(
    analysis_id: str,
    language: str = Query("en", pattern="^(en|bn|hi)$"),
):
    decision = store.get_analysis(analysis_id)
    if decision is None:
        raise HTTPException(404, "analysis not found")
    return _pdf_response(decision, language)


@app.post("/analysis/pdf")
def build_analysis_pdf(
    decision: VentureDecision,
    language: str = Query("en", pattern="^(en|bn|hi)$"),
):
    """Build a PDF from a browser-held canonical decision after a host restart."""
    return _pdf_response(decision, language)


def _pdf_response(decision: VentureDecision, language: str) -> Response:
    if decision.selected_venture is None:
        raise HTTPException(409, "analysis has no selected venture to report")
    filename = f"GramArtha_{decision.analysis_id}_business_plan_{language}.pdf"
    payload = build_customer_pdf(decision, language)
    disposition = (
        f'attachment; filename="{filename}"; '
        f"filename*=UTF-8''{quote(filename)}"
    )
    return Response(
        content=payload,
        media_type="application/pdf",
        headers={
            "Content-Disposition": disposition,
            "Content-Length": str(len(payload)),
            "Cache-Control": "private, no-store",
            "X-Content-Type-Options": "nosniff",
        },
    )
