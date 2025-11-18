import { useState, useEffect, useMemo } from 'react';
import { formatCurrency } from '@/utils/formatters';
import { fetchAnalytics } from '@/services/api';
import { useTableSort, SortIcon } from '@/hooks/useTableSort';

interface AgencyData {
  name: string;
  count: number;
  total_budget: number;
}

interface ClassificationData {
  classification: string;
  count: number;
  total_budget: number;
}

const AnalyticsPage = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [analytics, setAnalytics] = useState<any>(null);

  // Transform analytics data for sorting
  const agenciesData = useMemo<AgencyData[]>(() => {
    if (!analytics?.top_agencies) return [];
    return analytics.top_agencies;
  }, [analytics]);

  const classificationsData = useMemo<ClassificationData[]>(() => {
    if (!analytics?.by_classification) return [];
    return Object.entries(analytics.by_classification).map(([key, value]: [string, any]) => ({
      classification: key,
      count: value.count,
      total_budget: value.total_budget,
    }));
  }, [analytics]);

  // Sorting for agencies table
  const {
    sortedData: sortedAgencies,
    requestSort: requestAgencySort,
    getSortDirection: getAgencySortDirection,
  } = useTableSort<AgencyData>(agenciesData, 'count', 'desc');

  // Sorting for classifications table
  const {
    sortedData: sortedClassifications,
    requestSort: requestClassificationSort,
    getSortDirection: getClassificationSortDirection,
  } = useTableSort<ClassificationData>(classificationsData, 'count', 'desc');

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    setIsLoading(true);
    try {
      const data = await fetchAnalytics();
      setAnalytics(data);
    } catch (err) {
      console.error('Error loading analytics:', err);
      setAnalytics(null);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      {/* Header */}
      <div className="border-b border-slate-200 px-6 py-3 bg-white">
        <span className="text-sm font-semibold text-slate-900">Analytics</span>
      </div>

      {/* Summary Bar */}
      <div className="px-6 py-3 bg-slate-50 border-b border-slate-200">
        <span className="text-sm text-slate-600">
          {isLoading ? 'Loading...' : 'Bid trends and insights'}
        </span>
      </div>

      {/* Content */}
      {isLoading ? (
        <div className="px-6 py-16 text-center">
          <p className="text-sm text-slate-500">Loading analytics...</p>
        </div>
      ) : !analytics ? (
        <div className="px-6 py-16 text-center">
          <p className="text-sm text-slate-500">No analytics data available</p>
          <p className="text-xs text-slate-400 mt-1">Analytics will appear once bid data is collected</p>
        </div>
      ) : (
        <div className="px-6 py-6 space-y-6">
          {/* Top Agencies */}
          {sortedAgencies.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-slate-900 mb-3">Top Procuring Entities</h3>
              <div className="border border-slate-200">
                <table className="w-full">
                  <thead className="border-b border-slate-200 text-left">
                    <tr className="text-xs text-slate-500 uppercase">
                      <th
                        className="px-6 py-3 font-medium cursor-pointer hover:bg-slate-50 select-none"
                        onClick={() => requestAgencySort('name')}
                      >
                        Agency
                        <SortIcon direction={getAgencySortDirection('name')} />
                      </th>
                      <th
                        className="px-6 py-3 font-medium text-right cursor-pointer hover:bg-slate-50 select-none"
                        onClick={() => requestAgencySort('count')}
                      >
                        Bids
                        <SortIcon direction={getAgencySortDirection('count')} />
                      </th>
                      <th
                        className="px-6 py-3 font-medium text-right cursor-pointer hover:bg-slate-50 select-none"
                        onClick={() => requestAgencySort('total_budget')}
                      >
                        Total Budget
                        <SortIcon direction={getAgencySortDirection('total_budget')} />
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {sortedAgencies.map((agency: AgencyData, idx: number) => (
                      <tr key={idx} className="hover:bg-slate-50 text-sm transition-colors">
                        <td className="px-6 py-4 font-medium text-slate-900">{agency.name}</td>
                        <td className="px-6 py-4 text-right text-slate-600">{agency.count}</td>
                        <td className="px-6 py-4 text-right font-medium text-slate-900">
                          {formatCurrency(agency.total_budget)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Classification Breakdown */}
          {sortedClassifications.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-slate-900 mb-3">By Classification</h3>
              <div className="border border-slate-200">
                <table className="w-full">
                  <thead className="border-b border-slate-200 text-left">
                    <tr className="text-xs text-slate-500 uppercase">
                      <th
                        className="px-6 py-3 font-medium cursor-pointer hover:bg-slate-50 select-none"
                        onClick={() => requestClassificationSort('classification')}
                      >
                        Classification
                        <SortIcon direction={getClassificationSortDirection('classification')} />
                      </th>
                      <th
                        className="px-6 py-3 font-medium text-right cursor-pointer hover:bg-slate-50 select-none"
                        onClick={() => requestClassificationSort('count')}
                      >
                        Count
                        <SortIcon direction={getClassificationSortDirection('count')} />
                      </th>
                      <th
                        className="px-6 py-3 font-medium text-right cursor-pointer hover:bg-slate-50 select-none"
                        onClick={() => requestClassificationSort('total_budget')}
                      >
                        Total Budget
                        <SortIcon direction={getClassificationSortDirection('total_budget')} />
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {sortedClassifications.map((item: ClassificationData, idx: number) => (
                      <tr key={idx} className="hover:bg-slate-50 text-sm transition-colors">
                        <td className="px-6 py-4 font-medium text-slate-900">{item.classification}</td>
                        <td className="px-6 py-4 text-right text-slate-600">{item.count}</td>
                        <td className="px-6 py-4 text-right font-medium text-slate-900">
                          {formatCurrency(item.total_budget)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AnalyticsPage;
