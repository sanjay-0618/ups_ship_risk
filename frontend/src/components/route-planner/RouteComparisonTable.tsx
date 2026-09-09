import React from 'react';
import type { RouteResult } from '../../types';
import RiskBadge from '../common/RiskBadge';
import { formatMinutes } from '../../utils/formatters';
import { Check } from 'lucide-react';

interface RouteComparisonTableProps {
  routes: RouteResult[];
  recommendedId: string;
  selectedId: string;
  onSelect: (id: string) => void;
}

export default function RouteComparisonTable({ routes, recommendedId, selectedId, onSelect }: RouteComparisonTableProps) {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Route</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Time</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Risk</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">SLA Prob.</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"></th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {routes.map((route) => (
            <tr 
              key={route.route_id}
              onClick={() => onSelect(route.route_id)}
              className={`cursor-pointer transition-colors ${selectedId === route.route_id ? 'bg-blue-50/50' : 'hover:bg-gray-50'}`}
            >
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="flex items-center">
                  <div>
                    <div className="font-medium text-gray-900 flex items-center">
                      {route.route_name}
                      {route.route_id === recommendedId && (
                        <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                          Recommended
                        </span>
                      )}
                    </div>
                    <div className="text-sm text-gray-500">{route.distance_km} km</div>
                  </div>
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm text-gray-900">{formatMinutes(route.risk_adjusted_time_minutes)}</div>
                <div className="text-sm text-red-500">+{formatMinutes(route.expected_delay_minutes)} delay</div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <RiskBadge level={route.risk_level} score={route.overall_risk_score} />
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {(route.sla_breach_probability * 100).toFixed(1)}%
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-right">
                {selectedId === route.route_id ? (
                  <Check className="w-5 h-5 text-blue-600 inline" />
                ) : (
                  <span className="text-sm text-gray-400 hover:text-gray-600">Select</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
