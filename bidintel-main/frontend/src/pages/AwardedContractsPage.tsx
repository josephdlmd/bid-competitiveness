import { useState, useEffect } from 'react';
import { Search, Filter, Download, TrendingUp, Building2, Award } from 'lucide-react';

interface AwardedContract {
  award_notice_number: string;
  awardee_name: string;
  procuring_entity: string;
  award_title: string;
  approved_budget: number;
  contract_amount: number;
  savings: number;
  savings_percentage: number;
  award_date: string;
  classification: string;
  procurement_mode: string;
  period_of_contract: string;
}

interface Stats {
  total_awards: number;
  total_abc: number;
  total_contract_amount: number;
  total_savings: number;
  avg_savings_percentage: number;
  unique_awardees: number;
  unique_procuring_entities: number;
}

const AwardedContractsPage = () => {
  const [contracts, setContracts] = useState<AwardedContract[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedClassification, setSelectedClassification] = useState('');
  const [page, setPage] = useState(0);
  const [total, setTotal] = useState(0);
  const limit = 20;

  useEffect(() => {
    fetchContracts();
    fetchStats();
  }, [page, searchTerm, selectedClassification]);

  const fetchContracts = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        limit: limit.toString(),
        offset: (page * limit).toString(),
      });

      if (searchTerm) params.append('search', searchTerm);
      if (selectedClassification) params.append('classification', selectedClassification);

      const response = await fetch(`http://localhost:8000/api/awarded-contracts?${params}`);
      const data = await response.json();

      setContracts(data.results);
      setTotal(data.total);
    } catch (error) {
      console.error('Error fetching contracts:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/awarded-contracts/stats/summary');
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-PH', {
      style: 'currency',
      currency: 'PHP',
      minimumFractionDigits: 2,
    }).format(amount);
  };

  const formatDate = (dateStr: string) => {
    if (!dateStr) return 'N/A';
    return new Date(dateStr).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                <Award className="w-7 h-7 text-blue-600" />
                Awarded Contracts
              </h1>
              <p className="mt-1 text-sm text-gray-500">
                Track awarded government contracts and competitive intelligence
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Contracts</p>
                  <p className="text-2xl font-bold text-gray-900 mt-2">
                    {stats.total_awards.toLocaleString()}
                  </p>
                </div>
                <div className="p-3 bg-blue-100 rounded-full">
                  <Award className="w-6 h-6 text-blue-600" />
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total ABC</p>
                  <p className="text-2xl font-bold text-gray-900 mt-2">
                    ₱{(stats.total_abc / 1000000).toFixed(1)}M
                  </p>
                </div>
                <div className="p-3 bg-green-100 rounded-full">
                  <TrendingUp className="w-6 h-6 text-green-600" />
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Savings</p>
                  <p className="text-2xl font-bold text-green-600 mt-2">
                    ₱{(stats.total_savings / 1000000).toFixed(1)}M
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    {stats.avg_savings_percentage.toFixed(1)}% avg
                  </p>
                </div>
                <div className="p-3 bg-purple-100 rounded-full">
                  <TrendingUp className="w-6 h-6 text-purple-600" />
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Unique Awardees</p>
                  <p className="text-2xl font-bold text-gray-900 mt-2">
                    {stats.unique_awardees}
                  </p>
                </div>
                <div className="p-3 bg-orange-100 rounded-full">
                  <Building2 className="w-6 h-6 text-orange-600" />
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Filters and Search */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  placeholder="Search by awardee, agency, or title..."
                  value={searchTerm}
                  onChange={(e) => {
                    setSearchTerm(e.target.value);
                    setPage(0);
                  }}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            <div className="flex gap-2">
              <select
                value={selectedClassification}
                onChange={(e) => {
                  setSelectedClassification(e.target.value);
                  setPage(0);
                }}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Classifications</option>
                <option value="Goods">Goods</option>
                <option value="Consulting Services">Consulting Services</option>
                <option value="Infrastructure">Infrastructure</option>
              </select>

              <button className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 flex items-center gap-2">
                <Filter className="w-4 h-4" />
                More Filters
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Contracts Table */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="bg-white rounded-lg shadow overflow-hidden">
          {loading ? (
            <div className="p-8 text-center text-gray-500">Loading...</div>
          ) : contracts.length === 0 ? (
            <div className="p-8 text-center text-gray-500">No contracts found</div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Award #
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Awardee
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Agency
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Title
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        ABC
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Contract Amount
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Savings
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Date
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {contracts.map((contract) => (
                      <tr key={contract.award_notice_number} className="hover:bg-gray-50 cursor-pointer">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-blue-600">
                          {contract.award_notice_number}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">
                            {contract.awardee_name?.substring(0, 30)}
                            {contract.awardee_name?.length > 30 ? '...' : ''}
                          </div>
                          <div className="text-xs text-gray-500">{contract.classification}</div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="text-sm text-gray-900">
                            {contract.procuring_entity?.substring(0, 30)}
                            {contract.procuring_entity?.length > 30 ? '...' : ''}
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="text-sm text-gray-900 max-w-xs truncate">
                            {contract.award_title}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                          {formatCurrency(contract.approved_budget)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium text-gray-900">
                          {formatCurrency(contract.contract_amount)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right">
                          <div className="text-sm font-medium text-green-600">
                            {contract.savings_percentage?.toFixed(1)}%
                          </div>
                          <div className="text-xs text-gray-500">
                            {formatCurrency(contract.savings)}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {formatDate(contract.award_date)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              <div className="bg-gray-50 px-6 py-4 flex items-center justify-between border-t border-gray-200">
                <div className="text-sm text-gray-700">
                  Showing <span className="font-medium">{page * limit + 1}</span> to{' '}
                  <span className="font-medium">{Math.min((page + 1) * limit, total)}</span> of{' '}
                  <span className="font-medium">{total}</span> results
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => setPage(Math.max(0, page - 1))}
                    disabled={page === 0}
                    className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Previous
                  </button>
                  <button
                    onClick={() => setPage(page + 1)}
                    disabled={(page + 1) * limit >= total}
                    className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Next
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default AwardedContractsPage;
