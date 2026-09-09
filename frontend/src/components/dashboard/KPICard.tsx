import React from 'react';
import { SkeletonLoader } from '../common/SkeletonLoader';

interface KPICardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  color: 'blue' | 'orange' | 'red' | 'green' | 'purple' | 'yellow';
  trend?: { value: number; direction: 'up' | 'down' };
  loading?: boolean;
}

const COLOR_STYLES = {
  blue: {
    iconBg: 'bg-blue-50 text-blue-600 border border-blue-200/60',
    borderAccent: 'group-hover:border-blue-300',
    topLine: 'bg-blue-500',
    hoverGlow: 'hover:shadow-blue-500/5',
  },
  orange: {
    iconBg: 'bg-amber-50 text-amber-600 border border-amber-200/60',
    borderAccent: 'group-hover:border-amber-300',
    topLine: 'bg-amber-500',
    hoverGlow: 'hover:shadow-amber-500/5',
  },
  red: {
    iconBg: 'bg-rose-50 text-rose-600 border border-rose-200/60',
    borderAccent: 'group-hover:border-rose-300',
    topLine: 'bg-rose-500',
    hoverGlow: 'hover:shadow-rose-500/5',
  },
  green: {
    iconBg: 'bg-emerald-50 text-emerald-600 border border-emerald-200/60',
    borderAccent: 'group-hover:border-emerald-300',
    topLine: 'bg-emerald-500',
    hoverGlow: 'hover:shadow-emerald-500/5',
  },
  purple: {
    iconBg: 'bg-indigo-50 text-indigo-600 border border-indigo-200/60',
    borderAccent: 'group-hover:border-indigo-300',
    topLine: 'bg-indigo-500',
    hoverGlow: 'hover:shadow-indigo-500/5',
  },
  yellow: {
    iconBg: 'bg-amber-50 text-amber-600 border border-amber-200/60',
    borderAccent: 'group-hover:border-amber-300',
    topLine: 'bg-amber-500',
    hoverGlow: 'hover:shadow-amber-500/5',
  },
};

export default function KPICard({ title, value, icon, color, trend, loading }: KPICardProps) {
  const style = COLOR_STYLES[color] || COLOR_STYLES.blue;

  return (
    <div
      className={`
        group relative bg-white rounded-2xl shadow-xs border border-slate-200/80 p-5 flex flex-col justify-between overflow-hidden
        transition-all duration-300 hover:-translate-y-1 hover:shadow-xl ${style.borderAccent} ${style.hoverGlow}
      `}
    >
      {/* Top micro-line accent */}
      <div className={`absolute top-0 left-0 right-0 h-1 ${style.topLine} opacity-80 group-hover:h-1.5 transition-all`} />

      <div className="flex justify-between items-start mb-3 pt-1">
        <h3 className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">{title}</h3>
        <div className={`p-2.5 rounded-xl ${style.iconBg} shadow-2xs group-hover:scale-105 transition-transform`}>
          {icon}
        </div>
      </div>
      
      {loading ? (
        <SkeletonLoader className="h-8 w-24 mb-1" />
      ) : (
        <div className="flex items-baseline justify-between mt-1">
          <span className="text-2xl lg:text-[26px] font-extrabold text-slate-900 tracking-tight font-feature-settings">{value}</span>
          {trend && (
            <span
              className={`inline-flex items-center gap-0.5 px-2 py-0.5 rounded-full text-[10px] font-bold tracking-wide ${
                trend.direction === 'up'
                  ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                  : 'bg-rose-50 text-rose-700 border border-rose-200'
              }`}
            >
              {trend.direction === 'up' ? '↑' : '↓'} {trend.value}%
            </span>
          )}
        </div>
      )}
    </div>
  );
}
