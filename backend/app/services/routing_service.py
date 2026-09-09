"""
NetworkX-based Route Optimization Service.
Finds K-shortest risk-aware routes between two logistics locations.
"""
from __future__ import annotations

import math
from typing import Any
import networkx as nx

from app.config import settings
from app.services.risk_engine import RiskEngine

_risk_engine = RiskEngine()


class RoutingService:
    """Builds the route graph from CSV/DB data and finds optimal paths."""

    def __init__(self, data_provider: Any):
        self.G: nx.DiGraph = nx.DiGraph()
        self._locations: dict[str, dict] = {}   # location_id → row
        self._city_to_id: dict[str, str] = {}   # city name (lower) → location_id
        self._edge_data: dict[tuple, dict] = {}  # (o,d) → edge attrs
        self._build_graph(data_provider)

    # ──────────────────────────────────────────
    # GRAPH CONSTRUCTION
    # ──────────────────────────────────────────

    def _build_graph(self, data_provider: Any) -> None:
        locations = data_provider.get_locations()
        for loc in locations:
            lid = loc["location_id"]
            self._locations[lid] = loc
            city_key = loc.get("city", "").strip().lower()
            self._city_to_id[city_key] = lid
            # Also index by full location_name lowercase
            name_key = loc.get("location_name", "").strip().lower()
            self._city_to_id[name_key] = lid

        routes = data_provider.get_routes()
        for edge in routes:
            o = edge["origin_location_id"]
            d = edge["destination_location_id"]
            dist = float(edge.get("distance_km", 100))
            base_time = float(edge.get("base_travel_time_minutes", 60))
            delay_rate = float(edge.get("historical_delay_rate", 0.1))
            avg_delay = float(edge.get("average_delay_minutes", 20))
            weather_exp = float(edge.get("weather_exposure", 0.3))
            traffic_base = float(edge.get("traffic_baseline", 0.3))
            cong_base = float(edge.get("congestion_baseline", 0.2))
            infra_risk = float(edge.get("infrastructure_risk", 0.3))
            road_q = float(edge.get("road_quality", 7))

            # Composite weight for Dijkstra (used as base; risk is added later)
            composite = base_time * (1 + delay_rate * 0.5)

            self.G.add_edge(
                o, d,
                weight=composite,
                distance=dist,
                base_time=base_time,
                delay_rate=delay_rate,
                avg_delay=avg_delay,
                weather_exposure=weather_exp,
                traffic_baseline=traffic_base,
                congestion_baseline=cong_base,
                infrastructure_risk=infra_risk,
                road_quality=road_q,
                edge_id=edge.get("edge_id", ""),
                transport_mode=edge.get("transport_mode", "road"),
            )
            self._edge_data[(o, d)] = self.G[o][d]

    # ──────────────────────────────────────────
    # PUBLIC: FIND ROUTES
    # ──────────────────────────────────────────

    def find_routes(
        self,
        origin: str,
        destination: str,
        optimization_mode: str,
        active_events: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Find ≥3 routes between origin and destination.
        Returns ranked list with recommended_route_id.
        """
        if active_events is None:
            active_events = {}

        o_id = self._find_location_id(origin)
        d_id = self._find_location_id(destination)

        if not o_id:
            return {"error": f"Origin '{origin}' not found", "routes": []}
        if not d_id:
            return {"error": f"Destination '{destination}' not found", "routes": []}
        if o_id == d_id:
            return {"error": "Origin and destination are the same", "routes": []}
        if not nx.has_path(self.G, o_id, d_id):
            return {"error": "No route found between origin and destination", "routes": []}

        # Collect K candidate paths using different strategies
        paths = self._collect_paths(o_id, d_id, k=5)
        if not paths:
            return {"error": "No feasible paths found", "routes": []}

        # Build route objects
        route_objects = []
        for idx, path in enumerate(paths):
            route = self._build_route_object(path, idx + 1, active_events, optimization_mode)
            if route:
                route_objects.append(route)

        if not route_objects:
            return {"error": "Could not calculate route metrics", "routes": []}

        # Score and rank
        ranked = self._rank_routes(route_objects, optimization_mode)

        # Mark recommended
        if ranked:
            ranked[0]["is_recommended"] = True
            recommended_id = ranked[0]["route_id"]
        else:
            recommended_id = ""

        return {
            "recommended_route_id": recommended_id,
            "routes": ranked,
            "optimization_mode": optimization_mode,
            "origin": self._locations.get(o_id, {}).get("city", origin),
            "destination": self._locations.get(d_id, {}).get("city", destination),
            "data_source": "local",
        }

    # ──────────────────────────────────────────
    # PATH COLLECTION
    # ──────────────────────────────────────────

    def _collect_paths(self, o_id: str, d_id: str, k: int = 5) -> list[list[str]]:
        paths = []
        seen: set[tuple] = set()

        # 1) Shortest by time weight
        try:
            p = nx.shortest_path(self.G, o_id, d_id, weight="weight")
            key = tuple(p)
            if key not in seen:
                paths.append(p)
                seen.add(key)
        except Exception:
            pass

        # 2) Shortest by distance
        try:
            p = nx.shortest_path(self.G, o_id, d_id, weight="distance")
            key = tuple(p)
            if key not in seen:
                paths.append(p)
                seen.add(key)
        except Exception:
            pass

        # 3) Yen's K-shortest (up to k)
        try:
            for p in nx.shortest_simple_paths(self.G, o_id, d_id, weight="weight"):
                key = tuple(p)
                if key not in seen:
                    paths.append(p)
                    seen.add(key)
                if len(paths) >= k:
                    break
        except Exception:
            pass

        # 4) Safest path (by infrastructure_risk)
        try:
            p = nx.shortest_path(self.G, o_id, d_id, weight="infrastructure_risk")
            key = tuple(p)
            if key not in seen:
                paths.append(p)
                seen.add(key)
        except Exception:
            pass

        # 5) Low-weather path (by weather_exposure)
        try:
            p = nx.shortest_path(self.G, o_id, d_id, weight="weather_exposure")
            key = tuple(p)
            if key not in seen:
                paths.append(p)
                seen.add(key)
        except Exception:
            pass

        return paths[:k]

    # ──────────────────────────────────────────
    # ROUTE OBJECT BUILDER
    # ──────────────────────────────────────────

    def _build_route_object(
        self,
        path: list[str],
        idx: int,
        active_events: dict[str, Any],
        mode: str,
    ) -> dict[str, Any] | None:
        if len(path) < 2:
            return None

        # Aggregate edge metrics
        total_dist = 0.0
        total_base_time = 0.0
        edge_attrs = []
        for a, b in zip(path[:-1], path[1:]):
            if not self.G.has_edge(a, b):
                return None
            ed = self.G[a][b]
            total_dist += ed["distance"]
            total_base_time += ed["base_time"]
            edge_attrs.append(dict(ed))

        # Build waypoints
        waypoints = []
        for seq, loc_id in enumerate(path):
            loc = self._locations.get(loc_id, {})
            waypoints.append({
                "location_id": loc_id,
                "location_name": loc.get("location_name", loc_id),
                "city": loc.get("city", loc_id),
                "latitude": loc.get("latitude", 0),
                "longitude": loc.get("longitude", 0),
                "sequence": seq,
            })

        # Risk calculation via risk engine
        route_risk = _risk_engine.calculate_route_risk(edge_attrs, active_events)

        overall_risk = route_risk["overall_risk_score"]
        expected_delay = route_risk["expected_delay_minutes"]
        risk_adjusted_time = total_base_time + expected_delay

        o_loc = self._locations.get(path[0], {})
        d_loc = self._locations.get(path[-1], {})

        route_id = f"ROUTE-{idx:02d}-{''.join(path[:3])}"
        route_name = f"Route {chr(64 + idx)}"
        if len(waypoints) >= 3:
            mid = waypoints[len(waypoints) // 2]
            route_name = f"Route {chr(64 + idx)} via {mid['city']}"

        sla_breach_prob = _risk_engine._sla_from_delay(
            expected_delay, 7200, overall_risk
        )

        # Risk factors list
        risk_factors = route_risk.get("risk_factors", [])

        return {
            "route_id": route_id,
            "route_name": route_name,
            "origin": o_loc.get("city", path[0]),
            "destination": d_loc.get("city", path[-1]),
            "waypoints": waypoints,
            "distance_km": round(total_dist, 1),
            "base_travel_time_minutes": round(total_base_time, 1),
            "expected_delay_minutes": expected_delay,
            "risk_adjusted_time_minutes": round(risk_adjusted_time, 1),
            "weather_risk": route_risk.get("weather_score", 1.0),
            "traffic_risk": route_risk.get("traffic_score", 1.0),
            "congestion_risk": route_risk.get("congestion_score", 1.0),
            "infrastructure_risk": route_risk.get("infrastructure_risk", 1.0),
            "transport_risk": route_risk.get("transport_score", 1.0),
            "external_event_risk": route_risk.get("external_event_score", 1.0),
            "historical_risk": route_risk.get("historical_score", 1.0),
            "overall_risk_score": overall_risk,
            "risk_level": route_risk["risk_level"],
            "sla_breach_probability": round(sla_breach_prob, 3),
            "final_cost": 0.0,  # filled in by ranker
            "risk_factors": risk_factors,
            "delay_breakdown": {
                "weather_delay": route_risk.get("expected_delay_minutes", 0),
                "traffic_delay": 0,
                "congestion_delay": 0,
                "transport_delay": 0,
                "external_event_delay": 0,
                "historical_delay": 0,
                "total_delay": expected_delay,
            },
            "recommendation": "",  # filled in by recommendation engine
            "is_recommended": False,
        }

    # ──────────────────────────────────────────
    # SCORING / RANKING
    # ──────────────────────────────────────────

    def _rank_routes(self, routes: list[dict], mode: str) -> list[dict]:
        if not routes:
            return routes

        times = [r["risk_adjusted_time_minutes"] for r in routes]
        dists = [r["distance_km"] for r in routes]
        risks = [r["overall_risk_score"] for r in routes]

        min_t, max_t = min(times), max(times)
        min_d, max_d = min(dists), max(dists)
        min_r, max_r = min(risks), max(risks)

        def norm(val, lo, hi):
            if hi == lo:
                return 0.0
            return (val - lo) / (hi - lo)

        mode_weights = {
            "fastest": (settings.ROUTE_FASTEST_TIME, settings.ROUTE_FASTEST_DISTANCE, settings.ROUTE_FASTEST_RISK),
            "safest":  (settings.ROUTE_SAFEST_TIME,  settings.ROUTE_SAFEST_DISTANCE,  settings.ROUTE_SAFEST_RISK),
            "balanced":(settings.ROUTE_BALANCED_TIME, settings.ROUTE_BALANCED_DISTANCE,settings.ROUTE_BALANCED_RISK),
        }
        wt, wd, wr = mode_weights.get(mode, mode_weights["balanced"])

        for r in routes:
            nt = norm(r["risk_adjusted_time_minutes"], min_t, max_t)
            nd = norm(r["distance_km"], min_d, max_d)
            nr = norm(r["overall_risk_score"], min_r, max_r)
            r["final_cost"] = round(wt * nt + wd * nd + wr * nr, 4)

        return sorted(routes, key=lambda x: x["final_cost"])

    # ──────────────────────────────────────────
    # LOCATION LOOKUP
    # ──────────────────────────────────────────

    def _find_location_id(self, name: str) -> str | None:
        if not name:
            return None
        key = name.strip().lower()
        # Exact city match
        if key in self._city_to_id:
            return self._city_to_id[key]
        # Partial match
        for k, lid in self._city_to_id.items():
            if key in k or k in key:
                return lid
        # location_id direct
        if name in self._locations:
            return name
        return None

    def get_location_names(self) -> list[str]:
        """Return list of city names for autocomplete."""
        seen = set()
        result = []
        for loc in self._locations.values():
            city = loc.get("city", "")
            if city and city not in seen:
                result.append(city)
                seen.add(city)
        return sorted(result)
