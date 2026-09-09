"""
Risk Engine — calculates weighted risk score 1–10 for shipments and routes.
All scores are causally derived from active events and route characteristics.
"""
from __future__ import annotations
from typing import Any
import math
from app.config import settings, RISK_WEIGHTS


class RiskEngine:
    """
    Weighted risk calculator.

    Component weights (sum = 1.0):
      weather        0.20
      traffic        0.15
      congestion     0.20
      transport      0.15
      external       0.10
      historical     0.10
      shipment       0.10
    """

    # ──────────────────────────────────────────
    # PUBLIC API
    # ──────────────────────────────────────────

    def calculate_shipment_risk(
        self,
        shipment_data: dict[str, Any],
        events: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Calculate full risk for a single shipment.

        Parameters
        ----------
        shipment_data : dict
            Fields: weight_kg, shipment_type, priority, distance_km,
                    number_of_stops, historical_route_delay_rate, etc.
        events : dict
            Keys: weather, traffic, congestion, transport, external, historical

        Returns
        -------
        dict with individual scores, overall_risk_score (1-10), delay_breakdown, etc.
        """
        w = events.get("weather", [])
        t = events.get("traffic", [])
        c = events.get("congestion", [])
        tr = events.get("transport", [])
        ext = events.get("external", [])
        hist = events.get("historical", {})

        weather_score, weather_delay, weather_factors = self._score_weather(w)
        traffic_score, traffic_delay, traffic_factors = self._score_traffic(t)
        congestion_score, congestion_delay, congestion_factors = self._score_congestion(c)
        transport_score, transport_delay, transport_factors = self._score_transport(tr)
        external_score, external_delay, external_factors = self._score_external(ext)
        historical_score, historical_delay, historical_factors = self._score_historical(hist)
        ship_score, ship_factors = self._score_shipment(shipment_data)

        raw = (
            weather_score * RISK_WEIGHTS["weather"]
            + traffic_score * RISK_WEIGHTS["traffic"]
            + congestion_score * RISK_WEIGHTS["congestion"]
            + transport_score * RISK_WEIGHTS["transport"]
            + external_score * RISK_WEIGHTS["external"]
            + historical_score * RISK_WEIGHTS["historical"]
            + ship_score * RISK_WEIGHTS["shipment"]
        )
        overall = round(max(1.0, min(10.0, raw)), 2)
        risk_level = self._get_risk_level(overall)

        total_delay = (
            weather_delay + traffic_delay + congestion_delay
            + transport_delay + external_delay + historical_delay
        )

        all_factors = weather_factors + traffic_factors + congestion_factors + transport_factors + external_factors + historical_factors + ship_factors

        # SLA breach probability from delay contributors
        sla_prob = self._sla_from_delay(
            total_delay,
            shipment_data.get("sla_limit_minutes", 7200),
            overall,
        )

        return {
            "weather_score": round(weather_score, 2),
            "traffic_score": round(traffic_score, 2),
            "congestion_score": round(congestion_score, 2),
            "transport_score": round(transport_score, 2),
            "external_event_score": round(external_score, 2),
            "historical_score": round(historical_score, 2),
            "shipment_characteristics_score": round(ship_score, 2),
            "overall_risk_score": overall,
            "risk_level": risk_level,
            "risk_factors": all_factors[:5],  # top-5
            "delay_breakdown": {
                "weather_delay": weather_delay,
                "traffic_delay": traffic_delay,
                "congestion_delay": congestion_delay,
                "transport_delay": transport_delay,
                "external_event_delay": external_delay,
                "historical_delay": historical_delay,
                "total_delay": total_delay,
            },
            "sla_breach_probability": round(sla_prob, 3),
            "expected_delay_minutes": total_delay,
        }

    def calculate_route_risk(
        self,
        route_edges: list[dict[str, Any]],
        active_events: dict[str, Any],
    ) -> dict[str, Any]:
        """Aggregate risk across all edges of a route."""
        if not route_edges:
            return self._empty_risk()

        n = len(route_edges)
        weather_scores, traffic_scores, congestion_scores = [], [], []
        infra_scores, weather_delays, traffic_delays = [], [], []

        for edge in route_edges:
            # Weather exposure on this edge
            w_exp = edge.get("weather_exposure", 0.3)
            weather_scores.append(max(1, min(10, w_exp * 10)))
            weather_delays.append(int(w_exp * 60))

            # Traffic
            t_base = edge.get("traffic_baseline", 0.3)
            traffic_scores.append(max(1, min(10, t_base * 10)))
            traffic_delays.append(int(t_base * 45))

            # Congestion
            c_base = edge.get("congestion_baseline", 0.2)
            congestion_scores.append(max(1, min(10, c_base * 10)))

            # Infrastructure
            road_q = edge.get("road_quality", 7)
            infra_scores.append(max(1, min(10, (10 - road_q) + 1)))

        weather_score = sum(weather_scores) / n
        traffic_score = sum(traffic_scores) / n
        congestion_score = sum(congestion_scores) / n
        infra_score = sum(infra_scores) / n

        # Apply active events
        active_weather = active_events.get("weather", [])
        active_traffic = active_events.get("traffic", [])
        if active_weather:
            sev_boost = {"LOW": 1, "MEDIUM": 2, "HIGH": 4, "CRITICAL": 6}
            for ev in active_weather:
                weather_score = min(10, weather_score + sev_boost.get(ev.get("severity", "LOW"), 1))
        if active_traffic:
            for ev in active_traffic:
                ti = ev.get("traffic_index", 30)
                traffic_score = min(10, traffic_score + ti / 25)

        external_score = 1.0
        for ev in active_events.get("external", []):
            sev_boost = {"LOW": 1, "MEDIUM": 3, "HIGH": 5, "CRITICAL": 8}
            external_score = min(10, external_score + sev_boost.get(ev.get("severity", "LOW"), 1))

        historical_score = 1.0
        for ev in active_events.get("historical", []):
            breach_rate = ev.get("sla_breach_rate", 0.1)
            historical_score = max(historical_score, min(10, 1 + breach_rate * 22))

        transport_score = 1.0
        for ev in active_events.get("transport", []):
            delay = ev.get("delay_minutes", 0)
            if ev.get("status") == "CANCELLED":
                transport_score = min(10, transport_score + 8)
            elif delay > 120:
                transport_score = min(10, transport_score + 5)
            elif delay > 60:
                transport_score = min(10, transport_score + 3)
            elif delay > 0:
                transport_score = min(10, transport_score + 1.5)

        raw = (
            weather_score * RISK_WEIGHTS["weather"]
            + traffic_score * RISK_WEIGHTS["traffic"]
            + congestion_score * RISK_WEIGHTS["congestion"]
            + transport_score * RISK_WEIGHTS["transport"]
            + external_score * RISK_WEIGHTS["external"]
            + historical_score * RISK_WEIGHTS["historical"]
            + infra_score * RISK_WEIGHTS["shipment"]
        )
        overall = round(max(1.0, min(10.0, raw)), 2)

        total_delay = sum(weather_delays) + sum(traffic_delays)
        total_delay += sum(ev.get("expected_delay_minutes", 0) for ev in active_weather)
        total_delay += sum(ev.get("expected_delay_minutes", 0) for ev in active_events.get("external", []))
        total_delay += sum(ev.get("delay_minutes", 0) for ev in active_events.get("transport", []))

        return {
            "weather_score": round(weather_score, 2),
            "traffic_score": round(traffic_score, 2),
            "congestion_score": round(congestion_score, 2),
            "transport_score": round(transport_score, 2),
            "external_event_score": round(external_score, 2),
            "historical_score": round(historical_score, 2),
            "infrastructure_risk": round(infra_score, 2),
            "overall_risk_score": overall,
            "risk_level": self._get_risk_level(overall),
            "expected_delay_minutes": total_delay,
        }

    # ──────────────────────────────────────────
    # COMPONENT SCORERS
    # ──────────────────────────────────────────

    def _score_weather(self, events: list) -> tuple[float, int, list[str]]:
        if not events:
            return 1.0, 0, []
        score = 1.0
        total_delay = 0
        factors = []
        sev_map = {"LOW": (2.0, 15), "MEDIUM": (4.5, 60), "HIGH": (7.0, 150), "CRITICAL": (9.5, 300)}
        for ev in events:
            sev = ev.get("severity", "LOW")
            s, d = sev_map.get(sev, (2.0, 15))
            score = max(score, s)
            total_delay += ev.get("expected_delay_minutes", d)
            factors.append(f"{ev.get('event_type', 'Weather event')} ({sev}) — +{ev.get('expected_delay_minutes', d)}m delay")
        return min(10.0, score), total_delay, factors[:2]

    def _score_traffic(self, events: list) -> tuple[float, int, list[str]]:
        if not events:
            return 1.0, 0, []
        avg_idx = sum(ev.get("traffic_index", 20) for ev in events) / len(events)
        if avg_idx <= 30:
            score = 1 + avg_idx / 30 * 2
        elif avg_idx <= 60:
            score = 3 + (avg_idx - 30) / 30 * 3
        elif avg_idx <= 80:
            score = 6 + (avg_idx - 60) / 20 * 2
        else:
            score = 8 + (avg_idx - 80) / 20 * 2
        total_delay = int(sum(ev.get("expected_delay_minutes", 0) for ev in events))
        factors = [f"Traffic congestion (index {avg_idx:.0f}) — +{total_delay}m delay"] if total_delay > 0 else []
        return min(10.0, score), total_delay, factors

    def _score_congestion(self, events: list) -> tuple[float, int, list[str]]:
        if not events:
            return 1.0, 0, []
        avg_score = sum(ev.get("congestion_score", 0.2) for ev in events) / len(events)
        score = max(1.0, avg_score * 10)
        total_delay = int(sum(ev.get("delay_minutes", 0) for ev in events))
        factors = [f"Hub congestion at {ev.get('location_id', 'hub')} — +{ev.get('delay_minutes', 0)}m" for ev in events[:2]]
        return min(10.0, score), total_delay, factors

    def _score_transport(self, events: list) -> tuple[float, int, list[str]]:
        if not events:
            return 1.0, 0, []
        score = 1.0
        total_delay = 0
        factors = []
        for ev in events:
            status = ev.get("status", "ON_TIME")
            delay = ev.get("delay_minutes", 0)
            if status == "CANCELLED":
                score = max(score, 9.5)
                total_delay += 480
                factors.append(f"Flight {ev.get('flight_number', '')} CANCELLED")
            elif delay > 120:
                score = max(score, 7.5)
                total_delay += delay
                factors.append(f"Flight {ev.get('flight_number', '')} delayed {delay}m")
            elif delay > 60:
                score = max(score, 5.5)
                total_delay += delay
            elif delay > 0:
                score = max(score, 3.5)
                total_delay += delay
        return min(10.0, score), total_delay, factors[:2]

    def _score_external(self, events: list) -> tuple[float, int, list[str]]:
        if not events:
            return 1.0, 0, []
        score = 1.0
        total_delay = 0
        factors = []
        sev_map = {"LOW": 2.0, "MEDIUM": 4.0, "HIGH": 6.5, "CRITICAL": 9.0}
        for ev in events:
            sev = ev.get("severity", "LOW")
            score = max(score, sev_map.get(sev, 2.0))
            total_delay += ev.get("expected_delay_minutes", 0)
            factors.append(f"{ev.get('event_type', 'Event')} near {ev.get('location', '')} ({sev})")
        return min(10.0, score), total_delay, factors[:2]

    def _score_historical(self, hist: dict) -> tuple[float, int, list[str]]:
        if not hist:
            return 1.0, 0, []
        breach_rate = hist.get("sla_breach_rate", 0.1)
        avg_delay = hist.get("average_delay_minutes", 0)
        score = max(1.0, min(10.0, 1 + breach_rate * 22))
        hist_delay = int(avg_delay * 0.3)
        factors = []
        if breach_rate > 0.2:
            factors.append(f"Historical SLA breach rate {breach_rate:.0%} on this corridor")
        return score, hist_delay, factors

    def _score_shipment(self, data: dict) -> tuple[float, list[str]]:
        score = 1.0
        factors = []
        s_type = data.get("shipment_type", "Standard")
        if s_type in ("Fragile", "Temperature Sensitive"):
            score += 3.0
            factors.append(f"{s_type} shipment requires extra care")
        weight = data.get("weight_kg", 0)
        if weight > 500:
            score += 1.5
            factors.append(f"Heavy shipment ({weight:.0f} kg)")
        priority = data.get("priority", "Normal")
        if priority == "Critical":
            score += 1.0
        return min(10.0, score), factors

    # ──────────────────────────────────────────
    # HELPERS
    # ──────────────────────────────────────────

    def _get_risk_level(self, score: float) -> str:
        if score <= settings.RISK_LOW_MAX:
            return "LOW"
        elif score <= settings.RISK_MEDIUM_MAX:
            return "MEDIUM"
        elif score <= settings.RISK_HIGH_MAX:
            return "HIGH"
        return "CRITICAL"

    def _sla_from_delay(self, total_delay: int, sla_limit: int, risk_score: float) -> float:
        base = 0.05
        delay_factor = min(total_delay / max(1, sla_limit), 0.60)
        risk_factor = (risk_score - 1) / 9 * 0.35
        return max(0.01, min(0.99, base + delay_factor + risk_factor))

    def _empty_risk(self) -> dict:
        return {
            "weather_score": 1.0, "traffic_score": 1.0, "congestion_score": 1.0,
            "transport_score": 1.0, "external_event_score": 1.0, "historical_score": 1.0,
            "shipment_characteristics_score": 1.0, "overall_risk_score": 1.0,
            "risk_level": "LOW", "risk_factors": [],
            "delay_breakdown": {k: 0 for k in ["weather_delay", "traffic_delay", "congestion_delay", "transport_delay", "external_event_delay", "historical_delay", "total_delay"]},
            "sla_breach_probability": 0.05, "expected_delay_minutes": 0,
        }

    def _normalize_to_10(self, value: float, min_val: float, max_val: float) -> float:
        if max_val <= min_val:
            return 1.0
        return max(1.0, min(10.0, 1 + 9 * (value - min_val) / (max_val - min_val)))
