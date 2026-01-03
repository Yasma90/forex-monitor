'use client';

import { useState, useEffect, useCallback } from 'react';
import { DollarSign, Euro, Bell, RefreshCw, Download, ArrowLeftRight, FileDown } from 'lucide-react';
import ExchangeCard from '@/components/ExchangeCard';
import PredictionChart from '@/components/PredictionChart';
import StatsCard from '@/components/StatsCard';
import NewsFeed from '@/components/NewsFeed';
import SentimentGauge from '@/components/SentimentGauge';
import PredictionCard from '@/components/PredictionCard';
import SignalBadge from '@/components/SignalBadge';
import AlertsPanel from '@/components/AlertsPanel';
import {
  getCurrentRate,
  getRateHistory,
  refreshRate,
  exportToCSV,
  getNewsFeed,
  getSentimentSummary,
  getPrediction,
  getQuickSignal,
  checkAlerts,
  ExchangeRate,
  ExchangeRateHistory,
  NewsArticle,
  SentimentSummary,
  Prediction,
  QuickSignal
} from '@/lib/api';
import { registerServiceWorker, isPWAInstalled, showNotification } from '@/lib/notifications';

export default function Home() {
  // Currency pair state
  const [baseCurrency, setBaseCurrency] = useState('USD');
  const [targetCurrency, setTargetCurrency] = useState('EUR');

  // State
  const [rate, setRate] = useState<ExchangeRate | null>(null);
  const [history, setHistory] = useState<ExchangeRateHistory | null>(null);
  const [news, setNews] = useState<NewsArticle[]>([]);
  const [sentiment, setSentiment] = useState<SentimentSummary | null>(null);
  const [prediction, setPrediction] = useState<Prediction | null>(null);
  const [signal, setSignal] = useState<QuickSignal | null>(null);

  // UI State
  const [loadingRate, setLoadingRate] = useState(true);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [loadingNews, setLoadingNews] = useState(true);
  const [loadingPrediction, setLoadingPrediction] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [alertsPanelOpen, setAlertsPanelOpen] = useState(false);
  const [installPrompt, setInstallPrompt] = useState<any>(null);
  const [isInstalled, setIsInstalled] = useState(false);

  // Swap currencies handler
  const handleSwapCurrencies = useCallback(() => {
    setBaseCurrency(targetCurrency);
    setTargetCurrency(baseCurrency);
  }, [baseCurrency, targetCurrency]);

  // Register service worker on mount
  useEffect(() => {
    registerServiceWorker();
    setIsInstalled(isPWAInstalled());

    // Listen for install prompt
    const handleBeforeInstallPrompt = (e: Event) => {
      e.preventDefault();
      setInstallPrompt(e);
    };
    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    };
  }, []);

  const fetchRate = useCallback(async () => {
    try {
      setLoadingRate(true);
      const data = await getCurrentRate(baseCurrency, targetCurrency);
      setRate(data);
      setLastUpdate(new Date());
      setError(null);
    } catch (err) {
      setError('Error al obtener el tipo de cambio');
      console.error(err);
    } finally {
      setLoadingRate(false);
    }
  }, [baseCurrency, targetCurrency]);

  const fetchHistory = useCallback(async () => {
    try {
      setLoadingHistory(true);
      const data = await getRateHistory(baseCurrency, targetCurrency, 30);
      setHistory(data);
    } catch (err) {
      console.error('Error fetching history:', err);
    } finally {
      setLoadingHistory(false);
    }
  }, [baseCurrency, targetCurrency]);

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

  const handleCheckAlerts = useCallback(async () => {
    try {
      const triggered = await checkAlerts();
      if (triggered.length > 0) {
        for (const t of triggered) {
          await showNotification(t.alert.name, { body: t.message });
        }
      }
    } catch (err) {
      console.error('Error checking alerts:', err);
    }
  }, []);

  const handleRefresh = async () => {
    try {
      setLoadingRate(true);
      await refreshRate(baseCurrency, targetCurrency);
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

  const handleInstall = async () => {
    if (!installPrompt) return;
    installPrompt.prompt();
    const result = await installPrompt.userChoice;
    if (result.outcome === 'accepted') {
      setInstallPrompt(null);
      setIsInstalled(true);
    }
  };

  const handleExportCSV = async () => {
    try {
      await exportToCSV(baseCurrency, targetCurrency, 30);
    } catch (err) {
      console.error('Error exporting CSV:', err);
      setError('Error al exportar CSV');
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
      handleCheckAlerts(); // Check alerts on each rate update
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
  }, [fetchRate, fetchHistory, fetchNews, fetchPrediction, handleCheckAlerts]);

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
                <p className="text-sm text-gray-500">{baseCurrency}/{targetCurrency} con predicciones ML</p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              {/* Quick Signal Badge */}
              <SignalBadge signal={signal} loading={loadingPrediction} compact />

              {/* Install PWA button */}
              {installPrompt && !isInstalled && (
                <button
                  onClick={handleInstall}
                  className="flex items-center gap-1 px-3 py-2 bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 transition-colors"
                  title="Instalar app"
                >
                  <Download className="w-4 h-4" />
                  <span className="hidden sm:inline text-sm">Instalar</span>
                </button>
              )}

              <button
                onClick={handleExportCSV}
                disabled={loadingHistory}
                className="flex items-center gap-2 px-3 py-2 bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition-colors disabled:opacity-50"
                title="Exportar datos a CSV"
              >
                <FileDown className="w-4 h-4" />
                <span className="hidden sm:inline text-sm">CSV</span>
              </button>

              <button
                onClick={handleRefresh}
                disabled={loadingRate}
                className="flex items-center gap-2 px-3 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors disabled:opacity-50"
                title="Actualizar todo"
              >
                <RefreshCw className={`w-4 h-4 ${loadingRate ? 'animate-spin' : ''}`} />
              </button>

              <button
                onClick={() => setAlertsPanelOpen(true)}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                title="Configurar alertas"
              >
                <Bell className="w-4 h-4" />
                <span className="hidden sm:inline">Alertas</span>
              </button>
            </div>
          </div>

          {lastUpdate && (
            <p className="text-xs text-gray-400 mt-2">
              Ultima actualizacion: {lastUpdate.toLocaleString('es-ES')}
              {isInstalled && <span className="ml-2 text-purple-500">(PWA)</span>}
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
              onSwap={handleSwapCurrencies}
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

      {/* Alerts Panel Modal */}
      <AlertsPanel
        isOpen={alertsPanelOpen}
        onClose={() => setAlertsPanelOpen(false)}
        currentRate={rate?.rate || null}
      />
    </main>
  );
}
