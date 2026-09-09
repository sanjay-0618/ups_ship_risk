"""
Synthetic Data Generator for AI-Powered Predictive Logistics Platform
Generates all datasets with realistic causal relationships.
SEED=42 for reproducibility.
"""
import pandas as pd
import numpy as np
import networkx as nx
import random
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

SEED = int(os.getenv("RANDOM_SEED", 42))
random.seed(SEED)
np.random.seed(SEED)

OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "generated"

CITIES = [
    ("Chicago", "IL", "US", 41.8781, -87.6298),
    ("Indianapolis", "IN", "US", 39.7684, -86.1581),
    ("Cleveland", "OH", "US", 41.4993, -81.6944),
    ("Pittsburgh", "PA", "US", 40.4406, -79.9959),
    ("Louisville", "KY", "US", 38.2527, -85.7585),
    ("Columbus", "OH", "US", 39.9612, -82.9988),
    ("Detroit", "MI", "US", 42.3314, -83.0458),
    ("Newark", "NJ", "US", 40.7357, -74.1724),
    ("New York", "NY", "US", 40.7128, -74.0060),
    ("Philadelphia", "PA", "US", 39.9526, -75.1652),
    ("Boston", "MA", "US", 42.3601, -71.0589),
    ("Memphis", "TN", "US", 35.1495, -90.0490),
    ("Atlanta", "GA", "US", 33.7490, -84.3880),
    ("Dallas", "TX", "US", 32.7767, -96.7970),
    ("Denver", "CO", "US", 39.7392, -104.9903),
    ("Kansas City", "MO", "US", 39.0997, -94.5786),
    ("Cincinnati", "OH", "US", 39.1031, -84.5120),
    ("Nashville", "TN", "US", 36.1627, -86.7816),
    ("Charlotte", "NC", "US", 35.2271, -80.8431),
    ("Baltimore", "MD", "US", 39.2904, -76.6122),
    ("Washington", "DC", "US", 38.9072, -77.0369),
    ("Richmond", "VA", "US", 37.5407, -77.4360),
    ("Raleigh", "NC", "US", 35.7796, -78.6382),
    ("Jacksonville", "FL", "US", 30.3322, -81.6557),
    ("Miami", "FL", "US", 25.7617, -80.1918),
    ("Tampa", "FL", "US", 27.9506, -82.4572),
    ("Orlando", "FL", "US", 28.5383, -81.3792),
    ("Minneapolis", "MN", "US", 44.9778, -93.2650),
    ("Milwaukee", "WI", "US", 43.0389, -87.9065),
    ("St Louis", "MO", "US", 38.6270, -90.1994),
    ("Oklahoma City", "OK", "US", 35.4676, -97.5164),
    ("Houston", "TX", "US", 29.7604, -95.3698),
    ("San Antonio", "TX", "US", 29.4241, -98.4936),
    ("Austin", "TX", "US", 30.2672, -97.7431),
    ("El Paso", "TX", "US", 31.7619, -106.4850),
    ("Albuquerque", "NM", "US", 35.0844, -106.6504),
    ("Phoenix", "AZ", "US", 33.4484, -112.0740),
    ("Las Vegas", "NV", "US", 36.1699, -115.1398),
    ("Los Angeles", "CA", "US", 34.0522, -118.2437),
    ("San Diego", "CA", "US", 32.7157, -117.1611),
    ("San Francisco", "CA", "US", 37.7749, -122.4194),
    ("Oakland", "CA", "US", 37.8044, -122.2712),
    ("Portland", "OR", "US", 45.5152, -122.6784),
    ("Seattle", "WA", "US", 47.6062, -122.3321),
    ("Salt Lake City", "UT", "US", 40.7608, -111.8910),
    ("Sacramento", "CA", "US", 38.5816, -121.4944),
    ("Fresno", "CA", "US", 36.7378, -119.7871),
    ("Tucson", "AZ", "US", 32.2226, -110.9747),
    ("Omaha", "NE", "US", 41.2565, -95.9345),
    ("Des Moines", "IA", "US", 41.5868, -93.6250),
    ("Madison", "WI", "US", 43.0731, -89.4012),
    ("Buffalo", "NY", "US", 42.8864, -78.8784),
    ("Rochester", "NY", "US", 43.1566, -77.6088),
    ("Albany", "NY", "US", 42.6526, -73.7562),
    ("Hartford", "CT", "US", 41.7658, -72.6734),
    ("Providence", "RI", "US", 41.8240, -71.4128),
    ("Manchester", "NH", "US", 42.9956, -71.4548),
    ("Portland ME", "ME", "US", 43.6591, -70.2568),
    ("Lexington", "KY", "US", 38.0406, -84.5037),
    ("Knoxville", "TN", "US", 35.9606, -83.9207),
    ("Chattanooga", "TN", "US", 35.0456, -85.3097),
    ("Birmingham", "AL", "US", 33.5186, -86.8104),
    ("Montgomery", "AL", "US", 32.3668, -86.2999),
    ("Jackson", "MS", "US", 32.2988, -90.1848),
    ("Baton Rouge", "LA", "US", 30.4515, -91.1871),
    ("New Orleans", "LA", "US", 29.9511, -90.0715),
    ("Little Rock", "AR", "US", 34.7465, -92.2896),
    ("Springfield", "MO", "US", 37.2090, -93.2923),
    ("Wichita", "KS", "US", 37.6872, -97.3301),
    ("Topeka", "KS", "US", 39.0473, -95.6752),
    ("Sioux Falls", "SD", "US", 43.5460, -96.7311),
    ("Fargo", "ND", "US", 46.8772, -96.7898),
    ("Billings", "MT", "US", 45.7833, -108.5007),
    ("Boise", "ID", "US", 43.6150, -116.2023),
    ("Spokane", "WA", "US", 47.6588, -117.4260),
]

