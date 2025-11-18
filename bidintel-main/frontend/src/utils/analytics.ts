import { Bid } from '../lib/types';

// ========================================
// OPPORTUNITY SCORING ENGINE
// ========================================

export interface OpportunityScore {
  bid: Bid;
  score: number;
  urgency_score: number;
  budget_score: number;
  competition_score: number;
  factors: {
    days_until_closing: number;
    budget_size: number;
    estimated_competition: number;
  };
}

/**
 * Calculate opportunity score (0-100) based on multiple factors
 * Higher score = better opportunity
 */
export const calculateOpportunityScore = (bid: Bid): OpportunityScore => {
  const daysUntilClosing = getDaysUntilClosing(bid.closing_date);

  // 1. Urgency Score (0-40 points) - More urgent = higher score
  let urgency_score = 0;
  if (daysUntilClosing <= 3) urgency_score = 40;
  else if (daysUntilClosing <= 7) urgency_score = 35;
  else if (daysUntilClosing <= 14) urgency_score = 30;
  else if (daysUntilClosing <= 30) urgency_score = 20;
  else urgency_score = 10;

  // 2. Budget Score (0-30 points) - Sweet spot: 500K-5M
  let budget_score = 0;
  const budget = bid.approved_budget;
  if (budget >= 500000 && budget <= 5000000) budget_score = 30; // Sweet spot
  else if (budget >= 100000 && budget < 500000) budget_score = 25; // Good
  else if (budget > 5000000 && budget <= 20000000) budget_score = 25; // Large but manageable
  else if (budget < 100000) budget_score = 10; // Too small
  else budget_score = 15; // Too large (high competition)

  // 3. Competition Score (0-30 points) - Estimate based on budget and type
  let competition_score = 30;
  if (budget > 10000000) competition_score = 15; // Large bids = high competition
  else if (bid.classification === 'Goods') competition_score = 25; // Goods = moderate competition
  else if (bid.classification === 'Infrastructure') competition_score = 10; // Infrastructure = very high competition
  else competition_score = 30; // Services = lower competition

  const total_score = urgency_score + budget_score + competition_score;

  return {
    bid,
    score: total_score,
    urgency_score,
    budget_score,
    competition_score,
    factors: {
      days_until_closing: daysUntilClosing,
      budget_size: budget,
      estimated_competition: 100 - competition_score
    }
  };
};

/**
 * Get top opportunities sorted by score
 */
export const getTopOpportunities = (bids: Bid[], limit: number = 50): OpportunityScore[] => {
  return bids
    .map(calculateOpportunityScore)
    .filter(opp => opp.factors.days_until_closing > 0) // Only active bids
    .sort((a, b) => b.score - a.score) // Highest score first
    .slice(0, limit);
};

// ========================================
// UNSPSC INTELLIGENCE ENGINE
// ========================================

export interface UNSPSCStats {
  unspsc_code: string;
  unspsc_name: string;
  frequency: number;
  total_market_size: number;
  avg_budget: number;
  avg_competition: number;
  trend_direction: 'rising' | 'falling' | 'stable';
  trend_percentage: number;
  recent_bids: Bid[];
  your_win_rate: number; // Simulated win rate based on market conditions (0-1)
}

/**
 * Analyze bids by UNSPSC product codes
 */
export const analyzeByUNSPSC = (bids: Bid[]): UNSPSCStats[] => {
  // Group bids by UNSPSC code (extracted from line items)
  const unspscMap = new Map<string, Bid[]>();

  bids.forEach(bid => {
    if (bid.line_items && bid.line_items.length > 0) {
      bid.line_items.forEach(item => {
        if (item.unspsc_code) {
          const code = item.unspsc_code;
          if (!unspscMap.has(code)) {
            unspscMap.set(code, []);
          }
          unspscMap.get(code)!.push(bid);
        }
      });
    }
  });

  // Calculate stats for each UNSPSC code
  const stats: UNSPSCStats[] = [];

  unspscMap.forEach((codeBids, code) => {
    const frequency = codeBids.length;
    const total_market_size = codeBids.reduce((sum, bid) => sum + bid.approved_budget, 0);
    const avg_budget = total_market_size / frequency;

    // Estimate competition based on frequency and budget
    let avg_competition = 50; // Base competition
    if (frequency > 50) avg_competition = 75; // High frequency = high competition
    else if (frequency > 20) avg_competition = 60;
    else if (frequency < 5) avg_competition = 30; // Low frequency = low competition

    // Calculate trend (compare recent vs older bids)
    const { trend_direction, trend_percentage } = calculateTrend(codeBids);

    // Get UNSPSC name from first item
    const unspsc_name = codeBids[0]?.line_items?.find(i => i.unspsc_code === code)?.lot_name || code;

    // Calculate simulated win rate based on competition and market conditions
    // Lower competition = higher win rate
    let your_win_rate = 0.50; // Base 50%
    if (avg_competition < 40) your_win_rate = 0.65; // Low competition
    else if (avg_competition > 70) your_win_rate = 0.30; // High competition

    // Adjust based on frequency (more experience = better rate)
    if (frequency > 20) your_win_rate *= 1.1; // More opportunities = more experience
    else if (frequency < 5) your_win_rate *= 0.9; // Less opportunities = less experience

    // Cap at realistic range
    your_win_rate = Math.min(0.75, Math.max(0.15, your_win_rate));

    stats.push({
      unspsc_code: code,
      unspsc_name,
      frequency,
      total_market_size,
      avg_budget,
      avg_competition,
      trend_direction,
      trend_percentage,
      recent_bids: codeBids.slice(0, 10), // Keep 10 most recent
      your_win_rate
    });
  });

  return stats.sort((a, b) => b.frequency - a.frequency); // Sort by frequency
};

