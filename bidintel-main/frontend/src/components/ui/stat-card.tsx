import { Card } from './card';
import { LucideIcon } from 'lucide-react';

interface StatCardProps {
  icon: LucideIcon;
  label: string;
  value: string | number;
  trend?: number;
  subtitle?: string;
  color?: 'slate' | 'emerald' | 'amber' | 'red';
}

const StatCard = ({ icon: Icon, label, value, trend, subtitle, color = 'slate' }: StatCardProps) => {
  const colors = {
    slate: 'text-slate-600 bg-slate-50',
    emerald: 'text-emerald-600 bg-emerald-50',
    amber: 'text-amber-600 bg-amber-50',
    red: 'text-red-600 bg-red-50'
  };

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-slate-600">{label}</p>
          <p className="text-2xl font-bold text-slate-900 mt-1">{value}</p>
          {subtitle && <p className="text-sm text-slate-500 mt-1">{subtitle}</p>}
        </div>
        <div className={`p-3 rounded-lg ${colors[color]}`}>
          <Icon className="w-6 h-6" />
        </div>
      </div>
      {trend !== undefined && (
        <div className="mt-4 flex items-center text-sm">
          <span className={`font-medium ${trend > 0 ? 'text-emerald-600' : 'text-red-600'}`}>
            {trend > 0 ? '+' : ''}{trend}%
          </span>
          <span className="text-slate-500 ml-2">from last week</span>
        </div>
      )}
    </Card>
  );
};

export { StatCard };