LOCATION_TYPES = ["Distribution Center", "Hub", "Warehouse", "Airport", "Port", "Sort Facility", "Last Mile Facility"]
SHIPMENT_TYPES = ["Standard", "Express", "International", "Priority", "Fragile", "Temperature Sensitive"]
PRIORITIES = ["Low", "Normal", "High", "Critical"]
WEATHER_TYPES = ["Heavy Rain", "Snowstorm", "Thunderstorm", "Hurricane", "Tornado", "Ice", "Fog", "Extreme Wind", "Extreme Heat"]
SEVERITIES = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
TRAFFIC_INCIDENTS = ["Accident", "Construction", "Event", "Rush Hour", "Weather-related"]
EXTERNAL_TYPES = ["Geopolitical Event", "Road Closure", "Labor Strike", "Port Disruption", "Infrastructure Failure", "Security Event", "Customs Delay", "Public Event"]
SHIPMENT_EVENT_TYPES = ["Picked Up", "Departed Facility", "Arrived Hub", "Processing", "Departed Hub", "In Transit", "Customs", "Delayed", "Out for Delivery", "Delivered"]
TRANSPORT_STATUSES = ["ON_TIME", "DELAYED", "CANCELLED", "BOARDING", "IN_TRANSIT", "COMPLETED"]


def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat / 2) ** 2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon / 2) ** 2
    return R * 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))


def rand_date(start: datetime, end: datetime) -> datetime:
    return start + timedelta(seconds=random.randint(0, int((end - start).total_seconds())))


# ─────────────────────────────────────────────
# 1. LOCATIONS
# ─────────────────────────────────────────────
def generate_locations() -> pd.DataFrame:
    rng = np.random.RandomState(SEED)
    rows = []
    for i, (city, state, country, lat, lon) in enumerate(CITIES, 1):
        loc_type = rng.choice(LOCATION_TYPES)
        rows.append({
            "location_id": f"LOC{i:03d}",
            "location_name": f"{city} {loc_type}",
            "city": city,
            "state": state,
            "country": country,
            "latitude": lat,
            "longitude": lon,
            "location_type": loc_type,
            "capacity": int(rng.randint(1000, 50001)),
            "processing_capacity": int(rng.randint(100, 5001)),
            "risk_baseline": round(float(rng.uniform(0.1, 0.9)), 2),
        })
    return pd.DataFrame(rows)


# ─────────────────────────────────────────────
# 2. ROUTE EDGES
# ─────────────────────────────────────────────
def generate_route_edges(locations_df: pd.DataFrame) -> pd.DataFrame:
    rng = np.random.RandomState(SEED + 1)
    loc_map = {row["city"]: row["location_id"] for _, row in locations_df.iterrows()}

    # Guaranteed Chicago→New York corridors
    guaranteed_paths = [
        ["Chicago", "Cleveland", "Pittsburgh", "Philadelphia", "New York"],
        ["Chicago", "Indianapolis", "Columbus", "Pittsburgh", "New York"],
        ["Chicago", "Indianapolis", "Cincinnati", "Cleveland", "Buffalo", "Rochester", "Albany", "New York"],
        # Extras for richer graph
        ["Chicago", "Detroit", "Cleveland", "Buffalo", "New York"],
        ["Chicago", "Milwaukee", "Detroit", "Cleveland", "Pittsburgh", "Philadelphia", "New York"],
        ["Chicago", "Indianapolis", "Louisville", "Nashville", "Charlotte", "Richmond", "Washington", "Baltimore", "Philadelphia", "New York"],
    ]

    edge_set: set = set()
    for path in guaranteed_paths:
        for a, b in zip(path, path[1:]):
            if a in loc_map and b in loc_map:
                edge_set.add((loc_map[a], loc_map[b]))

    # Connect each location to its 4 nearest neighbours (bidirectional)
    loc_ids = locations_df["location_id"].tolist()
    loc_coords = {r["location_id"]: (r["latitude"], r["longitude"]) for _, r in locations_df.iterrows()}
    for o_id in loc_ids:
        olat, olon = loc_coords[o_id]
        neighbours = sorted(
            [(d_id, haversine(olat, olon, *loc_coords[d_id])) for d_id in loc_ids if d_id != o_id],
            key=lambda x: x[1],
        )
        for d_id, _ in neighbours[:4]:
            edge_set.add((o_id, d_id))
            edge_set.add((d_id, o_id))  # bidirectional

    rows = []
    for idx, (o, d) in enumerate(edge_set, 1):
        olat, olon = loc_coords[o]
        dlat, dlon = loc_coords[d]
        dist_km = round(haversine(olat, olon, dlat, dlon), 2)
        mode = rng.choice(["road", "road", "road", "air", "rail"])
        speed = {"road": 80, "air": 700, "rail": 120}.get(mode, 80)
        road_quality = int(rng.randint(3, 11))
        delay_rate = round(max(0.05, 0.45 - road_quality * 0.035 + float(rng.uniform(-0.05, 0.05))), 3)
        # Northern routes get higher weather exposure
        weather_exp = round(min(1.0, max(0.0, (olat - 25) / 40 + float(rng.uniform(-0.2, 0.2)))), 2)
        rows.append({
            "edge_id": f"EDGE{idx:04d}",
            "origin_location_id": o,
            "destination_location_id": d,
            "distance_km": dist_km,
            "base_travel_time_minutes": round(dist_km / speed * 60, 1),
            "road_quality": road_quality,
            "capacity": int(rng.randint(100, 1001)),
            "historical_delay_rate": delay_rate,
            "average_delay_minutes": round(float(rng.uniform(5, 90)) * (1 + delay_rate), 1),
            "weather_exposure": weather_exp,
            "traffic_baseline": round(float(rng.uniform(0.1, 0.9)), 2),
            "congestion_baseline": round(float(rng.uniform(0.1, 0.8)), 2),
            "infrastructure_risk": round(max(0.0, min(1.0, 1 - road_quality / 10 + float(rng.uniform(-0.1, 0.1)))), 2),
            "transport_mode": mode,
        })

    return pd.DataFrame(rows)


