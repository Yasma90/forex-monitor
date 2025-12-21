'use client';

import { ExchangeRateHistory } from '@/lib/api';
import { TrendingUp, TrendingDown, Minus, BarChart3 } from 'lucide-react';

interface StatsCardProps {
  history: ExchangeRateHistory | null;
  loading: boolean;
}

export default function StatsCard({ history, loading }: StatsCardProps) {
  if (loading && !history) {
    return (
      <div className="card">
        <div className="animate-pulse space-y-3">
          <div className="h-4 bg-gray-200 rounded w-24"></div>
          <div className="h-8 bg-gray-200 rounded w-32"></div>
        </div>
      </div>
    );
  }

  if (!history || history.rates.length < 2) {
    return null;
  }

  const firstRate = history.rates[0].rate;
  const lastRate = history.rates[history.rates.length - 1].rate;
  const periodChange = lastRate - firstRate;
  const periodChangePercent = (periodChange / firstRate) * 100;

  const volatility = history.max_rate - history.min_rate;
  const volatilityPercent = (volatility / history.avg_rate) * 100;

  const getTrend = () => {
    if (periodChangePercent > 0.5) return { icon: TrendingUp, text: 'Tendencia alcista', color: 'text-green-600' };
    if (periodChangePercent < -0.5) return { icon: TrendingDown, text: 'Tendencia bajista', color: 'text-red-600' };
    return { icon: Minus, text: 'Estable', color: 'text-gray-600' };
  };

  const trend = getTrend();
  const TrendIcon = trend.icon;

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
        <BarChart3 className="w-5 h-5" />
        Estadisticas ({history.period_days} dias)
      </h3>

      <div className="grid grid-cols-2 gap-4">
        <div className="p-3 bg-gray-50 rounded-lg">
          <p className="text-xs text-gray-500 uppercase tracking-wide">Tendencia</p>
          <div className={`flex items-center gap-2 mt-1 ${trend.color}`}>
            <TrendIcon className="w-5 h-5" />
            <span className="font-medium">{trend.text}</span>
          </div>
        </div>

        <div className="p-3 bg-gray-50 rounded-lg">
          <p className="text-xs text-gray-500 uppercase tracking-wide">Cambio periodo</p>
          <p className={`text-lg font-semibold ${periodChange >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {periodChange >= 0 ? '+' : ''}{periodChangePercent.toFixed(2)}%
          </p>
        </div>

        <div className="p-3 bg-gray-50 rounded-lg">
          <p className="text-xs text-gray-500 uppercase tracking-wide">Volatilidad</p>
          <p className="text-lg font-semibold text-gray-900">
            {volatilityPercent.toFixed(2)}%
          </p>
        </div>

        <div className="p-3 bg-gray-50 rounded-lg">
          <p className="text-xs text-gray-500 uppercase tracking-wide">Rango</p>
          <p className="text-sm font-medium text-gray-900">
            {history.min_rate.toFixed(4)} - {history.max_rate.toFixed(4)}
          </p>
        </div>
      </div>
    </div>
  );
}
