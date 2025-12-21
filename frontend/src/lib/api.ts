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

// News API types
export interface NewsArticle {
  id: number;
  title: string;
  description: string | null;
  url: string;
  source: string;
  image_url: string | null;
  published_at: string;
  sentiment_score: number | null;
  sentiment_label: 'positive' | 'negative' | 'neutral' | null;
  relevance_score: number | null;
  keywords_matched: string | null;
}

export interface NewsFeed {
  articles: NewsArticle[];
  total: number;
  sentiment_summary: {
    positive: number;
    negative: number;
    neutral: number;
  };
  avg_sentiment: number;
}

export interface SentimentSummary {
  summary: {
    positive: number;
    negative: number;
    neutral: number;
  };
  total_articles: number;
  avg_sentiment: number;
  mood: 'BULLISH' | 'BEARISH' | 'NEUTRAL';
  mood_description: string;
  period_hours: number;
}

export async function getNewsFeed(
  limit: number = 20,
  hours: number = 48
): Promise<NewsFeed> {
  const res = await fetch(
    `${API_BASE}/api/news/feed?limit=${limit}&hours=${hours}`,
    { cache: 'no-store' }
  );
  if (!res.ok) {
    throw new Error('Failed to fetch news');
  }
  return res.json();
}

export async function getSentimentSummary(
  hours: number = 24
): Promise<SentimentSummary> {
  const res = await fetch(
    `${API_BASE}/api/news/sentiment-summary?hours=${hours}`,
    { cache: 'no-store' }
  );
  if (!res.ok) {
    throw new Error('Failed to fetch sentiment summary');
  }
  return res.json();
}

// Prediction API types
export interface PredictionPoint {
  date: string;
  predicted_rate: number;
  lower_bound: number;
  upper_bound: number;
}

export interface Prediction {
  base_currency: string;
  target_currency: string;
  current_rate: number;
  predictions: PredictionPoint[];
  signal: 'BULLISH' | 'BEARISH' | 'NEUTRAL';
  signal_strength: number;
  signal_description: string;
  sentiment_impact: number;
  sentiment_mood: string;
  model_type: string;
  confidence_level: number;
  generated_at: string;
  predicted_change_7d: number;
  predicted_change_30d: number;
}

export interface QuickSignal {
  signal: 'BULLISH' | 'BEARISH' | 'NEUTRAL';
  strength: number;
  description: string;
  factors: string[];
}

export async function getPrediction(
  days: number = 30
): Promise<Prediction> {
  const res = await fetch(
    `${API_BASE}/api/prediction/forecast?days=${days}`,
    { cache: 'no-store' }
  );
  if (!res.ok) {
    throw new Error('Failed to fetch prediction');
  }
  return res.json();
}

export async function getQuickSignal(): Promise<QuickSignal> {
  const res = await fetch(
    `${API_BASE}/api/prediction/signal`,
    { cache: 'no-store' }
  );
  if (!res.ok) {
    throw new Error('Failed to fetch signal');
  }
  return res.json();
}

// Alerts API types
export type AlertType = 'price_above' | 'price_below' | 'percent_change' | 'sentiment' | 'news_impact';
export type AlertStatus = 'active' | 'triggered' | 'paused' | 'expired';

export interface Alert {
  id: number;
  name: string;
  alert_type: AlertType;
  base_currency: string;
  target_currency: string;
  threshold_value: number;
  status: AlertStatus;
  is_recurring: boolean;
  cooldown_minutes: number;
  notify_push: boolean;
  notify_sound: boolean;
  created_at: string;
  last_triggered_at: string | null;
  expires_at: string | null;
}

export interface AlertCreate {
  name: string;
  alert_type: AlertType;
  threshold_value: number;
  base_currency?: string;
  target_currency?: string;
  is_recurring?: boolean;
  cooldown_minutes?: number;
  notify_push?: boolean;
  notify_sound?: boolean;
}

export interface AlertTemplate {
  name: string;
  description: string;
  config: Partial<AlertCreate>;
}

export interface TriggeredAlert {
  alert: Alert;
  current_value: number;
  message: string;
  triggered_at: string;
}

export async function getAlerts(includeInactive: boolean = false): Promise<Alert[]> {
  const res = await fetch(
    `${API_BASE}/api/alerts/?include_inactive=${includeInactive}`,
    { cache: 'no-store' }
  );
  if (!res.ok) throw new Error('Failed to fetch alerts');
  return res.json();
}

export async function createAlert(data: AlertCreate): Promise<Alert> {
  const res = await fetch(`${API_BASE}/api/alerts/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  if (!res.ok) throw new Error('Failed to create alert');
  return res.json();
}

export async function deleteAlert(id: number): Promise<void> {
  const res = await fetch(`${API_BASE}/api/alerts/${id}`, {
    method: 'DELETE'
  });
  if (!res.ok) throw new Error('Failed to delete alert');
}

export async function pauseAlert(id: number): Promise<Alert> {
  const res = await fetch(`${API_BASE}/api/alerts/${id}/pause`, {
    method: 'POST'
  });
  if (!res.ok) throw new Error('Failed to pause alert');
  return res.json();
}

export async function resumeAlert(id: number): Promise<Alert> {
  const res = await fetch(`${API_BASE}/api/alerts/${id}/resume`, {
    method: 'POST'
  });
  if (!res.ok) throw new Error('Failed to resume alert');
  return res.json();
}

export async function checkAlerts(): Promise<TriggeredAlert[]> {
  const res = await fetch(`${API_BASE}/api/alerts/check`, {
    method: 'POST'
  });
  if (!res.ok) throw new Error('Failed to check alerts');
  return res.json();
}

export async function getAlertTemplates(): Promise<AlertTemplate[]> {
  const res = await fetch(`${API_BASE}/api/alerts/templates/common`);
  if (!res.ok) throw new Error('Failed to fetch templates');
  return res.json();
}
