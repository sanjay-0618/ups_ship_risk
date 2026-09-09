"""
Comprehensive Backend Test Suite for AI Logistics Platform
Verifies all Section 68 & 69 acceptance criteria.
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_01_health_check():
    print("\n[TEST 1] GET /api/health ...", end=" ")
    with TestClient(app) as c:
        res = c.get("/api/health")
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        data = res.json()
        assert data["status"] == "ok"
        assert data["data_source"] in ("local", "supabase")
        assert data["route_graph_nodes"] >= 75
        assert data["route_graph_edges"] >= 250
        print(f"PASS (Nodes: {data['route_graph_nodes']}, Edges: {data['route_graph_edges']})")


def test_02_dashboard_summary():
    print("[TEST 2] GET /api/dashboard/summary ...", end=" ")
    with TestClient(app) as c:
        res = c.get("/api/dashboard/summary")
        assert res.status_code == 200
        data = res.json()
        assert data["total_shipments"] >= 2000
        assert 1.0 <= data["average_network_risk"] <= 10.0
        assert data["average_expected_delay"] >= 0
        assert "risk_distribution" in data
        assert len(data["recent_high_risk_shipments"]) > 0
        print(f"PASS (Total Shipments: {data['total_shipments']:,}, Avg Risk: {data['average_network_risk']})")


def test_03_shipments_list_and_details():
    print("[TEST 3] GET /api/shipments & details ...", end=" ")
    with TestClient(app) as c:
        res = c.get("/api/shipments?limit=10")
        assert res.status_code == 200
        data = res.json()
        assert len(data["items"]) == 10
        first_id = data["items"][0]["shipment_id"]

        # Detail
        res_det = c.get(f"/api/shipments/{first_id}")
        assert res_det.status_code == 200
        assert res_det.json()["shipment_id"] == first_id

        # Risk
        res_risk = c.get(f"/api/shipments/{first_id}/risk")
        assert res_risk.status_code == 200
        risk_data = res_risk.json()
        assert 1.0 <= risk_data["overall_risk_score"] <= 10.0
        assert 0.0 <= risk_data["sla_breach_probability"] <= 1.0

        # Timeline
        res_time = c.get(f"/api/shipments/{first_id}/timeline")
        # May be 200 or 404 depending on whether current shipment has historical events
        assert res_time.status_code in (200, 404)
        print(f"PASS (First: {first_id}, Risk: {risk_data['overall_risk_score']})")


def test_04_chicago_new_york_route_optimization():
    print("[TEST 4] POST /api/routes/optimize (Chicago -> New York) ...", end=" ")
    with TestClient(app) as c:
        for mode in ("balanced", "fastest", "safest"):
            res = c.post("/api/routes/optimize", json={
                "origin": "Chicago",
                "destination": "New York",
                "optimization_mode": mode
            })
            assert res.status_code == 200, f"Mode {mode} failed: {res.text}"
            data = res.json()
            routes = data["routes"]
            assert len(routes) >= 3, f"Expected >=3 routes for {mode}, got {len(routes)}"
            rec_id = data["recommended_route_id"]
            assert rec_id != "", "Recommended route ID should not be empty"

            # Verify metrics
            for r in routes:
                assert r["distance_km"] > 0
                assert r["base_travel_time_minutes"] > 0
                assert r["expected_delay_minutes"] >= 0
                assert 1.0 <= r["overall_risk_score"] <= 10.0
                assert 0.0 <= r["sla_breach_probability"] <= 1.0
                assert len(r["waypoints"]) >= 2
        print(f"PASS (Found {len(routes)} alternatives, Rec: {rec_id})")


def test_05_disruption_simulation():
    print("[TEST 5] POST /api/disruptions/simulate (Louisville Storm) ...", end=" ")
    with TestClient(app) as c:
        res = c.post("/api/disruptions/simulate", json={
            "scenario": "severe_weather",
            "location": "Louisville",
            "severity": "high"
        })
        assert res.status_code == 200, f"Simulation failed: {res.text}"
        data = res.json()
        assert data["before"]["avg_risk"] < data["after"]["avg_risk"], "Risk must increase after disruption"
        assert data["before"]["avg_delay"] < data["after"]["avg_delay"], "Delay must increase after disruption"
        assert data["recommendation"]["action"] != ""
        print(f"PASS (Risk: {data['before']['avg_risk']} -> {data['after']['avg_risk']}, Delay: +{data['after']['avg_delay'] - data['before']['avg_delay']:.0f}m)")


def test_06_analytics_summary():
    print("[TEST 6] GET /api/analytics/summary ...", end=" ")
    with TestClient(app) as c:
        res = c.get("/api/analytics/summary")
        assert res.status_code == 200
        data = res.json()
        assert "delay_trends" in data
        assert "sla_breach_rate_trend" in data
        assert "route_reliability" in data
        assert "ml_model_metrics" in data
        ml = data["ml_model_metrics"]
        if ml:
            assert "accuracy" in ml
            assert "roc_auc" in ml
        print(f"PASS (ML Model: {ml.get('accuracy') if ml else 'None'})")


if __name__ == "__main__":
    print("=" * 60)
    print(" AI Logistics Platform — Backend Automated Test Suite")
    print("=" * 60)
    test_01_health_check()
    test_02_dashboard_summary()
    test_03_shipments_list_and_details()
    test_04_chicago_new_york_route_optimization()
    test_05_disruption_simulation()
    test_06_analytics_summary()
    print("\n" + "=" * 60)
    print(" ALL 6 ACCEPTANCE CRITERIA TESTS PASSED!")
    print("=" * 60)

