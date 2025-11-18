import { useState, useEffect } from 'react';
import { formatCurrency, formatDate } from '@/utils/formatters';
import { fetchBids } from '@/services/api';
import { Bid } from '@/lib/types';

const CalendarPage = () => {
  const [bids, setBids] = useState<Bid[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth());
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());

  useEffect(() => {
    loadBids();
  }, [selectedMonth, selectedYear]);

  const getDaysUntilClosing = (closingDate: string): number => {
    const now = new Date();
    const closing = new Date(closingDate);
    const diffTime = closing.getTime() - now.getTime();
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  };

  const getUrgencyColor = (days: number): string => {
    if (days <= 3) return 'text-red-600 border-l-red-500 bg-red-50';
    if (days <= 7) return 'text-amber-600 border-l-amber-500 bg-amber-50';
    return 'text-emerald-600 border-l-emerald-500 bg-emerald-50';
  };

  const loadBids = async () => {
    setIsLoading(true);
    try {
      const response = await fetchBids({ limit: 100, offset: 0 });
      // Group by closing date
      const sorted = response.data.sort((a, b) =>
        new Date(a.closing_date).getTime() - new Date(b.closing_date).getTime()
      );
      setBids(sorted);
    } catch (err) {
      console.error('Error loading bids:', err);
      setBids([]);
    } finally {
      setIsLoading(false);
    }
  };

  // Group bids by date
  const bidsByDate = bids.reduce((acc, bid) => {
    const date = bid.closing_date;
    if (!acc[date]) acc[date] = [];
    acc[date].push(bid);
    return acc;
  }, {} as Record<string, Bid[]>);

  return (
    <div>
      {/* Header Bar */}
      <div className="border-b border-slate-200 px-6 py-3 bg-white">
        <div className="flex items-center justify-between">
          <span className="text-sm font-semibold text-slate-900">Bid Closing Calendar</span>
          <select
            value={`${selectedYear}-${selectedMonth}`}
            onChange={(e) => {
              const [year, month] = e.target.value.split('-');
              setSelectedYear(parseInt(year));
              setSelectedMonth(parseInt(month));
            }}
            className="px-3 py-1.5 text-sm border border-slate-200 rounded-lg focus:outline-none focus:border-slate-400"
          >
            {[...Array(12)].map((_, i) => {
              const date = new Date(selectedYear, i);
              return (
                <option key={i} value={`${selectedYear}-${i}`}>
                  {date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
                </option>
              );
            })}
          </select>
        </div>
      </div>

      {/* Summary Bar */}
      <div className="px-6 py-3 bg-slate-50 border-b border-slate-200">
        <span className="text-sm text-slate-600">
          {isLoading ? 'Loading...' : `${bids.length} bids closing this period`}
        </span>
      </div>

      {/* Timeline View */}
      {isLoading ? (
        <div className="px-6 py-16 text-center">
          <p className="text-sm text-slate-500">Loading calendar...</p>
        </div>
      ) : bids.length === 0 ? (
        <div className="px-6 py-16 text-center">
          <p className="text-sm text-slate-500">No bids found for this period</p>
        </div>
      ) : (
        <div className="px-6 py-3">
          <div className="space-y-4">
            {Object.entries(bidsByDate).map(([date, dateBids]) => (
              <div key={date}>
                <div className="mb-2">
                  <span className="text-sm font-semibold text-slate-900">
                    {formatDate(date)}
                  </span>
                  <span className="ml-2 text-xs text-slate-500">
                    ({dateBids.length} {dateBids.length === 1 ? 'bid' : 'bids'})
                  </span>
                </div>
                <div className="space-y-2">
                  {dateBids.map((bid) => {
                    const daysUntil = getDaysUntilClosing(bid.closing_date);
                    return (
                      <div
                        key={bid.reference_number}
                        className={`border-l-4 p-3 ${getUrgencyColor(daysUntil)} hover:opacity-80 transition-opacity cursor-pointer`}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="font-medium text-sm text-slate-900 mb-1">
                              {bid.title}
                            </div>
                            <div className="text-xs text-slate-600 space-x-3">
                              <span>{bid.procuring_entity}</span>
                              <span>•</span>
                              <span className="font-mono">{bid.reference_number}</span>
                            </div>
                          </div>
                          <div className="text-right ml-4">
                            <div className="font-medium text-sm text-slate-900">
                              {formatCurrency(bid.approved_budget)}
                            </div>
                            <div className={`text-xs font-semibold ${daysUntil <= 3 ? 'text-red-600' : daysUntil <= 7 ? 'text-amber-600' : 'text-emerald-600'}`}>
                              {daysUntil > 0 ? `${daysUntil}d left` : 'Closed'}
                            </div>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default CalendarPage;
