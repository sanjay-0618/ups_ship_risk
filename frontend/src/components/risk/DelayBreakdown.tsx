import React from 'react';
import type { DelayBreakdown as DelayBreakdownType } from '../../types';
import { formatMinutes } from '../../utils/formatters';

interface DelayBreakdownProps {
  delays?: DelayBreakdownType | null;
}

export default function DelayBreakdown({ delays }: DelayBreakdownProps) {
  const safeDelays: DelayBreakdownType = {
    weather_delay: delays?.weather_delay ?? 0,
    traffic_delay: delays?.traffic_delay ?? 0,
    congestion_delay: delays?.congestion_delay ?? 0,
    transport_delay: delays?.transport_delay ?? 0,
    external_event_delay: delays?.external_event_delay ?? 0,
    historical_delay: delays?.historical_delay ?? 0,
    total_delay: delays?.total_delay ?? 0,
  };

  const components = [
    { label: 'Weather Impact', value: safeDelays.weather_delay },
    { label: 'Traffic Conditions', value: safeDelays.traffic_delay },
    { label: 'Hub Congestion', value: safeDelays.congestion_delay },
    { label: 'Transport / Flight Issues', value: safeDelays.transport_delay },
    { label: 'External Events', value: safeDelays.external_event_delay },
    { label: 'Historical Baseline', value: safeDelays.historical_delay },
  ].filter((c) => c.value > 0);

  return (
    <div className="space-y-3">
      <div className="flex justify-between items-end mb-4 border-b border-slate-100 pb-2">
        <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
          Total Expected Delay
        </span>
        <span className="text-lg font-bold text-rose-600">
          +{formatMinutes(safeDelays.total_delay)}
        </span>
      </div>

      {components.length === 0 ? (
        <div className="text-xs text-slate-400 text-center py-4 bg-slate-50 rounded-lg">
          No significant operational delay factors detected.
        </div>
      ) : (
        <ul className="space-y-2">
          {components.map((comp) => (
            <li key={comp.label} className="flex justify-between text-xs py-1 border-b border-slate-50">
              <span className="text-slate-600">{comp.label}</span>
              <span className="font-semibold text-slate-900">+{formatMinutes(comp.value)}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
