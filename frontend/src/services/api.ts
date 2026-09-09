import axios from 'axios';
import type { 
  DashboardSummary, Shipment, RiskScore, ShipmentEvent, 
  RouteOptimizeRequest, RouteOptimizeResponse, RouteResult,
  DisruptionSimulateRequest, DisruptionResult, AnalyticsSummary,
  PaginatedResponse 
} from '../types';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export const dashboardApi = {
  getSummary: () => api.get<DashboardSummary>('/api/dashboard/summary').then(r => r.data),
};

export const shipmentsApi = {
  getAll: (params: any = {}) => api.get<PaginatedResponse<Shipment>>('/api/shipments', { params }).then(r => r.data),
  getById: (id: string) => api.get<Shipment>('/api/shipments/' + id).then(r => r.data),
  getRisk: (id: string) => api.get<RiskScore>('/api/shipments/' + id + '/risk').then(r => r.data),
  getTimeline: (id: string) => api.get<ShipmentEvent[]>('/api/shipments/' + id + '/timeline').then(r => r.data),
};

export const routesApi = {
  optimize: (req: RouteOptimizeRequest) => api.post<RouteOptimizeResponse>('/api/routes/optimize', req).then(r => r.data),
  getById: (id: string) => api.get<RouteResult>('/api/routes/' + id).then(r => r.data),
  analyze: (id: string, params: any = {}) => api.post('/api/routes/' + id + '/analyze', params).then(r => r.data),
};

export const riskApi = {
  calculate: (data: any) => api.post('/api/risk/calculate', data).then(r => r.data),
  getEvents: () => api.get('/api/risk/events').then(r => r.data),
};

export const disruptionsApi = {
  simulate: (req: DisruptionSimulateRequest) => api.post<DisruptionResult>('/api/disruptions/simulate', req).then(r => r.data),
  getAll: () => api.get('/api/disruptions').then(r => r.data),
};

export const analyticsApi = {
  getSummary: () => api.get<AnalyticsSummary>('/api/analytics/summary').then(r => r.data),
};

export const healthApi = {
  check: () => api.get<{status: string; data_source: 'supabase' | 'local'}>('/api/health').then(r => r.data),
};

export default api;
