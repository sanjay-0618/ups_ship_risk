"""
Complete LocalDataProvider and SupabaseDataProvider.
Auto-detects which to use; falls back to Local if Supabase unavailable.
"""
from __future__ import annotations

import os
import json
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
from dotenv import load_dotenv

load_dotenv()
load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "generated"

# ──────────────────────────────────────────────────────────────────────────────
# Abstract base
# ──────────────────────────────────────────────────────────────────────────────

class DataProvider(ABC):
    data_source_mode: str = "unknown"

    @abstractmethod
    def get_shipments(self, skip=0, limit=100, status=None, risk_level=None, search=None, sort_by="risk_score", sort_dir="desc") -> dict: ...
    @abstractmethod
    def get_shipment(self, shipment_id: str) -> dict: ...
    @abstractmethod
    def get_risk(self, shipment_id: str) -> dict: ...
    @abstractmethod
    def get_routes(self) -> list: ...
    @abstractmethod
    def get_events(self, shipment_id: str) -> list: ...
    @abstractmethod
    def get_locations(self) -> list: ...
    @abstractmethod
    def get_disruptions(self) -> list: ...
    @abstractmethod
    def get_weather_events(self, active_only: bool = True) -> list: ...
    @abstractmethod
    def get_traffic_events(self, active_only: bool = True) -> list: ...
    @abstractmethod
    def get_congestion_events(self, active_only: bool = True) -> list: ...
    @abstractmethod
    def get_historical_shipments(self, limit: int = 1000) -> list: ...
    @abstractmethod
    def get_dashboard_summary(self) -> dict: ...
    @abstractmethod
    def get_analytics_summary(self) -> dict: ...
    @abstractmethod
    def get_route_performance(self) -> list: ...


# ──────────────────────────────────────────────────────────────────────────────
# Local CSV provider
# ──────────────────────────────────────────────────────────────────────────────