# ─────────────────────────────────────────────
# 3. WEATHER EVENTS
# ─────────────────────────────────────────────
def generate_weather_events(locations_df: pd.DataFrame, n: int = 4000) -> pd.DataFrame:
    rng = np.random.RandomState(SEED + 2)
    start = datetime(2024, 1, 1)
    end = datetime(2026, 6, 30)
    severity_params = {
        "LOW": {"delay_mult": (1.0, 1.5), "delay_min": (5, 30), "radius": (50, 150)},
        "MEDIUM": {"delay_mult": (1.5, 2.0), "delay_min": (30, 90), "radius": (100, 300)},
        "HIGH": {"delay_mult": (2.0, 3.0), "delay_min": (90, 240), "radius": (200, 500)},
        "CRITICAL": {"delay_mult": (3.0, 5.0), "delay_min": (240, 600), "radius": (300, 800)},
    }
    rows = []
    lats = locations_df["latitude"].values
    lons = locations_df["longitude"].values
    for i in range(n):
        sev = rng.choice(SEVERITIES, p=[0.35, 0.35, 0.20, 0.10])
        p = severity_params[sev]
        base_idx = rng.randint(0, len(lats))
        lat = lats[base_idx] + float(rng.uniform(-3, 3))
        lon = lons[base_idx] + float(rng.uniform(-3, 3))
        dur_hours = float(rng.uniform(2, 72))
        s = rand_date(start, end - timedelta(hours=dur_hours))
        e = s + timedelta(hours=dur_hours)
        delay_mult = round(float(rng.uniform(*p["delay_mult"])), 2)
        exp_delay = int(rng.randint(*p["delay_min"]))
        rows.append({
            "event_id": f"WE{i+1:05d}",
            "event_type": rng.choice(WEATHER_TYPES),
            "severity": sev,
            "latitude": round(lat, 4),
            "longitude": round(lon, 4),
            "affected_radius_km": int(rng.randint(*p["radius"])),
            "start_time": s.isoformat(),
            "end_time": e.isoformat(),
            "temperature": round(float(rng.uniform(-20, 45)), 1),
            "precipitation": round(float(rng.uniform(0, 200)), 1) if sev != "Extreme Heat" else 0,
            "wind_speed": round(float(rng.uniform(0, 200)), 1),
            "visibility": round(max(0.0, float(rng.uniform(0, 10)) - ({"LOW": 0, "MEDIUM": 2, "HIGH": 5, "CRITICAL": 8}[sev])), 1),
            "delay_multiplier": delay_mult,
            "expected_delay_minutes": exp_delay,
        })
    return pd.DataFrame(rows)


# ─────────────────────────────────────────────
# 4. TRAFFIC EVENTS
# ─────────────────────────────────────────────
def generate_traffic_events(edges_df: pd.DataFrame, locations_df: pd.DataFrame, n: int = 8000) -> pd.DataFrame:
    rng = np.random.RandomState(SEED + 3)
    start = datetime(2024, 1, 1)
    end = datetime(2026, 6, 30)
    edge_ids = edges_df["edge_id"].tolist()
    loc_ids = locations_df["location_id"].tolist()
    rows = []
    for i in range(n):
        traffic_idx = int(rng.randint(0, 101))
        if traffic_idx <= 30:
            level, normal_speed = "Low", 90
        elif traffic_idx <= 60:
            level, normal_speed = "Moderate", 70
        elif traffic_idx <= 80:
            level, normal_speed = "High", 45
        else:
            level, normal_speed = "Severe", 20
        avg_speed = max(5, int(normal_speed * (1 - traffic_idx / 200)))
        exp_delay = int(traffic_idx * 1.8)
        rows.append({
            "event_id": f"TE{i+1:05d}",
            "route_edge_id": rng.choice(edge_ids),
            "location_id": rng.choice(loc_ids),
            "timestamp": rand_date(start, end).isoformat(),
            "congestion_level": level,
            "average_speed_kmh": avg_speed,
            "normal_speed_kmh": normal_speed,
            "traffic_index": traffic_idx,
            "incident_type": rng.choice(TRAFFIC_INCIDENTS),
            "expected_delay_minutes": exp_delay,
        })
    return pd.DataFrame(rows)


# ─────────────────────────────────────────────
# 5. CONGESTION EVENTS
# ─────────────────────────────────────────────
def generate_congestion_events(locations_df: pd.DataFrame, n: int = 4000) -> pd.DataFrame:
    rng = np.random.RandomState(SEED + 4)
    start = datetime(2024, 1, 1)
    end = datetime(2026, 6, 30)
    rows = []
    for i in range(n):
        row = locations_df.iloc[rng.randint(0, len(locations_df))]
        proc_cap = int(row["processing_capacity"])
        load_factor = float(rng.uniform(0.4, 1.8))
        current_load = int(proc_cap * load_factor)
        queue = max(0, int((current_load - proc_cap) * float(rng.uniform(0.5, 2.0)))) if current_load > proc_cap else 0
        avg_proc_time = round(30 + (queue / max(1, proc_cap)) * 120, 1)
        delay = int(max(0, (current_load - proc_cap) / max(1, proc_cap) * 90))
        cong_score = round(min(1.0, current_load / max(1, proc_cap) / 1.5), 2)
        rows.append({
            "event_id": f"CE{i+1:05d}",
            "location_id": row["location_id"],
            "location_type": row["location_type"],
            "timestamp": rand_date(start, end).isoformat(),
            "congestion_score": cong_score,
            "processing_capacity": proc_cap,
            "current_load": current_load,
            "queue_length": queue,
            "average_processing_time": avg_proc_time,
            "delay_minutes": delay,
        })
    return pd.DataFrame(rows)


