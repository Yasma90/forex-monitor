# API Documentation

Base URL: `http://localhost:8000`

Documentacion interactiva disponible en `/docs` (Swagger UI).

## Exchange Rate

### GET /api/exchange/rate

Obtiene la tasa de cambio actual.

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| base | string | USD | Moneda base |
| target | string | EUR | Moneda objetivo |

**Response:**
```json
{
  "id": 1,
  "base_currency": "USD",
  "target_currency": "EUR",
  "rate": 0.92,
  "source": "frankfurter",
  "timestamp": "2024-12-21T10:30:00",
  "change_24h": -0.003,
  "change_percent_24h": -0.32
}
```

### GET /api/exchange/history

Obtiene historico de tasas.

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| base | string | USD | Moneda base |
| target | string | EUR | Moneda objetivo |
| days | int | 30 | Dias de historia (1-365) |

**Response:**
```json
{
  "rates": [
    {
      "id": 1,
      "base_currency": "USD",
      "target_currency": "EUR",
      "rate": 0.92,
      "source": "frankfurter",
      "timestamp": "2024-12-20T10:30:00"
    }
  ],
  "min_rate": 0.90,
  "max_rate": 0.94,
  "avg_rate": 0.92,
  "period_days": 30
}
```

### POST /api/exchange/refresh

Fuerza actualizacion de la tasa.

**Response:**
```json
{
  "id": 100,
  "base_currency": "USD",
  "target_currency": "EUR",
  "rate": 0.92,
  "source": "frankfurter",
  "timestamp": "2024-12-21T10:35:00"
}
```

---

## News

### GET /api/news/feed

Obtiene noticias con analisis de sentimiento.

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| limit | int | 20 | Numero de noticias |
| hours | int | 48 | Horas hacia atras |
| sentiment | string | null | Filtrar: positive/negative/neutral |

**Response:**
```json
{
  "articles": [
    {
      "id": 1,
      "title": "Fed raises interest rates",
      "description": "The Federal Reserve...",
      "url": "https://...",
      "source": "Reuters",
      "published_at": "2024-12-21T09:00:00",
      "sentiment_score": -0.3,
      "sentiment_label": "negative",
      "relevance_score": 0.85,
      "keywords_matched": "fed,interest rate"
    }
  ],
  "total": 15,
  "sentiment_summary": {
    "positive": 5,
    "negative": 7,
    "neutral": 3
  },
  "avg_sentiment": -0.15
}
```

### GET /api/news/sentiment-summary

Resumen de sentimiento de noticias recientes.

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| hours | int | 24 | Periodo en horas |

**Response:**
```json
{
  "positive": 5,
  "negative": 7,
  "neutral": 3
}
```

---

## Prediction

### GET /api/prediction/forecast

Genera prediccion de tipo de cambio.

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| days | int | 7 | Dias a predecir (1-30) |

**Response:**
```json
{
  "predictions": [
    {
      "date": "2024-12-22",
      "predicted_rate": 0.921,
      "lower_bound": 0.915,
      "upper_bound": 0.927,
      "confidence": 0.85
    }
  ],
  "model_type": "trend_ema",
  "sentiment_adjustment": -0.002,
  "current_rate": 0.92,
  "generated_at": "2024-12-21T10:30:00"
}
```

### GET /api/prediction/signal

Obtiene senal de trading rapida.

**Response:**
```json
{
  "signal": "BEARISH",
  "strength": 0.65,
  "reasons": [
    "Tendencia bajista en 7 dias",
    "Sentimiento negativo en noticias"
  ],
  "recommendation": "El EUR podria debilitarse frente al USD",
  "generated_at": "2024-12-21T10:30:00"
}
```

---

## Alerts

### GET /api/alerts

Lista todas las alertas.

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| include_inactive | bool | false | Incluir alertas inactivas |

**Response:**
```json
[
  {
    "id": 1,
    "name": "EUR baja de 0.90",
    "alert_type": "price_below",
    "base_currency": "USD",
    "target_currency": "EUR",
    "threshold_value": 0.90,
    "status": "active",
    "is_recurring": true,
    "cooldown_minutes": 60,
    "created_at": "2024-12-20T10:00:00",
    "last_triggered_at": null
  }
]
```

### POST /api/alerts

