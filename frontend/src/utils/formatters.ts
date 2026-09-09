import { format } from 'date-fns';
import type { RiskLevel } from '../types';

export function formatMinutes(minutes: number): string {
  if (minutes < 60) return `${Math.round(minutes)}m`;
  const h = Math.floor(minutes / 60);
  const m = Math.round(minutes % 60);
  return m > 0 ? `${h}h ${m}m` : `${h}h`;
}

export function formatRiskLevel(level: RiskLevel): string {
  return level.charAt(0) + level.slice(1).toLowerCase();
}

export function formatPercentage(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

export function formatDateTime(iso: string): string {
  if (!iso) return '-';
  try {
    return format(new Date(iso), 'MMM d, h:mm a');
  } catch (e) {
    return iso;
  }
}

export function getRiskColor(level: RiskLevel): string {
  switch (level) {
    case 'LOW': return 'text-risk-low';
    case 'MEDIUM': return 'text-risk-medium';
    case 'HIGH': return 'text-risk-high';
    case 'CRITICAL': return 'text-risk-critical';
    default: return 'text-gray-500';
  }
}

export function getRiskBgColor(level: RiskLevel): string {
  switch (level) {
    case 'LOW': return 'bg-risk-low/10';
    case 'MEDIUM': return 'bg-risk-medium/10';
    case 'HIGH': return 'bg-risk-high/10';
    case 'CRITICAL': return 'bg-risk-critical/10';
    default: return 'bg-gray-100';
  }
}
