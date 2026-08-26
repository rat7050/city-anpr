import { LucideIcon } from 'lucide-react';
import { cn } from '../lib/utils';

interface StatsCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon | any;
  trend?: string;
  trendDirection?: 'up' | 'down' | 'neutral';
  color?: 'primary' | 'emerald' | 'amber' | 'red' | 'blue';
}

export default function StatsCard({ title, value, icon: Icon, trend, trendDirection, color = 'primary' }: StatsCardProps) {
  const colorMap = {
    primary: 'text-primary-500 bg-primary-500/10',
    emerald: 'text-emerald-500 bg-emerald-500/10',
    amber: 'text-amber-500 bg-amber-500/10',
    red: 'text-red-500 bg-red-500/10',
    blue: 'text-blue-500 bg-blue-500/10',
  };

  return (
    <div className="bg-surface rounded-xl p-5 border border-slate-700/50 shadow-sm">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-slate-400 mb-1">{title}</p>
          <h3 className="text-2xl font-bold text-slate-100">{value}</h3>
        </div>
        <div className={cn("p-3 rounded-lg", colorMap[color])}>
          <Icon size={24} />
        </div>
      </div>
      {trend && (
        <div className="mt-4 flex items-center text-sm">
          <span className={cn(
            "font-medium mr-2",
            trendDirection === 'up' ? "text-emerald-400" : trendDirection === 'down' ? "text-red-400" : "text-slate-400"
          )}>
            {trend}
          </span>
          <span className="text-slate-500">vs last period</span>
        </div>
      )}
    </div>
  );
}
