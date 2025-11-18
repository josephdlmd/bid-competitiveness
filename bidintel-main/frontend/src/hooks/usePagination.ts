import { useState, useEffect, useCallback } from 'react';

interface UsePaginationOptions {
  defaultItemsPerPage?: number;
  useUrlParams?: boolean;
}

interface UsePaginationReturn {
  currentPage: number;
  itemsPerPage: number;
  setCurrentPage: (page: number) => void;
  setItemsPerPage: (items: number) => void;
  resetPagination: () => void;
  getOffset: () => number;
}

export const usePagination = (
  options: UsePaginationOptions = {}
): UsePaginationReturn => {
  const { defaultItemsPerPage = 50, useUrlParams = true } = options;

  // Initialize state from URL params if enabled
  const getInitialPage = (): number => {
    if (useUrlParams && typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search);
      const page = parseInt(params.get('page') || '1');
      return page > 0 ? page : 1;
    }
    return 1;
  };

  const getInitialItemsPerPage = (): number => {
    if (useUrlParams && typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search);
      const limit = parseInt(params.get('limit') || String(defaultItemsPerPage));
      return limit > 0 ? limit : defaultItemsPerPage;
    }
    return defaultItemsPerPage;
  };

  const [currentPage, setCurrentPageState] = useState<number>(getInitialPage);
  const [itemsPerPage, setItemsPerPageState] = useState<number>(getInitialItemsPerPage);

  // Update URL params when pagination state changes
  useEffect(() => {
    if (useUrlParams && typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search);

      if (currentPage === 1) {
        params.delete('page');
      } else {
        params.set('page', String(currentPage));
      }

      if (itemsPerPage === defaultItemsPerPage) {
        params.delete('limit');
      } else {
        params.set('limit', String(itemsPerPage));
      }

      const newUrl = params.toString()
        ? `${window.location.pathname}?${params.toString()}`
        : window.location.pathname;

      window.history.replaceState({}, '', newUrl);
    }
  }, [currentPage, itemsPerPage, useUrlParams, defaultItemsPerPage]);

  const setCurrentPage = useCallback((page: number) => {
    setCurrentPageState(Math.max(1, page));
  }, []);

  const setItemsPerPage = useCallback((items: number) => {
    setItemsPerPageState(items);
    // Reset to page 1 when changing items per page
    setCurrentPageState(1);
  }, []);

  const resetPagination = useCallback(() => {
    setCurrentPageState(1);
  }, []);

  const getOffset = useCallback((): number => {
    return (currentPage - 1) * itemsPerPage;
  }, [currentPage, itemsPerPage]);

  return {
    currentPage,
    itemsPerPage,
    setCurrentPage,
    setItemsPerPage,
    resetPagination,
    getOffset,
  };
};
