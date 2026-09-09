"""
SLA Predictor — uses a trained RandomForestClassifier if available,
or falls back to the deterministic causal formula.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

MODEL_PATH = Path(__file__).parent.parent / "models" / "sla_model.joblib"
METRICS_PATH = Path(__file__).parent.parent / "models" / "model_metrics.json"

PRIORITY_MAP = {"Low": 0, "Normal": 1, "High": 2, "Critical": 3}
FEATURE_COLUMNS = [
    "distance_km",
    "planned_duration_minutes",
    "weather_exposure",
    "traffic_exposure",
    "congestion_exposure",
    "transport_delay_minutes",
    "external_event_exposure",
    "historical_route_delay_rate",
    "number_of_stops",
    "number_of_handoffs",
    "weight_kg",
    "priority_encoded",
]


class SLAPredictor:
    def __init__(self):
        self.model = None
        self.model_loaded = False
        self._load_model()

    def _load_model(self) -> None:
        try:
            import joblib
            if MODEL_PATH.exists():
                self.model = joblib.load(MODEL_PATH)
                self.model_loaded = True
        except Exception:
            self.model = None
            self.model_loaded = False

    def predict(self, features: dict[str, Any]) -> float:
        """Return SLA breach probability between 0 and 1."""
        if self.model_loaded and self.model is not None:
            try:
                return self._ml_predict(features)
            except Exception:
                pass
        return self._fallback_predict(features)

    def _ml_predict(self, features: dict[str, Any]) -> float:
        priority = features.get("priority", "Normal")
        priority_enc = PRIORITY_MAP.get(priority, 1)
        row = [
            features.get("distance_km", 500),
            features.get("planned_duration_minutes", 480),
            features.get("weather_exposure", 0.3),
            features.get("traffic_exposure", 0.3),
            features.get("congestion_exposure", 0.2),
            features.get("transport_delay_minutes", 0),
            features.get("external_event_exposure", 0.1),
            features.get("historical_route_delay_rate", 0.15),
            features.get("number_of_stops", 2),
            features.get("number_of_handoffs", 3),
            features.get("weight_kg", 50),
            priority_enc,
        ]
        X = np.array([row])
        prob = self.model.predict_proba(X)[0][1]
        return float(round(max(0.01, min(0.99, prob)), 3))

    def _fallback_predict(self, features: dict[str, Any]) -> float:
        """Deterministic causal probability — mirrors data generation logic."""
        base = 0.08
        weather_eff = features.get("weather_exposure", 0) * 0.35
        traffic_eff = features.get("traffic_exposure", 0) * 0.20
        congestion_eff = features.get("congestion_exposure", 0) * 0.20
        transport_eff = min(features.get("transport_delay_minutes", 0) / 480, 0.25)
        external_eff = features.get("external_event_exposure", 0) * 0.15
        historical_eff = features.get("historical_route_delay_rate", 0) * 0.10
        priority = features.get("priority", "Normal")
        priority_adj = {"Low": 0.05, "Normal": 0.0, "High": -0.05, "Critical": -0.10}.get(priority, 0)
        prob = base + weather_eff + traffic_eff + congestion_eff + transport_eff + external_eff + historical_eff + priority_adj
        return round(max(0.01, min(0.95, prob)), 3)

    def get_model_metrics(self) -> dict | None:
        if METRICS_PATH.exists():
            try:
                with open(METRICS_PATH) as f:
                    return json.load(f)
            except Exception:
                return None
        return None
