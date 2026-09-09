import React, { useState, useEffect } from 'react';
import { 
  Zap, AlertTriangle, CloudRain, Flame, Radio, 
  ArrowRight, ShieldAlert, CheckCircle2, TrendingUp,
  MapPin, Clock, RefreshCw, Layers
} from 'lucide-react';
import { disruptionsApi } from '../services/api';
import type { DisruptionResult, DisruptionScenario } from '../types';
import { formatMinutes } from '../utils/formatters';

const SCENARIOS = [
  { id: 'severe_weather', label: 'Severe Weather', icon: CloudRain, color: 'text-blue-600', defaultLoc: 'Louisville' },
  { id: 'traffic_congestion', label: 'Major Traffic Congestion', icon: TrendingUp, color: 'text-amber-600', defaultLoc: 'Chicago' },
  { id: 'hub_congestion', label: 'Hub / Warehouse Congestion', icon: Layers, color: 'text-purple-600', defaultLoc: 'Newark' },
  { id: 'flight_delay', label: 'Flight Delay / Cancellation', icon: Radio, color: 'text-indigo-600', defaultLoc: 'Atlanta' },
  { id: 'port_delay', label: 'Port Disruption', icon: AnchorIcon, color: 'text-cyan-600', defaultLoc: 'Long Beach' },
  { id: 'geopolitical', label: 'Geopolitical / Border Event', icon: ShieldAlert, color: 'text-red-600', defaultLoc: 'El Paso' },
  { id: 'road_closure', label: 'Road Closure / Incident', icon: AlertTriangle, color: 'text-orange-600', defaultLoc: 'Cleveland' },
];

function AnchorIcon(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg {...props} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <circle cx="12" cy="5" r="3" strokeWidth="2"/>
      <path strokeWidth="2" strokeLinecap="round" d="M12 8v13m-7-5c0 3.866 3.134 7 7 7s7-3.134 7-7"/>
    </svg>
  );
}

