from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.state import get_state

router = APIRouter()


class DisruptionSimulateRequest(BaseModel):
    scenario: str          # severe_weather | traffic_congestion | hub_congestion | flight_delay | port_delay | geopolitical | road_closure
    location: str
    severity: str = "high" # low | medium | high | critical


@router.post("/disruptions/simulate")
def simulate_disruption(req: DisruptionSimulateRequest):
    state = get_state()
    provider = state.get("data_provider")
    disruption_svc = state.get("disruption_service")
    routing = state.get("routing_service")

    if not provider or not disruption_svc:
        raise HTTPException(503, "Disruption service not ready")

    result = disruption_svc.simulate(
        scenario=req.scenario,
        location=req.location,
        severity=req.severity,
        data_provider=provider,
        routing_service=routing,
    )

    if "error" in result:
        raise HTTPException(422, result["error"])

    return result


@router.get("/disruptions")
def list_disruptions():
    state = get_state()
    provider = state.get("data_provider")
    if not provider:
        raise HTTPException(503, "Service not ready")
    disruptions = provider.get_disruptions()
    return {"disruptions": disruptions, "total": len(disruptions)}
