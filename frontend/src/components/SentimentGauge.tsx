'use client';

import { TrendingUp, TrendingDown, Minus, Activity } from 'lucide-react';
import { SentimentSummary } from '@/lib/api';

interface SentimentGaugeProps {
  summary: SentimentSummary | null;
  loading: boolean;
}

export default function SentimentGauge({ summary, loading }: SentimentGaugeProps) {
  if (loading && !summary) {
    return (
      <div className="card">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-32 mb-4"></div>
          <div className="h-16 bg-gray-200 rounded mb-2"></div>
        </div>
      </div>
    );
  }

  if (!summary) {
    return null;
  }

  const getMoodIcon = () => {
    switch (summary.mood) {
      case 'BULLISH':
        return <TrendingUp className="w-8 h-8 text-green-500" />;
      case 'BEARISH':
        return <TrendingDown className="w-8 h-8 text-red-500" />;
      default:
        return <Minus className="w-8 h-8 text-gray-500" />;
    }
  };

  const getMoodColor = () => {
    switch (summary.mood) {
      case 'BULLISH':
        return 'text-green-600 bg-green-50';
      case 'BEARISH':
        return 'text-red-600 bg-red-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  const total = summary.total_articles;
  const positivePercent = total > 0 ? (summary.summary.positive / total) * 100 : 0;
  const negativePercent = total > 0 ? (summary.summary.negative / total) * 100 : 0;
  const neutralPercent = total > 0 ? (summary.summary.neutral / total) * 100 : 0;

  return (
    <div className="card">
      <div className="flex items-center gap-2 mb-4">
        <Activity className="w-5 h-5" />
        <h3 className="text-lg font-semibold">Sentimiento del Mercado</h3>
      </div>

      {/* Mood indicator */}
      <div className={`flex items-center gap-3 p-4 rounded-lg mb-4 ${getMoodColor()}`}>
        {getMoodIcon()}
        <div>
          <p className="font-bold text-lg">{summary.mood}</p>
          <p className="text-sm opacity-80">{summary.mood_description}</p>
        </div>
      </div>

      {/* Sentiment bar */}
      <div className="mb-4">
        <div className="flex h-3 rounded-full overflow-hidden bg-gray-200">
          <div
            className="bg-green-500 transition-all"
            style={{ width: `${positivePercent}%` }}
          />
          <div
            className="bg-gray-400 transition-all"
            style={{ width: `${neutralPercent}%` }}
          />
          <div
            className="bg-red-500 transition-all"
            style={{ width: `${negativePercent}%` }}
          />
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-2 text-center">
        <div className="p-2 bg-green-50 rounded-lg">
          <p className="text-lg font-bold text-green-600">{summary.summary.positive}</p>
          <p className="text-xs text-gray-500">Positivas</p>
        </div>
        <div className="p-2 bg-gray-50 rounded-lg">
          <p className="text-lg font-bold text-gray-600">{summary.summary.neutral}</p>
          <p className="text-xs text-gray-500">Neutrales</p>
        </div>
        <div className="p-2 bg-red-50 rounded-lg">
          <p className="text-lg font-bold text-red-600">{summary.summary.negative}</p>
          <p className="text-xs text-gray-500">Negativas</p>
        </div>
      </div>

      <p className="text-xs text-gray-400 mt-3 text-center">
        Basado en {total} articulos de las ultimas {summary.period_hours}h
      </p>
    </div>
  );
}
