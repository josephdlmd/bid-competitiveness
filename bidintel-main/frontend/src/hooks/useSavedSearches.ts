import { useState, useEffect, useCallback } from 'react';
import { SavedSearch, BidFilters } from '../lib/types';

const STORAGE_KEY = 'philgeps_saved_searches';

export function useSavedSearches() {
  const [savedSearches, setSavedSearches] = useState<SavedSearch[]>([]);

  // Load saved searches from localStorage on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        setSavedSearches(parsed);
      }
    } catch (error) {
      console.error('Error loading saved searches:', error);
    }
  }, []);

  // Save to localStorage whenever savedSearches changes
  const persistToStorage = useCallback((searches: SavedSearch[]) => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(searches));
    } catch (error) {
      console.error('Error saving searches:', error);
    }
  }, []);

  // Create a new saved search
  const saveSearch = useCallback((name: string, filters: BidFilters) => {
    const newSearch: SavedSearch = {
      id: Date.now().toString(),
      name,
      filters,
      createdAt: new Date().toISOString(),
    };

    setSavedSearches(prev => {
      const updated = [...prev, newSearch];
      persistToStorage(updated);
      return updated;
    });

    return newSearch;
  }, [persistToStorage]);

  // Delete a saved search
  const deleteSearch = useCallback((id: string) => {
    setSavedSearches(prev => {
      const updated = prev.filter(search => search.id !== id);
      persistToStorage(updated);
      return updated;
    });
  }, [persistToStorage]);

  // Update last used timestamp
  const markAsUsed = useCallback((id: string) => {
    setSavedSearches(prev => {
      const updated = prev.map(search =>
        search.id === id
          ? { ...search, lastUsed: new Date().toISOString() }
          : search
      );
      persistToStorage(updated);
      return updated;
    });
  }, [persistToStorage]);

  // Rename a saved search
  const renameSearch = useCallback((id: string, newName: string) => {
    setSavedSearches(prev => {
      const updated = prev.map(search =>
        search.id === id ? { ...search, name: newName } : search
      );
      persistToStorage(updated);
      return updated;
    });
  }, [persistToStorage]);

  // Update a saved search's filters
  const updateSearch = useCallback((id: string, filters: BidFilters) => {
    setSavedSearches(prev => {
      const updated = prev.map(search =>
        search.id === id ? { ...search, filters } : search
      );
      persistToStorage(updated);
      return updated;
    });
  }, [persistToStorage]);

  return {
    savedSearches,
    saveSearch,
    deleteSearch,
    markAsUsed,
    renameSearch,
    updateSearch,
  };
}
