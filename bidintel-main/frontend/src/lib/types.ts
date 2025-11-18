// TypeScript types for PhilGEPS Bid Intelligence App

export interface Bid {
  id: number;
  reference_number: string;
  control_number?: string;
  status?: string;
  title: string;
  procuring_entity: string;
  classification?: string;
  category?: string;
  procurement_mode?: string;
  procurement_rules?: string;
  lot_type?: string;
  approved_budget: number;
  bid_form_fee?: number;
  bid_validity_days?: number;
  publish_date?: string;
  closing_date: string;
  date_created?: string;
  date_last_updated?: string;
  description?: string;
  delivery_period?: string;
  delivery_location?: string;
  agency_address?: string;
  contact_person?: string;
  contact_email?: string;
  contact_phone?: string;
  created_by?: string;
  funding_source?: string;
  download_count?: number;

  // Enhanced fields from bidEnhancer
  region_code?: string;
  administrative_region?: string;
  province?: string;
  city_municipality?: string;

  // Relations
  line_items?: LineItem[];
  documents?: BidDocument[];
  activity_schedule?: ActivitySchedule[];
  bid_supplements?: BidSupplement[];
}

export interface LineItem {
  item_number?: number;
  unspsc_code?: string;
  lot_name?: string;
  lot_description?: string;
  quantity?: number;
  unit_of_measure?: string;
}

export interface ActivitySchedule {
  id: number;
  activity_type?: string;
  scheduled_date?: string;
  location?: string;
  description?: string;
}

export interface BidSupplement {
  id: number;
  supplement_number?: number;
  amendment_type?: string;
  description?: string;
  issued_date?: string;
}

export interface BidDocument {
  id: number;
  filename?: string;
  document_url: string;
  document_type?: string;
  file_size?: number;
  scraped_at?: string;
}

export interface ScrapingLog {
  id: number;
  start_time?: string;
  end_time?: string;
  duration_seconds?: number;
  total_scraped: number;
  new_records: number;
  errors: number;
  success: boolean;
  notes?: string;
  created_at?: string;
}

export interface Stats {
  total_bids: number;
  active_bids: number;
  total_budget: number;
  total_scraping_sessions: number;
}

export interface Analytics {
  status_counts: Record<string, number>;
  classification_counts: Record<string, number>;
  budget_by_classification: Record<string, number>;
  by_classification: Record<string, { count: number; total_budget: number }>;
  top_agencies: Array<{ name: string; count: number; total_budget: number }>;
  monthly_trend: Array<[string, { count: number; budget: number }]>;
}

export interface BidFilters {
  search?: string;
  status?: string;
  classification?: string;
  category?: string;
  region?: string;
  procuring_entity?: string;
  min_budget?: number;
  max_budget?: number;
  date_from?: string;
  date_to?: string;
  limit?: number;
  offset?: number;
}

export interface SavedSearch {
  id: string;
  name: string;
  filters: BidFilters;
  createdAt: string;
  lastUsed?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  limit: number;
  offset: number;
}
