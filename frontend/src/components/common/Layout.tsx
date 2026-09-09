import React, { useState } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, Navigation, Package, 
  AlertTriangle, Zap, BarChart2, Settings, 
  Search, Bell, Menu, X, ShieldCheck, Activity, Cpu
} from 'lucide-react';
import DataSourceBadge from './DataSourceBadge';

interface LayoutProps {
  children: React.ReactNode;
}

const navItems = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/route-planner', label: 'Route Planner', icon: Navigation },
  { path: '/shipments', label: 'Shipments', icon: Package },
  { path: '/risk-center', label: 'Risk Center', icon: AlertTriangle },
  { path: '/disruptions', label: 'Disruptions', icon: Zap },
  { path: '/analytics', label: 'Analytics', icon: BarChart2 },
  { path: '/settings', label: 'Settings', icon: Settings },
];

export default function Layout({ children }: LayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  return (
    <div className="min-h-screen bg-slate-50/70 flex text-slate-800">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs z-40 lg:hidden transition-opacity" 
          onClick={() => setSidebarOpen(false)} 
        />
      )}

      {/* Sidebar */}
      <aside className={`
        fixed top-0 left-0 z-50 h-screen w-64 bg-white border-r border-slate-200/80 transition-transform duration-300 ease-in-out flex flex-col justify-between
        lg:translate-x-0 ${sidebarOpen ? 'translate-x-0 shadow-2xl' : '-translate-x-full'}
      `}>
        <div>
          {/* Brand Header */}
          <div className="h-16 flex items-center justify-between px-5 border-b border-slate-100">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-sky-500 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
                <Navigation className="w-5 h-5 -rotate-45 fill-white/20" />
              </div>
              <div>
                <div className="text-base font-extrabold text-slate-900 tracking-tight flex items-center gap-1.5">
                  Logistics<span className="text-blue-600">AI</span>
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

          {/* Navigation Links */}
          <nav className="p-3.5 space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path || 
                (item.path !== '/' && location.pathname.startsWith(item.path));
              
              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={`
                    flex items-center px-3 py-2.5 text-xs font-semibold rounded-lg transition-all duration-150 relative
                    ${isActive 
                      ? 'bg-gradient-to-r from-blue-500/10 via-indigo-500/5 to-transparent text-blue-700 font-bold border-l-3 border-blue-600 shadow-2xs' 
                      : 'text-slate-600 hover:bg-slate-100/70 hover:text-slate-900 border-l-3 border-transparent'}
                  `}
                  onClick={() => setSidebarOpen(false)}
                >
                  <Icon className={`w-4 h-4 mr-3 transition-colors ${isActive ? 'text-blue-600' : 'text-slate-400'}`} />
                  {item.label}
                  {item.path === '/risk-center' && (
                    <span className="ml-auto px-1.5 py-0.2 rounded-full text-[9px] font-black bg-rose-100 text-rose-700 uppercase">
                      Radar
                    </span>
                  )}
                </NavLink>
              );
            })}
          </nav>
        </div>

        {/* Sidebar Footer Widget */}
        <div className="p-3.5 border-t border-slate-100">
          <div className="bg-gradient-to-br from-slate-900 to-slate-800 text-white rounded-xl p-3.5 shadow-sm space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
                </span>
                Surveillance Active
              </span>
              <span className="text-[10px] text-slate-400 font-mono">SEED: 42</span>
            </div>
            <div className="text-xs text-slate-200 font-medium leading-relaxed">
              75 North American hubs & 371 corridors under live risk evaluation.
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col lg:pl-64 min-w-0">
        {/* Topbar */}
        <header className="h-16 bg-white/85 backdrop-blur-md border-b border-slate-200/80 flex items-center justify-between px-4 lg:px-8 sticky top-0 z-30 transition-all">
          <div className="flex items-center flex-1">
            <button 
              className="lg:hidden mr-3 p-2 text-slate-500 hover:bg-slate-100 rounded-lg"
              onClick={() => setSidebarOpen(true)}
            >
              <Menu className="w-5 h-5" />
            </button>
            <div className="relative w-full max-w-md hidden md:block">
              <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <input 
                type="text" 
                placeholder="Search shipments, tracking #, locations..." 
                className="w-full pl-9 pr-12 py-1.5 text-xs bg-slate-100/70 border border-transparent rounded-lg focus:bg-white focus:border-blue-500 focus:ring-2 focus:ring-blue-100 outline-none transition-all"
              />
              <span className="absolute right-2.5 top-1/2 -translate-y-1/2 text-[10px] font-mono text-slate-400 border border-slate-200 px-1 py-0.5 rounded bg-white">
                ⌘K
              </span>
            </div>
          </div>

          <div className="flex items-center space-x-3.5">
            <DataSourceBadge />
            
            <button className="relative p-2 text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded-lg transition-colors">
              <Bell className="w-4 h-4" />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-rose-500 rounded-full ring-2 ring-white"></span>
            </button>
            
            <div className="h-4 w-px bg-slate-200" />
            
            <div className="flex items-center gap-2 pl-1">
              <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-white text-xs font-bold shadow-xs">
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
