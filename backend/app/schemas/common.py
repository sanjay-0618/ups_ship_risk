from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class ShipmentStatus(str, Enum):
    PROCESSING = "PROCESSING"
    IN_TRANSIT = "IN_TRANSIT"
    DELAYED = "DELAYED"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"

class OptimizationMode(str, Enum):
    fastest = "fastest"
    safest = "safest"
    balanced = "balanced"

class DisruptionScenario(str, Enum):
    severe_weather = "severe_weather"
    traffic_congestion = "traffic_congestion"
    hub_congestion = "hub_congestion"
    flight_delay = "flight_delay"
    port_delay = "port_delay"
    geopolitical = "geopolitical"
    road_closure = "road_closure"

class Location(BaseModel):
    location_id: str
    location_name: str
    city: str
    state: str
    country: str
    latitude: float
    longitude: float
    location_type: str
    capacity: int
    processing_capacity: int
    risk_baseline: float

class RouteEdge(BaseModel):
    edge_id: str
    origin_location_id: str
    destination_location_id: str
    distance_km: float
    base_travel_time_minutes: float
    road_quality: int
    capacity: int
    historical_delay_rate: float
    average_delay_minutes: float
    weather_exposure: float
    traffic_baseline: float
    congestion_baseline: float
    infrastructure_risk: float
    transport_mode: str

class Shipment(BaseModel):
    shipment_id: str
    tracking_number: str
    origin_location_id: str
    destination_location_id: str
    route_id: str
    shipment_type: str
    priority: str
    weight_kg: float
    distance_km: float
    number_of_stops: int
    number_of_handoffs: int
    planned_duration_minutes: float
    actual_duration_minutes: Optional[float]
    planned_delivery_time: datetime
    actual_delivery_time: Optional[datetime]
    status: ShipmentStatus
    risk_level: RiskLevel

class RiskScore(BaseModel):
    risk_id: str
    shipment_id: str
    weather_score: float
    traffic_score: float
    congestion_score: float
    transport_score: float
    external_event_score: float
    historical_score: float
    shipment_characteristics_score: float
    overall_risk_score: float
    risk_level: RiskLevel
    sla_breach_probability: float
    expected_delay_minutes: float
    created_at: datetime

class WeatherEvent(BaseModel):
    event_id: str
    event_type: str
    severity: RiskLevel
    latitude: float
    longitude: float
    affected_radius_km: float
    start_time: datetime
    end_time: datetime
    temperature: float
    precipitation: float
    wind_speed: float
    visibility: float
    delay_multiplier: float
    expected_delay_minutes: float

class TrafficEvent(BaseModel):
    event_id: str
    route_edge_id: str
    location_id: Optional[str]
    timestamp: datetime
    congestion_level: str
    average_speed_kmh: float
    normal_speed_kmh: float
    traffic_index: int
    incident_type: str
    expected_delay_minutes: float

class CongestionEvent(BaseModel):
    event_id: str
    location_id: str
    location_type: str
    timestamp: datetime
    congestion_score: float
    processing_capacity: int
    current_load: int
    queue_length: int
    average_processing_time: float
    delay_minutes: float

class TransportEvent(BaseModel):
    transport_id: str
    flight_number: Optional[str]
    origin_location_id: str
    destination_location_id: str
    scheduled_departure: datetime
    actual_departure: Optional[datetime]
    scheduled_arrival: datetime
    actual_arrival: Optional[datetime]
    delay_minutes: float
    status: str
    weather_impact: float
    airport_congestion: float

class ExternalEvent(BaseModel):
    event_id: str
    event_type: str
    title: str
    severity: RiskLevel
    location: str
    latitude: float
    longitude: float
    start_time: datetime
    end_time: datetime
    affected_radius_km: float
    impact_type: str
    expected_delay_minutes: float
    description: str

class RouteResult(BaseModel):
    route_id: str
    total_distance_km: float
    expected_time_minutes: float
    risk_score: float
    path: List[str]
    segments: List[Any]
    sla_probability: float

class RouteOptimizeRequest(BaseModel):
    origin: str
    destination: str
    optimization_mode: OptimizationMode

class DisruptionSimulateRequest(BaseModel):
    scenario: DisruptionScenario
    location: str
    severity: RiskLevel

class DisruptionResult(BaseModel):
    scenario: str
    location: str
    affected_routes: int
    affected_shipments: int
    avg_delay_increase_minutes: float
    recommendations: List[Any]

class DashboardSummary(BaseModel):
    total_shipments: int
    at_risk_count: int
    critical_count: int
    predicted_sla_breaches: int
    average_network_risk: float
    average_expected_delay: float
    active_disruptions_count: int
    risk_distribution: Dict[str, int]
    recent_high_risk_shipments: List[Any]
    data_source: str

class AnalyticsSummary(BaseModel):
    delay_trends: Dict[str, Any]
    sla_breach_rate_trend: Dict[str, Any]
    route_reliability: List[Any]
    risk_trends: Dict[str, Any]
    disruption_frequency: Dict[str, int]
    avg_delay_by_disruption_type: Dict[str, float]
    performance_by_priority: Dict[str, Any]
    ml_model_metrics: Optional[Dict[str, Any]]

class Recommendation(BaseModel):
    action: str
    reason: str
    expected_benefit: str
    confidence: str