export default function Disruptions() {
  const [scenario, setScenario] = useState<DisruptionScenario>('severe_weather');
  const [location, setLocation] = useState('Louisville');
  const [severity, setSeverity] = useState<'low' | 'medium' | 'high' | 'critical'>('high');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<DisruptionResult | null>(null);

  const [activeDisruptions, setActiveDisruptions] = useState<any[]>([]);
  const [loadingList, setLoadingList] = useState(false);

  useEffect(() => {
    loadActiveDisruptions();
  }, []);

  const loadActiveDisruptions = async () => {
    setLoadingList(true);
    try {
      const res = await disruptionsApi.getAll();
      setActiveDisruptions(res.disruptions || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingList(false);
    }
  };

  const handleScenarioChange = (id: string, defLoc: string) => {
    setScenario(id as DisruptionScenario);
    setLocation(defLoc);
  };

  const handleSimulate = async () => {
    if (!location) return;
    setLoading(true);
    try {
      const res = await disruptionsApi.simulate({
        scenario,
        location,
        severity,
      });
      setResult(res);
    } catch (err) {
      console.error('Simulation error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <Zap className="w-7 h-7 text-amber-500" />
          Disruption Simulator & Threat Radar
        </h1>
        <p className="text-gray-500 text-sm mt-1">
          Predictive disruption simulation engine. Evaluate the ripple impact of weather, traffic, and hub incidents before they propagate across the network.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Simulator Controls */}
        <div className="lg:col-span-5 space-y-6">
          <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm space-y-5">
            <h2 className="text-base font-semibold text-gray-900 flex items-center gap-2 border-b border-gray-100 pb-3">
              <Zap className="w-4 h-4 text-amber-500" />
              Configure Simulation Scenario
            </h2>

            {/* Scenario Selection */}
            <div>
              <label className="block text-xs font-semibold text-gray-600 uppercase tracking-wider mb-2">
                Select Disruption Scenario
              </label>
              <div className="grid grid-cols-1 gap-2">
                {SCENARIOS.map((sc) => {
                  const Icon = sc.icon;
                  const isSelected = scenario === sc.id;
                  return (
                    <button
                      key={sc.id}
                      type="button"
                      onClick={() => handleScenarioChange(sc.id, sc.defaultLoc)}
                      className={`flex items-center gap-3 p-3 rounded-lg border text-left transition-all ${
                        isSelected
                          ? 'border-blue-500 bg-blue-50/50 ring-1 ring-blue-500 text-blue-900'
                          : 'border-gray-200 hover:bg-gray-50 text-gray-700'
                      }`}
                    >
                      <Icon className={`w-5 h-5 flex-shrink-0 ${sc.color}`} />
                      <span className="text-sm font-medium">{sc.label}</span>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Target Location */}
            <div>
              <label className="block text-xs font-semibold text-gray-600 uppercase tracking-wider mb-1">
                Affected Hub / Corridor Location
              </label>
              <div className="relative">
                <MapPin className="w-4 h-4 absolute left-3 top-3 text-gray-400" />
                <input
                  type="text"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  placeholder="e.g. Louisville, Chicago, Newark"
                  className="w-full pl-9 pr-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>

            {/* Severity Radio */}
            <div>
              <label className="block text-xs font-semibold text-gray-600 uppercase tracking-wider mb-2">
                Severity Level
              </label>
              <div className="grid grid-cols-4 gap-2">
                {(['low', 'medium', 'high', 'critical'] as const).map((sev) => {
                  const isSelected = severity === sev;
                  const colors = {
                    low: 'hover:bg-green-50 text-green-700 border-green-200 peer-checked:bg-green-100 peer-checked:border-green-500',
                    medium: 'hover:bg-amber-50 text-amber-700 border-amber-200 peer-checked:bg-amber-100 peer-checked:border-amber-500',
                    high: 'hover:bg-orange-50 text-orange-700 border-orange-200 peer-checked:bg-orange-100 peer-checked:border-orange-500',
                    critical: 'hover:bg-red-50 text-red-700 border-red-200 peer-checked:bg-red-100 peer-checked:border-red-500',
                  };
                  return (
                    <label
                      key={sev}
                      className={`cursor-pointer border rounded-lg p-2 text-center text-xs font-bold uppercase transition-all ${
                        isSelected
                          ? 'bg-blue-600 text-white border-blue-600 shadow-sm'
                          : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'
                      }`}
                    >
                      <input
                        type="radio"
                        name="severity"
                        value={sev}
                        checked={isSelected}
                        onChange={() => setSeverity(sev)}
                        className="sr-only"
                      />
                      {sev}
                    </label>
                  );
                })}
              </div>
            </div>

            {/* Trigger Button */}
            <button
              onClick={handleSimulate}
              disabled={loading || !location}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-4 rounded-lg shadow-sm transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {loading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  Calculating Impact...
                </>
              ) : (
                <>
                  <Zap className="w-4 h-4" />
                  Simulate Network Disruption
                </>
              )}
            </button>
          </div>
        </div>

        {/* Simulation Output Area */}
        <div className="lg:col-span-7 space-y-6">
          {result ? (
            <div className="space-y-6">
              {/* Impact Comparison Cards */}
              <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
                <div className="flex items-center justify-between border-b border-gray-100 pb-4 mb-5">
                  <div>
                    <h3 className="font-bold text-gray-900 text-lg">Simulation Impact Analysis</h3>
                    <p className="text-xs text-gray-500">
                      Scenario: <span className="font-semibold text-gray-800">{result.scenario}</span> at{' '}
                      <span className="font-semibold text-gray-800">{result.location}</span> ({result.severity})
                    </p>
                  </div>
                  <span className="px-3 py-1 bg-red-100 text-red-700 rounded-full text-xs font-semibold">
                    {result.affected_shipments_count} Shipments Affected
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* BEFORE Card */}
                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-gray-500 uppercase tracking-wider">Baseline (Before)</span>
                      <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                    </div>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Average Risk Score:</span>
                        <span className="font-semibold text-gray-900">{result.before.avg_risk} / 10</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Expected Delay:</span>
                        <span className="font-semibold text-gray-900">{formatMinutes(result.before.avg_delay)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">SLA Breach Prob:</span>
                        <span className="font-semibold text-gray-900">
                          {(result.before.avg_sla_breach_probability * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* AFTER Card */}
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4 space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-red-600 uppercase tracking-wider">Post-Disruption (After)</span>
                      <AlertTriangle className="w-4 h-4 text-red-500" />
                    </div>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-red-700">Average Risk Score:</span>
                        <span className="font-bold text-red-900">
                          {result.after.avg_risk} / 10
                          <span className="text-xs font-normal text-red-600 ml-1">
                            (+{(result.after.avg_risk - result.before.avg_risk).toFixed(1)})
                          </span>
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-red-700">Expected Delay:</span>
                        <span className="font-bold text-red-900">
                          {formatMinutes(result.after.avg_delay)}
                          <span className="text-xs font-normal text-red-600 ml-1">
                            (+{formatMinutes(result.after.avg_delay - result.before.avg_delay)})
                          </span>
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-red-700">SLA Breach Prob:</span>
                        <span className="font-bold text-red-900">
                          {(result.after.avg_sla_breach_probability * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* AI Recommendation Box */}
                {result.recommendation && (
                  <div className="mt-6 bg-blue-50 border border-blue-200 rounded-xl p-5 space-y-3">
                    <div className="flex items-center gap-2 text-blue-900 font-bold text-sm">
                      <ShieldAlert className="w-5 h-5 text-blue-600" />
                      AI MITIGATION ACTION RECOMMENDATION
                    </div>
                    <div>
                      <div className="text-xs font-semibold uppercase text-blue-700 tracking-wider">Recommended Action</div>
                      <div className="text-sm font-bold text-gray-900 mt-0.5">{result.recommendation.action}</div>
                    </div>
                    <div>
                      <div className="text-xs font-semibold uppercase text-blue-700 tracking-wider">Operational Rationale</div>
                      <div className="text-sm text-gray-700 mt-0.5">{result.recommendation.reason}</div>
                    </div>
                    <div>
                      <div className="text-xs font-semibold uppercase text-blue-700 tracking-wider">Expected Operational Benefit</div>
                      <div className="text-sm font-semibold text-emerald-800 mt-0.5">
                        {result.recommendation.expected_benefit}
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Sample Affected Shipments */}
              {result.sample_shipments && result.sample_shipments.length > 0 && (
                <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
                  <h4 className="font-bold text-gray-900 text-sm mb-3">Sample Impacted Shipments (First 5)</h4>
                  <div className="overflow-x-auto">
                    <table className="w-full text-xs text-left">
                      <thead className="bg-gray-50 text-gray-600 uppercase border-b">
                        <tr>
                          <th className="py-2.5 px-3">Tracking Number</th>
                          <th className="py-2.5 px-3">Baseline Risk</th>
                          <th className="py-2.5 px-3">Post-Risk</th>
                          <th className="py-2.5 px-3">Delay Change</th>
                          <th className="py-2.5 px-3">SLA Breach Prob</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-100">
                        {result.sample_shipments.map((s: any) => (
                          <tr key={s.shipment_id} className="hover:bg-gray-50">
                            <td className="py-2.5 px-3 font-mono font-medium text-blue-600">{s.tracking_number}</td>
                            <td className="py-2.5 px-3">{s.before.risk} / 10</td>
                            <td className="py-2.5 px-3 font-bold text-red-600">{s.after.risk} / 10</td>
                            <td className="py-2.5 px-3 font-medium text-gray-900">
                              {formatMinutes(s.before.delay)} → <span className="text-red-600 font-bold">{formatMinutes(s.after.delay)}</span>
                            </td>
                            <td className="py-2.5 px-3">
                              {(s.before.sla_prob * 100).toFixed(0)}% → <span className="font-bold text-red-600">{(s.after.sla_prob * 100).toFixed(0)}%</span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          ) : (
            /* Blank state / instruction */
            <div className="bg-white rounded-xl border border-gray-200 p-8 shadow-sm text-center flex flex-col items-center justify-center min-h-[350px]">
              <Zap className="w-12 h-12 text-amber-400 mb-3" />
              <h3 className="text-base font-bold text-gray-900 mb-1">Ready to Simulate</h3>
              <p className="text-sm text-gray-500 max-w-md">
                Select a scenario (e.g. Severe Weather at Louisville) and click "Simulate Network Disruption" to inspect predicted delays, risk elevation, and alternative reroutes.
              </p>
            </div>
          )}

          {/* Active Network Threats List */}
          <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-base font-bold text-gray-900 flex items-center gap-2">
                <Radio className="w-4 h-4 text-red-500 animate-pulse" />
                Active Network Threats & Incidents
              </h3>
              <button 
                onClick={loadActiveDisruptions}
                className="text-xs text-blue-600 hover:text-blue-700 flex items-center gap-1 font-medium"
              >
                <RefreshCw className="w-3.5 h-3.5" /> Refresh
              </button>
            </div>

            {loadingList ? (
              <div className="py-8 text-center text-gray-400 text-sm">Loading active disruptions...</div>
            ) : activeDisruptions.length === 0 ? (
              <div className="py-6 text-center text-gray-400 text-sm">No critical disruptions currently active.</div>
            ) : (
              <div className="divide-y divide-gray-100 max-h-72 overflow-y-auto pr-1">
                {activeDisruptions.slice(0, 10).map((d, i) => (
                  <div key={d.disruption_id || i} className="py-3 flex items-start justify-between gap-3 text-xs">
                    <div>
                      <div className="font-semibold text-gray-900 flex items-center gap-2">
                        <span>{d.type || 'Incident'}</span>
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                          d.severity === 'CRITICAL' ? 'bg-red-100 text-red-700' :
                          d.severity === 'HIGH' ? 'bg-orange-100 text-orange-700' :
                          'bg-amber-100 text-amber-700'
                        }`}>
                          {d.severity}
                        </span>
                      </div>
                      <div className="text-gray-500 mt-0.5 flex items-center gap-3">
                        <span>Location: {d.location}</span>
                        {d.expected_delay_minutes > 0 && (
                          <span>Delay: ~{formatMinutes(d.expected_delay_minutes)}</span>
                        )}
                      </div>
                    </div>
                    <button
                      onClick={() => {
                        setScenario('severe_weather');
                        setLocation(d.location.replace(/[^a-zA-Z\s]/g, '').trim() || 'Louisville');
                      }}
                      className="text-blue-600 hover:underline text-[11px] font-medium flex-shrink-0"
                    >
                      Simulate Impact
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