# ─────────────────────────────────────────────
# 6. TRANSPORT / FLIGHT EVENTS
# ─────────────────────────────────────────────
def generate_transport_events(locations_df: pd.DataFrame, n: int = 2000) -> pd.DataFrame:
    rng = np.random.RandomState(SEED + 5)
    start = datetime(2024, 1, 1)
    end = datetime(2026, 6, 30)
    airports = locations_df[locations_df["location_type"].isin(["Airport", "Hub"])]["location_id"].tolist()
    if len(airports) < 2:
        airports = locations_df["location_id"].tolist()
    rows = []
    for i in range(n):
        o = rng.choice(airports)
        d = rng.choice([x for x in airports if x != o])
        sched_dep = rand_date(start, end)
        flight_hrs = float(rng.uniform(1, 8))
        sched_arr = sched_dep + timedelta(hours=flight_hrs)
        weather_impact = float(rng.uniform(0, 1))
        airport_cong = float(rng.uniform(0, 1))
        delay_prob = 0.15 + weather_impact * 0.35 + airport_cong * 0.20
        delayed = rng.random() < delay_prob
        cancelled = rng.random() < 0.03
        if cancelled:
            delay_min = int(rng.randint(480, 1441))
            status = "CANCELLED"
        elif delayed:
            delay_min = int(rng.randint(30, 300))
            status = "DELAYED"
        else:
            delay_min = 0
            status = rng.choice(["ON_TIME", "COMPLETED", "BOARDING", "IN_TRANSIT"])
        actual_dep = sched_dep + timedelta(minutes=delay_min)
        actual_arr = sched_arr + timedelta(minutes=delay_min)
        rows.append({
            "transport_id": f"TR{i+1:05d}",
            "flight_number": f"UA{rng.randint(100, 9999)}",
            "origin_location_id": o,
            "destination_location_id": d,
            "scheduled_departure": sched_dep.isoformat(),
            "actual_departure": actual_dep.isoformat(),
            "scheduled_arrival": sched_arr.isoformat(),
            "actual_arrival": actual_arr.isoformat(),
            "delay_minutes": delay_min,
            "status": status,
            "weather_impact": round(weather_impact, 2),
            "airport_congestion": round(airport_cong, 2),
        })
    return pd.DataFrame(rows)


# ─────────────────────────────────────────────
# 7. EXTERNAL EVENTS
# ─────────────────────────────────────────────
def generate_external_events(locations_df: pd.DataFrame, n: int = 1200) -> pd.DataFrame:
    rng = np.random.RandomState(SEED + 6)
    start = datetime(2024, 1, 1)
    end = datetime(2026, 6, 30)
    titles = {
        "Geopolitical Event": ["Trade restrictions imposed", "Border control tightened", "Tariff increase announced"],
        "Road Closure": ["Highway section closed for repairs", "Bridge weight restriction", "Emergency road closure"],
        "Labor Strike": ["Port workers strike", "Truck drivers work stoppage", "Warehouse staff walkout"],
        "Port Disruption": ["Port congestion surge", "Equipment malfunction at terminal", "Vessel backlog"],
        "Infrastructure Failure": ["Bridge structural issue", "Rail track damage", "Power outage at facility"],
        "Security Event": ["Facility lockdown", "Security inspection delays", "Heightened screening"],
        "Customs Delay": ["Increased customs inspections", "Documentation backlog", "System outage at customs"],
        "Public Event": ["Major sporting event causing traffic", "Political rally road closures", "Festival road closures"],
    }
    severity_delay = {"LOW": (10, 60), "MEDIUM": (60, 180), "HIGH": (180, 480), "CRITICAL": (480, 1440)}
    rows = []
    for i in range(n):
        evt_type = rng.choice(EXTERNAL_TYPES)
        sev = rng.choice(SEVERITIES, p=[0.30, 0.35, 0.25, 0.10])
        loc_row = locations_df.iloc[rng.randint(0, len(locations_df))]
        lat = loc_row["latitude"] + float(rng.uniform(-1, 1))
        lon = loc_row["longitude"] + float(rng.uniform(-1, 1))
        dur_hours = float(rng.uniform(4, 168))
        s = rand_date(start, end - timedelta(hours=dur_hours))
        e = s + timedelta(hours=dur_hours)
        exp_delay = int(rng.randint(*severity_delay[sev]))
        title_list = titles.get(evt_type, ["Event"])
        rows.append({
            "event_id": f"EE{i+1:05d}",
            "event_type": evt_type,
            "title": rng.choice(title_list),
            "severity": sev,
            "location": loc_row["city"],
            "latitude": round(lat, 4),
            "longitude": round(lon, 4),
            "start_time": s.isoformat(),
            "end_time": e.isoformat(),
            "affected_radius_km": int(rng.randint(50, 500)),
            "impact_type": rng.choice(["Delay", "Route Closure", "Capacity Reduction", "Inspection Required"]),
            "expected_delay_minutes": exp_delay,
            "description": f"{evt_type} near {loc_row['city']} — severity {sev}. Expected delays of up to {exp_delay} minutes.",
        })
    return pd.DataFrame(rows)


