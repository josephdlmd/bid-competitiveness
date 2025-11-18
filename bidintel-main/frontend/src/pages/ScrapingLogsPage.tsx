import { useState, useEffect } from 'react';
import { Activity, CheckCircle, XCircle, Clock, RefreshCw } from 'lucide-react';
import { Button, Table, TableBody, TableCell, TableHead, TableHeader, TableRow, Badge, Pagination } from '@/components/ui';
import { formatDate } from '@/utils/formatters';
import { useApp } from '@/context/AppContext';
import { fetchLogs } from '@/services/api';
import { usePagination } from '@/hooks/usePagination';
import { useTableSort, SortIcon } from '@/hooks/useTableSort';

interface ScraperLog {
  id: string;
  timestamp: string;
  status: 'success' | 'error' | 'running';
  bids_scraped: number;
  duration: number;
  message: string;
}

const ScrapingLogsPage = () => {
  const { addNotification } = useApp();
  const [logs, setLogs] = useState<ScraperLog[]>([]);
  const [totalLogs, setTotalLogs] = useState(0);
  const [isLoading, setIsLoading] = useState(true);

  // Pagination
  const {
    currentPage,
    itemsPerPage,
    setCurrentPage,
    setItemsPerPage,
    getOffset,
  } = usePagination({ defaultItemsPerPage: 50 });

  // Sorting for logs table
  const {
    sortedData: sortedLogs,
    requestSort,
    getSortDirection,
  } = useTableSort<ScraperLog>(logs, 'timestamp', 'desc');

  useEffect(() => {
    loadLogs();
  }, [currentPage, itemsPerPage]);

  const loadLogs = async () => {
    setIsLoading(true);
    try {
      const response = await fetchLogs(itemsPerPage, getOffset());
      setLogs(response.data || []);
      setTotalLogs(response.total || 0);
    } catch (err) {
      console.error('Error loading logs:', err);
      addNotification('Failed to load scraping logs', 'error');
      setLogs([]);
      setTotalLogs(0);
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusIcon = (status: ScraperLog['status']) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="w-4 h-4 text-emerald-600" />;
      case 'error':
        return <XCircle className="w-4 h-4 text-red-600" />;
      case 'running':
        return <Clock className="w-4 h-4 text-amber-600 animate-spin" />;
    }
  };

  const getStatusBadge = (status: ScraperLog['status']) => {
    switch (status) {
      case 'success':
        return <Badge variant="success">Success</Badge>;
      case 'error':
        return <Badge variant="destructive">Error</Badge>;
      case 'running':
        return <Badge variant="warning">Running</Badge>;
    }
  };

  return (
    <div className="max-w-[1400px]">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-lg font-semibold text-slate-900 flex items-center">
          <Activity className="w-5 h-5 mr-2" />
          Scraping Logs
        </h1>
        <Button variant="outline" size="sm" onClick={loadLogs}>
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Logs Table */}
      <div className="bg-white border border-slate-200 rounded-lg">
        <div className="px-6 py-2 border-b border-slate-200 bg-slate-50">
          <div className="flex items-center justify-between text-sm">
            <span className="text-slate-600">
              {isLoading ? 'Loading...' : `${totalLogs.toLocaleString()} log entries`}
            </span>
          </div>
        </div>

        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-10"></TableHead>
                <TableHead
                  className="cursor-pointer hover:bg-slate-50 select-none"
                  onClick={() => requestSort('timestamp')}
                >
                  Timestamp
                  <SortIcon direction={getSortDirection('timestamp')} />
                </TableHead>
                <TableHead
                  className="cursor-pointer hover:bg-slate-50 select-none"
                  onClick={() => requestSort('status')}
                >
                  Status
                  <SortIcon direction={getSortDirection('status')} />
                </TableHead>
                <TableHead
                  className="text-right cursor-pointer hover:bg-slate-50 select-none"
                  onClick={() => requestSort('bids_scraped')}
                >
                  Bids Scraped
                  <SortIcon direction={getSortDirection('bids_scraped')} />
                </TableHead>
                <TableHead
                  className="text-right cursor-pointer hover:bg-slate-50 select-none"
                  onClick={() => requestSort('duration')}
                >
                  Duration (s)
                  <SortIcon direction={getSortDirection('duration')} />
                </TableHead>
                <TableHead
                  className="cursor-pointer hover:bg-slate-50 select-none"
                  onClick={() => requestSort('message')}
                >
                  Message
                  <SortIcon direction={getSortDirection('message')} />
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-16 text-slate-500">
                    Loading...
                  </TableCell>
                </TableRow>
              ) : sortedLogs.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-16">
                    <p className="text-slate-500">No scraping logs found</p>
                  </TableCell>
                </TableRow>
              ) : (
                sortedLogs.map(log => (
                  <TableRow key={log.id}>
                    <TableCell>
                      {getStatusIcon(log.status)}
                    </TableCell>
                    <TableCell className="text-sm text-slate-900">
                      {formatDate(log.timestamp)}
                    </TableCell>
                    <TableCell>
                      {getStatusBadge(log.status)}
                    </TableCell>
                    <TableCell className="text-right font-medium text-slate-900">
                      {log.bids_scraped}
                    </TableCell>
                    <TableCell className="text-right text-slate-600">
                      {log.duration}
                    </TableCell>
                    <TableCell className="text-sm text-slate-600">
                      {log.message}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>

        {/* Pagination */}
        {!isLoading && totalLogs > 0 && (
          <Pagination
            currentPage={currentPage}
            totalPages={Math.ceil(totalLogs / itemsPerPage)}
            totalItems={totalLogs}
            itemsPerPage={itemsPerPage}
            onPageChange={setCurrentPage}
            onItemsPerPageChange={setItemsPerPage}
          />
        )}
      </div>
    </div>
  );
};

export default ScrapingLogsPage;
