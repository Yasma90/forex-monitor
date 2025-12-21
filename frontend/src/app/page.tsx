'use client';

import { useState, useEffect, useCallback } from 'react';
import { DollarSign, Euro, Bell, RefreshCw } from 'lucide-react';
import ExchangeCard from '@/components/ExchangeCard';
import PredictionChart from '@/components/PredictionChart';
import StatsCard from '@/components/StatsCard';
import NewsFeed from '@/components/NewsFeed';
import SentimentGauge from '@/components/SentimentGauge';
import PredictionCard from '@/components/PredictionCard';
import SignalBadge from '@/components/SignalBadge';
import {
  getCurrentRate,
  getRateHistory,
  refreshRate,
  getNewsFeed,
  getSentimentSummary,
  getPrediction,
  getQuickSignal,
  ExchangeRate,
  ExchangeRateHistory,
  NewsArticle,
  SentimentSummary,
  Prediction,
  QuickSignal
} from '@/lib/api';

export default function Home() {
  // State
  const [rate, setRate] = useState<ExchangeRate | null>(null);
  const [history, setHistory] = useState<ExchangeRateHistory | null>(null);
  const [news, setNews] = useState<NewsArticle[]>([]);
  const [sentiment, setSentiment] = useState<SentimentSummary | null>(null);
  const [prediction, setPrediction] = useState<Prediction | null>(null);
  const [signal, setSignal] = useState<QuickSignal | null>(null);

  // Loading states
  const [loadingRate, setLoadingRate] = useState(true);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [loadingNews, setLoadingNews] = useState(true);
  const [loadingPrediction, setLoadingPrediction] = useState(true);

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

  const fetchNews = useCallback(async () => {
    try {
      setLoadingNews(true);
      const [feedData, sentimentData] = await Promise.all([
        getNewsFeed(15, 48),
        getSentimentSummary(24)
      ]);
      setNews(feedData.articles);
      setSentiment(sentimentData);
    } catch (err) {
      console.error('Error fetching news:', err);
    } finally {
      setLoadingNews(false);
    }
  }, []);

  const fetchPrediction = useCallback(async () => {
    try {
      setLoadingPrediction(true);
      const [predData, signalData] = await Promise.all([
        getPrediction(30),
        getQuickSignal()
      ]);
      setPrediction(predData);
      setSignal(signalData);
    } catch (err) {
      console.error('Error fetching prediction:', err);
    } finally {
      setLoadingPrediction(false);
    }
  }, []);

  const handleRefresh = async () => {
    try {
      setLoadingRate(true);
      await refreshRate();
      await Promise.all([
        fetchRate(),
        fetchHistory(),
        fetchPrediction()
      ]);
    } catch (err) {
      setError('Error al actualizar');
      console.error(err);
    }
  };

  useEffect(() => {
    // Initial fetch
    fetchRate();
    fetchHistory();
    fetchNews();
    fetchPrediction();

    // Auto-refresh rates every 5 minutes
    const rateInterval = setInterval(() => {
      fetchRate();
    }, 5 * 60 * 1000);

    // Auto-refresh news every 30 minutes
    const newsInterval = setInterval(() => {
      fetchNews();
    }, 30 * 60 * 1000);

    // Auto-refresh predictions every hour
    const predictionInterval = setInterval(() => {
      fetchPrediction();
    }, 60 * 60 * 1000);

    return () => {
      clearInterval(rateInterval);
      clearInterval(newsInterval);
      clearInterval(predictionInterval);
    };
  }, [fetchRate, fetchHistory, fetchNews, fetchPrediction]);

  return (
    <main className="min-h-screen p-4 md:p-6 bg-gray-50">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <header className="mb-6">
          <div className="flex items-center justify-between flex-wrap gap-4">
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
                <p className="text-sm text-gray-500">USD/EUR con predicciones ML</p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              {/* Quick Signal Badge */}
              <SignalBadge signal={signal} loading={loadingPrediction} compact />

              <button
                onClick={handleRefresh}
                disabled={loadingRate}
                className="flex items-center gap-2 px-3 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors disabled:opacity-50"
                title="Actualizar todo"
              >
                <RefreshCw className={`w-4 h-4 ${loadingRate ? 'animate-spin' : ''}`} />
              </button>

              <button
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                title="Configurar alertas (proximamente)"
              >
                <Bell className="w-4 h-4" />
                <span className="hidden sm:inline">Alertas</span>
              </button>
            </div>
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

        {/* Main Grid Layout */}
        <div className="grid grid-cols-1 xl:grid-cols-12 gap-6">
          {/* Left Column - Rate, Stats, Sentiment */}
          <div className="xl:col-span-3 space-y-6">
            <ExchangeCard
              rate={rate}
              loading={loadingRate}
              onRefresh={handleRefresh}
            />
            <StatsCard history={history} loading={loadingHistory} />
            <SentimentGauge summary={sentiment} loading={loadingNews} />
          </div>

          {/* Center Column - Chart & Prediction */}
          <div className="xl:col-span-5 space-y-6">
            <PredictionChart
              history={history}
              prediction={prediction}
              loading={loadingHistory || loadingPrediction}
            />
            <PredictionCard
              prediction={prediction}
              loading={loadingPrediction}
            />
          </div>

          {/* Right Column - News */}
          <div className="xl:col-span-4">
            <NewsFeed articles={news} loading={loadingNews} />
          </div>
        </div>

        {/* Footer */}
        <footer className="mt-8 text-center text-sm text-gray-400">
          <p>Cambio: Frankfurter (BCE) | Noticias: GNews/NewsData | ML: Prophet/Trend</p>
          <p>Actualizacion: Tasa 5min | Noticias 30min | Prediccion 1h</p>
        </footer>
      </div>
    </main>
  );
}
