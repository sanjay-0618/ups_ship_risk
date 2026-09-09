from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.state import get_state

router = APIRouter()


class RouteOptimizeRequest(BaseModel):
    origin: str
    destination: str
    optimization_mode: str = "balanced"  # fastest | safest | balanced


@router.post("/routes/optimize")
def optimize_routes(req: RouteOptimizeRequest):
    state = get_state()
    routing = state.get("routing_service")
    provider = state.get("data_provider")
    rec_engine = state.get("recommendation_engine")

    if not routing or not provider:
        raise HTTPException(503, "Routing service not ready")

    # Gather active events
    active_events = {
        "weather": provider.get_weather_events(active_only=True)[:20],
        "traffic": provider.get_traffic_events(active_only=True)[:20],
        "congestion": provider.get_congestion_events(active_only=True)[:20],
        "external": [],
        "transport": [],
        "historical": [],
    }

    result = routing.find_routes(
        origin=req.origin,
        destination=req.destination,
        optimization_mode=req.optimization_mode,
        active_events=active_events,
    )

    if "error" in result:
        raise HTTPException(422, result["error"])

    # Add recommendation text to each route
    if rec_engine and result.get("routes"):
        for route in result["routes"]:
            if route.get("is_recommended"):
                rec = rec_engine.generate_route_recommendation(result["routes"], req.optimization_mode)
                route["recommendation"] = rec.get("action", "")
        result["recommendation"] = rec_engine.generate_route_recommendation(
            result["routes"], req.optimization_mode
        )

    return result


@router.get("/routes/{route_id}")
def get_route(route_id: str):
    state = get_state()
    provider = state.get("data_provider")
    if not provider:
        raise HTTPException(503, "Service not ready")
    routes = provider.get_routes()
    for r in routes:
        if r.get("edge_id") == route_id or r.get("route_id") == route_id:
            return r
    raise HTTPException(404, f"Route {route_id} not found")


@router.post("/routes/{route_id}/analyze")
def analyze_route(route_id: str, body: dict = {}):
    """Return risk analysis for a specific route edge."""
    state = get_state()
    provider = state.get("data_provider")
    risk_engine = state.get("risk_engine")
    if not provider or not risk_engine:
        raise HTTPException(503, "Service not ready")

    routes = provider.get_routes()
    route = next((r for r in routes if r.get("edge_id") == route_id), None)
    if not route:
        raise HTTPException(404, f"Route {route_id} not found")

    active_events = {
        "weather": provider.get_weather_events(active_only=True)[:10],
        "traffic": provider.get_traffic_events(active_only=True)[:10],
        "congestion": provider.get_congestion_events(active_only=True)[:10],
        "external": [],
        "transport": [],
        "historical": [],
    }
    risk = risk_engine.calculate_route_risk([route], active_events)
    return {"route_id": route_id, "route": route, "risk_analysis": risk}


@router.get("/locations")
def get_locations():
    state = get_state()
    provider = state.get("data_provider")
    routing = state.get("routing_service")
    if not provider:
        raise HTTPException(503, "Service not ready")
    locations = provider.get_locations()
    # Also return city name list for autocomplete
    city_names = []
    if routing:
        city_names = routing.get_location_names()
    return {"locations": locations, "city_names": city_names}
