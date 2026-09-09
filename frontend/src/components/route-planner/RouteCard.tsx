import React from 'react';
import { Clock, Navigation, AlertTriangle, ShieldCheck } from 'lucide-react';
import type { RouteResult } from '../../types';
import RiskBadge from '../common/RiskBadge';
import { formatMinutes } from '../../utils/formatters';

interface RouteCardProps {
  route: RouteResult;
  isRecommended: boolean;
  isSelected: boolean;
  onSelect: (routeId: string) => void;
}

export default function RouteCard({ route, isRecommended, isSelected, onSelect }: RouteCardProps) {
  return (
    <div 
      className={`
        relative rounded-xl border p-5 cursor-pointer transition-all
        ${isSelected ? 'border-blue-500 ring-1 ring-blue-500 bg-blue-50/30' : 'border-gray-200 hover:border-blue-300 hover:shadow-md bg-white'}
      `}
      onClick={() => onSelect(route.route_id)}
    >
      {isRecommended && (
        <div className="absolute -top-3 left-4 bg-blue-600 text-white px-2 py-0.5 rounded-full text-xs font-bold flex items-center shadow-sm">
          <ShieldCheck className="w-3 h-3 mr-1" />
          AI RECOMMENDED
        </div>
      )}

      <div className="flex justify-between items-start mb-3 mt-1">
        <h3 className="font-semibold text-gray-900">{route.route_name}</h3>
        <RiskBadge level={route.risk_level} score={route.overall_risk_score} />
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
        <div>
          <span className="text-gray-500 block mb-1">Distance</span>
          <div className="flex items-center text-gray-900 font-medium">
            <Navigation className="w-4 h-4 mr-1.5 text-gray-400" />
            {route.distance_km} km
          </div>
        </div>
        <div>
          <span className="text-gray-500 block mb-1">Base Time</span>
          <div className="flex items-center text-gray-900 font-medium">
            <Clock className="w-4 h-4 mr-1.5 text-gray-400" />
            {formatMinutes(route.base_travel_time_minutes)}
          </div>
        </div>
      </div>

      <div className="bg-gray-50 rounded-lg p-3 space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="text-gray-600">Expected Delay:</span>
          <span className={`font-medium ${route.expected_delay_minutes > 60 ? 'text-red-600' : 'text-orange-600'}`}>
            +{formatMinutes(route.expected_delay_minutes)}
          </span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-600">SLA Breach Prob:</span>
          <span className={`font-medium ${route.sla_breach_probability > 0.5 ? 'text-red-600' : 'text-gray-900'}`}>
            {(route.sla_breach_probability * 100).toFixed(1)}%
          </span>
        </div>
        <div className="flex justify-between border-t border-gray-200 pt-2 mt-2">
          <span className="font-medium text-gray-900">Total Est. Time:</span>
          <span className="font-bold text-gray-900">
            {formatMinutes(route.risk_adjusted_time_minutes)}
          </span>
        </div>
      </div>
    </div>
  );
}
