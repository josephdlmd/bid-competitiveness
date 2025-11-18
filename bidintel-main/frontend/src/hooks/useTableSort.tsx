import { useState, useMemo } from 'react';

export type SortDirection = 'asc' | 'desc' | null;

export interface SortConfig<T> {
  key: keyof T | null;
  direction: SortDirection;
}

export function useTableSort<T>(data: T[], initialKey?: keyof T, initialDirection: SortDirection = 'asc') {
  const [sortConfig, setSortConfig] = useState<SortConfig<T>>({
    key: initialKey || null,
    direction: initialDirection,
  });

  const sortedData = useMemo(() => {
    if (!sortConfig.key || !sortConfig.direction) {
      return data;
    }

    const sorted = [...data].sort((a, b) => {
      const aValue = a[sortConfig.key as keyof T];
      const bValue = b[sortConfig.key as keyof T];

      // Handle null/undefined
      if (aValue === null || aValue === undefined) return 1;
      if (bValue === null || bValue === undefined) return -1;

      // Handle dates
      if (aValue instanceof Date && bValue instanceof Date) {
        return sortConfig.direction === 'asc'
          ? aValue.getTime() - bValue.getTime()
          : bValue.getTime() - aValue.getTime();
      }

      // Handle strings (date strings)
      if (typeof aValue === 'string' && typeof bValue === 'string') {
        // Check if it's a valid ISO date string (YYYY-MM-DD format)
        // This prevents false positives like "PR-2024-001" from being treated as dates
        const isISODate = (str: string) => /^\d{4}-\d{2}-\d{2}/.test(str);

        if (isISODate(aValue) && isISODate(bValue)) {
          const aDate = new Date(aValue);
          const bDate = new Date(bValue);
          if (!isNaN(aDate.getTime()) && !isNaN(bDate.getTime())) {
            return sortConfig.direction === 'asc'
              ? aDate.getTime() - bDate.getTime()
              : bDate.getTime() - aDate.getTime();
          }
        }

        // String comparison (case-insensitive for better UX)
        return sortConfig.direction === 'asc'
          ? aValue.localeCompare(bValue, undefined, { sensitivity: 'base' })
          : bValue.localeCompare(aValue, undefined, { sensitivity: 'base' });
      }

      // Handle numbers
      if (typeof aValue === 'number' && typeof bValue === 'number') {
        return sortConfig.direction === 'asc' ? aValue - bValue : bValue - aValue;
      }

      // Default comparison
      if (aValue < bValue) return sortConfig.direction === 'asc' ? -1 : 1;
      if (aValue > bValue) return sortConfig.direction === 'asc' ? 1 : -1;
      return 0;
    });

    return sorted;
  }, [data, sortConfig]);

  const requestSort = (key: keyof T) => {
    let direction: SortDirection = 'asc';

    if (sortConfig.key === key) {
      if (sortConfig.direction === 'asc') {
        direction = 'desc';
      } else if (sortConfig.direction === 'desc') {
        direction = null;
      }
    }

    setSortConfig({ key: direction ? key : null, direction });
  };

  const getSortDirection = (key: keyof T): SortDirection => {
    return sortConfig.key === key ? sortConfig.direction : null;
  };

  return { sortedData, sortConfig, requestSort, getSortDirection };
}

// Utility component for rendering sort icons
export const SortIcon = ({ direction }: { direction: SortDirection }) => {
  if (direction === 'asc') {
    return <span className="ml-1 text-slate-900">↑</span>;
  }
  if (direction === 'desc') {
    return <span className="ml-1 text-slate-900">↓</span>;
  }
  return <span className="ml-1 text-slate-300">↕</span>;
};