# ─────────────────────────────────────────────
# 8. HISTORICAL SHIPMENTS  (causal model)
# ─────────────────────────────────────────────
def generate_historical_shipments(
    locations_df: pd.DataFrame,
    edges_df: pd.DataFrame,
    weather_df: pd.DataFrame,
    traffic_df: pd.DataFrame,
    congestion_df: pd.DataFrame,
    transport_df: pd.DataFrame,
    external_df: pd.DataFrame,
    n: int = 30000,
) -> pd.DataFrame:
    rng = np.random.RandomState(SEED + 7)
    start = datetime(2024, 1, 1)
    end = datetime(2026, 6, 30)
    loc_ids = locations_df["location_id"].tolist()
    loc_coords = {r["location_id"]: (r["latitude"], r["longitude"]) for _, r in locations_df.iterrows()}

    # Build NetworkX graph for paths
    G = nx.DiGraph()
    for _, e in edges_df.iterrows():
        G.add_edge(e["origin_location_id"], e["destination_location_id"],
                   distance=e["distance_km"], time=e["base_travel_time_minutes"],
                   delay_rate=e["historical_delay_rate"], avg_delay=e["average_delay_minutes"],
                   weather_exp=e["weather_exposure"], traffic_base=e["traffic_baseline"],
                   edge_id=e["edge_id"])

    # Pre-aggregate event stats for fast lookup (by month-location bucket)
    weather_df["start_dt"] = pd.to_datetime(weather_df["start_time"])
    traffic_df["ts_dt"] = pd.to_datetime(traffic_df["timestamp"])
    congestion_df["ts_dt"] = pd.to_datetime(congestion_df["timestamp"])
    transport_df["dep_dt"] = pd.to_datetime(transport_df["scheduled_departure"])
    external_df["start_dt"] = pd.to_datetime(external_df["start_time"])

    severity_score_map = {"LOW": 0.15, "MEDIUM": 0.35, "HIGH": 0.65, "CRITICAL": 0.90}
    priority_breach_effect = {"Low": 0.05, "Normal": 0.0, "High": -0.05, "Critical": -0.10}

    rows = []
    for i in range(n):
        o_id = rng.choice(loc_ids)
        candidates = [x for x in loc_ids if x != o_id]
        d_id = rng.choice(candidates)

        # Find path
        try:
            path = nx.shortest_path(G, o_id, d_id, weight="time")
        except nx.NetworkXNoPath:
            # fallback: pick random pair with edge
            edge_row = edges_df.iloc[rng.randint(0, len(edges_df))]
            o_id = edge_row["origin_location_id"]
            d_id = edge_row["destination_location_id"]
            path = [o_id, d_id]

        # Route attributes
        route_edges = []
        total_dist = 0.0
        base_time = 0.0
        avg_delay_rate = 0.0
        avg_delay_mins = 0.0
        avg_weather_exp = 0.0
        avg_traffic_base = 0.0
        avg_cong_base = 0.0
        for a, b in zip(path[:-1], path[1:]):
            if G.has_edge(a, b):
                ed = G[a][b]
                total_dist += ed["distance"]
                base_time += ed["time"]
                avg_delay_rate += ed["delay_rate"]
                avg_delay_mins += ed["avg_delay"]
                avg_weather_exp += ed["weather_exp"]
                avg_traffic_base += ed["traffic_base"]
                route_edges.append(ed["edge_id"])

        n_edges = max(1, len(path) - 1)
        avg_delay_rate /= n_edges
        avg_delay_mins /= n_edges
        avg_weather_exp /= n_edges
        avg_traffic_base /= n_edges

        # Shipment attributes
        s_type = rng.choice(SHIPMENT_TYPES, p=[0.35, 0.25, 0.15, 0.10, 0.10, 0.05])
        priority = rng.choice(PRIORITIES, p=[0.20, 0.45, 0.25, 0.10])
        weight_kg = round(float(rng.exponential(50)) + 0.1, 2)
        n_stops = len(path) - 1
        n_handoffs = n_stops + int(rng.randint(0, 3))
        sla_limit = {"Low": 10080, "Normal": 7200, "High": 4320, "Critical": 2880}[priority]

        # Pick date
        planned_dt = rand_date(start, end - timedelta(days=10))
        planned_dur = base_time
        sla_mins = sla_limit

        # Event exposures (simplified fast approximation)
        weather_exposure = round(float(avg_weather_exp * rng.uniform(0.5, 1.5)), 3)
        weather_exposure = min(1.0, weather_exposure)
        traffic_exposure = round(float(avg_traffic_base * rng.uniform(0.5, 1.5)), 3)
        traffic_exposure = min(1.0, traffic_exposure)
        congestion_exposure = round(float(rng.uniform(0.0, 0.8)), 3)
        transport_delay_mins = int(rng.choice([0, 0, 0, 30, 60, 120, 240], p=[0.5, 0.15, 0.15, 0.08, 0.06, 0.04, 0.02]))
        external_exposure = round(float(rng.uniform(0.0, 0.5)), 3)

        # Causal delay calculation
        weather_delay = int(weather_exposure * rng.uniform(0, 180))
        traffic_delay = int(traffic_exposure * rng.uniform(0, 90))
        congestion_delay = int(congestion_exposure * rng.uniform(0, 120))
        external_delay = int(external_exposure * rng.uniform(0, 60))
        historical_delay = int(avg_delay_mins * 0.3)
        total_delay = weather_delay + traffic_delay + congestion_delay + transport_delay_mins + external_delay + historical_delay
        expected_delay = total_delay

        actual_dur = planned_dur + total_delay
        actual_dt = planned_dt + timedelta(minutes=actual_dur)
        actual_planned_delivery = planned_dt + timedelta(minutes=planned_dur)

        # SLA breach — causal probability
        base_prob = 0.08
        weather_eff = weather_exposure * 0.35
        traffic_eff = traffic_exposure * 0.20
        congestion_eff = congestion_exposure * 0.20
        transport_eff = min(transport_delay_mins / 480, 0.25)
        external_eff = external_exposure * 0.15
        hist_eff = avg_delay_rate * 0.10
        priority_eff = priority_breach_effect.get(priority, 0)
        breach_prob = max(0.01, min(0.95, base_prob + weather_eff + traffic_eff + congestion_eff + transport_eff + external_eff + hist_eff + priority_eff))
        sla_breached = bool(rng.random() < breach_prob)

        # Risk score (1–10)
        weather_score = min(10, max(1, weather_exposure * 10))
        traffic_score = min(10, max(1, traffic_exposure * 10))
        congestion_score = min(10, max(1, congestion_exposure * 10))
        transport_score = min(10, max(1, min(transport_delay_mins / 48, 10)))
        external_score = min(10, max(1, external_exposure * 10))
        hist_score = min(10, max(1, avg_delay_rate * 25))
        ship_score = min(10, max(1, (1 if s_type in ["Fragile", "Temperature Sensitive"] else 0) * 3 + (weight_kg / 500)))
        raw_risk = (
            weather_score * 0.20 + traffic_score * 0.15 + congestion_score * 0.20 +
            transport_score * 0.15 + external_score * 0.10 + hist_score * 0.10 + ship_score * 0.10
        )
        final_risk = round(max(1.0, min(10.0, raw_risk)), 2)

        # Tracking number
        tracking = "1Z" + "".join(rng.choice(list("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"), 16))
        route_id = "RT-" + "-".join(path[:3])

        rows.append({
            "shipment_id": f"HIST{i+1:06d}",
            "tracking_number": tracking,
            "origin_location_id": o_id,
            "destination_location_id": d_id,
            "route_id": route_id,
            "shipment_type": s_type,
            "priority": priority,
            "weight_kg": weight_kg,
            "distance_km": round(total_dist, 2),
            "number_of_stops": n_stops,
            "number_of_handoffs": n_handoffs,
            "planned_duration_minutes": round(planned_dur, 1),
            "actual_duration_minutes": round(actual_dur, 1),
            "planned_delivery_time": actual_planned_delivery.isoformat(),
            "actual_delivery_time": actual_dt.isoformat(),
            "weather_exposure": weather_exposure,
            "traffic_exposure": traffic_exposure,
            "congestion_exposure": congestion_exposure,
            "transport_delay_minutes": transport_delay_mins,
            "external_event_exposure": external_exposure,
            "historical_route_delay_rate": round(avg_delay_rate, 3),
            "historical_route_avg_delay": round(avg_delay_mins, 1),
            "expected_delay_minutes": expected_delay,
            "delay_minutes": int(total_delay),
            "sla_limit_minutes": sla_mins,
            "sla_breached": sla_breached,
            "final_risk_score": final_risk,
            "planned_date": planned_dt.isoformat(),
        })

    return pd.DataFrame(rows)


