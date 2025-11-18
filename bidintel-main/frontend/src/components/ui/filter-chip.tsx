import { X } from 'lucide-react';
import { cn } from '@/lib/utils';

interface FilterChipProps {
  label: string;
  value: string;
  onRemove: () => void;
  className?: string;
}

const FilterChip = ({ label, value, onRemove, className }: FilterChipProps) => {
  return (
    <div className={cn(
      "inline-flex items-center space-x-1 px-3 py-1 bg-slate-100 text-slate-700 rounded-full text-sm border border-slate-200",
      className
    )}>
      <span className="font-medium">{label}:</span>
      <span>{value}</span>
      <button
        onClick={onRemove}
        className="ml-1 hover:bg-slate-200 rounded-full p-0.5 transition-colors"
        aria-label={`Remove ${label} filter`}
      >
        <X className="w-3 h-3" />
      </button>
    </div>
  );
};

export { FilterChip };
