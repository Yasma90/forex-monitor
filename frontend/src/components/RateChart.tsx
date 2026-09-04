'use client';

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import { ExchangeRateHistory } from '@/lib/api';

interface RateChartProps {
  history: ExchangeRateHistory | null;
  loading: boolean;
}

export default function RateChart({ history, loading }: RateChartProps) {
  if (loading && !history) {
    return (
      <div className="card h-80">
        <div className="animate-pulse h-full flex items-center justify-center">
          <div className="text-gray-400">Cargando historico...</div>
        </div>
      </div>
    );
  }

  if (!history || history.rates.length === 0) {
    return (
      <div className="card h-80">
        <div className="h-full flex items-center justify-center text-gray-500">
          No hay datos historicos disponibles
        </div>
      </div>
    );
  }

  const chartData = history.rates.map((r) => ({
    date: new Date(r.timestamp).toLocaleDateString('es-ES', {
      month: 'short',
      day: 'numeric',
    }),
    rate: r.rate,
    fullDate: new Date(r.timestamp).toLocaleString('es-ES'),
  }));

  // Take samples to avoid overcrowding
  const sampledData = chartData.filter((_, i) => i % Math.max(1, Math.floor(chartData.length / 30)) === 0);

  return (
    <div className="card">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-900">
          Historico ({history.period_days} dias)
        </h3>
        <div className="flex gap-4 text-sm text-gray-500">
          <span>Min: <strong>{history.min_rate.toFixed(4)}</strong></span>
          <span>Max: <strong>{history.max_rate.toFixed(4)}</strong></span>
          <span>Prom: <strong>{history.avg_rate.toFixed(4)}</strong></span>
        </div>
      </div>

      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={sampledData} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis
              dataKey="date"
              tick={{ fontSize: 12 }}
              stroke="#9ca3af"
            />
            <YAxis
              domain={['auto', 'auto']}
              tick={{ fontSize: 12 }}
              stroke="#9ca3af"
              tickFormatter={(value) => value.toFixed(3)}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: 'white',
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
              }}
              formatter={(value: number) => [value.toFixed(4), 'Tasa']}
              labelFormatter={(label, payload) => {
                if (payload && payload[0]) {
                  return payload[0].payload.fullDate;
                }
                return label;
              }}
            />
            <ReferenceLine
              y={history.avg_rate}
              stroke="#94a3b8"
              strokeDasharray="5 5"
              label={{ value: 'Prom', fill: '#94a3b8', fontSize: 10 }}
            />
            <Line
              type="monotone"
              dataKey="rate"
              stroke="#3b82f6"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 6, fill: '#3b82f6' }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
