import { X, Calendar, DollarSign, Building, FileText } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogClose } from '@/components/ui';
import { formatCurrency, formatDate } from '@/utils/formatters';
import { Bid } from '@/lib/types';

interface BidDetailModalProps {
  bid: Bid;
  onClose: () => void;
}

const BidDetailModal = ({ bid, onClose }: BidDetailModalProps) => {
  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl">
        <DialogHeader>
          <DialogTitle>{bid.title}</DialogTitle>
          <DialogClose onClose={onClose} />
        </DialogHeader>

        <div className="px-6 py-4 space-y-6 max-h-[70vh] overflow-y-auto">
          {/* Reference Number */}
          <div>
            <label className="text-xs text-slate-500 uppercase font-medium">Reference Number</label>
            <p className="mt-1 font-mono text-sm text-slate-900">{bid.reference_number}</p>
          </div>

          {/* Basic Info Grid */}
          <div className="grid grid-cols-2 gap-6">
            <div>
              <label className="text-xs text-slate-500 uppercase font-medium flex items-center">
                <Building className="w-3 h-3 mr-1" />
                Procuring Entity
              </label>
              <p className="mt-1 text-sm text-slate-900">{bid.procuring_entity}</p>
            </div>
            <div>
              <label className="text-xs text-slate-500 uppercase font-medium flex items-center">
                <DollarSign className="w-3 h-3 mr-1" />
                Approved Budget
              </label>
              <p className="mt-1 text-lg font-semibold text-slate-900">{formatCurrency(bid.approved_budget)}</p>
            </div>
            <div>
              <label className="text-xs text-slate-500 uppercase font-medium flex items-center">
                <Calendar className="w-3 h-3 mr-1" />
                Publish Date
              </label>
              <p className="mt-1 text-sm text-slate-900">{formatDate(bid.publish_date)}</p>
            </div>
            <div>
              <label className="text-xs text-slate-500 uppercase font-medium flex items-center">
                <Calendar className="w-3 h-3 mr-1" />
                Closing Date
              </label>
              <p className="mt-1 text-sm text-slate-900">{formatDate(bid.closing_date)}</p>
            </div>
          </div>

          {/* Classification */}
          <div>
            <label className="text-xs text-slate-500 uppercase font-medium">Classification</label>
            <p className="mt-1 text-sm text-slate-900">{bid.classification}</p>
          </div>

          {/* Procurement Mode */}
          <div>
            <label className="text-xs text-slate-500 uppercase font-medium">Procurement Mode</label>
            <p className="mt-1 text-sm text-slate-900">{bid.procurement_mode}</p>
          </div>

          {/* Description */}
          {bid.description && (
            <div>
              <label className="text-xs text-slate-500 uppercase font-medium flex items-center">
                <FileText className="w-3 h-3 mr-1" />
                Description
              </label>
              <p className="mt-1 text-sm text-slate-700 whitespace-pre-wrap">{bid.description}</p>
            </div>
          )}

          {/* Contact Info */}
          <div className="border-t border-slate-200 pt-4">
            <h3 className="text-sm font-semibold text-slate-900 mb-3">Contact Information</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-xs text-slate-500 uppercase font-medium">Contact Person</label>
                <p className="mt-1 text-sm text-slate-900">{bid.contact_person || 'N/A'}</p>
              </div>
              <div>
                <label className="text-xs text-slate-500 uppercase font-medium">Email</label>
                <p className="mt-1 text-sm text-slate-900">{bid.contact_email || 'N/A'}</p>
              </div>
            </div>
          </div>

          {/* Delivery Info */}
          {(bid.delivery_location || bid.delivery_period) && (
            <div className="border-t border-slate-200 pt-4">
              <h3 className="text-sm font-semibold text-slate-900 mb-3">Delivery Information</h3>
              <div className="grid grid-cols-2 gap-4">
                {bid.delivery_location && (
                  <div>
                    <label className="text-xs text-slate-500 uppercase font-medium">Location</label>
                    <p className="mt-1 text-sm text-slate-900">{bid.delivery_location}</p>
                  </div>
                )}
                {bid.delivery_period && (
                  <div>
                    <label className="text-xs text-slate-500 uppercase font-medium">Period</label>
                    <p className="mt-1 text-sm text-slate-900">{bid.delivery_period}</p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default BidDetailModal;
