import { useState, useEffect } from 'react';
import { formatCurrency } from '../utils/formatters';
import { fetchBids } from '../services/api';
import { analyzeByUNSPSC, UNSPSCStats, getTrendIcon, getTrendColor } from '../utils/analytics';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  ZAxis,
  Cell,
} from 'recharts';

const UNSPSCIntelligence = () => {
  const [products, setProducts] = useState<UNSPSCStats[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [sortField, setSortField] = useState<'frequency' | 'total_market_size' | 'avg_competition'>('frequency');

  useEffect(() => {
    loadProductsData();
  }, []);

  const loadProductsData = async () => {
    setIsLoading(true);
    try {
      const response = await fetchBids({ limit: 500, offset: 0 });

      // Use analytics engine to analyze by UNSPSC
      const analysis = analyzeByUNSPSC(response.data);

      setProducts(analysis);
    } catch (err) {
      console.error('Error loading products data:', err);
      setProducts([]);
    } finally {
      setIsLoading(false);
    }
  };

  const sortedProducts = [...products].sort((a, b) => {
    if (sortField === 'frequency') {
      return b.frequency - a.frequency;
    } else if (sortField === 'total_market_size') {
      return b.total_market_size - a.total_market_size;
    } else {
      return a.avg_competition - b.avg_competition; // Lower competition first
    }
  });

  const totalCount = products.reduce((sum, p) => sum + p.frequency, 0);
  const totalBudget = products.reduce((sum, p) => sum + p.total_market_size, 0);

  return (
    <div>
      {/* Stats Bar */}
      <div className="border-b border-slate-200 px-6 py-2 bg-white">
        <div className="flex items-center space-x-6 text-sm">
          <div>
            <span className="text-slate-600">Product Categories: </span>
            <span className="font-semibold text-slate-900">
              {products.length}
            </span>
          </div>
          <div>
            <span className="text-slate-600">Total Bids: </span>
            <span className="font-semibold text-slate-900">
              {totalCount.toLocaleString()}
            </span>
          </div>
          <div>
            <span className="text-slate-600">Total Market Size: </span>
            <span className="font-semibold text-slate-900">
              {formatCurrency(totalBudget)}
            </span>
          </div>
        </div>
      </div>

      {/* Summary Bar */}
      <div className="px-6 py-3 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
        <span className="text-sm font-semibold text-slate-900">
          {isLoading ? 'Loading...' : 'Top Products'}
        </span>

        <div className="flex items-center space-x-2 text-sm">
          <span className="text-slate-600">Sort by:</span>
          <button
            onClick={() => setSortField('frequency')}
            className={`px-2 py-1 text-sm rounded ${
              sortField === 'frequency'
                ? 'bg-slate-900 text-white'
                : 'border border-slate-200 hover:bg-slate-50'
            }`}
          >
            Frequency
          </button>
          <button
            onClick={() => setSortField('total_market_size')}
            className={`px-2 py-1 text-sm rounded ${
              sortField === 'total_market_size'
                ? 'bg-slate-900 text-white'
                : 'border border-slate-200 hover:bg-slate-50'
            }`}
          >
            Market Size
          </button>
          <button
            onClick={() => setSortField('avg_competition')}
            className={`px-2 py-1 text-sm rounded ${
              sortField === 'avg_competition'
                ? 'bg-slate-900 text-white'
                : 'border border-slate-200 hover:bg-slate-50'
            }`}
          >
            Competition
          </button>
        </div>
      </div>

      {/* Charts Section */}
      {!isLoading && products.length > 0 && (
        <div className="p-6 space-y-4">
          {/* UNSPSC Frequency Analysis Chart */}
          <div className="border border-slate-200 rounded bg-white">
            <div className="px-4 py-3 border-b border-slate-200">
              <h3 className="text-sm font-semibold text-slate-900">UNSPSC Frequency Analysis</h3>
            </div>
            <div className="p-4">
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={sortedProducts.slice(0, 10)}
                    layout="vertical"
                    margin={{ top: 5, right: 30, left: 120, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                    <XAxis type="number" stroke="#64748b" tick={{ fontSize: 12 }} />
                    <YAxis
                      type="category"
                      dataKey="unspsc_name"
                      stroke="#64748b"
                      width={110}
                      tick={{ fontSize: 11 }}
                    />
                    <Tooltip
                      contentStyle={{ fontSize: 12 }}
                      content={({ active, payload }) => {
                        if (active && payload && payload.length) {
                          const data = payload[0].payload;
                          return (
                            <div className="bg-white p-2 border border-slate-200 rounded shadow-sm text-xs">
                              <p className="font-semibold text-slate-900">{data.unspsc_name}</p>
                              <p className="text-slate-600">Frequency: {data.frequency}</p>
                              <p className="text-slate-600">Market: {formatCurrency(data.total_market_size)}</p>
                            </div>
                          );
                        }
                        return null;
                      }}
                    />
                    <Bar dataKey="frequency" fill="#10b981" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Market Opportunity Matrix Chart */}
          <div className="border border-slate-200 rounded bg-white">
            <div className="px-4 py-3 border-b border-slate-200">
              <h3 className="text-sm font-semibold text-slate-900">Market Opportunity Matrix</h3>
            </div>
            <div className="p-4">
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <ScatterChart margin={{ top: 10, right: 20, bottom: 40, left: 60 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                    <XAxis
                      type="number"
                      dataKey="x"
                      stroke="#64748b"
                      tick={{ fontSize: 11 }}
                      tickFormatter={(value) => `₱${(value / 1000000).toFixed(0)}M`}
                      label={{
                        value: 'Market Size',
                        position: 'bottom',
                        fontSize: 11,
                        fill: '#64748b',
                        offset: 20,
                      }}
                    />
                    <YAxis
                      type="number"
                      dataKey="y"
                      stroke="#64748b"
                      tick={{ fontSize: 11 }}
                      label={{
                        value: 'Competition',
                        angle: -90,
                        position: 'left',
                        fontSize: 11,
                        fill: '#64748b',
                      }}
                    />
                    <ZAxis type="number" dataKey="z" range={[50, 500]} />
                    <Tooltip
                      contentStyle={{ fontSize: 12 }}
                      content={({ active, payload }) => {
                        if (active && payload && payload.length) {
                          const data = payload[0].payload;
                          const avgX = products.reduce((sum, p) => sum + p.total_market_size, 0) / products.length;
                          const avgY = products.reduce((sum, p) => sum + p.avg_competition, 0) / products.length;

                          const getQuadrant = (x: number, y: number) => {
                            if (x >= avgX && y <= avgY) return { zone: 'Gold Mine', color: '#10b981' };
                            if (x >= avgX && y > avgY) return { zone: 'Bloodbath', color: '#ef4444' };
                            if (x < avgX && y <= avgY) return { zone: 'Niche', color: '#3b82f6' };
                            return { zone: 'Avoid', color: '#64748b' };
                          };

                          const quadrant = getQuadrant(data.x, data.y);

                          return (
                            <div className="bg-white p-2 border border-slate-200 rounded shadow-sm text-xs">
                              <p className="font-semibold text-slate-900">{data.unspsc_name}</p>
                              <p className="text-slate-600">Market: {formatCurrency(data.x)}</p>
                              <p className="text-slate-600">Competition: {data.y.toFixed(1)}%</p>
                              <p className="text-slate-600">Frequency: {data.z}</p>
                              <p className="font-semibold mt-1" style={{ color: quadrant.color }}>
                                {quadrant.zone}
                              </p>
                            </div>
                          );
                        }
                        return null;
                      }}
                    />
                    <Scatter
                      data={products.map((p) => ({
                        ...p,
                        x: p.total_market_size,
                        y: p.avg_competition,
                        z: p.frequency,
                      }))}
                    >
                      {products.map((entry, index) => {
                        const avgX = products.reduce((sum, p) => sum + p.total_market_size, 0) / products.length;
                        const avgY = products.reduce((sum, p) => sum + p.avg_competition, 0) / products.length;

                        let color = '#64748b'; // Avoid (gray)
                        if (entry.total_market_size >= avgX && entry.avg_competition <= avgY) color = '#10b981'; // Gold Mine (emerald)
                        else if (entry.total_market_size >= avgX && entry.avg_competition > avgY) color = '#ef4444'; // Bloodbath (red)
                        else if (entry.total_market_size < avgX && entry.avg_competition <= avgY) color = '#3b82f6'; // Niche (blue)

                        return <Cell key={`cell-${index}`} fill={color} fillOpacity={0.7} />;
                      })}
                    </Scatter>
                  </ScatterChart>
                </ResponsiveContainer>
              </div>
              {/* Legend */}
              <div className="grid grid-cols-4 gap-2 mt-2">
                <div className="flex items-center gap-1 text-xs">
                  <div className="h-2 w-2 rounded-full bg-emerald-500"></div>
                  <span className="text-slate-700">Gold Mine</span>
                </div>
                <div className="flex items-center gap-1 text-xs">
                  <div className="h-2 w-2 rounded-full bg-red-500"></div>
                  <span className="text-slate-700">Bloodbath</span>
                </div>
                <div className="flex items-center gap-1 text-xs">
                  <div className="h-2 w-2 rounded-full bg-blue-500"></div>
                  <span className="text-slate-700">Niche</span>
                </div>
                <div className="flex items-center gap-1 text-xs">
                  <div className="h-2 w-2 rounded-full bg-slate-500"></div>
                  <span className="text-slate-700">Avoid</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Content */}
      {isLoading ? (
        <div className="px-6 py-16 text-center">
          <p className="text-sm text-slate-500">Analyzing product data...</p>
        </div>
      ) : products.length === 0 ? (
        <div className="px-6 py-16 text-center">
          <p className="text-sm text-slate-500">No product data available</p>
          <p className="text-xs text-slate-400 mt-1">Product analysis requires bid line items with UNSPSC codes</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="border-b border-slate-200 text-left">
              <tr className="text-xs text-slate-500 uppercase">
                <th className="px-6 py-3 font-medium">Code</th>
                <th className="px-6 py-3 font-medium">Product</th>
                <th className="px-6 py-3 font-medium text-right">Freq</th>
                <th className="px-6 py-3 font-medium text-right">Market Size</th>
                <th className="px-6 py-3 font-medium text-right">Avg ABC</th>
                <th className="px-6 py-3 font-medium text-right">Comp</th>
                <th className="px-6 py-3 font-medium text-right">Win Rate</th>
                <th className="px-6 py-3 font-medium text-center">Trend</th>
                <th className="px-6 py-3 font-medium text-center">Zone</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {sortedProducts.map((product) => {
                const avgX = products.reduce((sum, p) => sum + p.total_market_size, 0) / products.length;
                const avgY = products.reduce((sum, p) => sum + p.avg_competition, 0) / products.length;

                let zoneColor = '#64748b'; // Avoid (gray)
                let zoneName = 'Avoid';
                if (product.total_market_size >= avgX && product.avg_competition <= avgY) {
                  zoneColor = '#10b981'; // Gold Mine (emerald)
                  zoneName = 'Gold Mine';
                } else if (product.total_market_size >= avgX && product.avg_competition > avgY) {
                  zoneColor = '#ef4444'; // Bloodbath (red)
                  zoneName = 'Bloodbath';
                } else if (product.total_market_size < avgX && product.avg_competition <= avgY) {
                  zoneColor = '#3b82f6'; // Niche (blue)
                  zoneName = 'Niche';
                }

                return (
                  <tr
                    key={product.unspsc_code}
                    className="hover:bg-slate-50 text-sm transition-colors"
                  >
                    <td className="px-6 py-4 font-mono text-xs text-slate-600">
                      {product.unspsc_code}
                    </td>
                    <td className="px-6 py-4 font-medium text-slate-900">
                      {product.unspsc_name}
                    </td>
                    <td className="px-6 py-4 text-right text-slate-600">
                      {product.frequency}
                    </td>
                    <td className="px-6 py-4 text-right font-medium text-slate-900">
                      {formatCurrency(product.total_market_size)}
                    </td>
                    <td className="px-6 py-4 text-right font-medium text-slate-900">
                      {formatCurrency(product.avg_budget)}
                    </td>
                    <td className="px-6 py-4 text-right text-slate-600">
                      {product.avg_competition.toFixed(1)}
                    </td>
                    <td className="px-6 py-4 text-right text-slate-900">
                      {(product.your_win_rate * 100).toFixed(0)}%
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span className={`inline-flex items-center space-x-1 ${getTrendColor(product.trend_direction)}`}>
                        <span className="text-lg">{getTrendIcon(product.trend_direction)}</span>
                        <span className="text-xs capitalize">{product.trend_direction}</span>
                      </span>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span
                        className="inline-flex items-center px-2 py-1 rounded text-xs font-medium"
                        style={{
                          backgroundColor: `${zoneColor}20`,
                          color: zoneColor
                        }}
                      >
                        {zoneName}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default UNSPSCIntelligence;
