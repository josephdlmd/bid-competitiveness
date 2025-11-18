import { useState, useEffect } from 'react';
import { formatCurrency, formatDate } from '../utils/formatters';
import { fetchBids } from '../services/api';
import { getTopOpportunities, OpportunityScore, getScoreColor, getUrgencyColor } from '../utils/analytics';

const OpportunityDashboard = () => {
  const [opportunities, setOpportunities] = useState<OpportunityScore[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [sortBy, setSortBy] = useState<'score' | 'urgency' | 'budget' | 'competition'>('score');
  const [quickFilter, setQuickFilter] = useState<'all' | 'urgent' | 'high_budget'>('all');

  useEffect(() => {
    loadOpportunities();
  }, []);

  const getDaysUntilClosing = (closingDate: string): number => {
    const now = new Date();
    const closing = new Date(closingDate);
    const diffTime = closing.getTime() - now.getTime();
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  };

  const getUrgencyBorderColor = (days: number): string => {
    if (days <= 3) return 'border-l-red-500 bg-red-50';
    if (days <= 7) return 'border-l-amber-500 bg-amber-50';
    return 'border-l-emerald-500 bg-emerald-50';
  };

  const loadOpportunities = async () => {
    setIsLoading(true);
    try {
      const response = await fetchBids({ limit: 200, offset: 0 });

      // Use analytics engine to calculate opportunity scores
      const scoredOpportunities = getTopOpportunities(response.data, 50);

      setOpportunities(scoredOpportunities);
    } catch (err) {
      console.error('Error loading opportunities:', err);
      setOpportunities([]);
    } finally {
      setIsLoading(false);
    }
  };

  // Apply quick filters
  const filteredOpportunities = opportunities.filter((opp) => {
    if (quickFilter === 'urgent') {
      return opp.factors.days_until_closing <= 7;
    } else if (quickFilter === 'high_budget') {
      return opp.bid.approved_budget >= 2000000;
    }
    return true;
  });

  // Apply sorting
  const sortedOpportunities = [...filteredOpportunities].sort((a, b) => {
    switch (sortBy) {
      case 'score':
        return b.score - a.score;
      case 'urgency':
        return a.factors.days_until_closing - b.factors.days_until_closing;
      case 'budget':
        return b.bid.approved_budget - a.bid.approved_budget;
      case 'competition':
        return a.competition_score - b.competition_score; // Lower competition is better
      default:
        return b.score - a.score;
    }
  });

  // Calculate priority distribution (from filtered results)
  const highPriority = sortedOpportunities.filter(o => o.score >= 80).length;
  const mediumPriority = sortedOpportunities.filter(o => o.score >= 60 && o.score < 80).length;
  const lowPriority = sortedOpportunities.filter(o => o.score < 60).length;

  return (
    <div>
      {/* Stats Bar */}
      <div className="border-b border-slate-200 px-6 py-2 bg-white">
        <div className="flex items-center space-x-6 text-sm">
          <div>
            <span className="text-slate-600">High Score (≥80): </span>
            <span className="font-semibold text-emerald-600">
              {highPriority}
            </span>
          </div>
          <div>
            <span className="text-slate-600">Medium Score (60-79): </span>
            <span className="font-semibold text-amber-600">
              {mediumPriority}
            </span>
          </div>
          <div>
            <span className="text-slate-600">Low Score (&lt;60): </span>
            <span className="font-semibold text-slate-600">
              {lowPriority}
            </span>
          </div>
          <div>
            <span className="text-slate-600">Total Opportunities: </span>
            <span className="font-semibold text-slate-900">
              {sortedOpportunities.length}
            </span>
          </div>
        </div>
      </div>

      {/* Summary Bar with Controls */}
      <div className="px-6 py-3 bg-slate-50 border-b border-slate-200">
        <div className="flex items-center justify-between">
          <span className="text-sm text-slate-600">
            {isLoading ? 'Loading...' : `${sortedOpportunities.length} opportunities ranked by AI-calculated score`}
          </span>

          <div className="flex items-center space-x-4">
            {/* Quick Filters */}
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setQuickFilter('all')}
                className={`px-2 py-1 text-xs rounded ${
                  quickFilter === 'all'
                    ? 'bg-slate-900 text-white'
                    : 'border border-slate-200 text-slate-600 hover:bg-slate-100'
                }`}
              >
                All
              </button>
              <button
                onClick={() => setQuickFilter('urgent')}
                className={`px-2 py-1 text-xs rounded ${
                  quickFilter === 'urgent'
                    ? 'bg-amber-600 text-white'
                    : 'border border-slate-200 text-slate-600 hover:bg-slate-100'
                }`}
              >
                ≤7 days
              </button>
              <button
                onClick={() => setQuickFilter('high_budget')}
                className={`px-2 py-1 text-xs rounded ${
                  quickFilter === 'high_budget'
                    ? 'bg-emerald-600 text-white'
                    : 'border border-slate-200 text-slate-600 hover:bg-slate-100'
                }`}
              >
                ≥₱2M
              </button>
            </div>

            {/* Sort Options */}
            <div className="flex items-center space-x-2 text-sm">
              <span className="text-slate-600">Sort by:</span>
              <button
                onClick={() => setSortBy('score')}
                className={`px-2 py-1 text-xs rounded ${
                  sortBy === 'score'
                    ? 'bg-slate-900 text-white'
                    : 'border border-slate-200 hover:bg-slate-50'
                }`}
              >
                Score
              </button>
              <button
                onClick={() => setSortBy('urgency')}
                className={`px-2 py-1 text-xs rounded ${
                  sortBy === 'urgency'
                    ? 'bg-slate-900 text-white'
                    : 'border border-slate-200 hover:bg-slate-50'
                }`}
              >
                Urgency
              </button>
              <button
                onClick={() => setSortBy('budget')}
                className={`px-2 py-1 text-xs rounded ${
                  sortBy === 'budget'
                    ? 'bg-slate-900 text-white'
                    : 'border border-slate-200 hover:bg-slate-50'
                }`}
              >
                Budget
              </button>
              <button
                onClick={() => setSortBy('competition')}
                className={`px-2 py-1 text-xs rounded ${
                  sortBy === 'competition'
                    ? 'bg-slate-900 text-white'
                    : 'border border-slate-200 hover:bg-slate-50'
                }`}
              >
                Competition
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Cards Grid */}
      {isLoading ? (
        <div className="px-6 py-16 text-center">
          <p className="text-sm text-slate-500">Loading opportunities...</p>
        </div>
      ) : opportunities.length === 0 ? (
        <div className="px-6 py-16 text-center">
          <p className="text-sm text-slate-500">No opportunities found</p>
          <p className="text-xs text-slate-400 mt-1">Check back later for new opportunities</p>
        </div>
      ) : (
        <div className="px-6 py-3">
          <h2 className="text-sm font-semibold text-slate-900 mb-3">
            Top 20 Opportunities by Score
          </h2>
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-2">
            {sortedOpportunities.slice(0, 20).map((opp) => {
              const daysUntil = opp.factors.days_until_closing;
              return (
                <div
                  key={opp.bid.reference_number}
                  className={`border-l-4 p-3 ${getUrgencyBorderColor(daysUntil)} hover:opacity-80 transition-opacity cursor-pointer`}
                >
                  {/* Header: Title and Score */}
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <div className="font-medium text-sm text-slate-900 mb-1">
                        {opp.bid.title}
                      </div>
                      <div className="text-xs text-slate-600 mb-2">
                        {opp.bid.procuring_entity}
                      </div>
                    </div>
                    <div className="text-right ml-4">
                      <div className={`text-2xl font-bold ${getScoreColor(opp.score)}`}>
                        {opp.score}
                      </div>
                      <div className="text-xs text-slate-500">score</div>
                    </div>
                  </div>

                  {/* Score Breakdown */}
                  <div className="flex items-center space-x-3 text-xs mb-2 pb-2 border-b border-slate-200">
                    <div>
                      <span className="text-slate-500">Urgency: </span>
                      <span className={`font-medium ${getUrgencyColor(daysUntil)}`}>
                        {opp.urgency_score}/40
                      </span>
                    </div>
                    <div>
                      <span className="text-slate-500">Budget: </span>
                      <span className="font-medium text-slate-700">{opp.budget_score}/30</span>
                    </div>
                    <div>
                      <span className="text-slate-500">Competition: </span>
                      <span className="font-medium text-slate-700">{opp.competition_score}/30</span>
                    </div>
                  </div>

                  {/* Details */}
                  <div className="flex items-center justify-between text-xs">
                    <div className="space-y-1">
                      <div>
                        <span className="text-slate-500">Ref: </span>
                        <span className="font-mono text-slate-600">{opp.bid.reference_number}</span>
                      </div>
                      <div>
                        <span className="text-slate-500">Class: </span>
                        <span className="text-slate-600">{opp.bid.classification}</span>
                      </div>
                      <div>
                        <span className="text-slate-500">Days Left: </span>
                        <span className={`font-semibold ${getUrgencyColor(daysUntil)}`}>
                          {daysUntil}d
                        </span>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-medium text-sm text-slate-900">
                        {formatCurrency(opp.bid.approved_budget)}
                      </div>
                      <div className="text-slate-500">
                        Closes: {formatDate(opp.bid.closing_date)}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default OpportunityDashboard;
