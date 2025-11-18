import { useState, useEffect } from 'react';
import { formatCurrency } from '../utils/formatters';
import { fetchBids } from '../services/api';
import { analyzeByAgency, AgencyStats, getTrendIcon, getTrendColor } from '../utils/analytics';

const AgencyIntelligence = () => {
  const [agencies, setAgencies] = useState<AgencyStats[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [sortField, setSortField] = useState<'bid_frequency' | 'total_annual_budget'>('total_annual_budget');

  useEffect(() => {
    loadAgenciesData();
  }, []);

  const loadAgenciesData = async () => {
    setIsLoading(true);
    try {
      const response = await fetchBids({ limit: 500, offset: 0 });

      // Use analytics engine to analyze by agency
      const analysis = analyzeByAgency(response.data);

      setAgencies(analysis);
    } catch (err) {
      console.error('Error loading agencies data:', err);
      setAgencies([]);
    } finally {
      setIsLoading(false);
    }
  };

  const sortedAgencies = [...agencies].sort((a, b) => {
    if (sortField === 'bid_frequency') {
      return b.bid_frequency - a.bid_frequency;
    } else {
      return b.total_annual_budget - a.total_annual_budget;
    }
  });

  const totalCount = agencies.reduce((sum, a) => sum + a.bid_frequency, 0);
  const totalBudget = agencies.reduce((sum, a) => sum + a.total_annual_budget, 0);

  return (
    <div>
      {/* Stats Bar */}
      <div className="border-b border-slate-200 px-6 py-2 bg-white">
        <div className="flex items-center space-x-6 text-sm">
          <div>
            <span className="text-slate-600">Agencies: </span>
            <span className="font-semibold text-slate-900">
              {agencies.length}
            </span>
          </div>
          <div>
            <span className="text-slate-600">Total Bids: </span>
            <span className="font-semibold text-slate-900">
              {totalCount.toLocaleString()}
            </span>
          </div>
          <div>
            <span className="text-slate-600">Total Budget: </span>
            <span className="font-semibold text-slate-900">
              {formatCurrency(totalBudget)}
            </span>
          </div>
        </div>
      </div>

      {/* Summary Bar */}
      <div className="px-6 py-3 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
        <span className="text-sm font-semibold text-slate-900">
          {isLoading ? 'Loading...' : 'Agency Market Size Ranking'}
        </span>

        <div className="flex items-center space-x-2 text-sm">
          <span className="text-slate-600">Sort by:</span>
          <button
            onClick={() => setSortField('bid_frequency')}
            className={`px-2 py-1 text-sm rounded ${
              sortField === 'bid_frequency'
                ? 'bg-slate-900 text-white'
                : 'border border-slate-200 hover:bg-slate-50'
            }`}
          >
            Frequency
          </button>
          <button
            onClick={() => setSortField('total_annual_budget')}
            className={`px-2 py-1 text-sm rounded ${
              sortField === 'total_annual_budget'
                ? 'bg-slate-900 text-white'
                : 'border border-slate-200 hover:bg-slate-50'
            }`}
          >
            Total Budget
          </button>
        </div>
      </div>

      {/* Content */}
      {isLoading ? (
        <div className="px-6 py-16 text-center">
          <p className="text-sm text-slate-500">Loading agency analytics...</p>
        </div>
      ) : agencies.length === 0 ? (
        <div className="px-6 py-16 text-center">
          <p className="text-sm text-slate-500">No agency data available</p>
          <p className="text-xs text-slate-400 mt-1">Data will appear once bids are collected</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="border-b border-slate-200 text-left">
              <tr className="text-xs text-slate-500 uppercase">
                <th className="px-6 py-3 font-medium">Rank</th>
                <th className="px-6 py-3 font-medium">Procuring Entity</th>
                <th className="px-6 py-3 font-medium text-right">Bid Count</th>
                <th className="px-6 py-3 font-medium text-right">Total Budget</th>
                <th className="px-6 py-3 font-medium text-right">Avg. Budget</th>
                <th className="px-6 py-3 font-medium">Preferred Mode</th>
                <th className="px-6 py-3 font-medium">Preferred Class</th>
                <th className="px-6 py-3 font-medium text-center">Trend</th>
                <th className="px-6 py-3 font-medium text-right">Penetration</th>
                <th className="px-6 py-3 font-medium text-right">Competition</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {sortedAgencies.map((agency, idx) => (
                <tr
                  key={agency.agency_name}
                  className="hover:bg-slate-50 text-sm transition-colors"
                >
                  <td className="px-6 py-4 text-slate-500">
                    #{idx + 1}
                  </td>
                  <td className="px-6 py-4 font-medium text-slate-900">
                    {agency.agency_name}
                  </td>
                  <td className="px-6 py-4 text-right text-slate-600">
                    {agency.bid_frequency.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 text-right font-medium text-slate-900">
                    {formatCurrency(agency.total_annual_budget)}
                  </td>
                  <td className="px-6 py-4 text-right text-slate-600">
                    {formatCurrency(agency.avg_budget)}
                  </td>
                  <td className="px-6 py-4 text-xs text-slate-600">
                    {agency.preferred_procurement_mode}
                  </td>
                  <td className="px-6 py-4 text-xs text-slate-600">
                    {agency.preferred_classification}
                  </td>
                  <td className="px-6 py-4 text-center">
                    <span className={`inline-flex items-center space-x-1 ${getTrendColor(agency.trend_direction)}`}>
                      <span className="text-lg">{getTrendIcon(agency.trend_direction)}</span>
                      <span className="text-xs">{agency.trend_percentage.toFixed(0)}%</span>
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right text-slate-600">
                    {agency.penetration_rate.toFixed(0)}%
                  </td>
                  <td className="px-6 py-4 text-right text-slate-600">
                    {agency.avg_competition.toFixed(0)}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default AgencyIntelligence;
