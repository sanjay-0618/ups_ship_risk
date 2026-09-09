-- AI-Powered Predictive Logistics Platform
-- Supabase / PostgreSQL Schema
-- Run this in the Supabase SQL Editor before seeding

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ─────────────────────────────────────────────────────────────
-- LOCATIONS
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS locations (
    location_id         VARCHAR(20) PRIMARY KEY,
    location_name       VARCHAR(200) NOT NULL,
    city                VARCHAR(100) NOT NULL,
    state               VARCHAR(10),
    country             VARCHAR(10) DEFAULT 'US',
    latitude            DOUBLE PRECISION NOT NULL,
    longitude           DOUBLE PRECISION NOT NULL,
    location_type       VARCHAR(50),
    capacity            INTEGER,
    processing_capacity INTEGER,
    risk_baseline       DOUBLE PRECISION,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_locations_city ON locations(city);
CREATE INDEX IF NOT EXISTS idx_locations_type ON locations(location_type);

-- ─────────────────────────────────────────────────────────────
-- ROUTE EDGES
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS route_edges (
    edge_id                 VARCHAR(20) PRIMARY KEY,
    origin_location_id      VARCHAR(20) REFERENCES locations(location_id),
    destination_location_id VARCHAR(20) REFERENCES locations(location_id),
    distance_km             DOUBLE PRECISION,
    base_travel_time_minutes DOUBLE PRECISION,
    road_quality            INTEGER,
    capacity                INTEGER,
    historical_delay_rate   DOUBLE PRECISION,
    average_delay_minutes   DOUBLE PRECISION,
    weather_exposure        DOUBLE PRECISION,
    traffic_baseline        DOUBLE PRECISION,
    congestion_baseline     DOUBLE PRECISION,
    infrastructure_risk     DOUBLE PRECISION,
    transport_mode          VARCHAR(20),
    created_at              TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_route_edges_origin ON route_edges(origin_location_id);
CREATE INDEX IF NOT EXISTS idx_route_edges_dest   ON route_edges(destination_location_id);

-- ─────────────────────────────────────────────────────────────
-- CURRENT SHIPMENTS
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS shipments (
    shipment_id             VARCHAR(20) PRIMARY KEY,
    tracking_number         VARCHAR(50) UNIQUE,
    origin_location_id      VARCHAR(20) REFERENCES locations(location_id),
    destination_location_id VARCHAR(20) REFERENCES locations(location_id),
    current_location_id     VARCHAR(20) REFERENCES locations(location_id),
    route_id                VARCHAR(100),
    status                  VARCHAR(30),
    priority                VARCHAR(20),
    shipment_type           VARCHAR(40),
    weight_kg               DOUBLE PRECISION,
    planned_delivery_time   TIMESTAMPTZ,
    current_eta             TIMESTAMPTZ,
    risk_score              DOUBLE PRECISION,
    risk_level              VARCHAR(10),
    sla_breach_probability  DOUBLE PRECISION,
    expected_delay_minutes  INTEGER,
    last_updated            TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_shipments_tracking  ON shipments(tracking_number);
CREATE INDEX IF NOT EXISTS idx_shipments_risk       ON shipments(risk_score DESC);
CREATE INDEX IF NOT EXISTS idx_shipments_status     ON shipments(status);
CREATE INDEX IF NOT EXISTS idx_shipments_risk_level ON shipments(risk_level);
CREATE INDEX IF NOT EXISTS idx_shipments_origin     ON shipments(origin_location_id);
CREATE INDEX IF NOT EXISTS idx_shipments_dest       ON shipments(destination_location_id);

-- ─────────────────────────────────────────────────────────────
-- HISTORICAL SHIPMENTS
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS historical_shipments (
    shipment_id                 VARCHAR(20) PRIMARY KEY,
    tracking_number             VARCHAR(50),
    origin_location_id          VARCHAR(20),
    destination_location_id     VARCHAR(20),
    route_id                    VARCHAR(100),
    shipment_type               VARCHAR(40),
    priority                    VARCHAR(20),
    weight_kg                   DOUBLE PRECISION,
    distance_km                 DOUBLE PRECISION,
    number_of_stops             INTEGER,
    number_of_handoffs          INTEGER,
    planned_duration_minutes    DOUBLE PRECISION,
    actual_duration_minutes     DOUBLE PRECISION,
    planned_delivery_time       TIMESTAMPTZ,
    actual_delivery_time        TIMESTAMPTZ,
    weather_exposure            DOUBLE PRECISION,
    traffic_exposure            DOUBLE PRECISION,
    congestion_exposure         DOUBLE PRECISION,
    transport_delay_minutes     INTEGER,
    external_event_exposure     DOUBLE PRECISION,
    historical_route_delay_rate DOUBLE PRECISION,
    historical_route_avg_delay  DOUBLE PRECISION,
    expected_delay_minutes      INTEGER,
    delay_minutes               INTEGER,
    sla_limit_minutes           INTEGER,
    sla_breached                BOOLEAN,
    final_risk_score            DOUBLE PRECISION,
    planned_date                TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_hist_route_id    ON historical_shipments(route_id);
CREATE INDEX IF NOT EXISTS idx_hist_planned     ON historical_shipments(planned_date);
CREATE INDEX IF NOT EXISTS idx_hist_sla_breached ON historical_shipments(sla_breached);

-- ─────────────────────────────────────────────────────────────
-- SHIPMENT EVENTS
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS shipment_events (
    event_id        VARCHAR(20) PRIMARY KEY,
    shipment_id     VARCHAR(20),
    timestamp       TIMESTAMPTZ,
    location_id     VARCHAR(20),
    event_type      VARCHAR(50),
    status          VARCHAR(30),
    delay_minutes   INTEGER DEFAULT 0,
    latitude        DOUBLE PRECISION,
    longitude       DOUBLE PRECISION,
    description     TEXT
);

CREATE INDEX IF NOT EXISTS idx_events_shipment   ON shipment_events(shipment_id);
CREATE INDEX IF NOT EXISTS idx_events_timestamp  ON shipment_events(timestamp);
CREATE INDEX IF NOT EXISTS idx_events_type       ON shipment_events(event_type);

-- ─────────────────────────────────────────────────────────────
-- WEATHER EVENTS
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS weather_events (
    event_id                VARCHAR(20) PRIMARY KEY,
    event_type              VARCHAR(50),
    severity                VARCHAR(10),
    latitude                DOUBLE PRECISION,
    longitude               DOUBLE PRECISION,
    affected_radius_km      INTEGER,
    start_time              TIMESTAMPTZ,
    end_time                TIMESTAMPTZ,
    temperature             DOUBLE PRECISION,
    precipitation           DOUBLE PRECISION,
    wind_speed              DOUBLE PRECISION,
    visibility              DOUBLE PRECISION,
    delay_multiplier        DOUBLE PRECISION,
    expected_delay_minutes  INTEGER
);

CREATE INDEX IF NOT EXISTS idx_weather_severity   ON weather_events(severity);
CREATE INDEX IF NOT EXISTS idx_weather_start      ON weather_events(start_time);
CREATE INDEX IF NOT EXISTS idx_weather_end        ON weather_events(end_time);

-- ─────────────────────────────────────────────────────────────
-- TRAFFIC EVENTS
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS traffic_events (
    event_id                VARCHAR(20) PRIMARY KEY,
    route_edge_id           VARCHAR(20),
    location_id             VARCHAR(20),
    timestamp               TIMESTAMPTZ,
    congestion_level        VARCHAR(20),
    average_speed_kmh       DOUBLE PRECISION,
    normal_speed_kmh        DOUBLE PRECISION,
    traffic_index           INTEGER,
    incident_type           VARCHAR(50),
    expected_delay_minutes  INTEGER
);

CREATE INDEX IF NOT EXISTS idx_traffic_timestamp ON traffic_events(timestamp);
CREATE INDEX IF NOT EXISTS idx_traffic_edge      ON traffic_events(route_edge_id);

-- ─────────────────────────────────────────────────────────────
-- CONGESTION EVENTS
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS congestion_events (
    event_id                VARCHAR(20) PRIMARY KEY,
    location_id             VARCHAR(20),
    location_type           VARCHAR(50),
    timestamp               TIMESTAMPTZ,
    congestion_score        DOUBLE PRECISION,
    processing_capacity     INTEGER,
    current_load            INTEGER,
    queue_length            INTEGER,
    average_processing_time DOUBLE PRECISION,
    delay_minutes           INTEGER
);

CREATE INDEX IF NOT EXISTS idx_congestion_location  ON congestion_events(location_id);
CREATE INDEX IF NOT EXISTS idx_congestion_timestamp ON congestion_events(timestamp);

-- ─────────────────────────────────────────────────────────────
-- TRANSPORT / FLIGHT EVENTS
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS transport_events (
    transport_id            VARCHAR(20) PRIMARY KEY,
    flight_number           VARCHAR(20),
    origin_location_id      VARCHAR(20),
    destination_location_id VARCHAR(20),
    scheduled_departure     TIMESTAMPTZ,
    actual_departure        TIMESTAMPTZ,
    scheduled_arrival       TIMESTAMPTZ,
    actual_arrival          TIMESTAMPTZ,
    delay_minutes           INTEGER DEFAULT 0,
    status                  VARCHAR(20),
    weather_impact          DOUBLE PRECISION,
    airport_congestion      DOUBLE PRECISION
);

CREATE INDEX IF NOT EXISTS idx_transport_status  ON transport_events(status);
CREATE INDEX IF NOT EXISTS idx_transport_origin  ON transport_events(origin_location_id);

-- ─────────────────────────────────────────────────────────────
-- EXTERNAL EVENTS
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS external_events (
    event_id                VARCHAR(20) PRIMARY KEY,
    event_type              VARCHAR(50),
    title                   VARCHAR(200),
    severity                VARCHAR(10),
    location                VARCHAR(100),
    latitude                DOUBLE PRECISION,
    longitude               DOUBLE PRECISION,
    start_time              TIMESTAMPTZ,
    end_time                TIMESTAMPTZ,
    affected_radius_km      INTEGER,
    impact_type             VARCHAR(50),
    expected_delay_minutes  INTEGER,
    description             TEXT
);

CREATE INDEX IF NOT EXISTS idx_external_severity ON external_events(severity);
CREATE INDEX IF NOT EXISTS idx_external_start    ON external_events(start_time);

-- ─────────────────────────────────────────────────────────────
-- HISTORICAL ROUTE PERFORMANCE
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS historical_route_performance (
    route_id                    VARCHAR(100) PRIMARY KEY,
    total_shipments             INTEGER,
    average_delay_minutes       DOUBLE PRECISION,
    median_delay_minutes        DOUBLE PRECISION,
    delay_rate                  DOUBLE PRECISION,
    sla_breach_rate             DOUBLE PRECISION,
    average_weather_exposure    DOUBLE PRECISION,
    average_traffic_exposure    DOUBLE PRECISION,
    average_congestion_exposure DOUBLE PRECISION,
    route_reliability_score     DOUBLE PRECISION
);

-- ─────────────────────────────────────────────────────────────
-- RISK SCORES
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS risk_scores (
    risk_id                         VARCHAR(20) PRIMARY KEY,
    shipment_id                     VARCHAR(20),
    weather_score                   DOUBLE PRECISION,
    traffic_score                   DOUBLE PRECISION,
    congestion_score                DOUBLE PRECISION,
    transport_score                 DOUBLE PRECISION,
    external_event_score            DOUBLE PRECISION,
    historical_score                DOUBLE PRECISION,
    shipment_characteristics_score  DOUBLE PRECISION,
    overall_risk_score              DOUBLE PRECISION,
    risk_level                      VARCHAR(10),
    sla_breach_probability          DOUBLE PRECISION,
    expected_delay_minutes          INTEGER,
    created_at                      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_risk_shipment    ON risk_scores(shipment_id);
CREATE INDEX IF NOT EXISTS idx_risk_overall     ON risk_scores(overall_risk_score DESC);
CREATE INDEX IF NOT EXISTS idx_risk_level       ON risk_scores(risk_level);

-- ─────────────────────────────────────────────────────────────
-- DISRUPTIONS (simulation runs stored)
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS disruptions (
    disruption_id   UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    scenario        VARCHAR(50),
    location        VARCHAR(100),
    severity        VARCHAR(10),
    start_time      TIMESTAMPTZ DEFAULT NOW(),
    end_time        TIMESTAMPTZ,
    before_avg_risk DOUBLE PRECISION,
    after_avg_risk  DOUBLE PRECISION,
    before_avg_delay DOUBLE PRECISION,
    after_avg_delay DOUBLE PRECISION,
    affected_shipments_count INTEGER,
    recommendation  TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ─────────────────────────────────────────────────────────────
-- SIMULATION RUNS
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS simulation_runs (
    run_id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    scenario        VARCHAR(50),
    parameters      JSONB,
    result          JSONB,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ─────────────────────────────────────────────────────────────
-- RECOMMENDATIONS
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS recommendations (
    rec_id      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    shipment_id VARCHAR(20),
    route_id    VARCHAR(100),
    action      TEXT,
    reason      TEXT,
    benefit     TEXT,
    confidence  VARCHAR(10),
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- ─────────────────────────────────────────────────────────────
-- ROUTE RISKS (cached per route query)
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS route_risks (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    route_id                VARCHAR(100),
    origin                  VARCHAR(100),
    destination             VARCHAR(100),
    overall_risk_score      DOUBLE PRECISION,
    risk_level              VARCHAR(10),
    expected_delay_minutes  INTEGER,
    sla_breach_probability  DOUBLE PRECISION,
    optimization_mode       VARCHAR(20),
    created_at              TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_route_risks_route ON route_risks(route_id);
