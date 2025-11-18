/**
 * API service for PhilGEPS Dashboard
 * Handles all communication with the FastAPI backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

/**
 * Generic fetch wrapper with error handling
 */
async function apiFetch(endpoint, options = {}) {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`API Error [${endpoint}]:`, error);
    throw error;
  }
}

/**
 * Fetch all bids with optional filtering
 * @param {Object} filters - Filter parameters
 * @param {string} filters.status - Filter by status (Open, Closed, Evaluation, Published)
 * @param {string} filters.classification - Filter by classification (Goods, Services, Infrastructure)
 * @param {number} filters.min_budget - Minimum approved budget
 * @param {number} filters.max_budget - Maximum approved budget
 * @param {string} filters.date_from - Publish date from (ISO format)
 * @param {string} filters.date_to - Closing date to (ISO format)
 * @param {string} filters.search - Search in title, description, reference number
 * @param {number} filters.limit - Results per page (default: 100)
 * @param {number} filters.offset - Pagination offset
 * @returns {Promise<{data: Array, total: number, limit: number, offset: number}>}
 */
export async function fetchBids(filters = {}) {
  const params = new URLSearchParams();

  Object.keys(filters).forEach(key => {
    if (filters[key] !== null && filters[key] !== undefined && filters[key] !== '') {
      params.append(key, filters[key]);
    }
  });

  const queryString = params.toString();
  const endpoint = `/bids${queryString ? `?${queryString}` : ''}`;

  return await apiFetch(endpoint);
}

/**
 * Fetch a single bid by ID with full details
 * @param {number} id - Bid ID
 * @returns {Promise<Object>} Bid details with line items
 */
export async function fetchBid(id) {
  return await apiFetch(`/bids/${id}`);
}

/**
 * Fetch dashboard statistics
 * @returns {Promise<{total_bids: number, active_bids: number, total_budget: number, total_scraping_sessions: number}>}
 */
export async function fetchStats() {
  return await apiFetch('/stats');
}

/**
 * Fetch analytics data for charts
 * @param {string} timeRange - Time range: "7d", "30d", "90d", "all" (default: "30d")
 * @returns {Promise<{status_counts: Object, classification_counts: Object, budget_by_classification: Object, top_agencies: Array, monthly_trend: Array}>}
 */
export async function fetchAnalytics(timeRange = '30d') {
  return await apiFetch(`/analytics?time_range=${timeRange}`);
}

/**
 * Fetch scraping logs
 * @param {number} limit - Results per page (default: 50)
 * @param {number} offset - Pagination offset
 * @returns {Promise<{data: Array, total: number, limit: number, offset: number}>}
 */
export async function fetchLogs(limit = 50, offset = 0) {
  return await apiFetch(`/logs?limit=${limit}&offset=${offset}`);
}

/**
 * Health check endpoint
 * @returns {Promise<{status: string, timestamp: string}>}
 */
export async function healthCheck() {
  try {
    const response = await fetch(`${API_BASE_URL.replace('/api', '')}/health`);
    return await response.json();
  } catch (error) {
    console.error('Health check failed:', error);
    throw error;
  }
}

export default {
  fetchBids,
  fetchBid,
  fetchStats,
  fetchAnalytics,
  fetchLogs,
  healthCheck,
};
