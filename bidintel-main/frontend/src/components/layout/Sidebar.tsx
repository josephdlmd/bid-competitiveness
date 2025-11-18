import { Home, Search, Settings, Activity, Package, X, Calendar, BarChart3 } from 'lucide-react';
import { useApp } from '@/context/AppContext';
import { useNavigate, useLocation } from 'react-router-dom';

interface MenuItem {
  id: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  path: string;
}

const Sidebar = () => {
  const { sidebarOpen, setSidebarOpen } = useApp();
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems: MenuItem[] = [
    { id: 'dashboard', label: 'Dashboard', icon: Home, path: '/' },
    { id: 'bids', label: 'Bid Search', icon: Search, path: '/bids' },
    { id: 'calendar', label: 'Calendar', icon: Calendar, path: '/calendar' },
    { id: 'analytics', label: 'Analytics', icon: BarChart3, path: '/analytics' },
    { id: 'config', label: 'Configuration', icon: Settings, path: '/config' },
    { id: 'logs', label: 'Scraping Logs', icon: Activity, path: '/logs' }
  ];

  const handleNavigation = (path: string) => {
    navigate(path);
    setSidebarOpen(false);
  };

  return (
    <>
      <div className={`fixed inset-0 z-40 lg:hidden ${sidebarOpen ? 'block' : 'hidden'}`} aria-hidden={!sidebarOpen}>
        <div className="fixed inset-0 bg-black/20" onClick={() => setSidebarOpen(false)} aria-label="Close navigation" />
      </div>

      <aside
        className={`fixed top-0 left-0 z-40 h-screen w-60 bg-white border-r border-slate-200 transform transition-transform lg:translate-x-0 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
        aria-label="Main navigation"
      >
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200">
          <div className="flex items-center space-x-2">
            <Package className="w-5 h-5 text-slate-700" aria-hidden="true" />
            <span className="text-base font-semibold text-slate-900">PhilGEPS</span>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden p-1.5 hover:bg-slate-50 rounded-md"
            aria-label="Close navigation menu"
          >
            <X className="w-4 h-4 text-slate-500" />
          </button>
        </div>

        <nav className="p-3 space-y-1" role="navigation" aria-label="Primary">
          {menuItems.map(item => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <button
                key={item.id}
                onClick={() => handleNavigation(item.path)}
                className={`w-full flex items-center space-x-2.5 px-3 py-2 rounded-md transition-all text-sm ${
                  isActive
                    ? 'bg-slate-100 text-slate-900 font-medium'
                    : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                }`}
                aria-label={`Navigate to ${item.label}`}
                aria-current={isActive ? 'page' : undefined}
              >
                <Icon className="w-4 h-4" aria-hidden="true" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </aside>
    </>
  );
};

export default Sidebar;
