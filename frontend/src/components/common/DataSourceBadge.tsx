import React from 'react';
import { useDataSource } from '../../hooks/useDataSource';
import { Database, HardDrive } from 'lucide-react';

export default function DataSourceBadge() {
  const { dataSource, isConnected } = useDataSource();

  if (!isConnected) {
    return (
      <div className="flex items-center px-3 py-1 rounded-full text-xs font-medium bg-slate-100 text-slate-600 border border-slate-200">
        <span className="w-2 h-2 rounded-full bg-slate-400 mr-2" />
        Connecting...
      </div>
    );
  }

  const isSupabase = dataSource === 'supabase';

  return (
    <div
      className={`
        inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold border shadow-xs transition-all
        ${isSupabase 
          ? 'bg-emerald-50 text-emerald-800 border-emerald-200 shadow-emerald-500/10' 
          : 'bg-gradient-to-r from-amber-50 to-orange-50 text-amber-800 border-amber-200/80 shadow-amber-500/10'}
      `}
    >
      <span className="relative flex h-2 w-2 mr-2">
        <span
          className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${
            isSupabase ? 'bg-emerald-400' : 'bg-amber-400'
          }`}
        />
        <span
          className={`relative inline-flex rounded-full h-2 w-2 ${
            isSupabase ? 'bg-emerald-500' : 'bg-amber-500'
          }`}
        />
      </span>
      {isSupabase ? (
        <span className="flex items-center gap-1.5">
          <Database className="w-3.5 h-3.5 text-emerald-600" />
          <span>Supabase Cloud</span>
        </span>
      ) : (
        <span className="flex items-center gap-1.5">
          <HardDrive className="w-3.5 h-3.5 text-amber-600" />
          <span>Local Engine</span>
        </span>
      )}
    </div>
  );
}
