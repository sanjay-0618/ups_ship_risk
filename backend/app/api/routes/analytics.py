from fastapi import APIRouter, HTTPException
from app.state import get_state

router = APIRouter()


@router.get("/analytics/summary")
def get_analytics_summary():
    state = get_state()
    provider = state.get("data_provider")
    predictor = state.get("sla_predictor")
    if not provider:
        raise HTTPException(503, "Service not ready")

    summary = provider.get_analytics_summary()

    # Attach ML model metrics
    if predictor and not summary.get("ml_model_metrics"):
        summary["ml_model_metrics"] = predictor.get_model_metrics()

    return summary


@router.get("/recommendations")
def get_recommendations():
    state = get_state()
    provider = state.get("data_provider")
    rec_engine = state.get("recommendation_engine")
    if not provider or not rec_engine:
        raise HTTPException(503, "Service not ready")

    # Top 10 high-risk shipments with recommendations
    result = provider.get_shipments(limit=10, sort_by="risk_score", sort_dir="desc")
    shipments = result.get("items", [])
    recommendations = []
    for s in shipments:
        risk = provider.get_risk(s.get("shipment_id", ""))
        if risk:
            rec = rec_engine.generate_shipment_recommendation(s, risk)
            recommendations.append({
                "shipment_id": s.get("shipment_id"),
                "tracking_number": s.get("tracking_number"),
                "risk_level": s.get("risk_level"),
                "risk_score": s.get("risk_score"),
                "recommendation": rec,
            })
    return {"recommendations": recommendations, "total": len(recommendations)}