class LocalDataProvider(DataProvider):
    data_source_mode = "local"

    def __init__(self, data_dir: Path = DATA_DIR):
        self._dir = data_dir
        self._cache: dict[str, pd.DataFrame] = {}

    def _load(self, filename: str) -> pd.DataFrame:
        if filename in self._cache:
            return self._cache[filename]
        path = self._dir / filename
        if not path.exists():
            return pd.DataFrame()
        df = pd.read_csv(path, low_memory=False)
        self._cache[filename] = df
        return df

    def _df_to_records(self, df: pd.DataFrame) -> list[dict]:
        return df.where(df.notna(), None).to_dict(orient="records")

    # ── Shipments ──────────────────────────────

    def get_shipments(self, skip=0, limit=100, status=None, risk_level=None, search=None, sort_by="risk_score", sort_dir="desc") -> dict:
        df = self._load("current_shipments.csv")
        if df.empty:
            return {"items": [], "total": 0, "skip": skip, "limit": limit}

        # Join location names
        locs = self._load("locations.csv")
        if not locs.empty:
            loc_map = dict(zip(locs["location_id"], locs["city"]))
            df["origin_name"] = df["origin_location_id"].map(loc_map)
            df["destination_name"] = df["destination_location_id"].map(loc_map)
            df["current_location_name"] = df.get("current_location_id", pd.Series()).map(loc_map)

        # Filters
        if status:
            df = df[df["status"] == status]
        if risk_level:
            df = df[df["risk_level"] == risk_level]
        if search:
            s = search.lower()
            mask = (
                df.get("tracking_number", pd.Series(dtype=str)).str.lower().str.contains(s, na=False)
                | df.get("origin_name", pd.Series(dtype=str)).str.lower().str.contains(s, na=False)
                | df.get("destination_name", pd.Series(dtype=str)).str.lower().str.contains(s, na=False)
            )
            df = df[mask]

        total = len(df)

        # Sort
        valid_sort = {"risk_score", "sla_breach_probability", "expected_delay_minutes", "current_eta"}
        col = sort_by if sort_by in valid_sort and sort_by in df.columns else "risk_score"
        if col in df.columns:
            df = df.sort_values(col, ascending=(sort_dir == "asc"))

        page = df.iloc[skip: skip + limit]
        return {"items": self._df_to_records(page), "total": total, "skip": skip, "limit": limit}

    def get_shipment(self, shipment_id: str) -> dict:
        df = self._load("current_shipments.csv")
        if df.empty:
            return {}
        row = df[df["shipment_id"] == shipment_id]
        if row.empty:
            return {}
        record = self._df_to_records(row)[0]
        # Enrich with location names
        locs = self._load("locations.csv")
        if not locs.empty:
            loc_map = dict(zip(locs["location_id"], locs["city"]))
            record["origin_name"] = loc_map.get(record.get("origin_location_id"), "")
            record["destination_name"] = loc_map.get(record.get("destination_location_id"), "")
            record["current_location_name"] = loc_map.get(record.get("current_location_id"), "")
        return record

    def get_risk(self, shipment_id: str) -> dict:
        df = self._load("risk_scores.csv")
        if df.empty:
            return {}
        row = df[df["shipment_id"] == shipment_id]
        if row.empty:
            return {}
        record = self._df_to_records(row)[0]
        # Add delay breakdown from current shipments
        curr = self._load("current_shipments.csv")
        if not curr.empty:
            ship_row = curr[curr["shipment_id"] == shipment_id]
            if not ship_row.empty:
                s = self._df_to_records(ship_row)[0]
                record["delay_breakdown"] = {
                    "weather_delay": s.get("_weather_delay", 0) or 0,
                    "traffic_delay": s.get("_traffic_delay", 0) or 0,
                    "congestion_delay": s.get("_congestion_delay", 0) or 0,
                    "transport_delay": s.get("_transport_delay", 0) or 0,
                    "external_event_delay": 0,
                    "historical_delay": 0,
                    "total_delay": s.get("expected_delay_minutes", 0) or 0,
                }
        record.setdefault("delay_breakdown", {"total_delay": 0})
        record.setdefault("risk_factors", [])
        return record

    # ── Routes (edges) ─────────────────────────

    def get_routes(self) -> list:
        df = self._load("route_edges.csv")
        return self._df_to_records(df)

    # ── Events ────────────────────────────────

    def get_events(self, shipment_id: str) -> list:
        df = self._load("shipment_events.csv")
        if df.empty:
            return []
        rows = df[df["shipment_id"] == shipment_id].sort_values("timestamp")
        # Enrich with location names
        locs = self._load("locations.csv")
        records = self._df_to_records(rows)
        if not locs.empty:
            loc_map = dict(zip(locs["location_id"], locs["city"]))
            for r in records:
                r["location_name"] = loc_map.get(r.get("location_id"), "")
        return records

    # ── Locations ─────────────────────────────

    def get_locations(self) -> list:
        df = self._load("locations.csv")
        return self._df_to_records(df)

    # ── Disruptions ───────────────────────────

    def get_disruptions(self) -> list:
        """Return active weather + external events as disruptions."""
        now = datetime.now(timezone.utc).isoformat()
        disruptions = []
        weather = self.get_weather_events(active_only=True)[:20]
        for w in weather:
            disruptions.append({
                "disruption_id": w.get("event_id"),
                "type": w.get("event_type"),
                "severity": w.get("severity"),
                "location": f"({w.get('latitude', 0):.2f}, {w.get('longitude', 0):.2f})",
                "start_time": w.get("start_time"),
                "end_time": w.get("end_time"),
                "expected_delay_minutes": w.get("expected_delay_minutes", 0),
                "category": "weather",
            })
        external = self.get_external_events(active_only=True)[:10]
        for e in external:
            disruptions.append({
                "disruption_id": e.get("event_id"),
                "type": e.get("event_type"),
                "severity": e.get("severity"),
                "location": e.get("location", ""),
                "start_time": e.get("start_time"),
                "end_time": e.get("end_time"),
                "expected_delay_minutes": e.get("expected_delay_minutes", 0),
                "category": "external",
            })
        return disruptions

    def get_external_events(self, active_only: bool = True) -> list:
        df = self._load("external_events.csv")
        if df.empty:
            return []
        if active_only:
            now = datetime.now(timezone.utc).isoformat()
            try:
                df = df[df["end_time"] >= now[:10]]
            except Exception:
                pass
        return self._df_to_records(df.head(500))

    # ── Weather ───────────────────────────────

    def get_weather_events(self, active_only: bool = True) -> list:
        df = self._load("weather_events.csv")
        if df.empty:
            return []
        if active_only:
            try:
                now = datetime.now(timezone.utc).isoformat()
                df = df[df["end_time"] >= now[:10]]
            except Exception:
                pass
        return self._df_to_records(df.head(500))

    # ── Traffic ───────────────────────────────

    def get_traffic_events(self, active_only: bool = True) -> list:
        df = self._load("traffic_events.csv")
        if df.empty:
            return []
        if active_only:
            # Traffic events near "now" (within 24h of 2026-07-01)
            try:
                df = df[df["timestamp"] >= "2026-06-30"]
            except Exception:
                pass
        return self._df_to_records(df.head(500))

    # ── Congestion ────────────────────────────

    def get_congestion_events(self, active_only: bool = True) -> list:
        df = self._load("congestion_events.csv")
        if df.empty:
            return []
        if active_only:
            try:
                df = df[df["timestamp"] >= "2026-06-30"]
            except Exception:
                pass
        return self._df_to_records(df.head(500))

    # ── Historical shipments ──────────────────

    def get_historical_shipments(self, limit: int = 1000) -> list:
        df = self._load("historical_shipments.csv")
        if df.empty:
            return []
        return self._df_to_records(df.head(limit))

    # ── Route performance ─────────────────────

    def get_route_performance(self) -> list:
        df = self._load("historical_route_performance.csv")
        return self._df_to_records(df)

    # ── Dashboard summary ─────────────────────

    def get_dashboard_summary(self) -> dict:
        curr = self._load("current_shipments.csv")
        risk = self._load("risk_scores.csv")

        if curr.empty:
            return self._empty_dashboard()

        total = len(curr)
        at_risk = int(curr[curr["risk_level"].isin(["HIGH", "CRITICAL"])].shape[0])
        critical = int(curr[curr["risk_level"] == "CRITICAL"].shape[0])

        risk_dist = {
            "LOW": int((curr["risk_level"] == "LOW").sum()),
            "MEDIUM": int((curr["risk_level"] == "MEDIUM").sum()),
            "HIGH": int((curr["risk_level"] == "HIGH").sum()),
            "CRITICAL": int((curr["risk_level"] == "CRITICAL").sum()),
        }

        avg_risk = float(curr["risk_score"].mean()) if "risk_score" in curr.columns else 0.0
        avg_delay = float(curr["expected_delay_minutes"].mean()) if "expected_delay_minutes" in curr.columns else 0.0
        pred_breaches = int(curr["sla_breach_probability"].gt(0.5).sum()) if "sla_breach_probability" in curr.columns else 0

        # Active disruptions = weather HIGH/CRITICAL
        weather = self._load("weather_events.csv")
        active_disruptions = 0
        if not weather.empty:
            try:
                now_str = "2026-07"
                active_disruptions = int(
                    weather[(weather["end_time"] >= now_str) & (weather["severity"].isin(["HIGH", "CRITICAL"]))].shape[0]
                )
            except Exception:
                pass

        # Top 10 high-risk shipments
        top_risk = curr.nlargest(10, "risk_score") if "risk_score" in curr.columns else curr.head(10)
        locs = self._load("locations.csv")
        top_records = self._df_to_records(top_risk)
        if not locs.empty:
            loc_map = dict(zip(locs["location_id"], locs["city"]))
            for r in top_records:
                r["origin_name"] = loc_map.get(r.get("origin_location_id"), "")
                r["destination_name"] = loc_map.get(r.get("destination_location_id"), "")

        # Risk trend (last 12 months from historical)
        risk_trend = self._compute_risk_trend()

        return {
            "total_shipments": total,
            "at_risk_count": at_risk,
            "critical_count": critical,
            "predicted_sla_breaches": pred_breaches,
            "average_network_risk": round(avg_risk, 2),
            "average_expected_delay": round(avg_delay, 1),
            "active_disruptions_count": active_disruptions,
            "risk_distribution": risk_dist,
            "recent_high_risk_shipments": top_records,
            "risk_trend": risk_trend,
            "data_source": "local",
        }

    def _compute_risk_trend(self) -> list:
        hist = self._load("historical_shipments.csv")
        if hist.empty or "planned_date" not in hist.columns:
            return []
        try:
            hist["month"] = pd.to_datetime(hist["planned_date"]).dt.to_period("M").astype(str)
            monthly = hist.groupby("month")["final_risk_score"].mean().reset_index()
            monthly = monthly.tail(12)
            return [{"month": r["month"], "value": round(r["final_risk_score"], 2)} for _, r in monthly.iterrows()]
        except Exception:
            return []

    def _empty_dashboard(self) -> dict:
        return {
            "total_shipments": 0, "at_risk_count": 0, "critical_count": 0,
            "predicted_sla_breaches": 0, "average_network_risk": 0.0,
            "average_expected_delay": 0.0, "active_disruptions_count": 0,
            "risk_distribution": {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0},
            "recent_high_risk_shipments": [], "risk_trend": [], "data_source": "local",
        }

    # ── Analytics summary ─────────────────────

    def get_analytics_summary(self) -> dict:
        hist = self._load("historical_shipments.csv")
        if hist.empty:
            return {"data_source": "local"}

        # Monthly delay trend
        delay_trend = []
        breach_trend = []
        if "planned_date" in hist.columns:
            try:
                hist["month"] = pd.to_datetime(hist["planned_date"]).dt.to_period("M").astype(str)
                monthly = hist.groupby("month").agg(
                    avg_delay=("delay_minutes", "mean"),
                    breach_rate=("sla_breached", "mean"),
                ).reset_index().tail(24)
                delay_trend = [{"month": r["month"], "value": round(r["avg_delay"], 1)} for _, r in monthly.iterrows()]
                breach_trend = [{"month": r["month"], "value": round(r["breach_rate"], 3)} for _, r in monthly.iterrows()]
            except Exception:
                pass

        # Route reliability
        perf = self._load("historical_route_performance.csv")
        route_rel = []
        if not perf.empty:
            top = perf.nlargest(10, "route_reliability_score")
            route_rel = [
                {
                    "route_id": r["route_id"],
                    "route_name": r["route_id"],
                    "reliability_score": round(r.get("route_reliability_score", 0), 3),
                    "avg_delay": round(r.get("average_delay_minutes", 0), 1),
                    "sla_breach_rate": round(r.get("sla_breach_rate", 0), 3),
                }
                for _, r in top.iterrows()
            ]

        # Performance by priority
        perf_by_priority = []
        if "priority" in hist.columns:
            for pri, grp in hist.groupby("priority"):
                total = len(grp)
                breached = int(grp["sla_breached"].sum())
                perf_by_priority.append({
                    "priority": pri,
                    "total": total,
                    "on_time": total - breached,
                    "delayed": breached,
                    "breach_rate": round(breached / total, 3) if total else 0,
                })

        # Disruption frequency by type (approximate from event counts)
        disruption_freq = [
            {"type": "Weather", "count": len(self.get_weather_events(False)), "avg_delay": 95},
            {"type": "Traffic", "count": len(self.get_traffic_events(False)), "avg_delay": 45},
            {"type": "Congestion", "count": len(self.get_congestion_events(False)), "avg_delay": 65},
            {"type": "External", "count": len(self.get_external_events(False)), "avg_delay": 120},
        ]

        # ML model metrics (if available)
        ml_metrics = None
        metrics_path = Path(__file__).parent.parent.parent.parent.parent / "backend" / "app" / "models" / "model_metrics.json"
        if not metrics_path.exists():
            metrics_path = Path(__file__).parent.parent / "models" / "model_metrics.json"
        if metrics_path.exists():
            try:
                with open(metrics_path) as f:
                    ml_metrics = json.load(f)
            except Exception:
                pass

        return {
            "delay_trends": delay_trend,
            "sla_breach_rate_trend": breach_trend,
            "route_reliability": route_rel,
            "disruption_frequency": disruption_freq,
            "avg_delay_by_disruption_type": {
                "Weather": 95, "Traffic": 45, "Hub Congestion": 65,
                "Flight Delay": 120, "External Event": 110,
            },
            "performance_by_priority": perf_by_priority,
            "ml_model_metrics": ml_metrics,
            "data_source": "local",
        }