# ─────────────────────────────────────────────
# 9. SHIPMENT EVENTS
# ─────────────────────────────────────────────
def generate_shipment_events(historical_df: pd.DataFrame, locations_df: pd.DataFrame) -> pd.DataFrame:
    rng = np.random.RandomState(SEED + 8)
    loc_ids = locations_df["location_id"].tolist()
    loc_coords = {r["location_id"]: (r["latitude"], r["longitude"]) for _, r in locations_df.iterrows()}
    rows = []
    evt_id = 1

    for _, ship in historical_df.iterrows():
        planned_dt = datetime.fromisoformat(ship["planned_date"])
        o_id = ship["origin_location_id"]
        d_id = ship["destination_location_id"]
        delay_mins = ship["delay_minutes"]
        sla_breached = ship["sla_breached"]

        # Build timeline
        timeline = []
        cur_time = planned_dt
        # Picked Up
        olat, olon = loc_coords.get(o_id, (0, 0))
        timeline.append(("Picked Up", o_id, cur_time, 0, olat, olon, "Shipment picked up from origin."))
        cur_time += timedelta(hours=float(rng.uniform(0.5, 2)))
        timeline.append(("Departed Facility", o_id, cur_time, 0, olat, olon, "Departed origin facility."))

        # Intermediate hubs
        n_stops = ship["number_of_stops"]
        for s in range(n_stops - 1):
            hub_id = rng.choice(loc_ids)
            hlat, hlon = loc_coords.get(hub_id, (0, 0))
            cur_time += timedelta(hours=float(rng.uniform(4, 20)))
            # Proportional delay at each hub
            hub_delay = int(delay_mins * float(rng.uniform(0.1, 0.3)) / max(1, n_stops))
            timeline.append(("Arrived Hub", hub_id, cur_time, 0, hlat, hlon, f"Arrived at hub."))
            cur_time += timedelta(hours=float(rng.uniform(0.5, 2)))
            timeline.append(("Processing", hub_id, cur_time, hub_delay, hlat, hlon, f"Processing at hub. Delay: {hub_delay}m."))
            if hub_delay > 30:
                cur_time += timedelta(minutes=hub_delay)
                timeline.append(("Delayed", hub_id, cur_time, hub_delay, hlat, hlon, f"Shipment delayed {hub_delay} minutes at hub."))
            cur_time += timedelta(hours=float(rng.uniform(0.5, 1.5)))
            timeline.append(("Departed Hub", hub_id, cur_time, 0, hlat, hlon, "Departed hub facility."))
            cur_time += timedelta(hours=float(rng.uniform(1, 6)))
            timeline.append(("In Transit", hub_id, cur_time, 0, hlat, hlon, "In transit to next location."))

        # Check if international (Customs event)
        if ship["shipment_type"] == "International":
            customs_delay = int(rng.randint(60, 480))
            cur_time += timedelta(hours=float(rng.uniform(2, 8)))
            dlat, dlon = loc_coords.get(d_id, (0, 0))
            timeline.append(("Customs", d_id, cur_time, customs_delay, dlat, dlon, f"Customs clearance. Delay: {customs_delay}m."))
            cur_time += timedelta(minutes=customs_delay)

        # Destination
        dlat, dlon = loc_coords.get(d_id, (0, 0))
        cur_time += timedelta(hours=float(rng.uniform(2, 12)))
        timeline.append(("Out for Delivery", d_id, cur_time, 0, dlat, dlon, "Out for delivery to recipient."))
        cur_time += timedelta(hours=float(rng.uniform(1, 4)))
        timeline.append(("Delivered", d_id, cur_time, 0, dlat, dlon, "Delivered to recipient."))

        for (etype, loc_id, ts, delay, lat, lon, desc) in timeline:
            rows.append({
                "event_id": f"EVT{evt_id:07d}",
                "shipment_id": ship["shipment_id"],
                "timestamp": ts.isoformat(),
                "location_id": loc_id,
                "event_type": etype,
                "status": "DELAYED" if delay > 0 else "ON_TIME",
                "delay_minutes": delay,
                "latitude": round(lat, 4),
                "longitude": round(lon, 4),
                "description": desc,
            })
            evt_id += 1

    return pd.DataFrame(rows)


