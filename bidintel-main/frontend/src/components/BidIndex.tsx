import { useState, useEffect, useCallback, useRef } from 'react';
import { FileText, Filter, Search, Building2, MapPin, Layers, DollarSign, X } from 'lucide-react';
import { formatCurrency, formatDate } from '../utils/formatters';
import { fetchBids } from '../services/api';
import { Bid, BidDocument, BidFilters } from '../lib/types';
import { Pagination } from './ui/pagination';
import { usePagination } from '../hooks/usePagination';
import { useTableSort, SortIcon } from '../hooks/useTableSort';
import DocumentListModal from './DocumentListModal';
import PDFViewerModal from './PDFViewerModal';
import { enhanceBids } from '../utils/bidEnhancer';
import { getAllRegions } from '../utils/regionMapping';
import { SavedSearchesPanel } from './SavedSearchesPanel';

const BidIndex = () => {
  const [bids, setBids] = useState<Bid[]>([]);
  const [totalBids, setTotalBids] = useState(0);
  const [isLoading, setIsLoading] = useState(true);

  // Document modals state
  const [selectedBid, setSelectedBid] = useState<Bid | null>(null);
  const [showDocumentList, setShowDocumentList] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState<BidDocument | null>(null);
  const [showPDFViewer, setShowPDFViewer] = useState(false);

  // Pagination
  const {
    currentPage,
    itemsPerPage,
    setCurrentPage,
    setItemsPerPage,
    resetPagination,
    getOffset,
  } = usePagination({ defaultItemsPerPage: 50 });

  // Filters
  const [search, setSearch] = useState('');
  const [classification, setClassification] = useState('');
  const [region, setRegion] = useState('');
  const [procuringEntity, setProcuringEntity] = useState('');
  const [minBudget, setMinBudget] = useState('');
  const [maxBudget, setMaxBudget] = useState('');

  // Debounce timer for text inputs
  const debounceTimer = useRef<NodeJS.Timeout | null>(null);
  const isInitialMount = useRef(true);

  // Sorting with the new hook
  const {
    sortedData: processedBids,
    requestSort,
    getSortDirection,
  } = useTableSort<Bid>(bids, 'closing_date', 'asc');

  useEffect(() => {
    loadBids();
  }, [currentPage, itemsPerPage]);

  // Auto-load when dropdown filters change (instant)
  useEffect(() => {
    // Skip on initial mount
    if (isInitialMount.current) {
      return;
    }
    resetPagination();
    loadBids();
  }, [classification, region]);

  // Auto-load when text/number filters change (debounced)
  useEffect(() => {
    // Skip on initial mount, but mark that we've mounted
    if (isInitialMount.current) {
      isInitialMount.current = false;
      return;
    }

    // Clear existing timer
    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current);
    }

    // Set new timer for debounced search
    debounceTimer.current = setTimeout(() => {
      resetPagination();
      loadBids();
    }, 500); // 500ms debounce

    // Cleanup on unmount or when dependencies change
    return () => {
      if (debounceTimer.current) {
        clearTimeout(debounceTimer.current);
      }
    };
  }, [search, procuringEntity, minBudget, maxBudget]);

  const getDaysUntilClosing = (closingDate: string): number => {
    const now = new Date();
    const closing = new Date(closingDate);
    const diffTime = closing.getTime() - now.getTime();
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  };

  const getUrgencyColor = (days: number): string => {
    if (days <= 3) return 'text-red-600';
    if (days <= 7) return 'text-amber-600';
    return 'text-emerald-600';
  };

  const loadBids = async () => {
    setIsLoading(true);
    try {
      const response = await fetchBids({
        search: search || undefined,
        classification: classification || undefined,
        min_budget: minBudget ? parseInt(minBudget) : undefined,
        max_budget: maxBudget ? parseInt(maxBudget) : undefined,
        limit: itemsPerPage,
        offset: getOffset()
      });
      // Enhance bids with region data
      const enhancedBids = enhanceBids(response.data);
      setBids(enhancedBids);
      setTotalBids(response.total);
    } catch (err) {
      console.error('Error loading bids:', err);
      setBids([]);
      setTotalBids(0);
    } finally {
      setIsLoading(false);
    }
  };

  // Get current filters as BidFilters object
  const getCurrentFilters = (): BidFilters => ({
    search: search || undefined,
    classification: classification || undefined,
    region: region || undefined,
    procuring_entity: procuringEntity || undefined,
    min_budget: minBudget ? parseInt(minBudget) : undefined,
    max_budget: maxBudget ? parseInt(maxBudget) : undefined,
  });

  // Apply saved search filters
  const handleApplySavedSearch = (filters: BidFilters) => {
    setSearch(filters.search || '');
    setClassification(filters.classification || '');
    setRegion(filters.region || '');
    setProcuringEntity(filters.procuring_entity || '');
    setMinBudget(filters.min_budget ? String(filters.min_budget) : '');
    setMaxBudget(filters.max_budget ? String(filters.max_budget) : '');
    resetPagination();
    // loadBids will be called by useEffect when filters change
    setTimeout(() => loadBids(), 100);
  };

  const handleSearch = () => {
    resetPagination();
    loadBids();
  };

  const handleClearFilters = () => {
    setSearch('');
    setClassification('');
    setRegion('');
    setProcuringEntity('');
    setMinBudget('');
    setMaxBudget('');
    resetPagination();
    loadBids();
  };

  // Client-side filtering for region and procuring entity (since backend doesn't support them yet)
  const filteredBids = processedBids.filter(bid => {
    // Handle region filtering including "Unknown"
    if (region) {
      if (region === 'UNKNOWN') {
        if (bid.region_code && bid.region_code !== '') return false;
      } else {
        if (bid.region_code !== region) return false;
      }
    }
    if (procuringEntity && !bid.procuring_entity.toLowerCase().includes(procuringEntity.toLowerCase())) return false;
    return true;
  });

  const totalPages = Math.ceil(totalBids / itemsPerPage);

  const exportCSV = () => {
    const csv = [
      ['Reference', 'Title', 'Entity', 'Region', 'Location', 'Budget', 'Closing Date', 'Days Left'],
      ...filteredBids.map(bid => [
        bid.reference_number,
        `"${bid.title.replace(/"/g, '""')}"`,
        `"${bid.procuring_entity.replace(/"/g, '""')}"`,
        `"${bid.administrative_region || 'Unknown'}"`,
        `"${bid.delivery_location || 'N/A'}"`,
        bid.approved_budget,
        bid.closing_date,
        getDaysUntilClosing(bid.closing_date)
      ])
    ].map(row => row.join(',')).join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `philgeps_bids_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
  };

  const handleOpenDocuments = (bid: Bid) => {
    setSelectedBid(bid);
    setShowDocumentList(true);
  };

  const handlePreviewDocument = (document: BidDocument) => {
    setSelectedDocument(document);
    setShowDocumentList(false);
    setShowPDFViewer(true);
  };

  const handleClosePDFViewer = (open: boolean) => {
    setShowPDFViewer(open);
    if (!open) {
      // Return to document list if we came from there
      setTimeout(() => {
        if (selectedBid) {
          setShowDocumentList(true);
        }
      }, 100);
    }
  };

  return (
    <div>
      {/* Enhanced Filters Bar */}
      <div className="bg-gradient-to-r from-slate-50 to-slate-100 border-b-2 border-slate-300 px-6 py-4">
        <div className="space-y-4">
          {/* Filter Header */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Filter className="w-5 h-5 text-slate-700" />
              <div>
                <h3 className="text-base font-semibold text-slate-900">Filter Bids</h3>
                <p className="text-xs text-slate-500 mt-0.5">Search updates automatically as you type or select</p>
              </div>
            </div>
            {(search || classification || region || procuringEntity || minBudget || maxBudget) && (
              <button
                onClick={handleClearFilters}
                className="inline-flex items-center space-x-1 px-3 py-1.5 text-sm font-medium text-red-600 bg-red-50 rounded-lg hover:bg-red-100 transition-colors"
              >
                <X className="w-4 h-4" />
                <span>Clear All Filters</span>
              </button>
            )}
          </div>

          {/* Row 1: Main Search and Dropdowns */}
          <div className="flex items-center space-x-3">
            <div className="relative w-80">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
              <input
                type="text"
                placeholder="Search by title or reference..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                className="w-full pl-10 pr-3 py-2.5 text-sm border-2 border-slate-300 rounded-lg focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200 bg-white shadow-sm"
              />
            </div>

            <div className="relative min-w-[280px] flex-1">
              <Layers className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none z-10" />
              <select
                value={classification}
                onChange={(e) => setClassification(e.target.value)}
                className="w-full pl-10 pr-3 py-2.5 text-sm font-medium border-2 border-slate-300 rounded-lg focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200 bg-white shadow-sm appearance-none cursor-pointer"
              >
                <option value="">All Classifications</option>
                <option value="Goods">Goods</option>
                <option value="Goods - General Support Services">Goods - General Support Services</option>
                <option value="Consulting Services">Consulting Services</option>
                <option value="Civil Works - Infra Project">Civil Works - Infra Project</option>
              </select>
            </div>

            <div className="relative min-w-[280px] flex-1">
              <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none z-10" />
              <select
                value={region}
                onChange={(e) => setRegion(e.target.value)}
                className="w-full pl-10 pr-3 py-2.5 text-sm font-medium border-2 border-slate-300 rounded-lg focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200 bg-white shadow-sm appearance-none cursor-pointer"
              >
                <option value="">All Regions</option>
                {getAllRegions().map((r) => (
                  <option key={r.code} value={r.code}>
                    {r.name}
                  </option>
                ))}
                <option value="UNKNOWN">Unknown Region</option>
              </select>
            </div>
          </div>

          {/* Row 2: Procuring Entity and Budget */}
          <div className="flex items-center space-x-3">
            <div className="relative w-80">
              <Building2 className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
              <input
                type="text"
                placeholder="Filter by entity (e.g., DepEd, DPWH)..."
                value={procuringEntity}
                onChange={(e) => setProcuringEntity(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                className="w-full pl-10 pr-3 py-2.5 text-sm border-2 border-slate-300 rounded-lg focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200 bg-white shadow-sm"
              />
            </div>

            <div className="relative w-40">
              <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
              <input
                type="number"
                placeholder="Min Budget"
                value={minBudget}
                onChange={(e) => setMinBudget(e.target.value)}
                className="w-full pl-10 pr-3 py-2.5 text-sm border-2 border-slate-300 rounded-lg focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200 bg-white shadow-sm"
              />
            </div>

            <div className="relative w-40">
              <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
              <input
                type="number"
                placeholder="Max Budget"
                value={maxBudget}
                onChange={(e) => setMaxBudget(e.target.value)}
                className="w-full pl-10 pr-3 py-2.5 text-sm border-2 border-slate-300 rounded-lg focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200 bg-white shadow-sm"
              />
            </div>

            <button
              onClick={handleSearch}
              className="inline-flex items-center space-x-2 px-5 py-2.5 text-sm font-medium text-slate-700 bg-white border-2 border-slate-300 rounded-lg hover:bg-slate-50 hover:border-slate-400 shadow-sm transition-all duration-200"
              title="Search updates automatically as you type"
            >
              <Search className="w-4 h-4" />
              <span>Refresh</span>
            </button>

            <button
              onClick={exportCSV}
              className="inline-flex items-center space-x-2 px-5 py-2.5 text-sm font-medium text-slate-700 bg-white border-2 border-slate-300 rounded-lg hover:bg-slate-50 hover:border-slate-400 shadow-sm transition-all duration-200"
            >
              <FileText className="w-4 h-4" />
              <span>Export</span>
            </button>
          </div>
        </div>
      </div>

      {/* Saved Searches Panel */}
      <SavedSearchesPanel
        currentFilters={getCurrentFilters()}
        onApplySearch={handleApplySavedSearch}
      />

      {/* Summary Bar */}
      <div className="px-6 py-3 bg-slate-50 border-b border-slate-200">
        <span className="text-sm text-slate-600">
          {isLoading ? 'Loading...' : (region || procuringEntity)
            ? `${filteredBids.length.toLocaleString()} of ${totalBids.toLocaleString()} opportunities (client-side filtered)`
            : `${totalBids.toLocaleString()} opportunities`}
        </span>
      </div>

      {/* Table */}
      {isLoading ? (
        <div className="px-6 py-16 text-center">
          <p className="text-sm text-slate-500">Loading bids...</p>
        </div>
      ) : filteredBids.length === 0 ? (
        <div className="px-6 py-16 text-center">
          <p className="text-sm text-slate-500">No bids found</p>
          <p className="text-xs text-slate-400 mt-1">Try adjusting your filters</p>
        </div>
      ) : (
        <>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="border-b border-slate-200 text-left">
                <tr className="text-xs text-slate-500 uppercase">
                  <th
                    className="px-6 py-3 font-medium cursor-pointer hover:bg-slate-50 select-none"
                    onClick={() => requestSort('closing_date')}
                  >
                    Days
                    <SortIcon direction={getSortDirection('closing_date')} />
                  </th>
                  <th
                    className="px-6 py-3 font-medium cursor-pointer hover:bg-slate-50 select-none"
                    onClick={() => requestSort('reference_number')}
                  >
                    Reference
                    <SortIcon direction={getSortDirection('reference_number')} />
                  </th>
                  <th
                    className="px-6 py-3 font-medium cursor-pointer hover:bg-slate-50 select-none"
                    onClick={() => requestSort('title')}
                  >
                    Title
                    <SortIcon direction={getSortDirection('title')} />
                  </th>
                  <th
                    className="px-6 py-3 font-medium cursor-pointer hover:bg-slate-50 select-none"
                    onClick={() => requestSort('procuring_entity')}
                  >
                    Procuring Entity
                    <SortIcon direction={getSortDirection('procuring_entity')} />
                  </th>
                  <th
                    className="px-6 py-3 font-medium cursor-pointer hover:bg-slate-50 select-none"
                    onClick={() => requestSort('administrative_region')}
                  >
                    Region
                    <SortIcon direction={getSortDirection('administrative_region')} />
                  </th>
                  <th
                    className="px-6 py-3 font-medium cursor-pointer hover:bg-slate-50 select-none"
                    onClick={() => requestSort('classification')}
                  >
                    Classification
                    <SortIcon direction={getSortDirection('classification')} />
                  </th>
                  <th
                    className="px-6 py-3 font-medium text-right cursor-pointer hover:bg-slate-50 select-none"
                    onClick={() => requestSort('approved_budget')}
                  >
                    Budget
                    <SortIcon direction={getSortDirection('approved_budget')} />
                  </th>
                  <th className="px-6 py-3 font-medium text-center">
                    Docs
                  </th>
                  <th
                    className="px-6 py-3 font-medium text-right cursor-pointer hover:bg-slate-50 select-none"
                    onClick={() => requestSort('closing_date')}
                  >
                    Closing Date
                    <SortIcon direction={getSortDirection('closing_date')} />
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredBids.map((bid) => {
                  const daysUntil = getDaysUntilClosing(bid.closing_date);
                  return (
                    <tr
                      key={bid.reference_number}
                      className="hover:bg-slate-50 text-sm transition-colors"
                    >
                      <td className="px-6 py-4">
                        {daysUntil > 0 ? (
                          <span className={`font-semibold ${getUrgencyColor(daysUntil)}`}>
                            {daysUntil}d
                          </span>
                        ) : (
                          <span className="text-slate-400">Closed</span>
                        )}
                      </td>
                      <td className="px-6 py-4 font-mono text-xs text-slate-600">
                        {bid.reference_number}
                      </td>
                      <td className="px-6 py-4 font-medium text-slate-900">
                        {bid.title}
                      </td>
                      <td className="px-6 py-4 text-slate-600">
                        {bid.procuring_entity}
                      </td>
                      <td className="px-6 py-4 text-slate-600">
                        {bid.administrative_region || 'Unknown'}
                      </td>
                      <td className="px-6 py-4 text-slate-500">
                        {bid.classification}
                      </td>
                      <td className="px-6 py-4 text-right font-medium text-slate-900">
                        {formatCurrency(bid.approved_budget)}
                      </td>
                      <td className="px-6 py-4 text-center">
                        {bid.documents && bid.documents.length > 0 ? (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleOpenDocuments(bid);
                            }}
                            className="inline-flex items-center space-x-1 px-2 py-1 text-xs font-medium text-emerald-700 bg-emerald-50 rounded-md hover:bg-emerald-100 transition-colors"
                          >
                            <FileText className="w-3 h-3" />
                            <span>({bid.documents.length})</span>
                          </button>
                        ) : (
                          <span className="text-xs text-slate-400">--</span>
                        )}
                      </td>
                      <td className="px-6 py-4 text-right text-slate-600">
                        {formatDate(bid.closing_date)}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            totalItems={totalBids}
            itemsPerPage={itemsPerPage}
            onPageChange={setCurrentPage}
            onItemsPerPageChange={setItemsPerPage}
          />
        </>
      )}

      {/* Document Modals */}
      <DocumentListModal
        open={showDocumentList}
        onOpenChange={setShowDocumentList}
        documents={selectedBid?.documents || []}
        bidReference={selectedBid?.reference_number || ''}
        onPreview={handlePreviewDocument}
      />
      <PDFViewerModal
        open={showPDFViewer}
        onOpenChange={handleClosePDFViewer}
        document={selectedDocument}
      />
    </div>
  );
};

export default BidIndex;
