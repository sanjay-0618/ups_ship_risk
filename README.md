<<<<<<< HEAD
# ups_ship_risk
Ups hackathon
=======
# AI-Powered Predictive Logistics & Risk-Aware Route Optimization Platform

> An enterprise-grade, hackathon-ready predictive logistics visibility and dynamic route optimization engine. Answers: *"Which shipments or routes are likely to be disrupted BEFORE the disruption happens, why, and what should operations do about it?"*

---

## 1. Project Overview

Modern logistics platforms show *where* shipments are. This platform shows **where problems will occur before they happen**, explains the causal contributors to disruption risk, and dynamically recommends risk-adjusted alternative routes across North America.

### Core Capabilities
* **Predictive Risk Engine**: Multi-signal normalized risk scoring (1.0 to 10.0 scale) combining weather, traffic, hub congestion, flight delays, external events, historical corridor performance, and cargo characteristics.
* **Risk-Aware Route Optimization**: NetworkX-powered multi-path routing evaluating distance, travel time, and real-time hazard exposure to recommend the fastest risk-adjusted path.
* **Explainable Delay Decomposition**: Every delay prediction decomposes additively into weather, traffic, hub queue, transit, and historical components.
* **ML SLA Breach Predictor**: Explainable `RandomForestClassifier` trained on 30,000 historical shipments using temporal splits (no future data leakage).
* **Interactive Disruption Simulator**: Test "what-if" disruption scenarios (severe storms, hub bottlenecks, road closures) and watch dynamic network rerouting in real time.
* **Autonomous Fallback Architecture**: Seamlessly operates in dual-mode: Supabase PostgreSQL cloud database or 100% self-contained local synthetic data.

---

## 2. Problem Statement

Supply chain operations face continuous disruptions from weather events, highway congestion, hub bottlenecks, port strikes, and infrastructure failures. Legacy systems notify operators after delays have already occurred. This platform shifts operations from **reactive fire-fighting** to **proactive mitigation**.

---

## 3. Architecture

```
                  ┌──────────────────────────────┐
                  │    React 18 + Vite + TS      │
                  │   Tailwind + Leaflet + Charts│
                  └──────────────┬───────────────┘
                                 │ REST APIs
                                 ▼
                  ┌──────────────────────────────┐
                  │       FastAPI Backend        │
                  │    Uvicorn ASGI (Port 8000)  │
                  └──────────────┬───────────────┘
                                 │
                 ┌───────────────┼───────────────┐
                 ▼               ▼               ▼
           ┌───────────┐   ┌───────────┐   ┌───────────┐
           │Risk Engine│   │Route Engine│  │ML Predict │
           │(7 Signals)│   │ (NetworkX)│   │(RandomFor)│
           └─────┬─────┘   └─────┬─────┘   └─────┬─────┘
                 └───────────────┼───────────────┘
                                 ▼
                    ┌─────────────────────────┐
                    │      DataProvider       │
                    │   (Transparent Proxy)   │
                    └────────────┬────────────┘
                                 │
                   ┌─────────────┴─────────────┐
                   ▼                           ▼
        ┌─────────────────────┐     ┌─────────────────────┐
        │ Supabase PostgreSQL │     │  Local CSV Fallback │
        │ (Cloud / Primary)   │     │ (Offline/Zero Config│
        └─────────────────────┘     └─────────────────────┘
```

---

## 4. Technology Stack

* **Frontend**: React 18, Vite, TypeScript, Tailwind CSS, React Router v6, Leaflet & React-Leaflet, Recharts, Lucide React, Axios.
* **Backend**: Python 3.11+, FastAPI, Uvicorn, Pydantic v2, NetworkX, Pandas, NumPy, Scikit-learn, Joblib.
* **Database**: Supabase (PostgreSQL 15) with Row-Level Security (RLS) and B-Tree indexing.
* **Deployment Targets**: Frontend on **Vercel**, Backend on **Render**, Database on **Supabase**. *Zero Docker dependencies.*

---

## 5. Synthetic Data Architecture & Relationships

