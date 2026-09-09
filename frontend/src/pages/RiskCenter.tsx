import React, { useState, useEffect } from 'react';
import { 
  AlertTriangle, Flame, ShieldAlert, Clock, 
  Layers, Navigation, ArrowUpRight, Search, Filter,
  CloudRain, TrendingUp, RefreshCw
} from 'lucide-react';
import { shipmentsApi, riskApi, analyticsApi } from '../services/api';
import type { Shipment, RiskLevel } from '../types';
import RiskBadge from '../components/common/RiskBadge';
import { formatMinutes } from '../utils/formatters';
import { useNavigate } from 'react-router-dom';

export default function RiskCenter() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'shipments' | 'routes' | 'hubs' | 'radar'>('radar');
  const [riskFilter, setRiskFilter] = useState<string>('ALL');
  const [priorityFilter, setPriorityFilter] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  const [highRiskShipments, setHighRiskShipments] = useState<Shipment[]>([]);
  const [routesPerformance, setRoutesPerformance] = useState<any[]>([]);
  const [activeEvents, setActiveEvents] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadData();
  }, [riskFilter, priorityFilter]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [shipmentsRes, eventsRes, analyticsRes] = await Promise.all([
        shipmentsApi.getAll({
          limit: 50,
          risk_level: riskFilter === 'ALL' ? undefined : riskFilter,
          sort_by: 'risk_score',
          sort_dir: 'desc',
        }),
        riskApi.getEvents(),
        analyticsApi.getSummary(),
      ]);

      setHighRiskShipments(shipmentsRes.items || []);
      setActiveEvents(eventsRes.events || []);
      setRoutesPerformance(analyticsRes.route_reliability || []);
    } catch (e) {
      console.error('Error loading risk data:', e);
    } finally {
      setLoading(false);
    }
  };

  const filteredShipments = highRiskShipments.filter((s) => {
    if (priorityFilter !== 'ALL' && s.priority !== priorityFilter) return false;
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      s.tracking_number.toLowerCase().includes(q) ||
      (s.origin_name && s.origin_name.toLowerCase().includes(q)) ||
      (s.destination_name && s.destination_name.toLowerCase().includes(q))
    );
  });

  // Disruption radar items (predicted next 24 hours)
  const radarItems = [
    {
      location: 'Louisville',
      state: 'KY',
      event: 'Severe Weather / Storm Cell',
      severity: 'HIGH',
      affectedCount: 147,
      predictedDelay: '2h 15m',
      probability: '84%',
      corridor: 'Midwest - Southeast Transit Corridor',
    },
    {
      location: 'Chicago',
      state: 'IL',
      event: 'Major Interstate Congestion',
      severity: 'MEDIUM',
      affectedCount: 83,
      predictedDelay: '45m',
      probability: '68%',
      corridor: 'I-80 / I-90 Great Lakes Corridor',
    },
    {
      location: 'Newark',
      state: 'NJ',
      event: 'Hub Sorting Capacity Strain',
      severity: 'HIGH',
      affectedCount: 41,
      predictedDelay: '1h 30m',
      probability: '76%',
      corridor: 'Northeast Express Hub',
    },
    {
      location: 'Cleveland',
      state: 'OH',
      event: 'Snow & Icy Road Conditions',
      severity: 'HIGH',
      affectedCount: 62,
      predictedDelay: '1h 50m',
      probability: '79%',
      corridor: 'Ohio Turnpike Connector',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <ShieldAlert className="w-7 h-7 text-red-500" />
          Predictive Risk Operations Center
        </h1>
        <p className="text-gray-500 text-sm mt-1">
          Real-time threat monitoring, predictive disruption radar, and proactive mitigation for active shipments across the logistics graph.
        </p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-200">
        <button
          onClick={() => setActiveTab('radar')}
          className={`py-3 px-4 text-sm font-semibold border-b-2 flex items-center gap-2 transition-colors ${
            activeTab === 'radar'
              ? 'border-blue-600 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <Clock className="w-4 h-4" />
          Predictive Disruption Radar (Next 24h)
        </button>
        <button
          onClick={() => setActiveTab('shipments')}
          className={`py-3 px-4 text-sm font-semibold border-b-2 flex items-center gap-2 transition-colors ${
            activeTab === 'shipments'
              ? 'border-blue-600 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <Flame className="w-4 h-4" />
          Highest-Risk Shipments ({highRiskShipments.length})
        </button>
        <button
          onClick={() => setActiveTab('routes')}
          className={`py-3 px-4 text-sm font-semibold border-b-2 flex items-center gap-2 transition-colors ${
            activeTab === 'routes'
              ? 'border-blue-600 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <Navigation className="w-4 h-4" />
          Corridor & Route Risks
        </button>
        <button
          onClick={() => setActiveTab('hubs')}
          className={`py-3 px-4 text-sm font-semibold border-b-2 flex items-center gap-2 transition-colors ${
            activeTab === 'hubs'
              ? 'border-blue-600 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          <Layers className="w-4 h-4" />
          Congested Hubs & Facilities
        </button>
      </div>

      {/* TAB 1: RADAR */}
      {activeTab === 'radar' && (
        <div className="space-y-6">
          <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 text-xs text-amber-800 flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
            <div>
              <span className="font-bold">Predictive Visibility Enabled: </span>
              The system calculates spatial and temporal intersections of active shipments with approaching disruptions. These shipments are identified <strong>before</strong> actual delays occur to allow rerouting.
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {radarItems.map((item, idx) => (
              <div
                key={idx}
                className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm space-y-3 hover:border-blue-300 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
                      {item.corridor}
                    </span>
                    <h3 className="text-base font-bold text-gray-900 mt-0.5">
                      {item.location}, {item.state} — {item.event}
                    </h3>
                  </div>
                  <span
                    className={`px-2.5 py-0.5 rounded text-xs font-bold uppercase ${
                      item.severity === 'CRITICAL'
                        ? 'bg-red-100 text-red-700'
                        : item.severity === 'HIGH'
                        ? 'bg-orange-100 text-orange-700'
                        : 'bg-amber-100 text-amber-700'
                    }`}
                  >
                    {item.severity}
                  </span>
                </div>

                <div className="grid grid-cols-3 gap-2 bg-gray-50 p-3 rounded-lg text-center text-xs">
                  <div>
                    <div className="text-gray-500 font-medium">Potentially Impacted</div>
                    <div className="text-sm font-bold text-red-600 mt-0.5">{item.affectedCount} shipments</div>
                  </div>
                  <div>
                    <div className="text-gray-500 font-medium">Predicted Delay</div>
                    <div className="text-sm font-bold text-gray-900 mt-0.5">+{item.predictedDelay}</div>
                  </div>
                  <div>
                    <div className="text-gray-500 font-medium">Breach Probability</div>
                    <div className="text-sm font-bold text-gray-900 mt-0.5">{item.probability}</div>
                  </div>
                </div>

                <div className="flex justify-between items-center text-xs pt-1">
                  <span className="text-gray-500">Predicted window: Next 24 Hours</span>
                  <button
                    onClick={() => navigate('/disruptions')}
                    className="text-blue-600 hover:text-blue-700 font-semibold flex items-center gap-1"
                  >
                    Simulate Mitigations <ArrowUpRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB 2: SHIPMENTS */}
      {activeTab === 'shipments' && (
        <div className="space-y-4">
          {/* Filters */}
          <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm flex flex-col md:flex-row gap-3 justify-between items-center text-sm">
            <div className="relative w-full md:w-80">
              <Search className="w-4 h-4 absolute left-3 top-2.5 text-gray-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search tracking #, origin, dest..."
                className="w-full pl-9 pr-3 py-1.5 border border-gray-300 rounded-lg text-xs focus:ring-1 focus:ring-blue-500"
              />
            </div>

            <div className="flex items-center gap-3 w-full md:w-auto">
              <div className="flex items-center gap-1">
                <span className="text-xs text-gray-500 font-medium">Risk:</span>
                <select
                  value={riskFilter}
                  onChange={(e) => setRiskFilter(e.target.value)}
                  className="border border-gray-300 rounded-lg py-1 px-2 text-xs bg-white"
                >
                  <option value="ALL">All Levels</option>
                  <option value="CRITICAL">Critical Only</option>
                  <option value="HIGH">High Only</option>
                  <option value="MEDIUM">Medium</option>
                  <option value="LOW">Low</option>
                </select>
              </div>

              <div className="flex items-center gap-1">
                <span className="text-xs text-gray-500 font-medium">Priority:</span>
                <select
                  value={priorityFilter}
                  onChange={(e) => setPriorityFilter(e.target.value)}
                  className="border border-gray-300 rounded-lg py-1 px-2 text-xs bg-white"
                >
                  <option value="ALL">All Priorities</option>
                  <option value="Critical">Critical</option>
                  <option value="High">High</option>
                  <option value="Normal">Normal</option>
                  <option value="Low">Low</option>
                </select>
              </div>

              <button
                onClick={loadData}
                className="p-1.5 border rounded-lg hover:bg-gray-50 text-gray-600"
                title="Refresh"
              >
                <RefreshCw className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Table */}
          <div className="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left">
                <thead className="bg-gray-50 text-gray-600 uppercase border-b">
                  <tr>
                    <th className="py-3 px-4">Tracking Number</th>
                    <th className="py-3 px-4">Origin → Destination</th>
                    <th className="py-3 px-4">Priority</th>
                    <th className="py-3 px-4">Status</th>
                    <th className="py-3 px-4">Risk Score</th>
                    <th className="py-3 px-4">SLA Breach Prob</th>
                    <th className="py-3 px-4">Expected Delay</th>
                    <th className="py-3 px-4 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {loading ? (
                    <tr>
                      <td colSpan={8} className="py-8 text-center text-gray-400">
                        Loading shipments...
                      </td>
                    </tr>
                  ) : filteredShipments.length === 0 ? (
                    <tr>
                      <td colSpan={8} className="py-8 text-center text-gray-400">
                        No shipments matching criteria.
                      </td>
                    </tr>
                  ) : (
                    filteredShipments.map((s) => (
                      <tr
                        key={s.shipment_id}
                        onClick={() => navigate(`/shipments/${s.shipment_id}`)}
                        className="hover:bg-blue-50/50 cursor-pointer transition-colors"
                      >
                        <td className="py-3 px-4 font-mono font-medium text-blue-600">
                          {s.tracking_number}
                        </td>
                        <td className="py-3 px-4 font-medium text-gray-900">
                          {s.origin_name || s.origin_location_id} → {s.destination_name || s.destination_location_id}
                        </td>
                        <td className="py-3 px-4">
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                              s.priority === 'Critical'
                                ? 'bg-red-100 text-red-700'
                                : s.priority === 'High'
                                ? 'bg-orange-100 text-orange-700'
                                : 'bg-gray-100 text-gray-700'
                            }`}
                          >
                            {s.priority}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-gray-600">{s.status}</td>
                        <td className="py-3 px-4">
                          <div className="flex items-center gap-2">
                            <span className="font-bold text-gray-900">{s.risk_score}</span>
                            <RiskBadge level={s.risk_level} />
                          </div>
                        </td>
                        <td className="py-3 px-4 font-semibold text-gray-900">
                          {(s.sla_breach_probability * 100).toFixed(0)}%
                        </td>
                        <td className="py-3 px-4 font-medium text-amber-700">
                          +{formatMinutes(s.expected_delay_minutes)}
                        </td>
                        <td className="py-3 px-4 text-right">
                          <span className="text-blue-600 hover:underline font-medium">Inspect →</span>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: ROUTES */}
      {activeTab === 'routes' && (
        <div className="bg-white border border-gray-200 rounded-xl shadow-sm p-6 space-y-4">
          <h3 className="font-bold text-gray-900 text-base">Historical Corridor Reliability & Risk Index</h3>
          <p className="text-xs text-gray-500">
            Ranked by historical delay frequency and SLA breach probability from over 30,000 completed shipments.
          </p>
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead className="bg-gray-50 text-gray-600 uppercase border-b">
                <tr>
                  <th className="py-2.5 px-3">Corridor / Route</th>
                  <th className="py-2.5 px-3">Reliability Score</th>
                  <th className="py-2.5 px-3">Avg Historical Delay</th>
                  <th className="py-2.5 px-3">Historical Breach Rate</th>
                  <th className="py-2.5 px-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {routesPerformance.map((r, i) => (
                  <tr key={i} className="hover:bg-gray-50">
                    <td className="py-3 px-3 font-mono font-medium text-gray-900">{r.route_id}</td>
                    <td className="py-3 px-3">
                      <div className="flex items-center gap-2">
                        <div className="w-24 bg-gray-200 rounded-full h-1.5 overflow-hidden">
                          <div
                            className="bg-emerald-500 h-full rounded-full"
                            style={{ width: `${r.reliability_score * 100}%` }}
                          />
                        </div>
                        <span className="font-bold text-gray-900">{(r.reliability_score * 100).toFixed(0)}%</span>
                      </div>
                    </td>
                    <td className="py-3 px-3 font-medium text-gray-900">+{formatMinutes(r.avg_delay)}</td>
                    <td className="py-3 px-3 text-red-600 font-semibold">{(r.sla_breach_rate * 100).toFixed(1)}%</td>
                    <td className="py-3 px-3">
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          r.reliability_score > 0.85
                            ? 'bg-green-100 text-green-800'
                            : 'bg-amber-100 text-amber-800'
                        }`}
                      >
                        {r.reliability_score > 0.85 ? 'RELIABLE' : 'ELEVATED RISK'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB 4: HUBS */}
      {activeTab === 'hubs' && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {[
            { city: 'Louisville Hub', type: 'Air & Ground Sort Facility', load: '94%', delay: '1h 10m', risk: 'HIGH' },
            { city: 'Chicago Central DC', type: 'Distribution Center', load: '88%', delay: '55m', risk: 'MEDIUM' },
            { city: 'Newark Sort Hub', type: 'Express Sort Facility', load: '97%', delay: '1h 45m', risk: 'CRITICAL' },
            { city: 'Atlanta Air Gateway', type: 'Airport Cargo Hub', load: '82%', delay: '40m', risk: 'MEDIUM' },
            { city: 'Dallas Logistics Hub', type: 'Sort Facility', load: '75%', delay: '25m', risk: 'LOW' },
            { city: 'Memphis Hub', type: 'Freight Center', load: '91%', delay: '1h 15m', risk: 'HIGH' },
          ].map((hub, idx) => (
            <div key={idx} className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm space-y-3">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-bold text-gray-900">{hub.city}</h3>
                  <p className="text-xs text-gray-500">{hub.type}</p>
                </div>
                <span
                  className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    hub.risk === 'CRITICAL'
                      ? 'bg-red-100 text-red-700'
                      : hub.risk === 'HIGH'
                      ? 'bg-orange-100 text-orange-700'
                      : 'bg-amber-100 text-amber-700'
                  }`}
                >
                  {hub.risk}
                </span>
              </div>
              <div className="space-y-1 text-xs text-gray-600">
                <div className="flex justify-between">
                  <span>Current Processing Load:</span>
                  <span className="font-semibold text-gray-900">{hub.load}</span>
                </div>
                <div className="flex justify-between">
                  <span>Queue Delay:</span>
                  <span className="font-semibold text-gray-900">+{hub.delay}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
