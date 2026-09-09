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

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Shipments</h1>
          <p className="text-gray-500 mt-1">Manage and track all network shipments.</p>
        </div>
      </div>

      <div className="bg-white p-4 rounded-xl border border-gray-100 shadow-sm flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input 
            type="text" 
            placeholder="Search tracking numbers..." 
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        
        <div className="flex items-center space-x-2">
          <Filter className="w-5 h-5 text-gray-400" />
          <select 
            value={riskFilter}
            onChange={(e) => setRiskFilter(e.target.value as any)}
            className="border border-gray-300 rounded-lg py-2 pl-3 pr-8 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="ALL">All Risk Levels</option>
            <option value="CRITICAL">Critical Risk</option>
            <option value="HIGH">High Risk</option>
            <option value="MEDIUM">Medium Risk</option>
            <option value="LOW">Low Risk</option>
          </select>
        </div>
      </div>

      <div className="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tracking #</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Route</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Risk Level</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Exp. Delay</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {loading ? (
                Array(5).fill(0).map((_, i) => (
                  <tr key={i}>
                    <td colSpan={6} className="px-6 py-4 whitespace-nowrap">
                      <SkeletonLoader className="h-6 w-full" />
                    </td>
                  </tr>
                ))
              ) : shipments.filter(s => search === '' || s.tracking_number.includes(search)).length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-gray-500">
                    No shipments found matching the criteria.
                  </td>
                </tr>
              ) : (
                shipments
                  .filter(s => search === '' || s.tracking_number.includes(search))
                  .map((shipment) => (
                  <tr 
                    key={shipment.shipment_id} 
                    className="hover:bg-gray-50 cursor-pointer transition-colors"
                    onClick={() => navigate(`/shipments/${shipment.shipment_id}`)}
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="font-medium text-blue-600">{shipment.tracking_number}</div>
                      <div className="text-xs text-gray-500">{shipment.priority} Priority</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{shipment.origin_name || shipment.origin_location_id}</div>
                      <div className="text-sm text-gray-500">to {shipment.destination_name || shipment.destination_location_id}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="px-2.5 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800">
                        {shipment.status.replace(/_/g, ' ')}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <RiskBadge level={shipment.risk_level} score={shipment.risk_score} />
                      {shipment.sla_breach_probability > 0.5 && (
                        <div className="text-xs text-red-500 mt-1 flex items-center">
                          <AlertTriangle className="w-3 h-3 mr-1" />
                          High SLA Risk
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className={`text-sm font-medium ${shipment.expected_delay_minutes > 60 ? 'text-red-600' : 'text-orange-600'}`}>
                        {shipment.expected_delay_minutes > 0 ? `+${formatMinutes(shipment.expected_delay_minutes)}` : 'On time'}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button 
                        className="text-gray-400 hover:text-blue-600 p-2"
                        onClick={(e) => { e.stopPropagation(); navigate(`/shipments/${shipment.shipment_id}`); }}
                      >
                        <Eye className="w-5 h-5" />
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
