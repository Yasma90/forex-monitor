'use client';

import { TrendingUp, TrendingDown, RefreshCw } from 'lucide-react';
import { ExchangeRate } from '@/lib/api';

interface ExchangeCardProps {
  rate: ExchangeRate | null;
  loading: boolean;
  onRefresh: () => void;
}

export default function ExchangeCard({ rate, loading, onRefresh }: ExchangeCardProps) {
  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleString('es-ES', {
      dateStyle: 'medium',
      timeStyle: 'short',
    });
  };

  const isPositive = rate?.change_24h !== null && rate?.change_24h !== undefined && rate.change_24h >= 0;

  return (
    <div className="card">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h2 className="text-sm font-medium text-gray-500">Tipo de Cambio</h2>
          <p className="text-lg font-semibold text-gray-900">
            {rate?.base_currency || 'USD'} / {rate?.target_currency || 'EUR'}
          </p>
        </div>
        <button
          onClick={onRefresh}
          disabled={loading}
          className="p-2 rounded-lg hover:bg-gray-100 transition-colors disabled:opacity-50"
          title="Actualizar"
        >
          <RefreshCw className={`w-5 h-5 text-gray-500 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {loading && !rate ? (
        <div className="animate-pulse">
          <div className="h-12 bg-gray-200 rounded w-32 mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-24"></div>
        </div>
      ) : rate ? (
        <>
          <div className="flex items-end gap-3">
            <span className="text-4xl font-bold text-gray-900">
              {rate.rate.toFixed(4)}
            </span>
            {rate.change_percent_24h !== null && (
              <div className={`flex items-center gap-1 pb-1 ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
                {isPositive ? (
                  <TrendingUp className="w-5 h-5" />
                ) : (
                  <TrendingDown className="w-5 h-5" />
                )}
                <span className="text-sm font-medium">
                  {isPositive ? '+' : ''}{rate.change_percent_24h.toFixed(2)}%
                </span>
              </div>
            )}
          </div>

          <div className="mt-4 text-sm text-gray-500">
            <p>Actualizado: {formatDate(rate.timestamp)}</p>
            <p className="text-xs">Fuente: {rate.source}</p>
          </div>

          {rate.change_24h !== null && (
            <div className="mt-3 pt-3 border-t border-gray-100">
              <p className="text-xs text-gray-500">
                Cambio 24h: <span className={isPositive ? 'text-green-600' : 'text-red-600'}>
                  {isPositive ? '+' : ''}{rate.change_24h.toFixed(4)}
                </span>
              </p>
            </div>
          )}
        </>
      ) : (
        <p className="text-gray-500">No hay datos disponibles</p>
      )}
    </div>
  );
}
