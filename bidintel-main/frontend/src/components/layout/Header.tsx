import { useState, useEffect, useRef, useMemo } from 'react';
import { Menu, Search, User, Loader2, Star } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '@/context/AppContext';
import { formatCurrency } from '@/utils/formatters';
import { mockBids } from '@/data/mockBids';
import { Button } from '@/components/ui';
import { Bid } from '@/lib/types';

const Header = () => {
  const { setSidebarOpen, scraperRunning, isInWatchlist } = useApp();
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [debouncedQuery, setDebouncedQuery] = useState('');
  const searchRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(searchQuery);
    }, 300);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const suggestions = useMemo(() => {
    if (!debouncedQuery || debouncedQuery.length < 2) return [];

    const query = debouncedQuery.toLowerCase();
    return mockBids
      .filter(bid =>
        bid.title.toLowerCase().includes(query) ||
        bid.description?.toLowerCase().includes(query) ||
        bid.reference_number.toLowerCase().includes(query) ||
        bid.procuring_entity.toLowerCase().includes(query)
      )
      .slice(0, 5);
  }, [debouncedQuery]);

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setSearchQuery(value);
    setShowSuggestions(true);
  };

  const handleSuggestionClick = (bid: Bid) => {
    setSearchQuery('');
    setShowSuggestions(false);
    navigate('/bids', { state: { selectedBidId: bid.reference_number } });
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate('/bids', { state: { searchQuery } });
      setSearchQuery('');
      setShowSuggestions(false);
    }
  };

  return (
    <header className="bg-white border-b border-slate-200 px-6 py-3">
      <div className="flex items-center justify-between max-w-7xl">
        <button
          onClick={() => setSidebarOpen(true)}
          className="lg:hidden p-2 hover:bg-slate-50 rounded-md"
          aria-label="Open navigation menu"
        >
          <Menu className="w-5 h-5 text-slate-600" />
        </button>

        <div className="flex-1 max-w-xl mx-auto px-4" ref={searchRef}>
          <form onSubmit={handleSearchSubmit} className="relative" role="search">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" aria-hidden="true" />
            <input
              type="text"
              placeholder="Search bids..."
              value={searchQuery}
              onChange={handleSearchChange}
              onFocus={() => searchQuery && setShowSuggestions(true)}
              className="w-full pl-9 pr-4 py-1.5 text-sm border border-slate-200 rounded-lg focus:outline-none focus:border-slate-400 transition-colors"
              aria-label="Search bids"
              aria-autocomplete="list"
              aria-controls="search-suggestions"
              aria-expanded={showSuggestions && suggestions.length > 0}
            />

            {showSuggestions && suggestions.length > 0 && (
              <div
                id="search-suggestions"
                role="listbox"
                className="absolute top-full left-0 right-0 mt-2 bg-white rounded-lg border border-slate-200 max-h-96 overflow-y-auto z-50 shadow-lg"
              >
                <div className="p-2">
                  <p className="text-xs text-slate-500 px-3 py-2 font-medium uppercase">
                    Suggestions
                  </p>
                  {suggestions.map(bid => (
                    <button
                      key={bid.reference_number}
                      onClick={() => handleSuggestionClick(bid)}
                      className="w-full text-left px-3 py-2 hover:bg-slate-50 rounded-lg transition-colors"
                      role="option"
                      aria-label={`View bid ${bid.title}`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center space-x-2 mb-1">
                            {isInWatchlist(bid.reference_number) && (
                              <Star className="w-3 h-3 fill-amber-500 text-amber-500 flex-shrink-0" />
                            )}
                            <p className="text-sm font-medium text-slate-900 line-clamp-1">
                              {bid.title}
                            </p>
                          </div>
                          <p className="text-xs text-slate-500 mb-1">{bid.procuring_entity}</p>
                          <div className="flex items-center space-x-2">
                            <span className="text-xs font-mono text-slate-600">
                              {bid.reference_number}
                            </span>
                            <span className="text-xs font-medium text-slate-900">
                              {formatCurrency(bid.approved_budget)}
                            </span>
                          </div>
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {showSuggestions && searchQuery && suggestions.length === 0 && debouncedQuery === searchQuery && (
              <div className="absolute top-full left-0 right-0 mt-2 bg-white rounded-lg border border-slate-200 p-4 z-50 shadow-lg">
                <p className="text-sm text-slate-500 text-center">No results found</p>
              </div>
            )}
          </form>
        </div>

        <div className="flex items-center space-x-4">
          {scraperRunning && (
            <div className="flex items-center space-x-2 px-3 py-1 bg-emerald-50 text-emerald-700 rounded-full border border-emerald-200">
              <Loader2 className="w-4 h-4 animate-spin" />
              <span className="text-sm font-medium">Scraping...</span>
            </div>
          )}
          <Button variant="ghost" size="sm">
            <User className="w-5 h-5" />
          </Button>
        </div>
      </div>
    </header>
  );
};

export default Header;
