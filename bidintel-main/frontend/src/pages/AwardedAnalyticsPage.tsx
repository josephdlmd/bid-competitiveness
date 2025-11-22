import { useState, useEffect } from 'react';
import { TrendingUp, Building2, Users, BarChart3 } from 'lucide-react';

interface TopWinner {
  awardee_name: string;
  contract_count: number;
  total_amount: number;
  total_abc: number;
  total_savings: number;
  avg_savings_percentage: number;
  avg_contract_amount: number;
}

interface Agency {
  procuring_entity: string;
  contract_count: number;
  total_amount: number;
  total_abc: number;
  total_savings: number;
  avg_contract_amount: number;
}

interface Trend {
  period: string;
  contract_count: number;
  total_amount: number;
  avg_contract_amount: number;
}

const AwardedAnalyticsPage = () => {
  const [topWinners, setTopWinners] = useState<TopWinner[]>([]);
  const [topAgencies, setTopAgencies] = useState<Agency[]>([]);
  const [trends, setTrends] = useState<Trend[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    setLoading(true);
    try {
      const [winnersRes, agenciesRes, trendsRes] = await Promise.all([
        fetch('http://localhost:8000/api/awarded-contracts/analytics/top-winners?limit=10'),
        fetch('http://localhost:8000/api/awarded-contracts/analytics/by-agency?limit=10'),
        fetch('http://localhost:8000/api/awarded-contracts/analytics/trends?period=month&limit=12'),
      ]);

      const [winnersData, agenciesData, trendsData] = await Promise.all([
        winnersRes.json(),
        agenciesRes.json(),
        trendsRes.json(),
      ]);

      setTopWinners(winnersData.top_winners);
      setTopAgencies(agenciesData.agencies);
      setTrends(trendsData.trends);
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    if (amount >= 1000000) {
      return `₱${(amount / 1000000).toFixed(1)}M`;
    }
    if (amount >= 1000) {
      return `₱${(amount / 1000).toFixed(0)}K`;
    }
    return `₱${amount.toFixed(0)}`;
  };

  const getMaxAmount = (data: TopWinner[] | Agency[]) => {
    return Math.max(...data.map(item => item.total_amount));
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-500">Loading analytics...</div>
      </div>
    );
  }

  const maxWinnerAmount = getMaxAmount(topWinners);
  const maxAgencyAmount = getMaxAmount(topAgencies);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
              <BarChart3 className="w-7 h-7 text-blue-600" />
              Awarded Contracts Analytics
            </h1>
            <p className="mt-1 text-sm text-gray-500">
              Competitive intelligence and market insights
            </p>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Top Winners */}
          <div className="bg-white rounded-lg shadow">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                <Users className="w-5 h-5 text-blue-600" />
                Top 10 Winners
              </h2>
              <p className="text-sm text-gray-500 mt-1">Companies with most contracts won</p>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                {topWinners.map((winner, index) => (
                  <div key={index} className="space-y-2">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <span className="text-lg font-bold text-gray-400">#{index + 1}</span>
                          <span className="text-sm font-medium text-gray-900 truncate">
                            {winner.awardee_name}
                          </span>
                        </div>
                        <div className="flex gap-4 mt-1 text-xs text-gray-500">
                          <span>{winner.contract_count} contracts</span>
                          <span className="text-green-600">
                            {winner.avg_savings_percentage.toFixed(1)}% avg savings
                          </span>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-semibold text-gray-900">
                          {formatCurrency(winner.total_amount)}
                        </div>
                        <div className="text-xs text-gray-500">total value</div>
                      </div>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full transition-all"
                        style={{
                          width: `${(winner.total_amount / maxWinnerAmount) * 100}%`,
                        }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Top Agencies */}
          <div className="bg-white rounded-lg shadow">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                <Building2 className="w-5 h-5 text-green-600" />
                Top 10 Procuring Entities
              </h2>
              <p className="text-sm text-gray-500 mt-1">Agencies with highest spending</p>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                {topAgencies.map((agency, index) => (
                  <div key={index} className="space-y-2">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <span className="text-lg font-bold text-gray-400">#{index + 1}</span>
                          <span className="text-sm font-medium text-gray-900 truncate">
                            {agency.procuring_entity}
                          </span>
                        </div>
                        <div className="flex gap-4 mt-1 text-xs text-gray-500">
                          <span>{agency.contract_count} contracts</span>
                          <span>Avg: {formatCurrency(agency.avg_contract_amount)}</span>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-semibold text-gray-900">
                          {formatCurrency(agency.total_amount)}
                        </div>
                        <div className="text-xs text-gray-500">total spent</div>
                      </div>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-green-600 h-2 rounded-full transition-all"
                        style={{
                          width: `${(agency.total_amount / maxAgencyAmount) * 100}%`,
                        }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Trends Chart */}
          <div className="bg-white rounded-lg shadow lg:col-span-2">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-purple-600" />
                Monthly Trends
              </h2>
              <p className="text-sm text-gray-500 mt-1">Contract awards over time</p>
            </div>
            <div className="p-6">
              <div className="space-y-6">
                {/* Simple Bar Chart */}
                <div className="relative" style={{ height: '300px' }}>
                  <div className="absolute inset-0 flex items-end justify-around gap-2">
                    {trends.map((trend, index) => {
                      const maxTrendAmount = Math.max(...trends.map(t => t.total_amount));
                      const height = (trend.total_amount / maxTrendAmount) * 100;

                      return (
                        <div key={index} className="flex-1 flex flex-col items-center">
                          <div
                            className="w-full bg-blue-600 rounded-t-lg hover:bg-blue-700 transition-all cursor-pointer relative group"
                            style={{ height: `${height}%` }}
                          >
                            {/* Tooltip */}
                            <div className="absolute bottom-full mb-2 left-1/2 transform -translate-x-1/2 bg-gray-900 text-white text-xs rounded py-1 px-2 opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
                              <div className="font-semibold">{formatCurrency(trend.total_amount)}</div>
                              <div>{trend.contract_count} contracts</div>
                            </div>
                          </div>
                          <div className="text-xs text-gray-600 mt-2 transform -rotate-45 origin-top-left w-16">
                            {trend.period}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Legend and Stats */}
                <div className="grid grid-cols-3 gap-4 pt-6 border-t border-gray-200">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-gray-900">
                      {trends.reduce((sum, t) => sum + t.contract_count, 0)}
                    </div>
                    <div className="text-sm text-gray-500">Total Contracts</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-gray-900">
                      {formatCurrency(trends.reduce((sum, t) => sum + t.total_amount, 0))}
                    </div>
                    <div className="text-sm text-gray-500">Total Value</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-gray-900">
                      {formatCurrency(
                        trends.reduce((sum, t) => sum + t.avg_contract_amount, 0) / trends.length
                      )}
                    </div>
                    <div className="text-sm text-gray-500">Avg Contract</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AwardedAnalyticsPage;
