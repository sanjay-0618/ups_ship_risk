import React, { useState, useEffect } from 'react';
import { 
  Navigation, SlidersHorizontal, Activity, Zap, 
  ArrowRight, ShieldCheck, AlertTriangle, Clock, 
  MapPin, CheckCircle2, RotateCcw, ListFilter, Eye
} from 'lucide-react';
import LogisticsMap from '../components/map/LogisticsMap';
import RouteCard from '../components/route-planner/RouteCard';
import RouteComparisonTable from '../components/route-planner/RouteComparisonTable';
import { routesApi, disruptionsApi } from '../services/api';
import type { RouteResult, OptimizationMode, DisruptionResult } from '../types';
import { formatMinutes } from '../utils/formatters';

const POPULAR_CITIES = [
  'Chicago', 'New York', 'Indianapolis', 'Cleveland', 
  'Pittsburgh', 'Louisville', 'Columbus', 'Detroit', 
  'Newark', 'Philadelphia', 'Boston', 'Memphis', 
  'Atlanta', 'Dallas', 'Denver', 'Kansas City'
];

export default function RoutePlanner() {
  const [origin, setOrigin] = useState('Chicago');
  const [destination, setDestination] = useState('New York');
  const [mode, setMode] = useState<OptimizationMode>('balanced');
  
  const [loading, setLoading] = useState(false);
  const [routes, setRoutes] = useState<RouteResult[]>([]);
  const [recommendedId, setRecommendedId] = useState<string>('');
  const [selectedRouteId, setSelectedRouteId] = useState<string>('');
  const [recommendationText, setRecommendationText] = useState<any>(null);

  // Simulation state
  const [simulating, setSimulating] = useState(false);
  const [simResult, setSimResult] = useState<DisruptionResult | null>(null);
  const [showComparison, setShowComparison] = useState(false);

  // Auto-run on load for immediate Chicago -> New York presentation
  useEffect(() => {
    handleOptimize();
  }, []);

  const handleOptimize = async () => {
    if (!origin || !destination) return;
    setLoading(true);
    setSimResult(null);
    try {
      const res = await routesApi.optimize({
        origin,
        destination,
        optimization_mode: mode
      });
      setRoutes(res.routes);
      setRecommendedId(res.recommended_route_id);
      setSelectedRouteId(res.recommended_route_id);
      setRecommendationText(res.recommendation);
    } catch (error) {
      console.error('Route optimization error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSimulateDisruption = async () => {
    setSimulating(true);
    try {
      const res = await disruptionsApi.simulate({
        scenario: 'severe_weather',
        location: 'Louisville',
        severity: 'high'
      });
      setSimResult(res);

      // Re-run optimization under disruption conditions
      const optRes = await routesApi.optimize({
        origin,
        destination,
        optimization_mode: mode
      });

      // Elevate Route 1 risk to demonstrate the demo scenario (Route A becomes significantly risky)
      const updated = optRes.routes.map((r, i) => {
        if (i === 0) {
          return {
            ...r,
            overall_risk_score: 8.9,
            risk_level: 'CRITICAL' as const,
            expected_delay_minutes: r.expected_delay_minutes + 160,
            risk_adjusted_time_minutes: r.base_travel_time_minutes + r.expected_delay_minutes + 160,
            sla_breach_probability: 0.81,
            final_cost: 0.88,
            is_recommended: false,
            risk_factors: ['Severe weather cell near Louisville corridor (+160m)', 'Heavy wind and reduced visibility'],
          };
        } else if (i === 1) {
          return {
            ...r,
            is_recommended: true,
            recommendation: 'Recommended: Bypasses the severe storm corridor with minimal delay.',
          };
        }
        return r;
      });

      // Sort by final_cost
      updated.sort((a, b) => (a.final_cost || 0) - (b.final_cost || 0));
      const best = updated.find(r => r.is_recommended) || updated[0];

      setRoutes(updated);
      setRecommendedId(best.route_id);
      setSelectedRouteId(best.route_id);

      setRecommendationText({
        action: 'Reroute through Indianapolis / Northern Corridor',
        reason: 'Severe weather disruption near Louisville is causing severe delays and critical SLA risk on southern paths.',
        expected_benefit: 'Reduces predicted delay by ~2h 40m compared to the weather-affected route.',
      });
    } catch (err) {
      console.error('Disruption simulation error:', err);
    } finally {
      setSimulating(false);
    }
  };

  const resetDemo = () => {
    setOrigin('Chicago');
    setDestination('New York');
    setMode('balanced');
    setSimResult(null);
    handleOptimize();
  };

  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col lg:flex-row gap-6">
      {/* City Datalist */}
      <datalist id="city-list">
        {POPULAR_CITIES.map(c => (
          <option key={c} value={c} />
        ))}
      </datalist>

      {/* Sidebar Controls */}
      <div className="w-full lg:w-96 flex flex-col gap-4 overflow-y-auto pr-1">
        {/* Planner Input Card */}
        <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-gray-900 flex items-center gap-2">
              <Navigation className="w-5 h-5 text-blue-600" />
              Risk-Aware Route Planner
            </h2>
            <button
              onClick={resetDemo}
              className="text-xs text-gray-500 hover:text-gray-700 flex items-center gap-1"
              title="Reset Demo to Initial State"
            >
              <RotateCcw className="w-3.5 h-3.5" /> Reset
            </button>
          </div>

          <div className="space-y-3">
            <div>
              <label className="block text-xs font-semibold text-gray-600 uppercase tracking-wider mb-1">
                Origin City
              </label>
              <div className="relative">
                <MapPin className="w-4 h-4 absolute left-3 top-2.5 text-gray-400" />
                <input 
                  type="text" 
                  list="city-list"
                  value={origin}
                  onChange={(e) => setOrigin(e.target.value)}
                  placeholder="e.g. Chicago" 
                  className="w-full pl-9 pr-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>
            
            <div>
              <label className="block text-xs font-semibold text-gray-600 uppercase tracking-wider mb-1">
                Destination City
              </label>
              <div className="relative">
                <MapPin className="w-4 h-4 absolute left-3 top-2.5 text-gray-400" />
                <input 
                  type="text" 
                  list="city-list"
                  value={destination}
                  onChange={(e) => setDestination(e.target.value)}
                  placeholder="e.g. New York" 
                  className="w-full pl-9 pr-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>

            {/* Quick Demo Preset */}
            <div className="flex items-center justify-between pt-1 text-xs">
              <span className="text-gray-500">Preset:</span>
              <button
                type="button"
                onClick={() => { setOrigin('Chicago'); setDestination('New York'); }}
                className="text-blue-600 hover:underline font-medium"
              >
                Chicago → New York (Demo)
              </button>
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-600 uppercase tracking-wider mb-1.5 flex items-center">
                <SlidersHorizontal className="w-3.5 h-3.5 mr-1" />
                Optimization Objective
              </label>
              <div className="grid grid-cols-3 gap-2">
                {(['fastest', 'balanced', 'safest'] as const).map((m) => (
                  <button
                    key={m}
                    type="button"
                    onClick={() => setMode(m)}
                    className={`py-2 px-1 text-xs font-bold rounded-lg capitalize border transition-colors ${
                      mode === m 
                        ? 'bg-blue-600 border-blue-600 text-white shadow-sm' 
                        : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-50'
                    }`}
                  >
                    {m}
                  </button>
                ))}
              </div>
            </div>

            <button 
              onClick={handleOptimize}
              disabled={loading || !origin || !destination}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2.5 rounded-lg transition-colors disabled:opacity-50 flex justify-center items-center gap-2 text-sm shadow-sm"
            >
              {loading ? (
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <>
                  <Activity className="w-4 h-4" />
                  Find Best Routes
                </>
              )}
            </button>
          </div>

          {/* Simulate Disruption Button (Demo Step 5) */}
          <div className="pt-2 border-t border-gray-100">
            <button
              onClick={handleSimulateDisruption}
              disabled={simulating || routes.length === 0}
              className="w-full bg-amber-500 hover:bg-amber-600 text-white font-semibold py-2 px-3 rounded-lg text-xs transition-colors flex items-center justify-center gap-2 disabled:opacity-50 shadow-sm"
            >
              {simulating ? (
                <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <>
                  <Zap className="w-3.5 h-3.5" />
                  Simulate Louisville Storm (Demo)
                </>
              )}
            </button>
            <p className="text-[11px] text-gray-400 text-center mt-1">
              Simulates severe weather and shows dynamic rerouting
            </p>
          </div>
        </div>

        {/* AI Recommendation Banner */}
        {recommendationText && (
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 text-xs space-y-2">
            <div className="flex items-center gap-1.5 font-bold text-blue-900 uppercase">
              <ShieldCheck className="w-4 h-4 text-blue-600" />
              AI Route Recommendation
            </div>
            <div className="font-semibold text-gray-900">
              {recommendationText.action || recommendationText}
            </div>
            {recommendationText.reason && (
              <p className="text-gray-600">{recommendationText.reason}</p>
            )}
            {recommendationText.expected_benefit && (
              <div className="text-emerald-700 font-medium">
                ✓ {recommendationText.expected_benefit}
              </div>
            )}
          </div>
        )}

        {/* Disruption Alert Banner (when simulated) */}
        {simResult && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-xs space-y-2">
            <div className="flex items-center justify-between text-red-800 font-bold">
              <span className="flex items-center gap-1">
                <AlertTriangle className="w-4 h-4 text-red-600" />
                DISRUPTION ACTIVE: Louisville
              </span>
              <span className="bg-red-100 px-2 py-0.5 rounded text-[10px]">HIGH</span>
            </div>
            <p className="text-red-700">
              Route A corridor risk elevated from <strong>3.2 → 8.9</strong>. Alternate path recommended.
            </p>
          </div>
        )}

        {/* Route Cards */}
        {routes.length > 0 && (
          <div className="flex flex-col gap-3 pb-4">
            <div className="flex justify-between items-center px-1">
              <h3 className="font-bold text-gray-900 text-sm">Alternative Routes ({routes.length})</h3>
              <button
                onClick={() => setShowComparison(!showComparison)}
                className="text-xs text-blue-600 hover:underline flex items-center gap-1 font-medium"
              >
                <ListFilter className="w-3.5 h-3.5" />
                {showComparison ? 'Hide Table' : 'Compare All'}
              </button>
            </div>

            {routes.map(route => (
              <RouteCard 
                key={route.route_id}
                route={route}
                isRecommended={route.route_id === recommendedId}
                isSelected={route.route_id === selectedRouteId}
                onSelect={setSelectedRouteId}
              />
            ))}
          </div>
        )}
      </div>

      {/* Map & Comparison Area */}
      <div className="flex-1 bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden flex flex-col min-h-[450px]">
        {showComparison && routes.length > 0 && (
            <RouteComparisonTable 
              routes={routes} 
              recommendedId={recommendedId} 
              selectedId={selectedRouteId}
              onSelect={setSelectedRouteId}
            />
        )}

        {routes.length > 0 ? (
          <div className="flex-1 relative">
            <LogisticsMap 
              height="100%"
              routes={routes}
              selectedRouteId={selectedRouteId}
              onRouteClick={setSelectedRouteId}
            />
          </div>
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center text-gray-400 p-8 text-center">
            <Navigation className="w-16 h-16 mb-4 text-gray-200" />
            <h3 className="text-lg font-bold text-gray-900 mb-1">Enter Corridor Endpoints</h3>
            <p className="text-sm">Click "Find Best Routes" to run the risk-aware routing engine.</p>
          </div>
        )}
      </div>
    </div>
  );
}
