import { useState, useEffect } from 'react';
import { Settings, Save, Play, StopCircle } from 'lucide-react';
import { Button, Input, Toggle, Card } from '@/components/ui';
import { useApp } from '@/context/AppContext';

const API_BASE_URL = 'http://localhost:8000';

const ConfigurationPage = () => {
  const { addNotification, scraperRunning, setScraperRunning } = useApp();
  const [localConfig, setLocalConfig] = useState({
    credentials: { username: '', password: '' },
    filters: { dateRange: { from: '', to: '' }, classification: '', businessCategory: '' },
    settings: { headless: true, interval: 60, delay: 2, maxRetries: 3 }
  });
  const [loading, setLoading] = useState(false);
  const [scraperStatus, setScraperStatus] = useState<any>(null);

  // Load configuration from backend on mount
  useEffect(() => {
    loadConfig();
    loadScraperStatus();

    // Poll scraper status every 3 seconds
    const interval = setInterval(loadScraperStatus, 3000);
    return () => clearInterval(interval);
  }, []);

  const loadConfig = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/scraper/config`);
      if (response.ok) {
        const data = await response.json();
        setLocalConfig(data);
      }
    } catch (error) {
      console.error('Failed to load config:', error);
      addNotification('Failed to load configuration from server', 'error');
    }
  };

  const loadScraperStatus = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/scraper/status`);
      if (response.ok) {
        const data = await response.json();
        setScraperStatus(data);
        setScraperRunning(data.running);
      }
    } catch (error) {
      console.error('Failed to load scraper status:', error);
    }
  };

  const handleSave = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/scraper/config`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(localConfig)
      });

      if (response.ok) {
        addNotification('Configuration saved successfully', 'success');
      } else {
        const error = await response.json();
        addNotification(`Failed to save: ${error.detail}`, 'error');
      }
    } catch (error) {
      addNotification('Failed to save configuration', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleRunScraper = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/scraper/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          config: localConfig,
          one_time: true
        })
      });

      if (response.ok) {
        addNotification('Scraper started in background', 'success');
        setScraperRunning(true);
      } else {
        const error = await response.json();
        addNotification(`Failed to start scraper: ${error.detail}`, 'error');
      }
    } catch (error) {
      addNotification('Failed to start scraper', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleStopScraper = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/scraper/stop`, {
        method: 'POST'
      });

      if (response.ok) {
        addNotification('Scraper stop requested', 'info');
        setScraperRunning(false);
      } else {
        const error = await response.json();
        addNotification(`Failed to stop scraper: ${error.detail}`, 'error');
      }
    } catch (error) {
      addNotification('Failed to stop scraper', 'error');
    }
  };

  return (
    <div>
      {/* Header Bar */}
      <div className="border-b border-slate-200 px-6 py-3 bg-white">
        <div className="flex items-center justify-between">
          <span className="text-sm font-semibold text-slate-900 flex items-center">
            <Settings className="w-4 h-4 mr-2" />
            Configuration
          </span>
          <div className="flex gap-2">
            <Button onClick={handleSave} disabled={loading}>
              <Save className="w-4 h-4 mr-2" />
              Save Changes
            </Button>
            {scraperRunning ? (
              <Button variant="destructive" onClick={handleStopScraper}>
                <StopCircle className="w-4 h-4 mr-2" />
                Stop Scraper
              </Button>
            ) : (
              <Button onClick={handleRunScraper} disabled={loading}>
                <Play className="w-4 h-4 mr-2" />
                Run Scraper
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="px-6 py-6 space-y-6">
        {/* Scraper Status */}
        {scraperStatus && (
          <Card className="p-6">
            <h2 className="text-sm font-semibold text-slate-900 mb-4">Scraper Status</h2>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-600">Status:</span>
                <span className={`text-sm font-medium ${scraperStatus.running ? 'text-green-600' : 'text-slate-600'}`}>
                  {scraperStatus.running ? '🟢 Running' : '⚪ Idle'}
                </span>
              </div>
              {scraperStatus.current_progress && (
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-600">Progress:</span>
                  <span className="text-sm text-slate-900">{scraperStatus.current_progress}</span>
                </div>
              )}
              {scraperStatus.last_run && (
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-600">Last Run:</span>
                  <span className="text-sm text-slate-900">
                    {new Date(scraperStatus.last_run).toLocaleString()}
                  </span>
                </div>
              )}
              {scraperStatus.error && (
                <div className="mt-2 p-3 bg-red-50 border border-red-200 rounded">
                  <p className="text-sm text-red-600">Error: {scraperStatus.error}</p>
                </div>
              )}
            </div>
          </Card>
        )}


        {/* Credentials */}
        <Card className="p-6">
          <h2 className="text-sm font-semibold text-slate-900 mb-4">PhilGEPS Credentials</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Username
              </label>
              <Input
                type="text"
                value={localConfig.credentials.username}
                onChange={e => setLocalConfig({
                  ...localConfig,
                  credentials: { ...localConfig.credentials, username: e.target.value }
                })}
                placeholder="Enter username"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Password
              </label>
              <Input
                type="password"
                value={localConfig.credentials.password}
                onChange={e => setLocalConfig({
                  ...localConfig,
                  credentials: { ...localConfig.credentials, password: e.target.value }
                })}
                placeholder="Enter password"
              />
            </div>
          </div>
        </Card>

        {/* Scraper Settings */}
        <Card className="p-6">
          <h2 className="text-sm font-semibold text-slate-900 mb-4">Scraper Settings</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <label className="block text-sm font-medium text-slate-700">
                  Headless Mode
                </label>
                <p className="text-xs text-slate-500 mt-1">
                  Run browser in background without UI
                </p>
              </div>
              <Toggle
                checked={localConfig.settings.headless}
                onCheckedChange={checked => setLocalConfig({
                  ...localConfig,
                  settings: { ...localConfig.settings, headless: checked }
                })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Scraping Interval (minutes)
              </label>
              <Input
                type="number"
                value={localConfig.settings.interval}
                onChange={e => setLocalConfig({
                  ...localConfig,
                  settings: { ...localConfig.settings, interval: Number(e.target.value) }
                })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Request Delay (seconds)
              </label>
              <Input
                type="number"
                value={localConfig.settings.delay}
                onChange={e => setLocalConfig({
                  ...localConfig,
                  settings: { ...localConfig.settings, delay: Number(e.target.value) }
                })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Max Retries
              </label>
              <Input
                type="number"
                value={localConfig.settings.maxRetries}
                onChange={e => setLocalConfig({
                  ...localConfig,
                  settings: { ...localConfig.settings, maxRetries: Number(e.target.value) }
                })}
              />
            </div>
          </div>
        </Card>

        {/* Filter Defaults */}
        <Card className="p-6">
          <h2 className="text-sm font-semibold text-slate-900 mb-4">Scraping Filters</h2>
          <p className="text-xs text-slate-500 mb-4">
            Configure filters to apply when scraping bid notices from PhilGEPS
          </p>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Date Range From (DD-MMM-YYYY)
              </label>
              <Input
                type="text"
                placeholder="e.g., 01-Nov-2025"
                value={localConfig.filters.dateRange.from}
                onChange={e => setLocalConfig({
                  ...localConfig,
                  filters: {
                    ...localConfig.filters,
                    dateRange: { ...localConfig.filters.dateRange, from: e.target.value }
                  }
                })}
              />
              <p className="text-xs text-slate-500 mt-1">
                Use format: DD-MMM-YYYY (e.g., 01-Nov-2025) or leave empty for no filter
              </p>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Date Range To (DD-MMM-YYYY)
              </label>
              <Input
                type="text"
                placeholder="e.g., 14-Nov-2025"
                value={localConfig.filters.dateRange.to}
                onChange={e => setLocalConfig({
                  ...localConfig,
                  filters: {
                    ...localConfig.filters,
                    dateRange: { ...localConfig.filters.dateRange, to: e.target.value }
                  }
                })}
              />
              <p className="text-xs text-slate-500 mt-1">
                Use format: DD-MMM-YYYY (e.g., 14-Nov-2025) or leave empty for no filter
              </p>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Classification
              </label>
              <Input
                type="text"
                placeholder="e.g., 2 for Goods"
                value={localConfig.filters.classification}
                onChange={e => setLocalConfig({
                  ...localConfig,
                  filters: { ...localConfig.filters, classification: e.target.value }
                })}
              />
              <p className="text-xs text-slate-500 mt-1">
                1=Civil Works, 2=Goods, 3=General Support Services, 4=Consulting Services
              </p>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Business Category
              </label>
              <Input
                type="text"
                placeholder="e.g., 256"
                value={localConfig.filters.businessCategory}
                onChange={e => setLocalConfig({
                  ...localConfig,
                  filters: { ...localConfig.filters, businessCategory: e.target.value }
                })}
              />
              <p className="text-xs text-slate-500 mt-1">
                Enter category ID from PhilGEPS (e.g., 256) or leave empty for all categories
              </p>
            </div>
          </div>
        </Card>
      </div>
      {/* End Main Content */}
    </div>
  );
};

export default ConfigurationPage;
