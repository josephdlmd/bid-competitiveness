import { LucideIcon } from 'lucide-react';

interface EmptyStateProps {
  icon: LucideIcon;
  title: string;
  description: string;
  variant?: 'primary' | 'secondary';
}

const EmptyState = ({ icon: Icon, title, description, variant = 'primary' }: EmptyStateProps) => {
  return (
    <div className="text-center py-12">
      <Icon className="w-12 h-12 mx-auto text-slate-400 mb-4" />
      <h3 className="text-sm font-medium text-slate-900 mb-1">{title}</h3>
      <p className="text-sm text-slate-500">{description}</p>
    </div>
  );
};

export default EmptyState;