// ========================================
// AGENCY INTELLIGENCE ENGINE
// ========================================

export interface AgencyStats {
  agency_name: string;
  total_annual_budget: number;
  bid_frequency: number;
  avg_budget: number;
  avg_competition: number;
  penetration_rate: number;
  preferred_procurement_mode: string;
  preferred_classification: string;
  trend_direction: 'rising' | 'falling' | 'stable';
  trend_percentage: number;
  recent_bids: Bid[];
}

/**
 * Analyze bids by procuring entities (agencies)
 */
export const analyzeByAgency = (bids: Bid[]): AgencyStats[] => {
  // Group bids by agency
  const agencyMap = new Map<string, Bid[]>();

  bids.forEach(bid => {
    const agency = bid.procuring_entity;
    if (!agencyMap.has(agency)) {
      agencyMap.set(agency, []);
    }
    agencyMap.get(agency)!.push(bid);
  });

  // Calculate stats for each agency
  const stats: AgencyStats[] = [];

  agencyMap.forEach((agencyBids, agency) => {
    const bid_frequency = agencyBids.length;
    const total_annual_budget = agencyBids.reduce((sum, bid) => sum + bid.approved_budget, 0);
    const avg_budget = total_annual_budget / bid_frequency;

    // Calculate preferred procurement mode (most common)
    const modeCount = new Map<string, number>();
    agencyBids.forEach(bid => {
      const mode = bid.procurement_mode || 'Unknown';
      modeCount.set(mode, (modeCount.get(mode) || 0) + 1);
    });
    const preferred_procurement_mode = Array.from(modeCount.entries())
      .sort((a, b) => b[1] - a[1])[0]?.[0] || 'Unknown';

    // Calculate preferred classification (most common)
    const classCount = new Map<string, number>();
    agencyBids.forEach(bid => {
      const classification = bid.classification || 'Unknown';
      classCount.set(classification, (classCount.get(classification) || 0) + 1);
    });
    const preferred_classification = Array.from(classCount.entries())
      .sort((a, b) => b[1] - a[1])[0]?.[0] || 'Unknown';

    // Estimate competition based on frequency and budget
    let avg_competition = 50;
    if (avg_budget > 10000000) avg_competition = 80; // Large budgets = high competition
    else if (avg_budget > 1000000) avg_competition = 60;
    else avg_competition = 40;

    // Penetration rate (estimate: how often you'd win - simplified)
    // In real app, track actual wins vs bids
    const penetration_rate = Math.max(0, Math.min(100, 100 - avg_competition + (bid_frequency > 10 ? 10 : 0)));

    // Calculate trend
    const { trend_direction, trend_percentage } = calculateTrend(agencyBids);

    stats.push({
      agency_name: agency,
      total_annual_budget,
      bid_frequency,
      avg_budget,
      avg_competition,
      penetration_rate,
      preferred_procurement_mode,
      preferred_classification,
      trend_direction,
      trend_percentage,
      recent_bids: agencyBids.slice(0, 10)
    });
  });

  return stats.sort((a, b) => b.total_annual_budget - a.total_annual_budget);
};

// ========================================
// TREND ANALYSIS ENGINE
// ========================================

/**
 * Calculate trend direction based on publish dates
 */
const calculateTrend = (bids: Bid[]): { trend_direction: 'rising' | 'falling' | 'stable', trend_percentage: number } => {
  if (bids.length < 2) return { trend_direction: 'stable', trend_percentage: 0 };

  // Sort by publish date
  const sorted = [...bids].sort((a, b) =>
    new Date(a.publish_date).getTime() - new Date(b.publish_date).getTime()
  );

  // Split into first half and second half
  const midpoint = Math.floor(sorted.length / 2);
  const firstHalf = sorted.slice(0, midpoint);
  const secondHalf = sorted.slice(midpoint);

  const firstHalfCount = firstHalf.length;
  const secondHalfCount = secondHalf.length;

  // Calculate percentage change
  const change = ((secondHalfCount - firstHalfCount) / firstHalfCount) * 100;

  let trend_direction: 'rising' | 'falling' | 'stable';
  if (change > 10) trend_direction = 'rising';
  else if (change < -10) trend_direction = 'falling';
  else trend_direction = 'stable';

  return {
    trend_direction,
    trend_percentage: Math.abs(change)
  };
};

// ========================================
// UTILITY FUNCTIONS
// ========================================

const getDaysUntilClosing = (closingDate: string): number => {
  const now = new Date();
  const closing = new Date(closingDate);
  const diffTime = closing.getTime() - now.getTime();
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
};

/**
 * Get urgency color based on days
 */
export const getUrgencyColor = (days: number): string => {
  if (days <= 3) return 'text-red-600';
  if (days <= 7) return 'text-amber-600';
  return 'text-emerald-600';
};

/**
 * Get score color based on score (0-100)
 */
export const getScoreColor = (score: number): string => {
  if (score >= 80) return 'text-emerald-600';
  if (score >= 60) return 'text-amber-600';
  return 'text-slate-600';
};

/**
 * Get trend icon
 */
export const getTrendIcon = (direction: 'rising' | 'falling' | 'stable'): string => {
  if (direction === 'rising') return '↗';
  if (direction === 'falling') return '↘';
  return '→';
};

/**
 * Get trend color
 */
export const getTrendColor = (direction: 'rising' | 'falling' | 'stable'): string => {
  if (direction === 'rising') return 'text-emerald-600';
  if (direction === 'falling') return 'text-red-600';
  return 'text-slate-600';
};
