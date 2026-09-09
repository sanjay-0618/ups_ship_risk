import React from 'react';
import { useDataSource } from '../hooks/useDataSource';
import { Sliders, Database, Server, Globe, Cpu, CheckCircle2 } from 'lucide-react';

export default function Settings() {
  const { dataSource, isConnected } = useDataSource();

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Platform Settings & Architecture</h1>
        <p className="text-gray-500 text-sm mt-1">
          System operational mode, model configurations, and deployment connections.
        </p>
      </div>

      {/* Data Source Connection Card */}
      <div className="bg-white border border-gray-200 rounded-xl shadow-sm p-6 space-y-4">
        <h3 className="text-base font-bold text-gray-900 flex items-center gap-2">
          <Database className="w-5 h-5 text-blue-600" />
          Data Source Connection
        </h3>
        <p className="text-xs text-gray-500">
          The system operates in dual-mode: using Supabase PostgreSQL when credentials exist, and automatically falling back to high-fidelity synthetic datasets offline.
        </p>

        <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-200">
          <div className="flex items-center space-x-3">
            <div className={`w-3.5 h-3.5 rounded-full ${dataSource === 'supabase' ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500'}`} />
            <div>
              <span className="font-bold text-sm text-gray-900">
                Active Source: {dataSource === 'supabase' ? 'Supabase PostgreSQL Cloud DB' : 'Local Synthetic Data Engine'}
              </span>
              <div className="text-xs text-gray-500 mt-0.5">
                {dataSource === 'supabase'
                  ? 'Connected to live cloud database instance with RLS policies.'
                  : 'Operating in self-contained offline fallback mode with 30,000 shipments and 100,000+ events.'}
              </div>
            </div>
          </div>
          <span className="text-xs font-semibold px-2.5 py-1 bg-white border border-gray-200 rounded text-gray-700">
            {isConnected ? 'HEALTHY' : 'STANDALONE'}
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs pt-2">
          <div>
            <label className="block font-semibold text-gray-700 mb-1">Supabase Endpoint URL</label>
            <input 
              type="text" 
              disabled 
              value={import.meta.env.VITE_SUPABASE_URL || 'https://your-project.supabase.co (Fallback active)'} 
              className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-600 font-mono text-xs" 
            />
          </div>
          <div>
            <label className="block font-semibold text-gray-700 mb-1">Backend API Base</label>
            <input 
              type="text" 
              disabled 
              value={import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'} 
              className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-600 font-mono text-xs" 
            />
          </div>
        </div>
      </div>

      {/* Risk Engine Configuration Display */}
      <div className="bg-white border border-gray-200 rounded-xl shadow-sm p-6 space-y-4">
        <h3 className="text-base font-bold text-gray-900 flex items-center gap-2">
          <Sliders className="w-5 h-5 text-amber-500" />
          Risk Engine Formula Weights (Configured in backend/app/config.py)
        </h3>
        <p className="text-xs text-gray-500">
          Normalized composite scoring formula weights applied to every segment and active shipment.
        </p>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
          {[
            { label: 'Weather Impact', weight: '20%', desc: 'Severity, radius & delay mult' },
            { label: 'Traffic Baseline', weight: '15%', desc: 'Live index & congestion speed' },
            { label: 'Hub Congestion', weight: '20%', desc: 'Processing queue & capacity ratio' },
            { label: 'Transport / Flight', weight: '15%', desc: 'Flight cancellation & airport lag' },
            { label: 'External Events', weight: '10%', desc: 'Road closures & port disruptions' },
            { label: 'Historical Corridor', weight: '10%', desc: 'Historical SLA breach frequency' },
            { label: 'Shipment Chars', weight: '10%', desc: 'Fragile, temp sensitive & weight' },
            { label: 'Total Weight', weight: '100%', desc: 'Normalized to 1.0 - 10.0 scale' },
          ].map((w, idx) => (
            <div key={idx} className="p-3 bg-gray-50 border border-gray-200 rounded-lg">
              <div className="text-gray-500 font-medium">{w.label}</div>
              <div className="text-lg font-bold text-gray-900 mt-0.5">{w.weight}</div>
              <div className="text-[10px] text-gray-400 mt-0.5">{w.desc}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Deployment & Reproducibility */}
      <div className="bg-white border border-gray-200 rounded-xl shadow-sm p-6 space-y-3">
        <h3 className="text-base font-bold text-gray-900 flex items-center gap-2">
          <Server className="w-5 h-5 text-emerald-600" />
          Deployment & Seed Status
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
          <div className="p-3 bg-gray-50 rounded-lg border">
            <div className="font-semibold text-gray-500">Random Seed</div>
            <div className="font-mono text-sm font-bold text-gray-900 mt-1">42 (Deterministic)</div>
          </div>
          <div className="p-3 bg-gray-50 rounded-lg border">
            <div className="font-semibold text-gray-500">Frontend Target</div>
            <div className="font-mono text-sm font-bold text-gray-900 mt-1">Vercel (Vite SPA)</div>
          </div>
          <div className="p-3 bg-gray-50 rounded-lg border">
            <div className="font-semibold text-gray-500">Backend Target</div>
            <div className="font-mono text-sm font-bold text-gray-900 mt-1">Render (FastAPI/Uvicorn)</div>
          </div>
        </div>
      </div>
    </div>
  );
}
