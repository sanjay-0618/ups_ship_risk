"""
Dataset Validation Script.
Run: python -m app.data.validate_dataset
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from datetime import datetime

import pandas as pd
import numpy as np

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "generated"


def validate() -> dict:
    print("=" * 60)
    print(" AI Logistics Platform — Dataset Validator")
    print("=" * 60)

    errors: list[str] = []
    warnings: list[str] = []
    stats: dict = {}

    def load(name: str) -> pd.DataFrame:
        p = DATA_DIR / name
        if not p.exists():
            errors.append(f"Missing file: {name}")
            return pd.DataFrame()
        return pd.read_csv(p, low_memory=False)

    # ── Load all ──────────────────────────────────────────────────
    locs = load("locations.csv")
    edges = load("route_edges.csv")
    hist = load("historical_shipments.csv")
    curr = load("current_shipments.csv")
    events = load("shipment_events.csv")
    weather = load("weather_events.csv")
    traffic = load("traffic_events.csv")
    congestion = load("congestion_events.csv")
    risk_scores = load("risk_scores.csv")
    perf = load("historical_route_performance.csv")

    # ── Locations ─────────────────────────────────────────────────
    print("\n📍 Validating locations...")
    if not locs.empty:
        stats["locations"] = len(locs)
        if len(locs) < 75:
            warnings.append(f"Only {len(locs)} locations — expected ≥75")
        dup_ids = locs["location_id"].duplicated().sum()
        if dup_ids:
            errors.append(f"Duplicate location_ids: {dup_ids}")
        null_coords = locs[locs["latitude"].isna() | locs["longitude"].isna()].shape[0]
        if null_coords:
            errors.append(f"{null_coords} locations with null coordinates")
        print(f"   ✓ {len(locs)} locations, {dup_ids} duplicates, {null_coords} null coords")

    # ── Route edges ───────────────────────────────────────────────
    print("🛣  Validating route edges...")
    if not edges.empty and not locs.empty:
        stats["route_edges"] = len(edges)
        if len(edges) < 250:
            warnings.append(f"Only {len(edges)} route edges — expected ≥250")
        loc_ids = set(locs["location_id"])
        bad_o = edges[~edges["origin_location_id"].isin(loc_ids)].shape[0]
        bad_d = edges[~edges["destination_location_id"].isin(loc_ids)].shape[0]
        if bad_o:
            errors.append(f"{bad_o} edges with invalid origin_location_id")
        if bad_d:
            errors.append(f"{bad_d} edges with invalid destination_location_id")
        same_od = edges[edges["origin_location_id"] == edges["destination_location_id"]].shape[0]
        if same_od:
            errors.append(f"{same_od} edges where origin == destination")
        neg_dist = edges[edges["distance_km"] <= 0].shape[0]
        if neg_dist:
            errors.append(f"{neg_dist} edges with non-positive distance_km")
        print(f"   ✓ {len(edges)} edges | bad_origin={bad_o} bad_dest={bad_d} same_od={same_od} neg_dist={neg_dist}")

    # ── Historical shipments ──────────────────────────────────────
    print("📦 Validating historical shipments...")
    if not hist.empty:
        stats["historical_shipments"] = len(hist)
        if len(hist) < 25000:
            warnings.append(f"Only {len(hist)} historical shipments — expected ~30,000")
        if "sla_breached" in hist.columns:
            breach_rate = hist["sla_breached"].mean()
            stats["sla_breach_rate"] = round(float(breach_rate), 3)
            if breach_rate < 0.10 or breach_rate > 0.40:
                warnings.append(f"SLA breach rate {breach_rate:.1%} outside expected 10–40% range")
        if "final_risk_score" in hist.columns:
            bad_risk = hist[(hist["final_risk_score"] < 1) | (hist["final_risk_score"] > 10)].shape[0]
            if bad_risk:
                errors.append(f"{bad_risk} historical shipments with risk_score outside [1,10]")
        if "weight_kg" in hist.columns:
            neg_weight = hist[hist["weight_kg"] <= 0].shape[0]
            if neg_weight:
                errors.append(f"{neg_weight} shipments with non-positive weight")
        if "distance_km" in hist.columns:
            neg_dist_s = hist[hist["distance_km"] <= 0].shape[0]
            if neg_dist_s:
                errors.append(f"{neg_dist_s} shipments with non-positive distance_km")
        if "origin_location_id" in hist.columns and "destination_location_id" in hist.columns:
            same_od = hist[hist["origin_location_id"] == hist["destination_location_id"]].shape[0]
            if same_od:
                errors.append(f"{same_od} historical shipments where origin == destination")
        print(f"   ✓ {len(hist):,} shipments | breach_rate={breach_rate:.1%}")

    # ── Shipment events ───────────────────────────────────────────
    print("📝 Validating shipment events...")
    if not events.empty and not hist.empty:
        stats["shipment_events"] = len(events)
        if len(events) < 50000:
            warnings.append(f"Only {len(events):,} shipment events — expected ≥100,000")
        if "shipment_id" in events.columns and "shipment_id" in hist.columns:
            hist_ids = set(hist["shipment_id"])
            orphan_events = events[~events["shipment_id"].isin(hist_ids)].shape[0]
            if orphan_events:
                errors.append(f"{orphan_events} events referencing non-existent shipment_ids")
        print(f"   ✓ {len(events):,} events")

    # ── Current shipments ─────────────────────────────────────────
    print("🚢 Validating current shipments...")
    if not curr.empty:
        stats["current_shipments"] = len(curr)
        if len(curr) < 1000:
            warnings.append(f"Only {len(curr)} current shipments — expected ≥2,000")
        if "risk_score" in curr.columns:
            bad_risk = curr[(curr["risk_score"] < 1) | (curr["risk_score"] > 10)].shape[0]
            if bad_risk:
                errors.append(f"{bad_risk} current shipments with risk_score outside [1,10]")
        if "sla_breach_probability" in curr.columns:
            bad_prob = curr[(curr["sla_breach_probability"] < 0) | (curr["sla_breach_probability"] > 1)].shape[0]
            if bad_prob:
                errors.append(f"{bad_prob} current shipments with sla_breach_probability outside [0,1]")
        print(f"   ✓ {len(curr)} current shipments")

    # ── Risk scores ───────────────────────────────────────────────
    print("⚡ Validating risk scores...")
    if not risk_scores.empty:
        stats["risk_scores"] = len(risk_scores)
        if "overall_risk_score" in risk_scores.columns:
            bad = risk_scores[(risk_scores["overall_risk_score"] < 1) | (risk_scores["overall_risk_score"] > 10)].shape[0]
            if bad:
                errors.append(f"{bad} risk_scores outside [1,10]")
        if "sla_breach_probability" in risk_scores.columns:
            bad_p = risk_scores[(risk_scores["sla_breach_probability"] < 0) | (risk_scores["sla_breach_probability"] > 1)].shape[0]
            if bad_p:
                errors.append(f"{bad_p} sla_breach_probability outside [0,1]")
        print(f"   ✓ {len(risk_scores)} risk score records")

    # ── Weather events ────────────────────────────────────────────
    print("🌩  Validating weather events...")
    if not weather.empty:
        stats["weather_events"] = len(weather)
        if len(weather) < 2000:
            warnings.append(f"Only {len(weather)} weather events — expected 3,000–5,000")
        print(f"   ✓ {len(weather)} weather events")

    # ── Traffic events ────────────────────────────────────────────
    if not traffic.empty:
        stats["traffic_events"] = len(traffic)
        if "traffic_index" in traffic.columns:
            bad_ti = traffic[(traffic["traffic_index"] < 0) | (traffic["traffic_index"] > 100)].shape[0]
            if bad_ti:
                errors.append(f"{bad_ti} traffic events with traffic_index outside [0,100]")

    # ── Summary ───────────────────────────────────────────────────
    status = "PASS" if not errors else "FAIL"
    report = {
        "status": status,
        "timestamp": datetime.now().isoformat(),
        "stats": stats,
        "errors": errors,
        "warnings": warnings,
        "error_count": len(errors),
        "warning_count": len(warnings),
    }

    print(f"\n{'=' * 60}")
    print(f" Validation Result: {status}")
    print(f"{'=' * 60}")
    if errors:
        print(f"\n❌ ERRORS ({len(errors)}):")
        for e in errors:
            print(f"   • {e}")
    if warnings:
        print(f"\n⚠  WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"   • {w}")
    if not errors and not warnings:
        print("\n✅ All checks passed!")

    # Save report
    report_path = DATA_DIR / "dataset_validation_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n📄 Report saved → {report_path}")

    return report


if __name__ == "__main__":
    result = validate()
    sys.exit(0 if result["status"] == "PASS" else 1)
