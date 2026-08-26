import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Camera, Search, BarChart3, Bell, Shield, LogOut, ChevronLeft, ChevronRight } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useState } from 'react';
import { cn } from '../lib/utils';

export default function Sidebar() {
  const { user, role, logout } = useAuth();
  const [collapsed, setCollapsed] = useState(false);

  const navItems = [
    { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/cameras', icon: Camera, label: 'Cameras' },
    { to: '/vehicles', icon: Search, label: 'Vehicle Search' },
    { to: '/analytics', icon: BarChart3, label: 'Analytics' },
    { to: '/alerts', icon: Bell, label: 'Alerts' },
    { to: '/watchlist', icon: Shield, label: 'Watchlist' },
  ];

  return (
    <aside className={cn("bg-slate-900 border-r border-slate-800 flex flex-col transition-all duration-300", collapsed ? "w-20" : "w-64")}>
      <div className="h-16 flex items-center justify-between px-4 border-b border-slate-800">
        {!collapsed && <span className="font-bold text-lg tracking-wider text-primary-400">CITY ANPR</span>}
        <button onClick={() => setCollapsed(!collapsed)} className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400">
          {collapsed ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
        </button>
      </div>

      <nav className="flex-1 overflow-y-auto py-4">
        <ul className="space-y-2 px-3">
          {navItems.map(item => (
            <li key={item.to}>
              <NavLink
                to={item.to}
                className={({ isActive }) => cn(
                  "flex items-center px-3 py-2.5 rounded-lg transition-colors group",
                  isActive ? "bg-primary-600/10 text-primary-400" : "text-slate-400 hover:bg-slate-800 hover:text-slate-200"
                )}
              >
                <item.icon size={20} className={cn("shrink-0", collapsed ? "mx-auto" : "mr-3")} />
                {!collapsed && <span>{item.label}</span>}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>

      <div className="p-4 border-t border-slate-800">
        <div className={cn("flex items-center", collapsed ? "justify-center" : "justify-between")}>
          {!collapsed && (
            <div className="flex flex-col">
              <span className="text-sm font-medium text-slate-200">{user?.username}</span>
              <span className="text-xs text-slate-500 uppercase">{role}</span>
            </div>
          )}
          <button onClick={logout} className="p-2 rounded-lg hover:bg-red-500/10 text-slate-400 hover:text-red-400 transition-colors" title="Logout">
            <LogOut size={20} />
          </button>
        </div>
      </div>
    </aside>
  );
}