Data is generated causally with a deterministic random seed (`SEED=42`):
```
Severe Weather Cell (e.g. Louisville)
       ↓
Higher Route Weather Exposure
       ↓
Higher Additive Expected Delay (+160m)
       ↓
Elevated Shipment Risk Score (3.2 → 8.9 / 10)
       ↓
Higher SLA Breach Probability (18% → 81%)
       ↓
Dynamic Reroute Recommendation (Via Indianapolis corridor)
```

### Generated Datasets (`backend/data/generated/`)
| Dataset | Records | Description |
|---|---|---|
| `locations.csv` | 75+ | North American logistics hubs, airports, and DCs with coordinates and capacities |
| `route_edges.csv` | 250+ | Connected logistics graph with road quality, historical delay, and baselines |
| `weather_events.csv` | 4,000 | Severe weather cells (hurricanes, snowstorms, fog) with radius and delay multipliers |
| `traffic_events.csv` | 8,000 | Congestion incidents and traffic indices across corridor edges |
| `congestion_events.csv` | 4,000 | Hub throughput queues and capacity bottlenecks |
| `transport_events.csv` | 2,000 | Flight schedules, departures, arrivals, and cancellations |
| `external_events.csv` | 1,200 | Road closures, labor strikes, and port disruptions |
| `historical_shipments.csv` | 30,000 | 2.5 years of shipments (2024–2026) with causal outcomes |
| `shipment_events.csv` | 100,000+ | Chronological lifecycle event timeline per shipment |
| `historical_route_performance.csv` | Derived | Aggregated corridor delay rates and reliability indices |
| `current_shipments.csv` | 2,000 | Active in-transit, delayed, and processing shipments |
| `risk_scores.csv` | 2,000 | Granular multi-factor risk decomposition per active shipment |

---

## 6. Risk Scoring Methodology

Composite score normalized to a **1.0 to 10.0 scale**:
$$\text{Risk Score} = \sum (w_i \times s_i)$$

| Dimension | Weight | Input Signal |
|---|---|---|
| **Weather Exposure** | 20% | Real-time weather severity, affected radius, delay multiplier |
| **Traffic Congestion** | 15% | Segment traffic index (0–100), speed deficit vs. normal |
| **Hub Congestion** | 20% | Current facility load vs. processing capacity ratio |
| **Transport / Flight** | 15% | Flight cancellations, airport lag, departure delay |
| **External Incidents** | 10% | Road closures, geopolitical events, port strikes |
| **Historical Corridor** | 10% | Historical SLA breach rate on specific corridor edges |
| **Shipment Attributes** | 10% | Fragile, Temperature Sensitive, high weight penalties |

### Risk Thresholds
* `1.0 – 3.0`: **LOW** (Standard tracking)
* `3.1 – 5.0`: **MEDIUM** (Elevated monitoring)
* `5.1 – 7.5`: **HIGH** (Proactive reroute advisory)
* `7.6 – 10.0`: **CRITICAL** (Immediate intervention required)

---

## 7. Route Optimization Methodology

Uses NetworkX to extract candidate paths across the North American graph. Routes are scored and ranked according to the selected operational objective:

* **Balanced Mode** (Default):
  $$\text{Cost} = 0.45 \times \text{NormTime} + 0.20 \times \text{NormDist} + 0.35 \times \text{NormRisk}$$
* **Fastest Mode**:
  $$\text{Cost} = 0.75 \times \text{NormTime} + 0.10 \times \text{NormDist} + 0.15 \times \text{NormRisk}$$
* **Safest Mode**:
  $$\text{Cost} = 0.15 \times \text{NormTime} + 0.10 \times \text{NormDist} + 0.75 \times \text{NormRisk}$$

$$\text{Risk-Adjusted Travel Time} = \text{Base Travel Time} + \text{Expected Delay}$$

---

## 8. Local Setup & Quick Start

### Prerequisites
* Python 3.10+ (tested on Python 3.11)
* Node.js 18+ and npm

### 1. Generate Datasets & Train ML Model
```bash
cd backend

# Install backend dependencies
pip install -r requirements.txt

# Generate 30,000 shipments & 100,000+ events
python -m app.data.generate_dataset

# Validate dataset integrity
python -m app.data.validate_dataset

# Train the SLA breach prediction model
python -m app.ml.train_model
```

