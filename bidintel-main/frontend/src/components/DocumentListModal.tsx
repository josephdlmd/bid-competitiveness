import { useState } from 'react';
import { FileText, Download, ExternalLink, Eye, X } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogClose, Badge } from '@/components/ui';
import { BidDocument } from '@/lib/types';

interface DocumentListModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  documents: BidDocument[];
  bidReference: string;
  onPreview: (document: BidDocument) => void;
}

const DocumentListModal = ({
  open,
  onOpenChange,
  documents,
  bidReference,
  onPreview,
}: DocumentListModalProps) => {
  const formatFileSize = (bytes: number | null): string => {
    if (!bytes) return 'Unknown size';
    const mb = bytes / (1024 * 1024);
    if (mb >= 1) return `${mb.toFixed(1)} MB`;
    const kb = bytes / 1024;
    return `${kb.toFixed(0)} KB`;
  };

  const getDocumentTypeBadge = (type: string | null) => {
    if (!type) return <Badge variant="outline">Document</Badge>;

    const typeColors: Record<string, string> = {
      'Bid Notice': 'bg-blue-100 text-blue-700',
      'Technical Specifications': 'bg-purple-100 text-purple-700',
      'TOR': 'bg-green-100 text-green-700',
      'Terms of Reference': 'bg-green-100 text-green-700',
      'Requirements': 'bg-amber-100 text-amber-700',
    };

    const colorClass = typeColors[type] || 'bg-slate-100 text-slate-700';

    return (
      <Badge variant="outline" className={`${colorClass} border-0`}>
        {type}
      </Badge>
    );
  };

  if (documents.length === 0) {
    return (
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <div className="flex items-center space-x-2">
              <FileText className="w-5 h-5 text-slate-600" />
              <DialogTitle>Documents - {bidReference}</DialogTitle>
            </div>
            <DialogClose onClose={() => onOpenChange(false)} />
          </DialogHeader>
          <div className="px-6 py-8 text-center">
            <FileText className="w-12 h-12 text-slate-300 mx-auto mb-3" />
            <p className="text-sm text-slate-500">No documents available for this bid</p>
          </div>
        </DialogContent>
      </Dialog>
    );
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl">
        <DialogHeader>
          <div className="flex items-center space-x-2">
            <FileText className="w-5 h-5 text-slate-600" />
            <DialogTitle>
              Documents - {bidReference} ({documents.length})
            </DialogTitle>
          </div>
          <DialogClose onClose={() => onOpenChange(false)} />
        </DialogHeader>

        <div className="px-6 py-4 space-y-3 max-h-[60vh] overflow-y-auto">
          {documents.map((doc) => (
            <div
              key={doc.id}
              className="border border-slate-200 rounded-lg p-4 hover:bg-slate-50 transition-colors"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2 mb-2">
                    <FileText className="w-4 h-4 text-slate-500 flex-shrink-0" />
                    <span className="text-sm font-medium text-slate-900 truncate">
                      {doc.filename || 'Untitled Document'}
                    </span>
                  </div>

                  <div className="flex items-center space-x-3 text-xs text-slate-500">
                    {getDocumentTypeBadge(doc.document_type)}
                    <span>{formatFileSize(doc.file_size)}</span>
                    {doc.scraped_at && (
                      <span>Added {new Date(doc.scraped_at).toLocaleDateString()}</span>
                    )}
                  </div>
                </div>

                <div className="flex items-center space-x-2 ml-4">
                  <button
                    onClick={() => onPreview(doc)}
                    className="p-2 text-slate-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                    title="Preview PDF"
                  >
                    <Eye className="w-4 h-4" />
                  </button>

                  <a
                    href={doc.document_url}
                    download
                    className="p-2 text-slate-600 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                    title="Download PDF"
                  >
                    <Download className="w-4 h-4" />
                  </a>

                  <a
                    href={doc.document_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-2 text-slate-600 hover:text-purple-600 hover:bg-purple-50 rounded-lg transition-colors"
                    title="Open in New Tab"
                  >
                    <ExternalLink className="w-4 h-4" />
                  </a>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="px-6 py-3 border-t border-slate-200 bg-slate-50">
          <p className="text-xs text-slate-500">
            Click the eye icon to preview, download icon to save, or external link to open in a new tab
          </p>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default DocumentListModal;
