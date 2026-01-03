'use client';

import { useState, useMemo } from 'react';
import {
  ComposedChart,
  Line,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Brush,
} from 'recharts';
import { ZoomIn, ZoomOut, RotateCcw, TrendingUp, TrendingDown } from 'lucide-react';
import { ExchangeRateHistory, Prediction } from '@/lib/api';
import { useTheme } from '@/lib/theme';

interface PredictionChartProps {
  history: ExchangeRateHistory | null;
  prediction: Prediction | null;
  loading: boolean;
}

interface CustomTooltipProps {
  active?: boolean;
  payload?: any[];
  label?: string;
  isDark: boolean;
}

function CustomTooltip({ active, payload, isDark }: CustomTooltipProps) {
  if (!active || !payload || payload.length === 0) return null;

  const data = payload[0]?.payload;
  if (!data) return null;

  const isHistorical = data.type === 'historical';
  const rate = isHistorical ? data.actual : data.predicted;
  const change = data.change;

  return (
    <div className={`px-3 py-2 rounded-lg shadow-lg border ${
      isDark
        ? 'bg-gray-800 border-gray-700 text-white'
        : 'bg-white border-gray-200 text-gray-900'
    }`}>
      <p className={`text-xs ${isDark ? 'text-gray-400' : 'text-gray-500'} mb-1`}>
        {data.fullDate}
      </p>
      <div className="flex items-center gap-2">
        <span className={`font-bold text-lg ${isHistorical ? 'text-blue-500' : 'text-purple-500'}`}>
          {rate?.toFixed(4)}
        </span>
        {change !== undefined && change !== null && (
          <span className={`text-xs flex items-center gap-0.5 ${
            change >= 0 ? 'text-green-500' : 'text-red-500'
          }`}>
            {change >= 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
            {change >= 0 ? '+' : ''}{(change * 100).toFixed(2)}%
          </span>
        )}
      </div>
      <p className={`text-xs mt-1 ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
        {isHistorical ? 'Dato historico' : 'Prediccion'}
      </p>
      {!isHistorical && data.lower && data.upper && (
        <p className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>
          Rango: {data.lower.toFixed(4)} - {data.upper.toFixed(4)}
        </p>
      )}
    </div>
  );
}

export default function PredictionChart({ history, prediction, loading }: PredictionChartProps) {
  const { theme } = useTheme();
  const isDark = theme === 'dark';
  const [showBrush, setShowBrush] = useState(false);

  if (loading && !history) {
    return (
      <div className={`rounded-xl p-6 h-96 ${isDark ? 'bg-gray-800' : 'bg-white'} shadow-sm`}>
        <div className="animate-pulse h-full flex items-center justify-center">
          <div className={isDark ? 'text-gray-500' : 'text-gray-400'}>Cargando datos...</div>
        </div>
      </div>
    );
  }

  // Prepare chart data with memoization
  const chartData = useMemo(() => {
    // Prepare historical data with change calculation
    const historicalData = history?.rates.map((r, i, arr) => {
      const prevRate = i > 0 ? arr[i - 1].rate : r.rate;
      const change = (r.rate - prevRate) / prevRate;
      return {
        date: new Date(r.timestamp).toLocaleDateString('es-ES', {
          month: 'short',
          day: 'numeric',
        }),
        fullDate: new Date(r.timestamp).toLocaleString('es-ES'),
        actual: r.rate,
        change,
        type: 'historical',
      };
    }) || [];

    // Sample historical data to avoid overcrowding
    const sampledHistorical = historicalData.filter(
      (_, i) => i % Math.max(1, Math.floor(historicalData.length / 30)) === 0
    );

    // Prepare prediction data
    const lastHistoricalRate = history?.rates[history.rates.length - 1]?.rate;
    const predictionData = prediction?.predictions.map((p, i, arr) => {
      const prevRate = i > 0 ? arr[i - 1].predicted_rate : lastHistoricalRate || p.predicted_rate;
      const change = (p.predicted_rate - prevRate) / prevRate;
      return {
        date: new Date(p.date).toLocaleDateString('es-ES', {
          month: 'short',
          day: 'numeric',
        }),
        fullDate: new Date(p.date).toLocaleString('es-ES'),
        predicted: p.predicted_rate,
        lower: p.lower_bound,
        upper: p.upper_bound,
        range: [p.lower_bound, p.upper_bound],
        change,
        type: 'prediction',
      };
    }) || [];

    // Sample predictions
    const sampledPredictions = predictionData.filter((_, i) => i % 2 === 0 || i === predictionData.length - 1);

    return [...sampledHistorical, ...sampledPredictions];
  }, [history, prediction]);

  if (chartData.length === 0) {
    return (
      <div className={`rounded-xl p-6 h-96 ${isDark ? 'bg-gray-800' : 'bg-white'} shadow-sm`}>
        <div className={`h-full flex items-center justify-center ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>
          No hay datos disponibles
        </div>
      </div>
    );
  }

  // Calculate domain
  const allRates = chartData.flatMap((d) => [
    d.actual,
    d.predicted,
    d.lower,
    d.upper,
  ]).filter(Boolean) as number[];

  const minRate = Math.min(...allRates) * 0.998;
  const maxRate = Math.max(...allRates) * 1.002;

  // Theme colors
  const colors = {
    grid: isDark ? '#374151' : '#f0f0f0',
    axis: isDark ? '#9ca3af' : '#6b7280',
    text: isDark ? '#e5e7eb' : '#374151',
    textMuted: isDark ? '#9ca3af' : '#6b7280',
    historical: '#3b82f6',
    prediction: '#8b5cf6',
    bounds: isDark ? '#a78bfa' : '#c4b5fd',
    confidence: isDark ? 'rgba(139, 92, 246, 0.2)' : 'rgba(196, 181, 253, 0.3)',
    reference: isDark ? '#64748b' : '#94a3b8',
  };

  return (
    <div className={`rounded-xl p-6 ${isDark ? 'bg-gray-800' : 'bg-white'} shadow-sm`}>
      <div className="flex justify-between items-center mb-4">
        <h3 className={`text-lg font-semibold ${isDark ? 'text-white' : 'text-gray-900'}`}>
          Historico + Prediccion
        </h3>
        <div className="flex items-center gap-4">
          {/* Legend */}
          <div className="hidden sm:flex items-center gap-4 text-xs">
            <div className="flex items-center gap-1">
              <div className="w-3 h-0.5 bg-blue-500"></div>
              <span className={colors.textMuted}>Historico</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-3 h-0.5 bg-purple-500" style={{ borderStyle: 'dashed' }}></div>
              <span className={colors.textMuted}>Prediccion</span>
            </div>
            <div className="flex items-center gap-1">
              <div className={`w-3 h-3 rounded ${isDark ? 'bg-purple-900/50' : 'bg-purple-100'}`}></div>
              <span className={colors.textMuted}>IC 95%</span>
            </div>
          </div>

          {/* Zoom toggle */}
          <button
            onClick={() => setShowBrush(!showBrush)}
            className={`p-1.5 rounded-lg transition-colors ${
              showBrush
                ? 'bg-blue-100 dark:bg-blue-900/40 text-blue-600 dark:text-blue-400'
                : isDark ? 'bg-gray-700 text-gray-400 hover:text-white' : 'bg-gray-100 text-gray-500 hover:text-gray-700'
            }`}
            title={showBrush ? 'Ocultar zoom' : 'Mostrar zoom'}
          >
            {showBrush ? <ZoomOut className="w-4 h-4" /> : <ZoomIn className="w-4 h-4" />}
          </button>
        </div>
      </div>

      <div className={showBrush ? 'h-72' : 'h-80'}>
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={chartData} margin={{ top: 10, right: 20, left: 10, bottom: showBrush ? 30 : 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke={colors.grid} />
            <XAxis
              dataKey="date"
              tick={{ fontSize: 11, fill: colors.axis }}
              stroke={colors.axis}
              interval="preserveStartEnd"
              tickLine={{ stroke: colors.axis }}
            />
            <YAxis
              domain={[minRate, maxRate]}
              tick={{ fontSize: 11, fill: colors.axis }}
              stroke={colors.axis}
              tickFormatter={(value) => value.toFixed(3)}
              width={55}
              tickLine={{ stroke: colors.axis }}
            />
            <Tooltip content={<CustomTooltip isDark={isDark} />} />

            {/* Confidence interval area */}
            <Area
              type="monotone"
              dataKey="range"
              fill={colors.confidence}
              stroke="none"
            />

            {/* Prediction upper bound */}
            <Line
              type="monotone"
              dataKey="upper"
              stroke={colors.bounds}
              strokeWidth={1}
              strokeDasharray="3 3"
              dot={false}
              connectNulls={false}
            />

            {/* Prediction lower bound */}
            <Line
              type="monotone"
              dataKey="lower"
              stroke={colors.bounds}
              strokeWidth={1}
              strokeDasharray="3 3"
              dot={false}
              connectNulls={false}
            />

            {/* Historical actual rates */}
            <Line
              type="monotone"
              dataKey="actual"
              stroke={colors.historical}
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 5, fill: colors.historical, stroke: isDark ? '#1f2937' : '#fff', strokeWidth: 2 }}
              connectNulls={false}
            />

            {/* Predicted rates */}
            <Line
              type="monotone"
              dataKey="predicted"
              stroke={colors.prediction}
              strokeWidth={2}
              strokeDasharray="5 5"
              dot={{ r: 3, fill: colors.prediction }}
              activeDot={{ r: 6, fill: colors.prediction, stroke: isDark ? '#1f2937' : '#fff', strokeWidth: 2 }}
              connectNulls={false}
            />

            {/* Current rate reference line */}
            {history && history.rates.length > 0 && (
              <ReferenceLine
                y={history.rates[history.rates.length - 1].rate}
                stroke={colors.reference}
                strokeDasharray="5 5"
                label={{
                  value: 'Actual',
                  fill: colors.reference,
                  fontSize: 10,
                  position: 'right',
                }}
              />
            )}

            {/* Brush for zoom */}
            {showBrush && (
              <Brush
                dataKey="date"
                height={25}
                stroke={colors.historical}
                fill={isDark ? '#374151' : '#f3f4f6'}
                tickFormatter={() => ''}
              />
            )}
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {prediction && (
        <div className={`mt-4 pt-4 border-t ${isDark ? 'border-gray-700' : 'border-gray-100'} flex flex-wrap justify-between gap-2 text-sm`}>
          <span className={isDark ? 'text-gray-400' : 'text-gray-500'}>
            Modelo: <strong className={isDark ? 'text-gray-200' : 'text-gray-700'}>{prediction.model_type}</strong>
          </span>
          <span className={isDark ? 'text-gray-400' : 'text-gray-500'}>
            Confianza: <strong className={isDark ? 'text-gray-200' : 'text-gray-700'}>{(prediction.confidence_level * 100).toFixed(0)}%</strong>
          </span>
          <span className={isDark ? 'text-gray-400' : 'text-gray-500'}>
            Generado: <strong className={isDark ? 'text-gray-200' : 'text-gray-700'}>
              {new Date(prediction.generated_at).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })}
            </strong>
          </span>
        </div>
      )}
    </div>
  );
}
