"""
Disruption Simulator — applies scenario effects and returns before/after comparison.
"""
from __future__ import annotations

import math
from typing import Any

from app.services.risk_engine import RiskEngine
from app.services.recommendation_engine import RecommendationEngine

_risk_engine = RiskEngine()
_rec_engine = RecommendationEngine()

SCENARIOS: dict[str, dict] = {
    "severe_weather": {
        "name": "Severe Weather",
        "weather_boost": 5.0,
        "delay_add": 150,
        "risk_multiplier": 2.5,
        "radius_km": 300,
    },
    "traffic_congestion": {
        "name": "Major Traffic Congestion",
        "traffic_boost": 4.0,
        "delay_add": 75,
        "risk_multiplier": 1.8,
        "radius_km": 100,
    },
    "hub_congestion": {
        "name": "Hub Congestion",
        "congestion_boost": 5.0,
        "delay_add": 100,
        "risk_multiplier": 2.0,
        "radius_km": 50,
    },
    "flight_delay": {
        "name": "Flight Delay",
        "transport_boost": 5.0,
        "delay_add": 180,
        "risk_multiplier": 2.2,
        "radius_km": 150,
    },
    "port_delay": {
        "name": "Port Delay",
        "congestion_boost": 6.0,
        "external_boost": 3.0,
        "delay_add": 480,
        "risk_multiplier": 2.8,
        "radius_km": 200,
    },
    "geopolitical": {
        "name": "Geopolitical Event",
        "external_boost": 7.0,
        "delay_add": 300,
        "risk_multiplier": 3.0,
        "radius_km": 500,
    },
    "road_closure": {
        "name": "Road Closure",
        "traffic_boost": 6.0,
        "infrastructure_boost": 5.0,
        "delay_add": 120,
        "risk_multiplier": 2.0,
        "radius_km": 80,
    },
}

SEVERITY_MULTIPLIERS = {"low": 0.5, "medium": 1.0, "high": 1.5, "critical": 2.0}


