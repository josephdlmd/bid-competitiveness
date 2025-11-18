import { useState } from 'react';
import { Save, Search, Trash2, Edit2, Check, X, Star } from 'lucide-react';
import { SavedSearch, BidFilters } from '../lib/types';
import { useSavedSearches } from '../hooks/useSavedSearches';

interface SavedSearchesPanelProps {
  currentFilters: BidFilters;
  onApplySearch: (filters: BidFilters) => void;
}

export function SavedSearchesPanel({ currentFilters, onApplySearch }: SavedSearchesPanelProps) {
  const { savedSearches, saveSearch, deleteSearch, markAsUsed, renameSearch } = useSavedSearches();
  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const [searchName, setSearchName] = useState('');
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editingName, setEditingName] = useState('');

  const handleSaveCurrentSearch = () => {
    if (searchName.trim()) {
      saveSearch(searchName.trim(), currentFilters);
      setSearchName('');
      setShowSaveDialog(false);
    }
  };

  const handleApplySearch = (search: SavedSearch) => {
    markAsUsed(search.id);
    onApplySearch(search.filters);
  };

  const handleStartEdit = (search: SavedSearch) => {
    setEditingId(search.id);
    setEditingName(search.name);
  };

  const handleSaveEdit = () => {
    if (editingId && editingName.trim()) {
      renameSearch(editingId, editingName.trim());
      setEditingId(null);
      setEditingName('');
    }
  };

  const handleCancelEdit = () => {
    setEditingId(null);
    setEditingName('');
  };

  const hasActiveFilters = () => {
    return Object.keys(currentFilters).some(key => {
      const value = currentFilters[key as keyof BidFilters];
      return value !== undefined && value !== '' && value !== null;
    });
  };

  return (
    <div className="border-t border-slate-200 bg-slate-50 px-6 py-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-1.5">
          <Star className="w-3.5 h-3.5 text-slate-400" />
          <span className="text-xs font-medium text-slate-600">Saved Searches</span>
        </div>

        {hasActiveFilters() && (
          <button
            onClick={() => setShowSaveDialog(!showSaveDialog)}
            className="inline-flex items-center space-x-1 px-2 py-1 text-xs font-medium text-emerald-700 bg-emerald-50 rounded hover:bg-emerald-100 transition-colors"
          >
            <Save className="w-3 h-3" />
            <span>Save</span>
          </button>
        )}
      </div>

      {/* Save Dialog */}
      {showSaveDialog && (
        <div className="mt-2 p-2 bg-white border border-slate-200 rounded">
          <div className="flex items-center space-x-1.5">
            <input
              type="text"
              value={searchName}
              onChange={(e) => setSearchName(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSaveCurrentSearch()}
              placeholder="Name this search..."
              className="flex-1 px-2 py-1 text-xs border border-slate-200 rounded focus:outline-none focus:border-emerald-500"
              autoFocus
            />
            <button
              onClick={handleSaveCurrentSearch}
              disabled={!searchName.trim()}
              className="px-2 py-1 text-xs font-medium text-white bg-emerald-600 rounded hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Check className="w-3 h-3" />
            </button>
            <button
              onClick={() => {
                setShowSaveDialog(false);
                setSearchName('');
              }}
              className="px-2 py-1 text-xs text-slate-600 hover:text-slate-900"
            >
              <X className="w-3 h-3" />
            </button>
          </div>
        </div>
      )}

      {/* Saved Searches List */}
      {savedSearches.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-1.5">
          {savedSearches.map((search) => (
            <div
              key={search.id}
              className="inline-flex items-center space-x-1.5 px-2 py-1 bg-white border border-slate-200 rounded hover:border-slate-300 transition-colors"
            >
              {editingId === search.id ? (
                <>
                  <input
                    type="text"
                    value={editingName}
                    onChange={(e) => setEditingName(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') handleSaveEdit();
                      if (e.key === 'Escape') handleCancelEdit();
                    }}
                    className="w-24 px-1.5 py-0.5 text-xs border border-slate-200 rounded focus:outline-none focus:border-emerald-500"
                    autoFocus
                  />
                  <button
                    onClick={handleSaveEdit}
                    className="text-emerald-600 hover:text-emerald-700"
                  >
                    <Check className="w-3 h-3" />
                  </button>
                  <button
                    onClick={handleCancelEdit}
                    className="text-slate-400 hover:text-slate-600"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </>
              ) : (
                <>
                  <button
                    onClick={() => handleApplySearch(search)}
                    className="inline-flex items-center space-x-1 text-xs text-slate-700 hover:text-slate-900"
                  >
                    <Search className="w-3 h-3" />
                    <span>{search.name}</span>
                  </button>
                  <button
                    onClick={() => handleStartEdit(search)}
                    className="text-slate-400 hover:text-slate-600"
                  >
                    <Edit2 className="w-2.5 h-2.5" />
                  </button>
                  <button
                    onClick={() => deleteSearch(search.id)}
                    className="text-slate-400 hover:text-red-600"
                  >
                    <Trash2 className="w-2.5 h-2.5" />
                  </button>
                </>
              )}
            </div>
          ))}
        </div>
      )}

      {savedSearches.length === 0 && !showSaveDialog && (
        <p className="mt-1.5 text-[10px] text-slate-400">
          Apply filters and save them for quick access
        </p>
      )}
    </div>
  );
}
