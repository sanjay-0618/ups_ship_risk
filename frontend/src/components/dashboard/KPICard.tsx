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
    iconBg: 'bg-blue-50 text-blue-600 border border-blue-100',
    topBorder: 'hover:border-blue-300',
  },
  orange: {
    iconBg: 'bg-orange-50 text-orange-600 border border-orange-100',
    topBorder: 'hover:border-orange-300',
  },
  red: {
    iconBg: 'bg-red-50 text-red-600 border border-red-100',
    topBorder: 'hover:border-red-300',
  },
  green: {
    iconBg: 'bg-emerald-50 text-emerald-600 border border-emerald-100',
    topBorder: 'hover:border-emerald-300',
  },
  purple: {
    iconBg: 'bg-purple-50 text-purple-600 border border-purple-100',
    topBorder: 'hover:border-purple-300',
  },
  yellow: {
    iconBg: 'bg-amber-50 text-amber-600 border border-amber-100',
    topBorder: 'hover:border-amber-300',
  },
};

export default function KPICard({ title, value, icon, color, trend, loading }: KPICardProps) {
  const style = COLOR_STYLES[color] || COLOR_STYLES.blue;

  return (
    <div
      className={`
        bg-white rounded-xl shadow-xs border border-slate-200/80 p-5 flex flex-col justify-between
        transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md ${style.topBorder}
      `}
    >
      <div className="flex justify-between items-start mb-3">
        <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{title}</h3>
        <div className={`p-2.5 rounded-xl ${style.iconBg} shadow-xs`}>
          {icon}
        </div>
      </div>
      
      {loading ? (
        <SkeletonLoader className="h-8 w-24 mb-1" />
      ) : (
        <div className="flex items-baseline justify-between mt-1">
          <span className="text-2xl font-extrabold text-slate-900 tracking-tight">{value}</span>
          {trend && (
            <span
              className={`inline-flex items-center px-1.5 py-0.5 rounded text-[11px] font-bold ${
                trend.direction === 'up'
                  ? 'bg-emerald-50 text-emerald-700 border border-emerald-200/60'
                  : 'bg-rose-50 text-rose-700 border border-rose-200/60'
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