Crea una nueva alerta.

**Request Body:**
```json
{
  "name": "EUR baja de 0.90",
  "alert_type": "price_below",
  "base_currency": "USD",
  "target_currency": "EUR",
  "threshold_value": 0.90,
  "is_recurring": true,
  "cooldown_minutes": 60,
  "notify_push": true,
  "notify_sound": true
}
```

**Alert Types:**
| Type | Description |
|------|-------------|
| price_above | Tasa supera umbral |
| price_below | Tasa cae bajo umbral |
| percent_change | Cambio % en 24h supera umbral |
| sentiment | Sentimiento cruza umbral |
| news_impact | Noticias de alto impacto |

### PUT /api/alerts/{id}

Actualiza una alerta.

**Request Body:**
```json
{
  "name": "Nuevo nombre",
  "threshold_value": 0.89,
  "status": "paused"
}
```

### DELETE /api/alerts/{id}

Elimina una alerta.

### GET /api/alerts/history

Historial de alertas disparadas.

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| alert_id | int | null | Filtrar por alerta |
| limit | int | 50 | Limite de resultados |

---

## System

### GET /api/system/cache/stats

Estadisticas de cache.

**Response:**
```json
{
  "exchange_rate": {
    "entries": 10,
    "hits": 150,
    "misses": 20,
    "hit_rate": "88.2%",
    "max_entries": 100,
    "default_ttl": 300
  },
  "news": {...},
  "prediction": {...}
}
```

### POST /api/system/cache/clear

Limpia todos los caches.

### GET /api/system/scheduler/status

Estado del scheduler.

**Response:**
```json
{
  "running": true,
  "task_count": 4,
  "tasks": {
    "refresh_rate": {
      "name": "refresh_rate",
      "interval_seconds": 1800,
      "enabled": true,
      "last_run": "2024-12-21T10:30:00",
      "run_count": 48,
      "error_count": 0
    }
  }
}
```

### GET /api/system/prediction/accuracy

Verifica precision de predicciones recientes.

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| days | int | 7 | Dias a verificar (3-30) |

**Response:**
```json
{
  "average_error": 0.003,
  "max_error": 0.008,
  "in_bounds_percentage": 85.7,
  "comparisons": [...],
  "model_type": "trend_ema",
  "assessment": "bueno"
}
```

### POST /api/system/prediction/backtest

Ejecuta backtesting completo.

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| lookback_days | int | 30 | Dias de entrenamiento |
| prediction_horizon | int | 7 | Dias a predecir |

**Response:**
```json
{
  "predictions_count": 23,
  "actuals_count": 23,
  "metrics": {
    "mae": 0.0025,
    "rmse": 0.0031,
    "mape": 0.27,
    "direction_accuracy": 65.2,
    "confidence_interval_accuracy": 82.6,
    "bias": -0.0003,
    "sample_size": 23,
    "interpretation": "Predicciones razonablemente precisas, buena prediccion de tendencia"
  },
  "generated_at": "2024-12-21T10:30:00"
}
```

### GET /api/system/metrics

Metricas generales del sistema.

**Response:**
```json
{
  "exchange": {
    "data_points_30d": 1440,
    "min_rate": 0.90,
    "max_rate": 0.94,
    "avg_rate": 0.92
  },
  "news": {
    "sentiment_24h": {"positive": 5, "negative": 7, "neutral": 3},
    "total_articles_24h": 15
  },
  "alerts": {
    "total": 5,
    "active": 3,
    "triggered": 2
  },
  "cache": {...},
  "scheduler": {...}
}
```

---

## Codigos de Error

| Code | Description |
|------|-------------|
| 200 | OK |
| 201 | Created |
| 400 | Bad Request - Parametros invalidos |
| 404 | Not Found - Recurso no existe |
| 422 | Validation Error - Datos no pasan validacion |
| 500 | Internal Server Error |

**Formato de error:**
```json
{
  "detail": "Mensaje de error descriptivo"
}
```

---

## Rate Limits

Actualmente no hay rate limiting implementado. APIs externas tienen sus propios limites:

| API | Limite |
|-----|--------|
| Frankfurter | Ilimitado |
| ExchangeRate-API | 1500/mes |
| GNews | 100/dia |
| NewsData | 200/dia |
