import { useState, useEffect } from 'react';
import { FileText } from 'lucide-react';
import { formatCurrency, formatDate } from '@/utils/formatters';
import { fetchBids } from '@/services/api';
import { Bid, BidDocument } from '@/lib/types';
import { Pagination } from '@/components/ui';
import { usePagination } from '@/hooks/usePagination';
import { useTableSort, SortIcon } from '@/hooks/useTableSort';
import DocumentListModal from '@/components/DocumentListModal';
import PDFViewerModal from '@/components/PDFViewerModal';
import { enhanceBids } from '@/utils/bidEnhancer';
import { getAllRegions } from '@/utils/regionMapping';

const BidSearchPage = () => {
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
  const [minBudget, setMinBudget] = useState('');
  const [maxBudget, setMaxBudget] = useState('');

  // Sorting with the new hook
  const {
    sortedData: processedBids,
    requestSort,
    getSortDirection,
  } = useTableSort<Bid>(bids, 'closing_date', 'asc');

  useEffect(() => {
    loadBids();
  }, [currentPage, itemsPerPage]);

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

  const handleSearch = () => {
    resetPagination();
    loadBids();
  };

  const handleClearFilters = () => {
    setSearch('');
    setClassification('');
    setRegion('');
    setMinBudget('');
    setMaxBudget('');
    resetPagination();
    loadBids();
  };

  // Client-side region filtering
  const filteredByRegion = region
    ? processedBids.filter(bid => bid.region_code === region)
    : processedBids;

  const totalPages = Math.ceil(totalBids / itemsPerPage);

  const exportCSV = () => {
    const csv = [
      ['Reference', 'Title', 'Entity', 'Region', 'Location', 'Budget', 'Closing Date', 'Days Left'],
      ...filteredByRegion.map(bid => [
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
      {/* Filters Bar */}
      <div className="border-b border-slate-200 px-6 py-3 bg-white">
        <div className="flex items-center space-x-4">
          <input
            type="text"
            placeholder="Search by title, reference, or entity..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            className="flex-1 px-3 py-1.5 text-sm border border-slate-200 rounded-lg focus:outline-none focus:border-slate-400"
          />

          <select
            value={classification}
            onChange={(e) => setClassification(e.target.value)}
            className="px-3 py-1.5 text-sm border border-slate-200 rounded-lg focus:outline-none focus:border-slate-400"
          >
            <option value="">All Classifications</option>
            <option value="Goods">Goods</option>
            <option value="Consulting Services">Consulting Services</option>
            <option value="Infrastructure">Infrastructure</option>
          </select>

          <select
            value={region}
            onChange={(e) => setRegion(e.target.value)}
            className="px-3 py-1.5 text-sm border border-slate-200 rounded-lg focus:outline-none focus:border-slate-400"
          >
            <option value="">All Regions</option>
            {getAllRegions().map((r) => (
              <option key={r.code} value={r.code}>
                {r.name}
              </option>
            ))}
          </select>

          <input
            type="number"
            placeholder="Min Budget"
            value={minBudget}
            onChange={(e) => setMinBudget(e.target.value)}
            className="w-32 px-3 py-1.5 text-sm border border-slate-200 rounded-lg focus:outline-none focus:border-slate-400"
          />

          <input
            type="number"
            placeholder="Max Budget"
            value={maxBudget}
            onChange={(e) => setMaxBudget(e.target.value)}
            className="w-32 px-3 py-1.5 text-sm border border-slate-200 rounded-lg focus:outline-none focus:border-slate-400"
          />

          <button
            onClick={handleSearch}
            className="px-4 py-1.5 text-sm font-medium text-white bg-slate-900 rounded-lg hover:bg-slate-800"
          >
            Search
          </button>

          <button
            onClick={handleClearFilters}
            className="px-4 py-1.5 text-sm text-slate-600 hover:text-slate-900"
          >
            Clear
          </button>

          <button
            onClick={exportCSV}
            className="px-4 py-1.5 text-sm text-slate-600 hover:text-slate-900"
          >
            Export CSV
          </button>
        </div>
      </div>

      {/* Summary Bar */}
      <div className="px-6 py-3 bg-slate-50 border-b border-slate-200">
        <span className="text-sm text-slate-600">
          {isLoading ? 'Loading...' : region
            ? `${filteredByRegion.length.toLocaleString()} of ${totalBids.toLocaleString()} opportunities (filtered by region)`
            : `${totalBids.toLocaleString()} opportunities`}
        </span>
      </div>

      {/* Table */}
      {isLoading ? (
        <div className="px-6 py-16 text-center">
          <p className="text-sm text-slate-500">Loading bids...</p>
        </div>
      ) : filteredByRegion.length === 0 ? (
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
                {filteredByRegion.map((bid) => {
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

export default BidSearchPage;