### 2. Start the Backend API
```bash
# In backend/
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
* Interactive API Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)
* Health Check: [http://localhost:8000/api/health](http://localhost:8000/api/health)

### 3. Start the Frontend UI
```bash
cd ../frontend

# Install dependencies
npm install

# Start Vite dev server
npm run dev
```
* Web Application: [http://localhost:5173](http://localhost:5173)

---

## 9. Supabase Cloud Database Setup (Optional)

If you have a Supabase account:
1. Create a new Supabase project.
2. Open the **SQL Editor** in Supabase and paste the contents of `database/schema.sql`. Run it.
3. Configure environment variables in `backend/.env`:
   ```env
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_SERVICE_KEY=your-service-role-key
   DATA_MODE=auto
   ```
4. Batch-seed the database:
   ```bash
   cd backend
   python -m app.data.seed_supabase
   ```
*If Supabase credentials are not provided or the network is unreachable, the system automatically falls back to local synthetic data.*

---

## 10. Hackathon Demo Walkthrough (Deterministic Demo Flow)

Follow this exact flow for a complete demo:

1. **Dashboard**: Open `http://localhost:5173`. Point out the live KPI summary cards, Network Risk Distribution chart, SLA Breach predictions, and the **Data Source Indicator** (`● Local Synthetic Data` or `● Supabase`).
2. **Route Planner**:
   * Navigate to `/route-planner`.
   * Origin: `Chicago`, Destination: `New York`. Mode: `Balanced`.
   * Click **Find Best Routes**.
   * Note the 3 alternative routes displayed. Explain: *Route A is shorter, but Route C is recommended because its lower risk yields a lower expected arrival time.*
3. **Simulate Disruption (The Hero Moment)**:
   * Click **Simulate Louisville Storm (Demo)**.
   * Observe Route A's corridor risk surge from **3.2 to 8.9 (CRITICAL)**.
   * Expected delay increases by +2h 40m.
   * The system dynamically changes the recommendation to **Route B / Northern Corridor via Indianapolis**.
4. **Predictive Disruption Radar**:
   * Navigate to `/risk-center`.
   * Show the **Predictive Disruption Radar (Next 24 Hours)** identifying approaching disruptions before shipments are delayed.
5. **Shipment Deep Dive**:
   * Navigate to `/shipments`.
   * Click on any shipment with a `CRITICAL` or `HIGH` badge.
   * Show the **7-signal Risk Breakdown**, **Additive Delay Decomposition**, and chronological **Shipment Lifecycle Stepper**.
6. **Analytics**:
   * Navigate to `/analytics`.
   * Review historical delay curves, SLA breach rates over time, and the **RandomForest Model Performance Card** (Accuracy ~88%, ROC-AUC ~0.91).

---

## 11. Manual Deployment Guide

### Backend Deployment (Render)
1. Push your repository to GitHub.
2. In Render, create a **New Web Service** and connect your repo.
3. Settings:
   * **Root Directory**: `backend`
   * **Environment**: `Python 3`
   * **Build Command**: `pip install -r requirements.txt`
   * **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Environment Variables:
   * `FRONTEND_URL`: `https://your-frontend.vercel.app`
   * `DATA_MODE`: `auto`
   * `RANDOM_SEED`: `42`
   * *(Optional)* `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`

### Frontend Deployment (Vercel)
1. In Vercel, click **Add New Project** and import the repository.
2. Settings:
   * **Root Directory**: `frontend`
   * **Framework Preset**: `Vite`
   * **Build Command**: `npm run build`
   * **Output Directory**: `dist`
3. Environment Variables:
   * `VITE_API_BASE_URL`: `https://your-render-backend.onrender.com`
   * *(Optional)* `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`
4. Deploy!

---

## 12. Environment Variables Reference

### Backend (`backend/.env`)
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key
FRONTEND_URL=http://localhost:5173
DATA_MODE=auto
RANDOM_SEED=42
```

### Frontend (`frontend/.env`)
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

---

## 13. License

MIT License. Designed for logistics operations and predictive route optimization demonstration.

>>>>>>> d30fbda (Initial commit)
