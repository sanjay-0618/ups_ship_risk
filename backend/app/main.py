"""FastAPI Application — AI-Powered Predictive Logistics Platform"""
from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.state import app_state, get_state


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup; clean up on shutdown."""
    print("Starting AI Logistics Platform...")

    # Data provider (auto-detects Supabase vs local)
    from app.data.data_provider import get_data_provider
    provider = get_data_provider()
    app_state["data_provider"] = provider
    print(f"   Data source: {provider.data_source_mode}")

    # Routing service (builds NetworkX graph)
    from app.services.routing_service import RoutingService
    routing = RoutingService(provider)
    app_state["routing_service"] = routing
    print(f"   Route graph: {routing.G.number_of_nodes()} nodes, {routing.G.number_of_edges()} edges")

    # Disruption service
    from app.services.disruption_service import DisruptionService
    app_state["disruption_service"] = DisruptionService()

    # Recommendation engine
    from app.services.recommendation_engine import RecommendationEngine
    app_state["recommendation_engine"] = RecommendationEngine()

    # Risk engine
    from app.services.risk_engine import RiskEngine
    app_state["risk_engine"] = RiskEngine()

    # SLA predictor (loads model if available)
    from app.services.sla_predictor import SLAPredictor
    predictor = SLAPredictor()
    app_state["sla_predictor"] = predictor
    print(f"   SLA model loaded: {predictor.model_loaded}")

    print("Startup complete!\n")
    yield

    print("Shutting down...")
    app_state.clear()


# ── FastAPI app ────────────────────────────────────────────────
app = FastAPI(
    title="AI Logistics Platform",
    description="AI-Powered Predictive Logistics & Risk-Aware Route Optimization",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ───────────────────────────────────────────────────────
_frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
_origins = list({_frontend_url, "http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"})

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────
from app.api.routes import health, dashboard, shipments, routes, risk, disruptions, analytics  # noqa: E402

app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(dashboard.router, prefix="/api", tags=["Dashboard"])
app.include_router(shipments.router, prefix="/api", tags=["Shipments"])
app.include_router(routes.router, prefix="/api", tags=["Routes"])
app.include_router(risk.router, prefix="/api", tags=["Risk"])
app.include_router(disruptions.router, prefix="/api", tags=["Disruptions"])
app.include_router(analytics.router, prefix="/api", tags=["Analytics"])
