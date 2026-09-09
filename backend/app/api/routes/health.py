from fastapi import APIRouter
from datetime import datetime, timezone
from app.state import get_state

router = APIRouter()

@router.get("/health")
def health_check():
    state = get_state()
    provider = state.get("data_provider")
    routing = state.get("routing_service")
    predictor = state.get("sla_predictor")
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data_source": getattr(provider, "data_source_mode", "unknown"),
        "route_graph_nodes": routing.G.number_of_nodes() if routing else 0,
        "route_graph_edges": routing.G.number_of_edges() if routing else 0,
        "ml_model_loaded": getattr(predictor, "model_loaded", False),
        "version": "1.0.0",
    }