# ──────────────────────────────────────────────────────────────────────────────
# Supabase provider
# ──────────────────────────────────────────────────────────────────────────────

class SupabaseDataProvider(DataProvider):
    data_source_mode = "supabase"

    def __init__(self, client: Any):
        self._client = client
        self._local = LocalDataProvider()  # fallback for analytics

    def _query(self, table: str, filters: dict | None = None, limit: int = 1000) -> list:
        try:
            q = self._client.table(table).select("*").limit(limit)
            if filters:
                for col, val in filters.items():
                    q = q.eq(col, val)
            resp = q.execute()
            return resp.data or []
        except Exception:
            return []

    def get_locations(self) -> list:
        return self._query("locations", limit=200)

    def get_routes(self) -> list:
        return self._query("route_edges", limit=2000)

    def get_shipments(self, skip=0, limit=100, status=None, risk_level=None, search=None, sort_by="risk_score", sort_dir="desc") -> dict:
        try:
            q = self._client.table("shipments").select("*").range(skip, skip + limit - 1)
            if status:
                q = q.eq("status", status)
            if risk_level:
                q = q.eq("risk_level", risk_level)
            resp = q.execute()
            items = resp.data or []
            count_resp = self._client.table("shipments").select("*", count="exact").execute()
            total = count_resp.count or len(items)
            return {"items": items, "total": total, "skip": skip, "limit": limit}
        except Exception:
            return self._local.get_shipments(skip, limit, status, risk_level, search, sort_by, sort_dir)

    def get_shipment(self, shipment_id: str) -> dict:
        rows = self._query("shipments", {"shipment_id": shipment_id})
        return rows[0] if rows else {}

    def get_risk(self, shipment_id: str) -> dict:
        rows = self._query("risk_scores", {"shipment_id": shipment_id})
        return rows[0] if rows else {}

    def get_events(self, shipment_id: str) -> list:
        return self._query("shipment_events", {"shipment_id": shipment_id}, limit=50)

    def get_disruptions(self) -> list:
        return self._query("disruptions", limit=50)

    def get_weather_events(self, active_only: bool = True) -> list:
        return self._query("weather_events", limit=500)

    def get_traffic_events(self, active_only: bool = True) -> list:
        return self._query("traffic_events", limit=500)

    def get_congestion_events(self, active_only: bool = True) -> list:
        return self._query("congestion_events", limit=500)

    def get_historical_shipments(self, limit: int = 1000) -> list:
        return self._query("historical_shipments", limit=limit)

    def get_route_performance(self) -> list:
        return self._query("historical_route_performance", limit=500)

    def get_dashboard_summary(self) -> dict:
        try:
            result = self._local.get_dashboard_summary()
            result["data_source"] = "supabase"
            return result
        except Exception:
            return {"data_source": "supabase"}

    def get_analytics_summary(self) -> dict:
        result = self._local.get_analytics_summary()
        result["data_source"] = "supabase"
        return result


