import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Package, AlertTriangle, Flame, Clock, 
  Activity, Timer, Zap, ArrowRight, ShieldCheck,
  Compass, Radio, Sparkles
} from 'lucide-react';
import { dashboardApi } from '../services/api';
import type { DashboardSummary } from '../types';
import KPICard from '../components/dashboard/KPICard';
import RiskDistributionChart from '../components/dashboard/RiskDistributionChart';
import LogisticsMap from '../components/map/LogisticsMap';
import RiskBadge from '../components/common/RiskBadge';
import { formatMinutes } from '../utils/formatters';

export default function Dashboard() {
  const [data, setData] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    dashboardApi.getSummary()
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      {/* Top Banner with Subtle Gradient & Live Indicator */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-slate-900 via-indigo-950 to-blue-900 text-white p-6 shadow-md border border-slate-800">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="inline-flex items-center gap-2 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-blue-500/20 text-cyan-300 border border-cyan-500/30">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75" />
                <span className="relative inline-flex rounded-full h-2 w-2 bg-cyan-400" />
              </span>
              REAL-TIME AUTONOMOUS VISIBILITY
            </div>
            <h1 className="text-xl md:text-2xl font-black text-white tracking-tight">
              Predictive Network Operations Hub
            </h1>
            <p className="text-xs md:text-sm text-slate-300 max-w-2xl">
              Causal risk propagation engine analyzing weather, corridor traffic, hub queue bottlenecks, and cargo traits before disruptions cascade.
            </p>
          </div>

          <div className="flex items-center gap-2.5 flex-shrink-0">
            <button
              onClick={() => navigate('/route-planner')}
              className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold transition-all shadow-sm flex items-center gap-1.5"
            >
              <Compass className="w-4 h-4" />
              Plan Route
            </button>
            <button
              onClick={() => navigate('/disruptions')}
              className="px-4 py-2 rounded-xl bg-white/10 hover:bg-white/15 text-white text-xs font-bold border border-white/20 transition-all flex items-center gap-1.5"
            >
              <Zap className="w-4 h-4 text-amber-400" />
              Simulate Threat
            </button>
          </div>
        </div>

        {/* Decorative background glow */}
        <div className="absolute -right-10 -bottom-10 w-64 h-64 bg-blue-500/10 rounded-full blur-3xl pointer-events-none" />
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3.5">
        <KPICard 
          title="Active Volume" 
          value={data?.total_shipments?.toLocaleString() || 0} 
          icon={<Package className="w-4 h-4" />} 
          color="blue" 
          loading={loading} 
        />
        <KPICard 
          title="At Risk" 
          value={data?.at_risk_count || 0} 
          icon={<AlertTriangle className="w-4 h-4" />} 
          color="orange" 
          trend={{ value: 4.2, direction: 'down' }}
          loading={loading} 
        />
        <KPICard 
          title="Critical" 
          value={data?.critical_count || 0} 
          icon={<Flame className="w-4 h-4" />} 
          color="red" 
          loading={loading} 
        />
        <KPICard 
          title="SLA Breaches" 
          value={data?.predicted_sla_breaches || 0} 
          icon={<Clock className="w-4 h-4" />} 
          color="red" 
          loading={loading} 
        />
        <KPICard 
          title="Network Risk" 
          value={data ? `${data.average_network_risk.toFixed(1)} / 10` : '-'} 
          icon={<Activity className="w-4 h-4" />} 
          color="purple" 
          loading={loading} 
        />
        <KPICard 
          title="Avg Delay" 
          value={data ? formatMinutes(data.average_expected_delay) : '-'} 
          icon={<Timer className="w-4 h-4" />} 
          color="yellow" 
          loading={loading} 
        />
      </div>

      {/* Main Content Grid: Map & Secondary Visuals */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Live Network Map */}
        <div className="lg:col-span-8 bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs flex flex-col h-[520px]">
          <div className="flex items-center justify-between mb-3 border-b border-slate-100 pb-3">
            <div>
              <h3 className="font-bold text-slate-900 text-sm flex items-center gap-2">
                <Radio className="w-4 h-4 text-emerald-500 animate-pulse" />
                Live Logistics Network Surveillance Map
              </h3>
              <p className="text-[11px] text-slate-400 mt-0.5">
                Displaying active corridors, high-risk shipments, and facility nodes across North America
              </p>
            </div>
            <span className="text-[11px] font-mono text-slate-500 bg-slate-50 px-2.5 py-1 rounded border border-slate-200">
              75 Nodes Active
            </span>
          </div>
          <div className="flex-1 rounded-xl overflow-hidden">
            <LogisticsMap 
              height="100%" 
              shipments={data?.recent_high_risk_shipments || []} 
              showShipments={true} 
            />
          </div>
        </div>

        {/* Side Panel: Risk Distribution & Priority Alerts */}
        <div className="lg:col-span-4 space-y-6">
          {/* Risk Distribution Chart */}
          <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs">
            <div className="flex justify-between items-center mb-2">
              <h3 className="font-bold text-slate-900 text-sm">Risk Distribution</h3>
              <span className="text-[11px] font-semibold text-slate-400 uppercase">Composite</span>
            </div>
            {data?.risk_distribution && !loading ? (
              <RiskDistributionChart data={data.risk_distribution} />
            ) : (
              <div className="h-48 flex items-center justify-center bg-slate-50 rounded-xl animate-pulse text-xs text-slate-400">
                Loading risk distribution...
              </div>
            )}
          </div>
          
          {/* Priority Watchlist */}
          <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs">
            <div className="flex justify-between items-center mb-3 border-b border-slate-100 pb-2.5">
              <div>
                <h3 className="font-bold text-slate-900 text-sm">Priority Threat Watchlist</h3>
                <p className="text-[11px] text-slate-400">Shipments with highest breach likelihood</p>
              </div>
              <button 
                onClick={() => navigate('/shipments')}
                className="text-xs text-blue-600 hover:text-blue-800 font-bold flex items-center gap-1"
              >
                View all <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
            
            <div className="space-y-2.5">
              {loading ? (
                Array(3).fill(0).map((_, i) => <div key={i} className="h-14 bg-slate-100 rounded-xl animate-pulse" />)
              ) : (
                data?.recent_high_risk_shipments.slice(0, 4).map(shipment => (
                  <div 
                    key={shipment.shipment_id}
                    onClick={() => navigate(`/shipments/${shipment.shipment_id}`)}
                    className="flex justify-between items-center p-2.5 hover:bg-slate-50/80 rounded-xl cursor-pointer border border-slate-100 transition-all hover:border-slate-200 hover:shadow-2xs"
                  >
                    <div>
                      <div className="font-mono text-xs font-bold text-slate-900">{shipment.tracking_number}</div>
                      <div className="text-[11px] text-slate-500 mt-0.5">
                        {shipment.origin_name || shipment.origin_location_id} → {shipment.destination_name || shipment.destination_location_id}
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="text-right">
                        <RiskBadge level={shipment.risk_level} score={shipment.risk_score} />
                        <div className="text-[10px] font-bold text-rose-600 mt-0.5">+{formatMinutes(shipment.expected_delay_minutes)}</div>
                      </div>
                      <ArrowRight className="w-3.5 h-3.5 text-slate-300" />
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