# ─────────────────────────────────────────────
# 10. HISTORICAL ROUTE PERFORMANCE (derived)
# ─────────────────────────────────────────────
def generate_route_performance(historical_df: pd.DataFrame) -> pd.DataFrame:
    grp = historical_df.groupby("route_id").agg(
        total_shipments=("shipment_id", "count"),
        average_delay_minutes=("delay_minutes", "mean"),
        median_delay_minutes=("delay_minutes", "median"),
        delay_rate=("sla_breached", "mean"),
        sla_breach_rate=("sla_breached", "mean"),
        average_weather_exposure=("weather_exposure", "mean"),
        average_traffic_exposure=("traffic_exposure", "mean"),
        average_congestion_exposure=("congestion_exposure", "mean"),
    ).reset_index()
    grp["route_reliability_score"] = (1 - grp["delay_rate"]).round(3)
    grp["average_delay_minutes"] = grp["average_delay_minutes"].round(1)
    grp["median_delay_minutes"] = grp["median_delay_minutes"].round(1)
    grp["delay_rate"] = grp["delay_rate"].round(3)
    grp["sla_breach_rate"] = grp["sla_breach_rate"].round(3)
    return grp


# ─────────────────────────────────────────────
# 11. CURRENT SHIPMENTS (2000+)
# ─────────────────────────────────────────────
def generate_current_shipments(
    locations_df: pd.DataFrame,
    edges_df: pd.DataFrame,
    route_perf_df: pd.DataFrame,
    n: int = 2000,
) -> pd.DataFrame:
    rng = np.random.RandomState(SEED + 9)
    now = datetime(2026, 7, 1)
    loc_ids = locations_df["location_id"].tolist()

    G = nx.DiGraph()
    for _, e in edges_df.iterrows():
        G.add_edge(e["origin_location_id"], e["destination_location_id"],
                   distance=e["distance_km"], time=e["base_travel_time_minutes"],
                   delay_rate=e["historical_delay_rate"])

    perf_map = {r["route_id"]: r for _, r in route_perf_df.iterrows()} if len(route_perf_df) > 0 else {}
    current_statuses = ["IN_TRANSIT", "IN_TRANSIT", "IN_TRANSIT", "PROCESSING", "DELAYED", "OUT_FOR_DELIVERY"]
    rows = []
    for i in range(n):
        o_id = rng.choice(loc_ids)
        candidates = [x for x in loc_ids if x != o_id]
        d_id = rng.choice(candidates)
        try:
            path = nx.shortest_path(G, o_id, d_id, weight="time")
        except Exception:
            path = [o_id, d_id]

        route_id = "RT-" + "-".join(path[:3])
        perf = perf_map.get(route_id, {})
        hist_delay_rate = float(perf.get("sla_breach_rate", rng.uniform(0.1, 0.4)))

        planned_dep = now - timedelta(hours=float(rng.uniform(2, 48)))
        base_time = sum(G[a][b]["time"] for a, b in zip(path[:-1], path[1:]) if G.has_edge(a, b))
        planned_del = planned_dep + timedelta(minutes=base_time)

        weather_exposure = round(float(rng.uniform(0, 0.9)), 3)
        traffic_exposure = round(float(rng.uniform(0, 0.8)), 3)
        congestion_exposure = round(float(rng.uniform(0, 0.7)), 3)
        transport_delay = int(rng.choice([0, 0, 30, 60, 120], p=[0.5, 0.2, 0.15, 0.10, 0.05]))
        external_exposure = round(float(rng.uniform(0, 0.4)), 3)

        weather_delay = int(weather_exposure * rng.uniform(0, 180))
        traffic_delay = int(traffic_exposure * rng.uniform(0, 90))
        congestion_delay = int(congestion_exposure * rng.uniform(0, 120))
        total_delay = weather_delay + traffic_delay + congestion_delay + transport_delay
        expected_delay = total_delay

        priority = rng.choice(PRIORITIES, p=[0.20, 0.45, 0.25, 0.10])
        s_type = rng.choice(SHIPMENT_TYPES, p=[0.35, 0.25, 0.15, 0.10, 0.10, 0.05])

        # Risk scores
        weather_score = min(10, max(1, weather_exposure * 10))
        traffic_score = min(10, max(1, traffic_exposure * 10))
        congestion_score = min(10, max(1, congestion_exposure * 10))
        transport_score = min(10, max(1, min(transport_delay / 48, 10)))
        external_score = min(10, max(1, external_exposure * 10))
        hist_score = min(10, max(1, hist_delay_rate * 25))
        ship_score = min(10, max(1, (3 if s_type in ["Fragile", "Temperature Sensitive"] else 1)))

        raw_risk = (weather_score * 0.20 + traffic_score * 0.15 + congestion_score * 0.20 +
                    transport_score * 0.15 + external_score * 0.10 + hist_score * 0.10 + ship_score * 0.10)
        risk_score = round(max(1.0, min(10.0, raw_risk)), 2)

        if risk_score <= 3.0:
            risk_level = "LOW"
        elif risk_score <= 5.0:
            risk_level = "MEDIUM"
        elif risk_score <= 7.5:
            risk_level = "HIGH"
        else:
            risk_level = "CRITICAL"

        breach_prob = round(max(0.01, min(0.95,
            0.08 + weather_exposure * 0.35 + traffic_exposure * 0.20 +
            congestion_exposure * 0.20 + min(transport_delay / 480, 0.25) +
            external_exposure * 0.15 + hist_delay_rate * 0.10)), 3)

        current_loc = path[int(len(path) * rng.uniform(0.3, 0.8))] if len(path) > 1 else o_id
        status = rng.choice(current_statuses)
        tracking = "1Z" + "".join(rng.choice(list("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"), 16))
        eta = planned_del + timedelta(minutes=expected_delay)

        rows.append({
            "shipment_id": f"CURR{i+1:05d}",
            "tracking_number": tracking,
            "origin_location_id": o_id,
            "destination_location_id": d_id,
            "current_location_id": current_loc,
            "route_id": route_id,
            "status": status,
            "priority": priority,
            "shipment_type": s_type,
            "weight_kg": round(float(rng.exponential(50)) + 0.1, 2),
            "planned_delivery_time": planned_del.isoformat(),
            "current_eta": eta.isoformat(),
            "risk_score": risk_score,
            "risk_level": risk_level,
            "sla_breach_probability": breach_prob,
            "expected_delay_minutes": expected_delay,
            "last_updated": now.isoformat(),
            # Extra scores for risk_scores table
            "_weather_score": round(weather_score, 2),
            "_traffic_score": round(traffic_score, 2),
            "_congestion_score": round(congestion_score, 2),
            "_transport_score": round(transport_score, 2),
            "_external_score": round(external_score, 2),
            "_hist_score": round(hist_score, 2),
            "_ship_score": round(ship_score, 2),
            "_weather_delay": weather_delay,
            "_traffic_delay": traffic_delay,
            "_congestion_delay": congestion_delay,
            "_transport_delay": transport_delay,
            "_total_delay": total_delay,
        })

    return pd.DataFrame(rows)


