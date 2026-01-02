'use client';

import {
  ComposedChart,
  Line,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  ReferenceLine,
} from 'recharts';
import { ExchangeRateHistory, Prediction } from '@/lib/api';

interface PredictionChartProps {
  history: ExchangeRateHistory | null;
  prediction: Prediction | null;
  loading: boolean;
}

export default function PredictionChart({ history, prediction, loading }: PredictionChartProps) {
  if (loading && !history) {
    return (
      <div className="card h-96">
        <div className="animate-pulse h-full flex items-center justify-center">
          <div className="text-gray-400">Cargando datos...</div>
        </div>
      </div>
    );
  }

  // Prepare historical data
  const historicalData = history?.rates.map((r) => ({
    date: new Date(r.timestamp).toLocaleDateString('es-ES', {
      month: 'short',
      day: 'numeric',
    }),
    fullDate: new Date(r.timestamp).toLocaleString('es-ES'),
    actual: r.rate,
    type: 'historical',
  })) || [];

  // Sample historical data to avoid overcrowding
  const sampledHistorical = historicalData.filter(
    (_, i) => i % Math.max(1, Math.floor(historicalData.length / 20)) === 0
  );

  // Prepare prediction data
  const predictionData = prediction?.predictions.map((p) => ({
    date: new Date(p.date).toLocaleDateString('es-ES', {
      month: 'short',
      day: 'numeric',
    }),
    fullDate: new Date(p.date).toLocaleString('es-ES'),
    predicted: p.predicted_rate,
    lower: p.lower_bound,
    upper: p.upper_bound,
    range: [p.lower_bound, p.upper_bound],
    type: 'prediction',
  })) || [];

  // Sample predictions (show every 3rd day for cleaner chart)
  const sampledPredictions = predictionData.filter((_, i) => i % 3 === 0 || i === predictionData.length - 1);

  // Combine data
  const chartData = [...sampledHistorical, ...sampledPredictions];

  if (chartData.length === 0) {
    return (
      <div className="card h-96">
        <div className="h-full flex items-center justify-center text-gray-500">
          No hay datos disponibles
        </div>
      </div>
    );
  }

  // Calculate domain
  const allRates = [
    ...sampledHistorical.map((d) => d.actual),
    ...sampledPredictions.map((d) => d.predicted),
    ...sampledPredictions.map((d) => d.lower),
    ...sampledPredictions.map((d) => d.upper),
  ].filter(Boolean) as number[];

  const minRate = Math.min(...allRates) * 0.995;
  const maxRate = Math.max(...allRates) * 1.005;

  return (
    <div className="card">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-900">
          Historico + Prediccion
        </h3>
        <div className="flex items-center gap-4 text-xs">
          <div className="flex items-center gap-1">
            <div className="w-3 h-0.5 bg-blue-500"></div>
            <span className="text-gray-500">Historico</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-0.5 bg-purple-500 border-dashed"></div>
            <span className="text-gray-500">Prediccion</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 bg-purple-100 rounded"></div>
            <span className="text-gray-500">Intervalo 95%</span>
          </div>
        </div>
      </div>

      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={chartData} margin={{ top: 10, right: 20, left: 10, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis
              dataKey="date"
              tick={{ fontSize: 11 }}
              stroke="#9ca3af"
              interval="preserveStartEnd"
            />
            <YAxis
              domain={[minRate, maxRate]}
              tick={{ fontSize: 11 }}
              stroke="#9ca3af"
              tickFormatter={(value) => value.toFixed(3)}
              width={50}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: 'white',
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
              }}
              formatter={(value: number, name: string) => {
                const labels: Record<string, string> = {
                  actual: 'Actual',
                  predicted: 'Prediccion',
                  lower: 'Minimo',
                  upper: 'Maximo',
                };
                return [value?.toFixed(4), labels[name] || name];
              }}
              labelFormatter={(label, payload) => {
                if (payload && payload[0]) {
                  return payload[0].payload.fullDate;
                }
                return label;
              }}
            />

            {/* Confidence interval area */}
            <Area
              type="monotone"
              dataKey="range"
              fill="#c4b5fd"
              fillOpacity={0.3}
              stroke="none"
            />

            {/* Prediction upper bound */}
            <Line
              type="monotone"
              dataKey="upper"
              stroke="#a78bfa"
              strokeWidth={1}
              strokeDasharray="3 3"
              dot={false}
              connectNulls={false}
            />

            {/* Prediction lower bound */}
            <Line
              type="monotone"
              dataKey="lower"
              stroke="#a78bfa"
              strokeWidth={1}
              strokeDasharray="3 3"
              dot={false}
              connectNulls={false}
            />

            {/* Historical actual rates */}
            <Line
              type="monotone"
              dataKey="actual"
              stroke="#3b82f6"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 5, fill: '#3b82f6' }}
              connectNulls={false}
            />

            {/* Predicted rates */}
            <Line
              type="monotone"
              dataKey="predicted"
              stroke="#8b5cf6"
              strokeWidth={2}
              strokeDasharray="5 5"
              dot={{ r: 3, fill: '#8b5cf6' }}
              activeDot={{ r: 6, fill: '#8b5cf6' }}
              connectNulls={false}
            />

            {/* Current rate reference line */}
            {history && history.rates.length > 0 && (
              <ReferenceLine
                y={history.rates[history.rates.length - 1].rate}
                stroke="#94a3b8"
                strokeDasharray="5 5"
                label={{
                  value: 'Actual',
                  fill: '#94a3b8',
                  fontSize: 10,
                  position: 'right',
                }}
              />
            )}
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {prediction && (
        <div className="mt-4 pt-4 border-t border-gray-100 flex justify-between text-sm text-gray-500">
          <span>
            Modelo: <strong className="text-gray-700">{prediction.model_type}</strong>
          </span>
          <span>
            Confianza: <strong className="text-gray-700">{(prediction.confidence_level * 100).toFixed(0)}%</strong>
          </span>
          <span>
            Generado: <strong className="text-gray-700">
              {new Date(prediction.generated_at).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })}
            </strong>
          </span>
        </div>
      )}
    </div>
  );
}
