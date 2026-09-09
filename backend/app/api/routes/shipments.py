from __future__ import annotations
from fastapi import APIRouter, HTTPException, Query
from app.state import get_state

router = APIRouter()


@router.get("/shipments")
def list_shipments(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: str | None = Query(None),
    risk_level: str | None = Query(None),
    search: str | None = Query(None),
    sort_by: str = Query("risk_score"),
    sort_dir: str = Query("desc"),
):
    state = get_state()
    provider = state.get("data_provider")
    if not provider:
        raise HTTPException(503, "Service not ready")
    return provider.get_shipments(
        skip=skip, limit=limit, status=status,
        risk_level=risk_level, search=search,
        sort_by=sort_by, sort_dir=sort_dir,
    )


@router.get("/shipments/{shipment_id}")
def get_shipment(shipment_id: str):
    state = get_state()
    provider = state.get("data_provider")
    if not provider:
        raise HTTPException(503, "Service not ready")
    result = provider.get_shipment(shipment_id)
    if not result:
        raise HTTPException(404, f"Shipment {shipment_id} not found")
    return result


@router.get("/shipments/{shipment_id}/risk")
def get_shipment_risk(shipment_id: str):
    state = get_state()
    provider = state.get("data_provider")
    rec_engine = state.get("recommendation_engine")
    if not provider:
        raise HTTPException(503, "Service not ready")
    risk = provider.get_risk(shipment_id)
    if not risk:
        raise HTTPException(404, f"Risk data for {shipment_id} not found")
    # Enrich with recommendation
    if rec_engine:
        shipment = provider.get_shipment(shipment_id)
        risk["recommendation"] = rec_engine.generate_shipment_recommendation(shipment, risk)
    return risk


@router.get("/shipments/{shipment_id}/timeline")
def get_shipment_timeline(shipment_id: str):
    state = get_state()
    provider = state.get("data_provider")
    if not provider:
        raise HTTPException(503, "Service not ready")
    events = provider.get_events(shipment_id)
    if not events:
        raise HTTPException(404, f"No events for shipment {shipment_id}")
    return {"shipment_id": shipment_id, "events": events, "total": len(events)}
