import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from 'lucide-react';

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  totalItems: number;
  itemsPerPage: number;
  onPageChange: (page: number) => void;
  onItemsPerPageChange?: (itemsPerPage: number) => void;
  showPageSizeSelector?: boolean;
  pageSizeOptions?: number[];
  className?: string;
}

export const Pagination = ({
  currentPage,
  totalPages,
  totalItems,
  itemsPerPage,
  onPageChange,
  onItemsPerPageChange,
  showPageSizeSelector = true,
  pageSizeOptions = [25, 50, 100, 200],
  className = '',
}: PaginationProps) => {
  const startItem = totalItems === 0 ? 0 : (currentPage - 1) * itemsPerPage + 1;
  const endItem = Math.min(currentPage * itemsPerPage, totalItems);

  const handlePageInput = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      const value = parseInt((e.target as HTMLInputElement).value);
      if (value >= 1 && value <= totalPages) {
        onPageChange(value);
        (e.target as HTMLInputElement).blur();
      }
    }
  };

  const handleFirstPage = () => onPageChange(1);
  const handlePrevPage = () => onPageChange(Math.max(1, currentPage - 1));
  const handleNextPage = () => onPageChange(Math.min(totalPages, currentPage + 1));
  const handleLastPage = () => onPageChange(totalPages);

  return (
    <div className={`border-t border-slate-200 px-6 py-3 bg-white flex items-center justify-between ${className}`}>
      <div className="flex items-center gap-4">
        <span className="text-sm text-slate-600">
          {totalItems > 0 ? (
            <>
              Showing <span className="font-medium">{startItem.toLocaleString()}</span> to{' '}
              <span className="font-medium">{endItem.toLocaleString()}</span> of{' '}
              <span className="font-medium">{totalItems.toLocaleString()}</span>
            </>
          ) : (
            'No items'
          )}
        </span>

        {showPageSizeSelector && onItemsPerPageChange && (
          <div className="flex items-center gap-2">
            <span className="text-sm text-slate-600">Show:</span>
            <select
              value={itemsPerPage}
              onChange={(e) => onItemsPerPageChange(parseInt(e.target.value))}
              className="px-2 py-1 text-sm border border-slate-200 rounded focus:outline-none focus:border-slate-400 bg-white"
            >
              {pageSizeOptions.map((size) => (
                <option key={size} value={size}>
                  {size}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <span className="text-sm text-slate-600">Page</span>
          <input
            type="number"
            min={1}
            max={totalPages}
            defaultValue={currentPage}
            onKeyDown={handlePageInput}
            className="w-16 px-2 py-1 text-sm text-center border border-slate-200 rounded focus:outline-none focus:border-slate-400"
            disabled={totalPages === 0}
          />
          <span className="text-sm text-slate-600">of {totalPages}</span>
        </div>

        <div className="flex items-center gap-1">
          <button
            onClick={handleFirstPage}
            disabled={currentPage === 1 || totalPages === 0}
            className="p-1 border border-slate-200 rounded hover:bg-slate-50 disabled:opacity-30 disabled:cursor-not-allowed disabled:hover:bg-transparent transition-colors"
            title="First page"
          >
            <ChevronsLeft className="w-4 h-4 text-slate-600" />
          </button>
          <button
            onClick={handlePrevPage}
            disabled={currentPage === 1 || totalPages === 0}
            className="p-1 border border-slate-200 rounded hover:bg-slate-50 disabled:opacity-30 disabled:cursor-not-allowed disabled:hover:bg-transparent transition-colors"
            title="Previous page"
          >
            <ChevronLeft className="w-4 h-4 text-slate-600" />
          </button>
          <button
            onClick={handleNextPage}
            disabled={currentPage === totalPages || totalPages === 0}
            className="p-1 border border-slate-200 rounded hover:bg-slate-50 disabled:opacity-30 disabled:cursor-not-allowed disabled:hover:bg-transparent transition-colors"
            title="Next page"
          >
            <ChevronRight className="w-4 h-4 text-slate-600" />
          </button>
          <button
            onClick={handleLastPage}
            disabled={currentPage === totalPages || totalPages === 0}
            className="p-1 border border-slate-200 rounded hover:bg-slate-50 disabled:opacity-30 disabled:cursor-not-allowed disabled:hover:bg-transparent transition-colors"
            title="Last page"
          >
            <ChevronsRight className="w-4 h-4 text-slate-600" />
          </button>
        </div>
      </div>
    </div>
  );
};
