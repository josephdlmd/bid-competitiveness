import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FileText } from 'lucide-react';
import { formatCurrency, formatDate } from '@/utils/formatters';
import { fetchStats, fetchBids } from '@/services/api';
import { Bid, BidDocument } from '@/lib/types';
import { useTableSort, SortIcon } from '@/hooks/useTableSort';
import DocumentListModal from '@/components/DocumentListModal';
import PDFViewerModal from '@/components/PDFViewerModal';
import { enhanceBids } from '@/utils/bidEnhancer';

const DashboardPage = () => {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(true);
  const [stats, setStats] = useState({
    total_bids: 0,
    active_bids: 0,
    urgent_bids: 0,
    total_budget: 0,
  });
  const [recentBids, setRecentBids] = useState<Bid[]>([]);
  const [urgentBids, setUrgentBids] = useState<Bid[]>([]);

  // Document modals state
  const [selectedBid, setSelectedBid] = useState<Bid | null>(null);
  const [showDocumentList, setShowDocumentList] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState<BidDocument | null>(null);
  const [showPDFViewer, setShowPDFViewer] = useState(false);

  // Sorting for urgent bids table
  const {
    sortedData: sortedUrgentBids,
    requestSort: requestUrgentSort,
    getSortDirection: getUrgentSortDirection,
  } = useTableSort<Bid>(urgentBids, 'closing_date', 'asc');

  // Sorting for recent bids table
  const {
    sortedData: sortedRecentBids,
    requestSort: requestRecentSort,
    getSortDirection: getRecentSortDirection,
  } = useTableSort<Bid>(recentBids, 'closing_date', 'asc');

  useEffect(() => {
    loadDashboardData();
  }, []);

  const getDaysUntilClosing = (closingDate: string): number => {
    const now = new Date();
    const closing = new Date(closingDate);
    const diffTime = closing.getTime() - now.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  const getUrgencyColor = (days: number): string => {
    if (days <= 3) return 'text-red-600';
    if (days <= 7) return 'text-amber-600';
    return 'text-emerald-600';
  };

  const loadDashboardData = async () => {
    setIsLoading(true);
    try {
      const [statsData, bidsData] = await Promise.all([
        fetchStats(),
        fetchBids({ limit: 50, offset: 0 })
      ]);

      // Enhance bids with region data
      const enhancedBids = enhanceBids(bidsData.data);

      // Calculate urgent bids from the fetched data
      const urgent = enhancedBids.filter((bid: Bid) => {
        const daysUntil = getDaysUntilClosing(bid.closing_date);
        return daysUntil <= 7 && daysUntil > 0;
      }).slice(0, 10);

      setStats({
        total_bids: statsData.total_bids || 0,
        active_bids: statsData.active_bids || 0,
        urgent_bids: urgent.length,
        total_budget: statsData.total_budget || 0,
      });

      setUrgentBids(urgent);
      setRecentBids(enhancedBids.slice(0, 20));
    } catch (err) {
      console.error('Error loading dashboard data:', err);
      setStats({ total_bids: 0, active_bids: 0, urgent_bids: 0, total_budget: 0 });
      setRecentBids([]);
      setUrgentBids([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleOpenDocuments = (bid: Bid, e: React.MouseEvent) => {
    e.stopPropagation();
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
      {/* Stats Bar */}
      <div className="border-b border-slate-200 px-6 py-2 bg-white">
        <div className="flex items-center space-x-6 text-sm">
          <div>
            <span className="text-slate-600">Total: </span>
            <span className="font-semibold text-slate-900">
              {isLoading ? '...' : stats.total_bids.toLocaleString()}
            </span>
          </div>
          <div>
            <span className="text-slate-600">Active: </span>
            <span className="font-semibold text-slate-900">
              {isLoading ? '...' : stats.active_bids.toLocaleString()}
            </span>
          </div>
          <div>
            <span className="text-slate-600">Urgent (≤7 days): </span>
            <span className="font-semibold text-red-600">
              {isLoading ? '...' : stats.urgent_bids}
            </span>
          </div>
          <div>
            <span className="text-slate-600">Total Budget: </span>
            <span className="font-semibold text-slate-900">
              {isLoading ? '...' : formatCurrency(stats.total_budget)}
            </span>
          </div>
        </div>
      </div>

      {/* Urgent Bids Section */}
      {urgentBids.length > 0 && (
        <div className="border-b border-slate-200">
          <div className="px-6 py-3 bg-slate-50 border-b border-slate-200">
            <span className="text-sm font-semibold text-slate-900">
              Closing Soon ({urgentBids.length})
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="border-b border-slate-200 text-left">
                <tr className="text-xs text-slate-500 uppercase">
                  <th
                    className="px-6 py-3 font-medium cursor-pointer hover:bg-slate-50 select-none"
                    onClick={() => requestUrgentSort('closing_date')}
                  >
                    Days
                    <SortIcon direction={getUrgentSortDirection('closing_date')} />
                  </th>
                  <th
                    className="px-6 py-3 font-medium cursor-pointer hover:bg-slate-50 select-none"
                    onClick={() => requestUrgentSort('reference_number')}
                  >
                    Reference
                    <SortIcon direction={getUrgentSortDirection('reference_number')} />
                  </th>
                  <th
                    className="px-6 py-3 font-medium cursor-pointer hover:bg-slate-50 select-none"
                    onClick={() => requestUrgentSort('title')}
                  >
                    Title
                    <SortIcon direction={getUrgentSortDirection('title')} />
                  </th>
                  <th
                    className="px-6 py-3 font-medium cursor-pointer hover:bg-slate-50 select-none"
                    onClick={() => requestUrgentSort('procuring_entity')}
                  >
                    Procuring Entity
                    <SortIcon direction={getUrgentSortDirection('procuring_entity')} />
                  </th>
                  <th
                    className="px-6 py-3 font-medium cursor-pointer hover:bg-slate-50 select-none"
                    onClick={() => requestUrgentSort('administrative_region')}
                  >
                    Region
                    <SortIcon direction={getUrgentSortDirection('administrative_region')} />
                  </th>
                  <th
                    className="px-6 py-3 font-medium text-right cursor-pointer hover:bg-slate-50 select-none"
                    onClick={() => requestUrgentSort('approved_budget')}
                  >
                    Budget
                    <SortIcon direction={getUrgentSortDirection('approved_budget')} />
                  </th>
                  <th className="px-6 py-3 font-medium text-center">
                    Docs
                  </th>
                  <th
                    className="px-6 py-3 font-medium text-right cursor-pointer hover:bg-slate-50 select-none"
                    onClick={() => requestUrgentSort('closing_date')}
                  >
                    Closing Date
                    <SortIcon direction={getUrgentSortDirection('closing_date')} />
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {sortedUrgentBids.map((bid) => {
                  const daysUntil = getDaysUntilClosing(bid.closing_date);
                  return (
                    <tr
                      key={bid.reference_number}
                      className="hover:bg-slate-50 text-sm transition-colors cursor-pointer"
                      onClick={() => navigate(`/bids?selected=${bid.id}`)}
                    >
                      <td className="px-6 py-4">
                        <span className={`font-semibold ${getUrgencyColor(daysUntil)}`}>
                          {daysUntil}d
                        </span>
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
                      <td className="px-6 py-4 text-right font-medium text-slate-900">
                        {formatCurrency(bid.approved_budget)}
                      </td>
                      <td className="px-6 py-4 text-center">
                        {bid.documents && bid.documents.length > 0 ? (
                          <button
                            onClick={(e) => handleOpenDocuments(bid, e)}
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
        </div>
      )}

      {/* Recent Bids Section */}
      <div>
        <div className="px-6 py-3 bg-slate-50 border-b border-slate-200">
          <span className="text-sm text-slate-600">
            {isLoading ? 'Loading...' : `${recentBids.length} recent opportunities`}
          </span>
        </div>

        {isLoading ? (
          <div className="px-6 py-16 text-center">
            <p className="text-sm text-slate-500">Loading bids...</p>
          </div>
        ) : recentBids.length === 0 ? (
          <div className="px-6 py-16 text-center">
            <p className="text-sm text-slate-500">No bids available</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="border-b border-slate-200 text-left">
                <tr className="text-xs text-slate-500 uppercase">
                  <th
                    className="px-6 py-3 font-medium cursor-pointer hover:bg-slate-50 select-none"
                    onClick={() => requestRecentSort('closing_date')}
                  >
                    Days
                    <SortIcon direction={getRecentSortDirection('closing_date')} />
                  </th>
                  <th
                    className="px-6 py-3 font-medium cursor-pointer hover:bg-slate-50 select-none"
                    onClick={() => requestRecentSort('reference_number')}
                  >
                    Reference
                    <SortIcon direction={getRecentSortDirection('reference_number')} />
                  </th>
                  <th
                    className="px-6 py-3 font-medium cursor-pointer hover:bg-slate-50 select-none"
                    onClick={() => requestRecentSort('title')}
                  >
                    Title
                    <SortIcon direction={getRecentSortDirection('title')} />
                  </th>
                  <th
                    className="px-6 py-3 font-medium cursor-pointer hover:bg-slate-50 select-none"
                    onClick={() => requestRecentSort('procuring_entity')}
                  >
                    Procuring Entity
                    <SortIcon direction={getRecentSortDirection('procuring_entity')} />
                  </th>
                  <th
                    className="px-6 py-3 font-medium cursor-pointer hover:bg-slate-50 select-none"
                    onClick={() => requestRecentSort('administrative_region')}
                  >
                    Region
                    <SortIcon direction={getRecentSortDirection('administrative_region')} />
                  </th>
                  <th
                    className="px-6 py-3 font-medium cursor-pointer hover:bg-slate-50 select-none"
                    onClick={() => requestRecentSort('classification')}
                  >
                    Classification
                    <SortIcon direction={getRecentSortDirection('classification')} />
                  </th>
                  <th
                    className="px-6 py-3 font-medium text-right cursor-pointer hover:bg-slate-50 select-none"
                    onClick={() => requestRecentSort('approved_budget')}
                  >
                    Budget
                    <SortIcon direction={getRecentSortDirection('approved_budget')} />
                  </th>
                  <th className="px-6 py-3 font-medium text-center">
                    Docs
                  </th>
                  <th
                    className="px-6 py-3 font-medium text-right cursor-pointer hover:bg-slate-50 select-none"
                    onClick={() => requestRecentSort('closing_date')}
                  >
                    Closing Date
                    <SortIcon direction={getRecentSortDirection('closing_date')} />
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {sortedRecentBids.map((bid) => {
                  const daysUntil = getDaysUntilClosing(bid.closing_date);
                  return (
                    <tr
                      key={bid.reference_number}
                      className="hover:bg-slate-50 text-sm transition-colors cursor-pointer"
                      onClick={() => navigate(`/bids?selected=${bid.id}`)}
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
                            onClick={(e) => handleOpenDocuments(bid, e)}
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
        )}
      </div>

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

export default DashboardPage;