# ──────────────────────────────────────────────────────────────────────────────
# Auto-detect factory
# ──────────────────────────────────────────────────────────────────────────────

_provider_cache: DataProvider | None = None


def get_data_provider() -> DataProvider:
    global _provider_cache
    if _provider_cache is not None:
        return _provider_cache

    supabase_url = os.getenv("SUPABASE_URL", "")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY", "")
    data_mode = os.getenv("DATA_MODE", "auto").lower()

    if data_mode == "local" or not supabase_url or not supabase_key:
        _provider_cache = LocalDataProvider()
        return _provider_cache

    if data_mode == "supabase":
        try:
            from supabase import create_client
            client = create_client(supabase_url, supabase_key)
            # Quick connectivity test
            client.table("locations").select("location_id").limit(1).execute()
            _provider_cache = SupabaseDataProvider(client)
            return _provider_cache
        except Exception:
            _provider_cache = LocalDataProvider()
            return _provider_cache

    # AUTO: try Supabase, fall back to local
    try:
        from supabase import create_client
        client = create_client(supabase_url, supabase_key)
        client.table("locations").select("location_id").limit(1).execute()
        _provider_cache = SupabaseDataProvider(client)
    except Exception:
        _provider_cache = LocalDataProvider()

    return _provider_cache


def reset_provider_cache():
    """Call this to force re-detection on next request."""
    global _provider_cache
    _provider_cache = None
