'use client';

import { TrendingUp, TrendingDown, Minus, Target, AlertTriangle, Zap } from 'lucide-react';
import { Prediction } from '@/lib/api';

interface PredictionCardProps {
  prediction: Prediction | null;
  loading: boolean;
}

export default function PredictionCard({ prediction, loading }: PredictionCardProps) {
  if (loading && !prediction) {
    return (
      <div className="card">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-32 mb-4"></div>
          <div className="h-20 bg-gray-200 rounded mb-4"></div>
          <div className="h-4 bg-gray-200 rounded w-full"></div>
        </div>
      </div>
    );
  }

  if (!prediction) {
    return (
      <div className="card">
        <div className="flex items-center gap-2 mb-4">
          <Target className="w-5 h-5" />
          <h3 className="text-lg font-semibold">Prediccion</h3>
        </div>
        <p className="text-gray-500 text-sm">
          No hay suficientes datos para generar prediccion.
        </p>
      </div>
    );
  }

  const getSignalIcon = () => {
    switch (prediction.signal) {
      case 'BULLISH':
        return <TrendingUp className="w-8 h-8 text-green-500" />;
      case 'BEARISH':
        return <TrendingDown className="w-8 h-8 text-red-500" />;
      default:
        return <Minus className="w-8 h-8 text-gray-500" />;
    }
  };

  const getSignalColor = () => {
    switch (prediction.signal) {
      case 'BULLISH':
        return 'bg-green-50 border-green-200 text-green-800';
      case 'BEARISH':
        return 'bg-red-50 border-red-200 text-red-800';
      default:
        return 'bg-gray-50 border-gray-200 text-gray-800';
    }
  };

  const getChangeColor = (change: number) => {
    if (change > 0) return 'text-green-600';
    if (change < 0) return 'text-red-600';
    return 'text-gray-600';
  };

  // Get 7-day and 30-day predictions
  const pred7d = prediction.predictions[6];
  const pred30d = prediction.predictions[prediction.predictions.length - 1];

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Target className="w-5 h-5" />
          <h3 className="text-lg font-semibold">Prediccion</h3>
        </div>
        <span className="text-xs text-gray-400 capitalize">
          {prediction.model_type.replace('_', ' ')}
        </span>
      </div>

      {/* Signal Badge */}
      <div className={`flex items-center gap-3 p-4 rounded-lg border mb-4 ${getSignalColor()}`}>
        {getSignalIcon()}
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <span className="font-bold text-lg">{prediction.signal}</span>
            <div className="flex items-center gap-1">
              {[...Array(5)].map((_, i) => (
                <div
                  key={i}
                  className={`w-2 h-2 rounded-full ${
                    i < prediction.signal_strength * 5
                      ? prediction.signal === 'BULLISH'
                        ? 'bg-green-500'
                        : prediction.signal === 'BEARISH'
                        ? 'bg-red-500'
                        : 'bg-gray-400'
                      : 'bg-gray-200'
                  }`}
                />
              ))}
            </div>
          </div>
          <p className="text-sm opacity-80">{prediction.signal_description}</p>
        </div>
      </div>

      {/* Predictions */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        <div className="p-3 bg-gray-50 rounded-lg">
          <p className="text-xs text-gray-500 mb-1">7 dias</p>
          <p className="text-lg font-bold">{pred7d?.predicted_rate.toFixed(4)}</p>
          <p className={`text-sm font-medium ${getChangeColor(prediction.predicted_change_7d)}`}>
            {prediction.predicted_change_7d > 0 ? '+' : ''}
            {prediction.predicted_change_7d.toFixed(2)}%
          </p>
        </div>
        <div className="p-3 bg-gray-50 rounded-lg">
          <p className="text-xs text-gray-500 mb-1">30 dias</p>
          <p className="text-lg font-bold">{pred30d?.predicted_rate.toFixed(4)}</p>
          <p className={`text-sm font-medium ${getChangeColor(prediction.predicted_change_30d)}`}>
            {prediction.predicted_change_30d > 0 ? '+' : ''}
            {prediction.predicted_change_30d.toFixed(2)}%
          </p>
        </div>
      </div>

      {/* Confidence & Sentiment */}
      <div className="space-y-2 text-sm">
        <div className="flex justify-between items-center">
          <span className="text-gray-500">Confianza</span>
          <div className="flex items-center gap-2">
            <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-blue-500 rounded-full"
                style={{ width: `${prediction.confidence_level * 100}%` }}
              />
            </div>
            <span className="font-medium">{(prediction.confidence_level * 100).toFixed(0)}%</span>
          </div>
        </div>

        <div className="flex justify-between items-center">
          <span className="text-gray-500">Impacto sentimiento</span>
          <span className={`font-medium ${prediction.sentiment_impact >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {prediction.sentiment_impact >= 0 ? '+' : ''}
            {(prediction.sentiment_impact * 100).toFixed(2)}%
          </span>
        </div>
      </div>

      {/* Warning */}
      <div className="mt-4 p-3 bg-amber-50 border border-amber-200 rounded-lg">
        <div className="flex items-start gap-2">
          <AlertTriangle className="w-4 h-4 text-amber-600 mt-0.5" />
          <p className="text-xs text-amber-700">
            Las predicciones son indicativas, no garantias. Los mercados forex son volatiles.
            Use esta informacion como una herramienta mas, no como unica referencia.
          </p>
        </div>
      </div>
    </div>
  );
}
