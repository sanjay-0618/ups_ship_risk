from fastapi import APIRouter
from app.state import get_state

router = APIRouter()


@router.get("/dashboard/summary")
def get_dashboard_summary():
    state = get_state()
    provider = state.get("data_provider")
    if not provider:
        return {"error": "Service not ready", "data_source": "unknown"}
    return provider.get_dashboard_summary()
