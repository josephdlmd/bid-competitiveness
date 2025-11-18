import { useState } from 'react';
import BidIndex from './components/BidIndex';
import OpportunityDashboard from './components/OpportunityDashboard';
import UNSPSCIntelligence from './components/UNSPSCIntelligence';
import AgencyIntelligence from './components/AgencyIntelligence';
import ConfigurationPage from './pages/ConfigurationPage';

type ViewType = 'index' | 'opportunities' | 'products' | 'agencies' | 'configuration';

function App() {
  const [currentView, setCurrentView] = useState<ViewType>('index');

  const renderView = () => {
    switch (currentView) {
      case 'index':
        return <BidIndex />;
      case 'opportunities':
        return <OpportunityDashboard />;
      case 'products':
        return <UNSPSCIntelligence />;
      case 'agencies':
        return <AgencyIntelligence />;
      case 'configuration':
        return <ConfigurationPage />;
      default:
        return <BidIndex />;
    }
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Top Navigation */}
      <header className="border-b border-slate-200">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-8">
              <h1 className="text-lg font-semibold text-slate-900">
                PhilGEPS Intel
              </h1>
              <nav className="flex space-x-6">
                <button
                  onClick={() => setCurrentView('index')}
                  className={`text-sm ${
                    currentView === 'index'
                      ? 'text-slate-900 font-medium'
                      : 'text-slate-500 hover:text-slate-900'
                  }`}
                >
                  All Bids
                </button>
                <button
                  onClick={() => setCurrentView('opportunities')}
                  className={`text-sm ${
                    currentView === 'opportunities'
                      ? 'text-slate-900 font-medium'
                      : 'text-slate-500 hover:text-slate-900'
                  }`}
                >
                  Top Opportunities
                </button>
                <button
                  onClick={() => setCurrentView('products')}
                  className={`text-sm ${
                    currentView === 'products'
                      ? 'text-slate-900 font-medium'
                      : 'text-slate-500 hover:text-slate-900'
                  }`}
                >
                  Products
                </button>
                <button
                  onClick={() => setCurrentView('agencies')}
                  className={`text-sm ${
                    currentView === 'agencies'
                      ? 'text-slate-900 font-medium'
                      : 'text-slate-500 hover:text-slate-900'
                  }`}
                >
                  Agencies
                </button>
                <button
                  onClick={() => setCurrentView('configuration')}
                  className={`text-sm ${
                    currentView === 'configuration'
                      ? 'text-slate-900 font-medium'
                      : 'text-slate-500 hover:text-slate-900'
                  }`}
                >
                  ⚙️ Configuration
                </button>
              </nav>
            </div>
            <div className="flex items-center space-x-2">
              <div className="h-2 w-2 rounded-full bg-emerald-500"></div>
              <span className="text-sm text-slate-500">Live</span>
            </div>
          </div>
        </div>
      </header>

      {/* Content Area */}
      <main>
        {renderView()}
      </main>
    </div>
  );
}

export default App;
