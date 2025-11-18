import { createContext, useContext, useState, ReactNode } from 'react';
import { FilterState } from '@/lib/types';

interface Notification {
  id: number;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
}

interface SavedSearch {
  id: string;
  name: string;
  filters: Partial<FilterState>;
  createdAt: string;
}

interface Config {
  credentials: {
    username: string;
    password: string;
  };
  filters: {
    dateRange: { from: string; to: string };
    classifications: string[];
    categories: string[];
  };
  settings: {
    headless: boolean;
    interval: number;
    delay: number;
    maxRetries: number;
  };
}

interface AppContextType {
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
  scraperRunning: boolean;
  setScraperRunning: (running: boolean) => void;
  notifications: Notification[];
  addNotification: (message: string, type?: Notification['type']) => void;
  config: Config;
  saveConfig: (config: Config) => void;
  watchlist: string[];
  toggleWatchlist: (bidId: string) => void;
  isInWatchlist: (bidId: string) => boolean;
  savedSearches: SavedSearch[];
  saveSearch: (name: string, filters: Partial<FilterState>) => void;
  deleteSavedSearch: (id: string) => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider = ({ children }: { children: ReactNode }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [scraperRunning, setScraperRunning] = useState(false);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [watchlist, setWatchlist] = useState<string[]>(() => {
    const saved = localStorage.getItem('philgeps_watchlist');
    return saved ? JSON.parse(saved) : [];
  });
  const [savedSearches, setSavedSearches] = useState<SavedSearch[]>(() => {
    const saved = localStorage.getItem('philgeps_saved_searches');
    return saved ? JSON.parse(saved) : [];
  });
  const [config, setConfig] = useState<Config>(() => {
    const saved = localStorage.getItem('philgeps_config');
    return saved ? JSON.parse(saved) : {
      credentials: { username: '', password: '' },
      filters: {
        dateRange: { from: '', to: '' },
        classifications: ['Goods', 'Services', 'Infrastructure'],
        categories: []
      },
      settings: {
        headless: true,
        interval: 30,
        delay: 2,
        maxRetries: 3
      }
    };
  });

  const addNotification = (message: string, type: Notification['type'] = 'info') => {
    const id = Date.now();
    setNotifications(prev => [...prev, { id, message, type }]);
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== id));
    }, 5000);
  };

  const saveConfig = (newConfig: Config) => {
    setConfig(newConfig);
    localStorage.setItem('philgeps_config', JSON.stringify(newConfig));
    addNotification('Configuration saved successfully', 'success');
  };

  const toggleWatchlist = (bidId: string) => {
    setWatchlist(prev => {
      const newWatchlist = prev.includes(bidId)
        ? prev.filter(id => id !== bidId)
        : [...prev, bidId];
      localStorage.setItem('philgeps_watchlist', JSON.stringify(newWatchlist));
      addNotification(
        prev.includes(bidId) ? 'Removed from watchlist' : 'Added to watchlist',
        'success'
      );
      return newWatchlist;
    });
  };

  const isInWatchlist = (bidId: string) => {
    return watchlist.includes(bidId);
  };

  const saveSearch = (name: string, filters: Partial<FilterState>) => {
    const newSearch: SavedSearch = {
      id: Date.now().toString(),
      name,
      filters,
      createdAt: new Date().toISOString()
    };
    const updated = [...savedSearches, newSearch];
    setSavedSearches(updated);
    localStorage.setItem('philgeps_saved_searches', JSON.stringify(updated));
    addNotification(`Search "${name}" saved successfully`, 'success');
  };

  const deleteSavedSearch = (id: string) => {
    const updated = savedSearches.filter(s => s.id !== id);
    setSavedSearches(updated);
    localStorage.setItem('philgeps_saved_searches', JSON.stringify(updated));
    addNotification('Saved search deleted', 'success');
  };

  const value: AppContextType = {
    sidebarOpen,
    setSidebarOpen,
    scraperRunning,
    setScraperRunning,
    notifications,
    addNotification,
    config,
    saveConfig,
    watchlist,
    toggleWatchlist,
    isInWatchlist,
    savedSearches,
    saveSearch,
    deleteSavedSearch
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within AppProvider');
  }
  return context;
};
