import { LucideIcon } from 'lucide-react';
import { Card } from './Card';

interface KPICardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  trend?: {
    value: string;
    positive: boolean;
  };
  color?: string;
}

export function KPICard({ title, value, icon: Icon, trend, color = 'text-neuro-blue' }: KPICardProps) {
  return (
    <Card hover>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-gray-600 mb-1">{title}</p>
          <p className="text-3xl font-bold font-mono">{value}</p>
          {trend && (
            <p className={`text-sm mt-2 ${trend.positive ? 'text-profit-green' : 'text-risk-red'}`}>
              {trend.positive ? '↑' : '↓'} {trend.value}
            </p>
          )}
        </div>
        <div className={`p-3 rounded-lg bg-gray-50 ${color}`}>
          <Icon size={24} />
        </div>
      </div>
    </Card>
  );
}
