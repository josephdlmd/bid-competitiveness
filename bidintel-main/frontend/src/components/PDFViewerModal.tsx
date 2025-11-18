import { FileText, Download, ExternalLink, X } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogClose } from '@/components/ui';
import { BidDocument } from '@/lib/types';

interface PDFViewerModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  document: BidDocument | null;
}

const PDFViewerModal = ({ open, onOpenChange, document }: PDFViewerModalProps) => {
  if (!document) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-6xl max-h-[95vh] h-[95vh] flex flex-col p-0">
        <DialogHeader className="px-6 py-4 border-b border-slate-200 flex-shrink-0">
          <div className="flex items-center space-x-2 flex-1 min-w-0">
            <FileText className="w-5 h-5 text-slate-600 flex-shrink-0" />
            <DialogTitle className="truncate">
              {document.filename || 'PDF Document'}
            </DialogTitle>
          </div>
          <div className="flex items-center space-x-2">
            <a
              href={document.document_url}
              download
              className="p-2 text-slate-600 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
              title="Download PDF"
            >
              <Download className="w-4 h-4" />
            </a>
            <a
              href={document.document_url}
              target="_blank"
              rel="noopener noreferrer"
              className="p-2 text-slate-600 hover:text-purple-600 hover:bg-purple-50 rounded-lg transition-colors"
              title="Open in New Tab"
            >
              <ExternalLink className="w-4 h-4" />
            </a>
            <DialogClose onClose={() => onOpenChange(false)} />
          </div>
        </DialogHeader>

        <div className="flex-1 overflow-hidden">
          <iframe
            src={`${document.document_url}#toolbar=1&navpanes=1&scrollbar=1`}
            className="w-full h-full border-0"
            title={document.filename || 'PDF Document'}
          />
        </div>

        <div className="px-6 py-3 border-t border-slate-200 bg-slate-50 flex-shrink-0">
          <p className="text-xs text-slate-500">
            {document.document_type && (
              <span className="font-medium">{document.document_type} • </span>
            )}
            {document.file_size && (
              <span>
                {(document.file_size / (1024 * 1024)).toFixed(1)} MB
              </span>
            )}
            {!document.file_size && !document.document_type && (
              <span>PDF Document</span>
            )}
          </p>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default PDFViewerModal;
