import React from 'react';
import type { RiskScore } from '../../types';

export default function RiskBreakdown({ risk }: { risk?: Partial<RiskScore> | null }) {
  const safeRisk = {
    weather_score: risk?.weather_score ?? 1.0,
    traffic_score: risk?.traffic_score ?? 1.0,
    congestion_score: risk?.congestion_score ?? 1.0,
    transport_score: risk?.transport_score ?? 1.0,
    external_event_score: risk?.external_event_score ?? 1.0,
    historical_score: risk?.historical_score ?? 1.0,
    risk_factors: risk?.risk_factors ?? [],
  };

  const components = [
    { label: 'Weather Exposure', value: safeRisk.weather_score, color: 'bg-blue-500' },
    { label: 'Corridor Traffic', value: safeRisk.traffic_score, color: 'bg-amber-500' },
    { label: 'Hub Congestion', value: safeRisk.congestion_score, color: 'bg-orange-500' },
    { label: 'Flight / Transport', value: safeRisk.transport_score, color: 'bg-purple-500' },
    { label: 'External Incidents', value: safeRisk.external_event_score, color: 'bg-red-500' },
    { label: 'Historical Corridor', value: safeRisk.historical_score, color: 'bg-slate-500' },
  ];

  return (
    <div className="space-y-3.5">
      {components.map((comp) => (
        <div key={comp.label}>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-slate-600 font-medium">{comp.label}</span>
            <span className="font-mono font-bold text-slate-900">{comp.value.toFixed(1)} / 10</span>
          </div>
          <div className="w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
            <div 
              className={`${comp.color} h-1.5 rounded-full transition-all duration-300`}
              style={{ width: `${Math.min(100, Math.max(5, (comp.value / 10) * 100))}%` }}
            />
          </div>
        </div>
      ))}
      
      {safeRisk.risk_factors && safeRisk.risk_factors.length > 0 && (
        <div className="mt-4 pt-3 border-t border-slate-100">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 mb-2">Key Operational Risk Factors</h4>
          <ul className="list-disc pl-4 text-xs text-slate-600 space-y-1">
            {safeRisk.risk_factors.map((factor, i) => (
              <li key={i}>{factor}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
