const API_BASE = process.env.NEXT_PUBLIC_API_URL || '';

export interface ExchangeRate {
  id: number;
  base_currency: string;
  target_currency: string;
  rate: number;
  source: string;
  timestamp: string;
  change_24h: number | null;
  change_percent_24h: number | null;
}

export interface ExchangeRateHistory {
  rates: ExchangeRate[];
  min_rate: number;
  max_rate: number;
  avg_rate: number;
  period_days: number;
}

export async function getCurrentRate(
  base: string = 'USD',
  target: string = 'EUR'
): Promise<ExchangeRate> {
  const res = await fetch(
    `${API_BASE}/api/exchange/rate?base=${base}&target=${target}`,
    { cache: 'no-store' }
  );
  if (!res.ok) {
    throw new Error('Failed to fetch exchange rate');
  }
  return res.json();
}

export async function getRateHistory(
  base: string = 'USD',
  target: string = 'EUR',
  days: number = 30
): Promise<ExchangeRateHistory> {
  const res = await fetch(
    `${API_BASE}/api/exchange/history?base=${base}&target=${target}&days=${days}`,
    { cache: 'no-store' }
  );
  if (!res.ok) {
    throw new Error('Failed to fetch rate history');
  }
  return res.json();
}

export async function refreshRate(
  base: string = 'USD',
  target: string = 'EUR'
): Promise<{ message: string; rate: number; source: string }> {
  const res = await fetch(
    `${API_BASE}/api/exchange/refresh?base=${base}&target=${target}`,
    { method: 'POST' }
  );
  if (!res.ok) {
    throw new Error('Failed to refresh rate');
  }
  return res.json();
}
