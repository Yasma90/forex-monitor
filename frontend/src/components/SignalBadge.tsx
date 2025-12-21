'use client';

import { TrendingUp, TrendingDown, Minus, Zap } from 'lucide-react';
import { QuickSignal } from '@/lib/api';

interface SignalBadgeProps {
  signal: QuickSignal | null;
  loading: boolean;
  compact?: boolean;
}

export default function SignalBadge({ signal, loading, compact = false }: SignalBadgeProps) {
  if (loading && !signal) {
    return (
      <div className="animate-pulse flex items-center gap-2 px-3 py-2 bg-gray-100 rounded-lg">
        <div className="w-4 h-4 bg-gray-300 rounded"></div>
        <div className="w-16 h-4 bg-gray-300 rounded"></div>
      </div>
    );
  }

  if (!signal) return null;

  const getSignalStyle = () => {
    switch (signal.signal) {
      case 'BULLISH':
        return {
          bg: 'bg-green-100',
          text: 'text-green-700',
          icon: TrendingUp,
        };
      case 'BEARISH':
        return {
          bg: 'bg-red-100',
          text: 'text-red-700',
          icon: TrendingDown,
        };
      default:
        return {
          bg: 'bg-gray-100',
          text: 'text-gray-700',
          icon: Minus,
        };
    }
  };

  const style = getSignalStyle();
  const Icon = style.icon;

  if (compact) {
    return (
      <div className={`inline-flex items-center gap-1.5 px-2 py-1 rounded-md ${style.bg}`}>
        <Icon className={`w-3 h-3 ${style.text}`} />
        <span className={`text-xs font-medium ${style.text}`}>{signal.signal}</span>
      </div>
    );
  }

  return (
    <div className={`flex items-center gap-3 px-4 py-3 rounded-lg ${style.bg}`}>
      <Icon className={`w-6 h-6 ${style.text}`} />
      <div className="flex-1">
        <div className="flex items-center gap-2">
          <span className={`font-bold ${style.text}`}>{signal.signal}</span>
          <Zap className={`w-3 h-3 ${style.text}`} />
          <span className={`text-sm ${style.text}`}>
            {(signal.strength * 100).toFixed(0)}%
          </span>
        </div>
        <p className="text-xs text-gray-600 line-clamp-1">{signal.description}</p>
      </div>
    </div>
  );
}
