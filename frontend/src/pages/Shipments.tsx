import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Filter, AlertTriangle, Eye } from 'lucide-react';
import { shipmentsApi } from '../services/api';
import type { Shipment, RiskLevel } from '../types';
import RiskBadge from '../components/common/RiskBadge';
import { formatMinutes, formatDateTime } from '../utils/formatters';
import { SkeletonLoader } from '../components/common/SkeletonLoader';

export default function Shipments() {
  const navigate = useNavigate();
  const [shipments, setShipments] = useState<Shipment[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [riskFilter, setRiskFilter] = useState<RiskLevel | 'ALL'>('ALL');

  useEffect(() => {
    setLoading(true);
    shipmentsApi.getAll({ limit: 50, risk_level: riskFilter !== 'ALL' ? riskFilter : undefined })
      .then(res => setShipments(res.items))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [riskFilter]);

  const filterOptions: { label: string; value: RiskLevel | 'ALL'; color: string }[] = [
    { label: 'All Shipments', value: 'ALL', color: 'border-slate-300 text-slate-700' },
    { label: 'Critical Risk', value: 'CRITICAL', color: 'border-rose-300 text-rose-700 bg-rose-50/70' },
    { label: 'High Risk', value: 'HIGH', color: 'border-orange-300 text-orange-700 bg-orange-50/70' },
    { label: 'Medium Risk', value: 'MEDIUM', color: 'border-amber-300 text-amber-800 bg-amber-50/70' },
    { label: 'Low Risk', value: 'LOW', color: 'border-emerald-300 text-emerald-700 bg-emerald-50/70' },
  ];

  const getPriorityStyle = (priority: string) => {
    switch (priority?.toUpperCase()) {
      case 'CRITICAL': return 'bg-rose-50 text-rose-700 border-rose-200';
      case 'HIGH': return 'bg-amber-50 text-amber-700 border-amber-200';
      case 'NORMAL': return 'bg-blue-50 text-blue-700 border-blue-200';
      default: return 'bg-slate-50 text-slate-700 border-slate-200';
    }
  };

  const getStatusStyle = (status: string) => {
    switch (status?.toUpperCase()) {
      case 'IN_TRANSIT': return 'bg-blue-50 text-blue-700 border-blue-200';
      case 'DELAYED': return 'bg-rose-50 text-rose-700 border-rose-200';
      case 'DELIVERED': return 'bg-emerald-50 text-emerald-700 border-emerald-200';
      case 'PROCESSING': return 'bg-indigo-50 text-indigo-700 border-indigo-200';
      default: return 'bg-slate-100 text-slate-700 border-slate-200';
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-black text-slate-900 tracking-tight">Active Shipments</h1>
            <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200">
              {shipments.length} Loaded
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">Real-time status, route tracking, and delay exposure across North America.</p>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-xs space-y-3">
        <div className="flex flex-col md:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input 
              type="text" 
              placeholder="Search by tracking number, origin, or destination..." 
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-4 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:ring-2 focus:ring-blue-100 focus:border-blue-500 outline-none transition-all placeholder:text-slate-400"
            />
          </div>

          {/* Risk Level Pills */}
          <div className="flex flex-wrap items-center gap-1.5">
            {filterOptions.map((opt) => (
              <button
                key={opt.value}
                onClick={() => setRiskFilter(opt.value)}
                className={`
                  px-3 py-1.5 text-xs font-bold rounded-xl border transition-all
                  ${riskFilter === opt.value
                    ? 'bg-slate-900 text-white border-slate-900 shadow-xs'
                    : 'bg-white text-slate-600 border-slate-200 hover:border-slate-300 hover:bg-slate-50'}
                `}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Shipments Table */}
      <div className="bg-white border border-slate-200/80 rounded-2xl shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-100">
            <thead className="bg-slate-50/80">
              <tr>
                <th className="px-6 py-3.5 text-left text-[11px] font-bold text-slate-500 uppercase tracking-wider">Tracking & Priority</th>
                <th className="px-6 py-3.5 text-left text-[11px] font-bold text-slate-500 uppercase tracking-wider">Transit Corridor</th>
                <th className="px-6 py-3.5 text-left text-[11px] font-bold text-slate-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3.5 text-left text-[11px] font-bold text-slate-500 uppercase tracking-wider">Risk Level</th>
                <th className="px-6 py-3.5 text-left text-[11px] font-bold text-slate-500 uppercase tracking-wider">Exp. Delay</th>
                <th className="px-6 py-3.5 text-right text-[11px] font-bold text-slate-500 uppercase tracking-wider">Details</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-slate-100">
              {loading ? (
                Array(5).fill(0).map((_, i) => (
                  <tr key={i}>
                    <td colSpan={6} className="px-6 py-4 whitespace-nowrap">
                      <SkeletonLoader className="h-7 w-full" />
                    </td>
                  </tr>
                ))
              ) : shipments.filter(s => search === '' || s.tracking_number.toLowerCase().includes(search.toLowerCase())).length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-slate-400 text-xs">
                    No shipments found matching the selected filter.
                  </td>
                </tr>
              ) : (
                shipments
                  .filter(s => search === '' || s.tracking_number.toLowerCase().includes(search.toLowerCase()))
                  .map((shipment) => (
                  <tr 
                    key={shipment.shipment_id} 
                    className="hover:bg-blue-50/30 cursor-pointer transition-colors group"
                    onClick={() => navigate(`/shipments/${shipment.shipment_id}`)}
                  >
                    <td className="px-6 py-3.5 whitespace-nowrap">
                      <div className="font-mono text-xs font-bold text-blue-600 group-hover:text-blue-700 flex items-center gap-1.5">
                        {shipment.tracking_number}
                      </div>
                      <span className={`inline-block mt-1 px-2 py-0.5 text-[10px] font-bold rounded-md border ${getPriorityStyle(shipment.priority)}`}>
                        {shipment.priority} Priority
                      </span>
                    </td>
                    <td className="px-6 py-3.5 whitespace-nowrap">
                      <div className="text-xs font-semibold text-slate-800">{shipment.origin_name || shipment.origin_location_id}</div>
                      <div className="text-[11px] text-slate-400">→ {shipment.destination_name || shipment.destination_location_id}</div>
                    </td>
                    <td className="px-6 py-3.5 whitespace-nowrap">
                      <span className={`px-2.5 py-1 text-[11px] font-bold rounded-full border ${getStatusStyle(shipment.status)}`}>
                        {shipment.status.replace(/_/g, ' ')}
                      </span>
                    </td>
                    <td className="px-6 py-3.5 whitespace-nowrap">
                      <RiskBadge level={shipment.risk_level} score={shipment.risk_score} />
                      {shipment.sla_breach_probability > 0.5 && (
                        <div className="text-[10px] font-bold text-rose-600 mt-1 flex items-center gap-1">
                          <AlertTriangle className="w-3 h-3" />
                          High SLA Threat
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-3.5 whitespace-nowrap">
                      <div className={`text-xs font-bold font-mono ${shipment.expected_delay_minutes > 60 ? 'text-rose-600' : 'text-amber-600'}`}>
                        {shipment.expected_delay_minutes > 0 ? `+${formatMinutes(shipment.expected_delay_minutes)}` : 'On Time'}
                      </div>
                    </td>
                    <td className="px-6 py-3.5 whitespace-nowrap text-right text-xs font-medium">
                      <button 
                        className="text-slate-400 hover:text-blue-600 p-1.5 rounded-lg hover:bg-blue-50 transition-colors"
                        onClick={(e) => { e.stopPropagation(); navigate(`/shipments/${shipment.shipment_id}`); }}
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
