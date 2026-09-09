import React, { useState } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, Navigation, Package, 
  AlertTriangle, Zap, BarChart2, Settings, 
  Menu, X, ShieldCheck, Activity, Cpu
} from 'lucide-react';
import DataSourceBadge from './DataSourceBadge';
import upsLogo from '../../assets/ups-logo.svg';

interface LayoutProps {
  children: React.ReactNode;
}

const navSections = [
  {
    title: 'OPERATIONS',
    items: [
      { path: '/', label: 'Command Center', icon: LayoutDashboard },
      { path: '/route-planner', label: 'Route Optimizer', icon: Navigation, badge: 'AI' },
      { path: '/shipments', label: 'Live Shipments', icon: Package },
    ],
  },
  {
    title: 'THREAT INTELLIGENCE',
    items: [
      { path: '/risk-center', label: 'Risk Radar', icon: AlertTriangle, badge: 'Active', badgeColor: 'bg-rose-50 text-rose-600 border border-rose-200' },
      { path: '/disruptions', label: 'Threat Simulator', icon: Zap, badge: 'What-If' },
      { path: '/analytics', label: 'Predictive Analytics', icon: BarChart2 },
    ],
  },
  {
    title: 'SYSTEM',
    items: [
      { path: '/settings', label: 'Configuration', icon: Settings },
    ],
  },
];

export default function Layout({ children }: LayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  return (
    <div className="min-h-screen bg-slate-50/60 flex text-slate-800 font-sans">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-slate-950/50 backdrop-blur-xs z-40 lg:hidden transition-opacity" 
          onClick={() => setSidebarOpen(false)} 
        />
      )}

      {/* Sidebar */}
      <aside className={`
        fixed top-0 left-0 z-50 h-screen w-64 bg-white/95 backdrop-blur-md border-r border-slate-200/80 transition-transform duration-300 ease-in-out flex flex-col justify-between
        lg:translate-x-0 ${sidebarOpen ? 'translate-x-0 shadow-2xl' : '-translate-x-full'}
      `}>
        <div className="flex-1 overflow-y-auto">
          {/* Brand Header */}
          <div className="h-16 flex items-center justify-between px-5 border-b border-slate-100">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-[#351c15] flex items-center justify-center overflow-hidden shadow-md shadow-slate-400/25">
                <img src={upsLogo} alt="UPS" className="w-8 h-8 object-contain" />
              </div>
              <div>
                <div className="text-base font-black text-slate-900 tracking-tight flex items-center gap-1.5">
                  UPS <span className="text-blue-600">TrackSafe</span>
                  <span className="px-1.5 py-0.2 rounded text-[9px] font-bold bg-blue-50 text-blue-600 border border-blue-200/60">v2.4</span>
                </div>
                <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                  Predictive Platform
                </div>
              </div>
            </div>
            <button className="lg:hidden p-1.5 rounded-lg text-slate-400 hover:bg-slate-100" onClick={() => setSidebarOpen(false)}>
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Navigation Sections */}
          <div className="p-3.5 space-y-6">
            {navSections.map((section, sIdx) => (
              <div key={sIdx} className="space-y-1">
                <div className="px-3 text-[10px] font-bold tracking-wider text-slate-400 uppercase">
                  {section.title}
                </div>
                {section.items.map((item) => {
                  const Icon = item.icon;
                  const isActive = location.pathname === item.path || 
                    (item.path !== '/' && location.pathname.startsWith(item.path));
                  
                  return (
                    <NavLink
                      key={item.path}
                      to={item.path}
                      className={`
                        group flex items-center px-3 py-2 text-xs font-semibold rounded-xl transition-all duration-150 relative
                        ${isActive 
                          ? 'bg-blue-50/80 text-blue-700 font-bold border border-blue-200/70 shadow-2xs' 
                          : 'text-slate-600 hover:bg-slate-100/80 hover:text-slate-900 border border-transparent'}
                      `}
                      onClick={() => setSidebarOpen(false)}
                    >
                      <Icon className={`w-4 h-4 mr-3 transition-colors ${isActive ? 'text-blue-600' : 'text-slate-400 group-hover:text-slate-600'}`} />
                      <span className="flex-1">{item.label}</span>
                      {item.badge && (
                        <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold ${item.badgeColor || 'bg-slate-100 text-slate-600'}`}>
                          {item.badge}
                        </span>
                      )}
                    </NavLink>
                  );
                })}
              </div>
            ))}
          </div>
        </div>

        {/* Sidebar Footer Widget */}
        <div className="p-3.5 border-t border-slate-100">
          <div className="bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 text-white rounded-xl p-3.5 shadow-sm space-y-2 border border-slate-800">
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
                </span>
                Surveillance Online
              </span>
              <span className="text-[10px] text-cyan-300/80 font-mono">SEED: 42</span>
            </div>
            <div className="text-[11px] text-slate-300 font-medium leading-relaxed">
              75 North American hubs & 371 corridors under live risk evaluation.
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col lg:pl-64 min-w-0">
        {/* Topbar */}
        <header className="h-16 bg-white/90 backdrop-blur-md border-b border-slate-200/80 flex items-center justify-between px-4 lg:px-8 sticky top-0 z-30 transition-all">
          <div className="flex items-center flex-1">
            <button 
              className="lg:hidden mr-3 p-2 text-slate-500 hover:bg-slate-100 rounded-lg"
              onClick={() => setSidebarOpen(true)}
            >
              <Menu className="w-5 h-5" />
            </button>
          </div>

          <div className="flex items-center space-x-3.5">
            <DataSourceBadge />
            
            <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200/70">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
              <span>Network Nominal</span>
            </div>

            <div className="h-4 w-px bg-slate-200" />
            
            <div className="flex items-center gap-2.5 pl-1">
              <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-cyan-500 flex items-center justify-center text-white text-xs font-black shadow-xs">
                OP
              </div>
              <div className="hidden sm:block text-left">
                <div className="text-xs font-bold text-slate-800 leading-tight">Operations Dispatch</div>
                <div className="text-[10px] text-slate-400">Chicago Hub HQ</div>
              </div>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 p-4 lg:p-7 overflow-x-hidden max-w-7xl w-full mx-auto">
          {children}
        </main>
      </div>
    </div>
  );
}