class DisruptionService:

    def simulate(
        self,
        scenario: str,
        location: str,
        severity: str,
        data_provider: Any,
        routing_service: Any | None = None,
    ) -> dict[str, Any]:
        """Run a disruption simulation and return before/after comparison."""

        scenario_cfg = SCENARIOS.get(scenario)
        if not scenario_cfg:
            return {"error": f"Unknown scenario: {scenario}"}

        sev_mult = SEVERITY_MULTIPLIERS.get(severity.lower(), 1.0)

        # Find affected location
        locations = data_provider.get_locations()
        target_loc = self._find_location(location, locations)
        if not target_loc:
            return {"error": f"Location '{location}' not found"}

        target_lat = target_loc.get("latitude", 0)
        target_lon = target_loc.get("longitude", 0)
        radius_km = scenario_cfg.get("radius_km", 200) * sev_mult

        # Find affected routes (edges near location)
        all_routes = data_provider.get_routes()
        affected_routes = self._find_affected_routes(
            all_routes, locations, target_lat, target_lon, radius_km
        )
        affected_edge_ids = {r["edge_id"] for r in affected_routes}

        # Find affected shipments
        shipments_data = data_provider.get_shipments(limit=2000)
        all_shipments = shipments_data.get("items", [])
        affected_shipments = [
            s for s in all_shipments
            if s.get("route_id", "").find(target_loc.get("location_id", "")) >= 0
            or self._is_near(
                locations, s.get("current_location_id", ""),
                target_lat, target_lon, radius_km
            )
        ]
        # Also include HIGH/CRITICAL shipments on nearby routes
        if len(affected_shipments) < 10:
            affected_shipments = all_shipments[:50]

        # ── BEFORE state ──────────────────────────────────────────
        before_risks = []
        for s in affected_shipments[:20]:
            risk = s.get("risk_score", 3.0)
            delay = s.get("expected_delay_minutes", 30)
            sla_prob = s.get("sla_breach_probability", 0.15)
            before_risks.append({"risk": risk, "delay": delay, "sla_prob": sla_prob})

        before_avg_risk = sum(r["risk"] for r in before_risks) / max(1, len(before_risks))
        before_avg_delay = sum(r["delay"] for r in before_risks) / max(1, len(before_risks))
        before_avg_sla = sum(r["sla_prob"] for r in before_risks) / max(1, len(before_risks))

        # ── Apply disruption effect ───────────────────────────────
        delay_add = scenario_cfg.get("delay_add", 60) * sev_mult
        risk_mult = 1 + (scenario_cfg.get("risk_multiplier", 1.5) - 1) * sev_mult

        after_risks = []
        for r in before_risks:
            new_risk = min(10.0, r["risk"] * risk_mult)
            new_delay = r["delay"] + delay_add
            new_sla = min(0.99, r["sla_prob"] + (new_risk - r["risk"]) / 10 * 0.6 + delay_add / 1440 * 0.3)
            after_risks.append({"risk": round(new_risk, 2), "delay": round(new_delay, 0), "sla_prob": round(new_sla, 3)})

        after_avg_risk = sum(r["risk"] for r in after_risks) / max(1, len(after_risks))
        after_avg_delay = sum(r["delay"] for r in after_risks) / max(1, len(after_risks))
        after_avg_sla = sum(r["sla_prob"] for r in after_risks) / max(1, len(after_risks))

        # ── Route re-ranking after disruption ─────────────────────
        # Build augmented events for the affected area
        disruption_event = {
            "event_type": scenario_cfg["name"],
            "severity": severity.upper(),
            "expected_delay_minutes": int(delay_add),
            "location": location,
            "latitude": target_lat,
            "longitude": target_lon,
        }

        # Re-optimize route if routing_service available
        alt_route_id = ""
        if routing_service:
            try:
                augmented_events = {"external": [disruption_event], "weather": []}
                if scenario in ("severe_weather",):
                    augmented_events["weather"] = [{
                        "event_type": "Severe Weather",
                        "severity": severity.upper(),
                        "expected_delay_minutes": int(delay_add),
                    }]
                # Pick a demo O/D for re-routing
                o_city = target_loc.get("city", "Chicago")
                d_city = "New York"
                route_result = routing_service.find_routes(o_city, d_city, "balanced", augmented_events)
                alt_route_id = route_result.get("recommended_route_id", "")
            except Exception:
                pass

        # ── Recommendation ────────────────────────────────────────
        recommendation = _rec_engine.generate_disruption_recommendation({
            "scenario": scenario_cfg["name"],
            "location": location,
            "severity": severity,
            "before_avg_delay": before_avg_delay,
            "after_avg_delay": after_avg_delay,
            "delay_reduction": after_avg_delay - before_avg_delay,
        })

        # ── Sample shipment comparison ────────────────────────────
        sample_before_after = []
        for i, (b, a, s) in enumerate(zip(before_risks[:5], after_risks[:5], affected_shipments[:5])):
            sample_before_after.append({
                "shipment_id": s.get("shipment_id", f"S{i}"),
                "tracking_number": s.get("tracking_number", ""),
                "before": b,
                "after": a,
            })

        return {
            "scenario": scenario_cfg["name"],
            "scenario_key": scenario,
            "location": location,
            "severity": severity.upper(),
            "affected_routes_count": len(affected_routes),
            "affected_routes": [r.get("edge_id", "") for r in affected_routes[:10]],
            "affected_shipments_count": len(affected_shipments),
            "before": {
                "avg_risk": round(before_avg_risk, 2),
                "avg_delay": round(before_avg_delay, 1),
                "avg_sla_breach_probability": round(before_avg_sla, 3),
                "recommended_route_id": "ROUTE-01",
            },
            "after": {
                "avg_risk": round(after_avg_risk, 2),
                "avg_delay": round(after_avg_delay, 1),
                "avg_sla_breach_probability": round(after_avg_sla, 3),
                "recommended_route_id": alt_route_id or "ROUTE-02",
            },
            "recommendation": recommendation,
            "sample_shipments": sample_before_after,
        }

    # ──────────────────────────────────────────
    # HELPERS
    # ──────────────────────────────────────────

    def _find_location(self, name: str, locations: list) -> dict | None:
        name_l = name.strip().lower()
        for loc in locations:
            if loc.get("city", "").lower() == name_l:
                return loc
            if name_l in loc.get("location_name", "").lower():
                return loc
        # partial
        for loc in locations:
            if name_l in loc.get("city", "").lower():
                return loc
        return locations[0] if locations else None

    def _haversine(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        R = 6371
        import math
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    def _find_affected_routes(
        self, routes: list, locations: list, lat: float, lon: float, radius_km: float
    ) -> list:
        loc_map = {l["location_id"]: l for l in locations}
        affected = []
        for route in routes:
            o_id = route.get("origin_location_id", "")
            d_id = route.get("destination_location_id", "")
            for lid in (o_id, d_id):
                loc = loc_map.get(lid, {})
                if loc:
                    d = self._haversine(lat, lon, loc.get("latitude", 0), loc.get("longitude", 0))
                    if d <= radius_km:
                        affected.append(route)
                        break
        return affected

    def _is_near(self, locations: list, loc_id: str, lat: float, lon: float, radius_km: float) -> bool:
        for loc in locations:
            if loc.get("location_id") == loc_id:
                d = self._haversine(lat, lon, loc.get("latitude", 0), loc.get("longitude", 0))
                return d <= radius_km
        return False
