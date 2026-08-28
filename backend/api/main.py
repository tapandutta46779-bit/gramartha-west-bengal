from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles

from backend.api.contracts import AnalyzeRequest, CompareRequest, StressRequest
from backend.evidence.store import EvidenceStore
from backend.finance.digital_twin import project_monthly_cashflow
from backend.finance.stress import find_failure_boundary, summarize_stress
from backend.service import analyze

app = FastAPI(title="SIH26091 Hyperlocal Network Repair", version="0.2.0")
store = EvidenceStore(os.environ.get("SIH26091_SQLITE_PATH", ":memory:"))
frontend_path = Path(__file__).resolve().parents[2] / "frontend"
if frontend_path.exists():
    app.mount("/ui", StaticFiles(directory=frontend_path, html=True), name="ui")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "methodology_version": "decision-v2"}


@app.get("/localities/search")
def search_localities(q: str = Query(min_length=1), limit: int = Query(20, ge=1, le=100)):
    return store.search_geographies(q, limit)


@app.get("/evidence/{geo_id}")
def evidence(geo_id: str):
    return {"geo_id": geo_id, "records": store.get_evidence(geo_id)}


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
