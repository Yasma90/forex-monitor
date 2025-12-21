'use client';

import { useState, useEffect, useCallback } from 'react';
import { DollarSign, Euro, Bell } from 'lucide-react';
import ExchangeCard from '@/components/ExchangeCard';
import RateChart from '@/components/RateChart';
import StatsCard from '@/components/StatsCard';
import { getCurrentRate, getRateHistory, refreshRate, ExchangeRate, ExchangeRateHistory } from '@/lib/api';

export default function Home() {
  const [rate, setRate] = useState<ExchangeRate | null>(null);
  const [history, setHistory] = useState<ExchangeRateHistory | null>(null);
  const [loadingRate, setLoadingRate] = useState(true);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  const fetchRate = useCallback(async () => {
    try {
      setLoadingRate(true);
      const data = await getCurrentRate();
      setRate(data);
      setLastUpdate(new Date());
      setError(null);
    } catch (err) {
      setError('Error al obtener el tipo de cambio');
      console.error(err);
    } finally {
      setLoadingRate(false);
    }
  }, []);

  const fetchHistory = useCallback(async () => {
    try {
      setLoadingHistory(true);
      const data = await getRateHistory('USD', 'EUR', 30);
      setHistory(data);
    } catch (err) {
      console.error('Error fetching history:', err);
    } finally {
      setLoadingHistory(false);
    }
  }, []);

  const handleRefresh = async () => {
    try {
      setLoadingRate(true);
      await refreshRate();
      await fetchRate();
      await fetchHistory();
    } catch (err) {
      setError('Error al actualizar');
      console.error(err);
    }
  };

  useEffect(() => {
    fetchRate();
    fetchHistory();

    // Auto-refresh every 5 minutes
    const interval = setInterval(() => {
      fetchRate();
    }, 5 * 60 * 1000);

    return () => clearInterval(interval);
  }, [fetchRate, fetchHistory]);

  return (
    <main className="min-h-screen p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <header className="mb-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex items-center">
                <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center">
                  <DollarSign className="w-6 h-6 text-green-600" />
                </div>
                <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center -ml-2">
                  <Euro className="w-6 h-6 text-blue-600" />
                </div>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Forex Monitor</h1>
                <p className="text-sm text-gray-500">USD/EUR en tiempo real</p>
              </div>
            </div>

            <button
              className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
              title="Configurar alertas (proximamente)"
            >
              <Bell className="w-4 h-4" />
              <span className="hidden sm:inline">Alertas</span>
            </button>
          </div>

          {lastUpdate && (
            <p className="text-xs text-gray-400 mt-2">
              Ultima actualizacion: {lastUpdate.toLocaleString('es-ES')}
            </p>
          )}
        </header>

        {/* Error message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}

        {/* Main content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left column - Rate card */}
          <div className="lg:col-span-1 space-y-6">
            <ExchangeCard
              rate={rate}
              loading={loadingRate}
              onRefresh={handleRefresh}
            />
            <StatsCard history={history} loading={loadingHistory} />
          </div>

          {/* Right column - Chart */}
          <div className="lg:col-span-2">
            <RateChart history={history} loading={loadingHistory} />
          </div>
        </div>

        {/* Info section */}
        <section className="mt-8 p-6 bg-blue-50 rounded-xl border border-blue-100">
          <h2 className="text-lg font-semibold text-blue-900 mb-2">
            Proximamente
          </h2>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>Alertas personalizadas por email y push</li>
            <li>Predicciones con Machine Learning</li>
            <li>Noticias relevantes con analisis de sentimiento</li>
            <li>Calendario de eventos economicos (Fed, BCE)</li>
          </ul>
        </section>

        {/* Footer */}
        <footer className="mt-8 text-center text-sm text-gray-400">
          <p>Datos proporcionados por Frankfurter API (BCE)</p>
          <p>Actualizacion cada 30 minutos</p>
        </footer>
      </div>
    </main>
  );
}