# ─────────────────────────────────────────────
# 12. RISK SCORES TABLE
# ─────────────────────────────────────────────
def generate_risk_scores(current_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    now = datetime(2026, 7, 1).isoformat()
    for i, (_, s) in enumerate(current_df.iterrows(), 1):
        rows.append({
            "risk_id": f"RISK{i:05d}",
            "shipment_id": s["shipment_id"],
            "weather_score": s["_weather_score"],
            "traffic_score": s["_traffic_score"],
            "congestion_score": s["_congestion_score"],
            "transport_score": s["_transport_score"],
            "external_event_score": s["_external_score"],
            "historical_score": s["_hist_score"],
            "shipment_characteristics_score": s["_ship_score"],
            "overall_risk_score": s["risk_score"],
            "risk_level": s["risk_level"],
            "sla_breach_probability": s["sla_breach_probability"],
            "expected_delay_minutes": s["expected_delay_minutes"],
            "created_at": now,
        })
    return pd.DataFrame(rows)


# ─────────────────────────────────────────────
# MASTER GENERATE
# ─────────────────────────────────────────────
def generate_all(output_dir: Path = OUTPUT_DIR, n_historical: int = 30000, n_current: int = 2000):
    output_dir.mkdir(parents=True, exist_ok=True)

    print("[1/12] Generating locations...")
    locations_df = generate_locations()
    locations_df.to_csv(output_dir / "locations.csv", index=False)
    print(f"      OK: {len(locations_df)} locations")

    print("[2/12] Generating route edges...")
    edges_df = generate_route_edges(locations_df)
    edges_df.to_csv(output_dir / "route_edges.csv", index=False)
    print(f"      OK: {len(edges_df)} route edges")

    print("[3/12] Generating weather events...")
    weather_df = generate_weather_events(locations_df)
    weather_df.to_csv(output_dir / "weather_events.csv", index=False)
    print(f"      OK: {len(weather_df)} weather events")

    print("[4/12] Generating traffic events...")
    traffic_df = generate_traffic_events(edges_df, locations_df)
    traffic_df.to_csv(output_dir / "traffic_events.csv", index=False)
    print(f"      OK: {len(traffic_df)} traffic events")

    print("[5/12] Generating congestion events...")
    congestion_df = generate_congestion_events(locations_df)
    congestion_df.to_csv(output_dir / "congestion_events.csv", index=False)
    print(f"      OK: {len(congestion_df)} congestion events")

    print("[6/12] Generating transport events...")
    transport_df = generate_transport_events(locations_df)
    transport_df.to_csv(output_dir / "transport_events.csv", index=False)
    print(f"      OK: {len(transport_df)} transport events")

    print("[7/12] Generating external events...")
    external_df = generate_external_events(locations_df)
    external_df.to_csv(output_dir / "external_events.csv", index=False)
    print(f"      OK: {len(external_df)} external events")

    print(f"[8/12] Generating {n_historical} historical shipments...")
    historical_df = generate_historical_shipments(
        locations_df, edges_df, weather_df, traffic_df, congestion_df, transport_df, external_df, n=n_historical
    )
    historical_df.to_csv(output_dir / "historical_shipments.csv", index=False)
    breach_rate = historical_df["sla_breached"].mean()
    print(f"      OK: {len(historical_df)} historical shipments (SLA breach rate: {breach_rate:.1%})")

    print("[9/12] Generating shipment events (100K+)...")
    events_df = generate_shipment_events(historical_df, locations_df)
    events_df.to_csv(output_dir / "shipment_events.csv", index=False)
    print(f"      OK: {len(events_df)} shipment events")

    print("[10/12] Calculating route performance...")
    perf_df = generate_route_performance(historical_df)
    perf_df.to_csv(output_dir / "historical_route_performance.csv", index=False)
    print(f"      OK: {len(perf_df)} route performance records")

    print(f"[11/12] Generating {n_current} current shipments...")
    current_df = generate_current_shipments(locations_df, edges_df, perf_df, n=n_current)
    # Drop internal scoring columns for CSV
    csv_current = current_df.drop(columns=[c for c in current_df.columns if c.startswith("_")])
    csv_current.to_csv(output_dir / "current_shipments.csv", index=False)
    print(f"      OK: {len(current_df)} current shipments")

    print("[12/12] Generating risk scores...")
    risk_df = generate_risk_scores(current_df)
    risk_df.to_csv(output_dir / "risk_scores.csv", index=False)
    print(f"      OK: {len(risk_df)} risk score records")

    print("\n[SUCCESS] All datasets generated!")
    print(f"   Location: {output_dir.resolve()}")
    return {
        "locations": locations_df,
        "edges": edges_df,
        "weather": weather_df,
        "traffic": traffic_df,
        "congestion": congestion_df,
        "transport": transport_df,
        "external": external_df,
        "historical": historical_df,
        "events": events_df,
        "route_performance": perf_df,
        "current": current_df,
        "risk": risk_df,
    }
