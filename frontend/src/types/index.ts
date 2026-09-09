export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type ShipmentStatus = 'IN_TRANSIT' | 'DELIVERED' | 'DELAYED' | 'PROCESSING' | 'OUT_FOR_DELIVERY' | 'PICKED_UP';
export type OptimizationMode = 'fastest' | 'safest' | 'balanced';
export type DisruptionScenario = 'severe_weather' | 'traffic_congestion' | 'hub_congestion' | 'flight_delay' | 'port_delay' | 'geopolitical' | 'road_closure';
export type DataSource = 'supabase' | 'local';

export interface Location {
  location_id: string;
  location_name: string;
  city: string;
  state: string;
  country: string;
  latitude: number;
  longitude: number;
  location_type: string;
  capacity: number;
  processing_capacity: number;
  risk_baseline: number;
}

export interface Shipment {
  shipment_id: string;
  tracking_number: string;
  origin_location_id: string;
  destination_location_id: string;
  current_location_id: string;
  route_id: string;
  status: ShipmentStatus;
  priority: string;
  shipment_type: string;
  weight_kg: number;
  planned_delivery_time: string;
  current_eta: string;
  risk_score: number;
  risk_level: RiskLevel;
  sla_breach_probability: number;
  expected_delay_minutes: number;
  last_updated: string;
  origin_name?: string;
  destination_name?: string;
  current_location_name?: string;
}

export interface RiskScore {
  risk_id: string;
  shipment_id: string;
  weather_score: number;
  traffic_score: number;
  congestion_score: number;
  transport_score: number;
  external_event_score: number;
  historical_score: number;
  shipment_characteristics_score: number;
  overall_risk_score: number;
  risk_level: RiskLevel;
  sla_breach_probability: number;
  expected_delay_minutes: number;
  delay_breakdown: DelayBreakdown;
  risk_factors: string[];
  created_at: string;
}

export interface DelayBreakdown {
  weather_delay: number;
  traffic_delay: number;
  congestion_delay: number;
  transport_delay: number;
  external_event_delay: number;
  historical_delay: number;
  total_delay: number;
}

export interface RouteResult {
  route_id: string;
  route_name: string;
  origin: string;
  destination: string;
  waypoints: Waypoint[];
  distance_km: number;
  base_travel_time_minutes: number;
  expected_delay_minutes: number;
  risk_adjusted_time_minutes: number;
  weather_risk: number;
  traffic_risk: number;
  congestion_risk: number;
  infrastructure_risk: number;
  transport_risk: number;
  external_event_risk: number;
  historical_risk: number;
  overall_risk_score: number;
  risk_level: RiskLevel;
  sla_breach_probability: number;
  final_cost: number;
  risk_factors: string[];
  delay_breakdown: DelayBreakdown;
  recommendation: string;
  is_recommended: boolean;
}

export interface Waypoint {
  location_id: string;
  location_name: string;
  city: string;
  latitude: number;
  longitude: number;
  sequence: number;
}

export interface RouteOptimizeRequest {
  origin: string;
  destination: string;
  optimization_mode: OptimizationMode;
}

export interface RouteOptimizeResponse {
  recommended_route_id: string;
  routes: RouteResult[];
  data_source: DataSource;
  optimization_mode: OptimizationMode;
  recommendation?: Recommendation | any;
}

export interface DisruptionSimulateRequest {
  scenario: DisruptionScenario;
  location: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
}

export interface DisruptionResult {
  scenario: string;
  location: string;
  severity: string;
  affected_routes: string[];
  affected_shipments_count: number;
  before: {
    avg_risk: number;
    avg_delay: number;
    avg_sla_breach_probability: number;
    recommended_route_id: string;
  };
  after: {
    avg_risk: number;
    avg_delay: number;
    avg_sla_breach_probability: number;
    recommended_route_id: string;
  };
  recommendation: Recommendation;
  sample_shipments?: any[];
}

export interface Recommendation {
  action: string;
  reason: string;
  expected_benefit: string;
  confidence: 'HIGH' | 'MEDIUM' | 'LOW';
}

export interface DashboardSummary {
  total_shipments: number;
  at_risk_count: number;
  critical_count: number;
  predicted_sla_breaches: number;
  average_network_risk: number;
  average_expected_delay: number;
  active_disruptions_count: number;
  risk_distribution: Record<RiskLevel, number>;
  recent_high_risk_shipments: Shipment[];
  data_source: DataSource;
}

export interface ShipmentEvent {
  event_id: string;
  shipment_id: string;
  timestamp: string;
  location_id: string;
  location_name?: string;
  event_type: string;
  status: string;
  delay_minutes: number;
  latitude: number;
  longitude: number;
  description: string;
}

export interface WeatherEvent {
  event_id: string;
  event_type: string;
  severity: string;
  latitude: number;
  longitude: number;
  affected_radius_km: number;
  start_time: string;
  end_time: string;
  delay_multiplier: number;
  expected_delay_minutes: number;
}

export interface AnalyticsSummary {
  delay_trends: MonthlyMetric[];
  sla_breach_rate_trend: MonthlyMetric[];
  route_reliability: RouteReliability[];
  disruption_frequency: DisruptionFrequency[];
  avg_delay_by_disruption_type: Record<string, number>;
  performance_by_priority: PerformanceByPriority[];
  ml_model_metrics?: MLModelMetrics;
}

export interface MonthlyMetric {
  month: string;
  value: number;
}

export interface RouteReliability {
  route_id: string;
  route_name: string;
  reliability_score: number;
  avg_delay: number;
  sla_breach_rate: number;
}

export interface DisruptionFrequency {
  type: string;
  count: number;
  avg_delay: number;
}

export interface PerformanceByPriority {
  priority: string;
  total: number;
  on_time: number;
  delayed: number;
  breach_rate: number;
}

export interface MLModelMetrics {
  accuracy: number;
  precision: number;
  recall: number;
  f1: number;
  roc_auc: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
}
