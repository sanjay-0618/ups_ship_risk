from __future__ import annotations
from fastapi import APIRouter, HTTPException
from app.state import get_state

router = APIRouter()


@router.post("/risk/calculate")
def calculate_risk(body: dict):
    """Calculate risk for arbitrary shipment+events payload."""
    state = get_state()
    risk_engine = state.get("risk_engine")
    if not risk_engine:
        raise HTTPException(503, "Risk engine not ready")
    shipment_data = body.get("shipment", {})
    events = body.get("events", {})
    return risk_engine.calculate_shipment_risk(shipment_data, events)


@router.get("/risk/events")
def get_risk_events():
    """Return all active disruption events (weather + traffic + congestion + external)."""
    state = get_state()
    provider = state.get("data_provider")
    if not provider:
        raise HTTPException(503, "Service not ready")

    weather = provider.get_weather_events(active_only=True)[:50]
    traffic = provider.get_traffic_events(active_only=True)[:50]
    congestion = provider.get_congestion_events(active_only=True)[:30]

    # Normalize into unified event format
    events = []
    for w in weather:
        events.append({
            "event_id": w.get("event_id"),
            "category": "weather",
            "event_type": w.get("event_type"),
            "severity": w.get("severity"),
            "latitude": w.get("latitude"),
            "longitude": w.get("longitude"),
            "affected_radius_km": w.get("affected_radius_km"),
            "expected_delay_minutes": w.get("expected_delay_minutes"),
            "start_time": w.get("start_time"),
            "end_time": w.get("end_time"),
        })
    for t in traffic:
        events.append({
            "event_id": t.get("event_id"),
            "category": "traffic",
            "event_type": t.get("incident_type", "Traffic"),
            "severity": t.get("congestion_level", "Moderate"),
            "traffic_index": t.get("traffic_index"),
            "expected_delay_minutes": t.get("expected_delay_minutes"),
            "timestamp": t.get("timestamp"),
        })
    for c in congestion:
        events.append({
            "event_id": c.get("event_id"),
            "category": "congestion",
            "event_type": "Hub Congestion",
            "location_id": c.get("location_id"),
            "congestion_score": c.get("congestion_score"),
            "delay_minutes": c.get("delay_minutes"),
        })

    return {
        "events": events,
        "total": len(events),
        "weather_count": len(weather),
        "traffic_count": len(traffic),
        "congestion_count": len(congestion),
    }
