# Arquitectura del Sistema

## Vision General

Forex Monitor es una aplicacion de monitoreo de tipo de cambio USD/EUR construida con una arquitectura de 3 capas: Frontend (Next.js), Backend (FastAPI), y Data Layer (SQLite).

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENTE                                  │
│  ┌─────────────────┐    ┌─────────────────┐                     │
│  │   Web Browser   │    │  PWA (Mobile)   │                     │
│  │   Next.js SSR   │    │  Service Worker │                     │
│  └────────┬────────┘    └────────┬────────┘                     │
│           └──────────┬───────────┘                               │
└──────────────────────┼──────────────────────────────────────────┘
                       │ HTTP/REST
┌──────────────────────┼──────────────────────────────────────────┐
│                   BACKEND (FastAPI)                              │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    API Layer (Routes)                        ││
│  │  /exchange  /news  /prediction  /alerts  /system            ││
│  └─────────────────────────────────────────────────────────────┘│
│                            │                                     │
│  ┌─────────────────────────┼───────────────────────────────────┐│
│  │                  Service Layer                               ││
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       ││
│  │  │ Exchange │ │   News   │ │Prediction│ │  Alerts  │       ││
│  │  │ Service  │ │ Service  │ │  Engine  │ │ Service  │       ││
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘       ││
│  └─────────────────────────┼───────────────────────────────────┘│
│                            │                                     │
│  ┌─────────────────────────┼───────────────────────────────────┐│
│  │              Infrastructure Layer                            ││
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐                     ││
│  │  │  Cache   │ │Scheduler │ │Repository│                     ││
│  │  │(In-Memory│ │ (Tasks)  │ │(SQLAlchemy)                    ││
│  │  └──────────┘ └──────────┘ └──────────┘                     ││
│  └─────────────────────────────────────────────────────────────┘│
└──────────────────────┼──────────────────────────────────────────┘
                       │
┌──────────────────────┼──────────────────────────────────────────┐
│                   DATA LAYER                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   SQLite    │  │  External   │  │   File      │              │
│  │  Database   │  │    APIs     │  │   System    │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

## Componentes Principales

### 1. Frontend (Next.js 14)

**Tecnologias:**
- Next.js 14 con App Router
- React 18 con Server Components
- TypeScript para tipado estatico
- Tailwind CSS para estilos
- Recharts para graficos

**Estructura:**
```
frontend/src/
├── app/                    # App Router pages
│   ├── page.tsx           # Dashboard principal
│   ├── layout.tsx         # Layout global
│   └── globals.css        # Estilos globales
├── components/            # Componentes React
│   ├── ExchangeCard.tsx   # Tasa actual
│   ├── PredictionChart.tsx# Grafico de predicciones
│   ├── PredictionCard.tsx # Resumen de prediccion
│   ├── NewsFeed.tsx       # Lista de noticias
│   ├── SentimentGauge.tsx # Medidor de sentimiento
│   ├── SignalBadge.tsx    # Senal de trading
│   └── AlertsPanel.tsx    # Panel de alertas
└── lib/
    ├── api.ts             # Cliente API tipado
    └── notifications.ts   # Web Push API
```

**Patrones:**
- Server Components por defecto para mejor SEO
- Client Components (`'use client'`) solo donde necesario
- Fetching de datos con `fetch` y `cache: 'no-store'`
- Error boundaries para manejo de errores

### 2. Backend (FastAPI)

**Tecnologias:**
- FastAPI para API REST async
- SQLAlchemy 2.0 con async support
- Pydantic v2 para validacion
- aiosqlite para SQLite async

**Estructura:**
```
backend/app/
├── api/routes/            # Endpoints REST
│   ├── exchange.py        # /api/exchange/*
│   ├── news.py            # /api/news/*
│   ├── prediction.py      # /api/prediction/*
│   ├── alerts.py          # /api/alerts/*
│   └── system.py          # /api/system/*
├── models/                # Modelos de datos
│   ├── database.py        # Configuracion SQLAlchemy
│   ├── exchange.py        # ExchangeRate model
│   ├── news.py            # NewsArticle model
│   └── alert.py           # Alert, AlertHistory models
├── services/              # Logica de negocio
│   ├── exchange/          # Fetcher, Repository
│   ├── news/              # Fetcher, Sentiment, Keywords
│   ├── prediction/        # Engine, Signals, Backtesting
│   ├── alerts/            # Service, Checker
│   └── cache.py           # InMemoryCache
└── jobs/
    └── scheduler.py       # Tareas programadas
```

**Patrones:**
- Repository Pattern para acceso a datos
- Service Layer para logica de negocio
- Dependency Injection con `Depends()`
- Async/await para operaciones I/O

### 3. Data Layer

**Base de Datos (SQLite):**
```
┌─────────────────────────────────────────────────────────────┐
│                        TABLES                                │
├─────────────────────────────────────────────────────────────┤
│  exchange_rates          │  news_articles                   │
│  ─────────────────       │  ────────────────                │
│  id (PK)                 │  id (PK)                         │
│  base_currency           │  title                           │
│  target_currency         │  description                     │
│  rate                    │  url (UNIQUE)                    │
│  source                  │  source                          │
│  timestamp               │  published_at                    │
│                          │  sentiment_score                 │
│                          │  sentiment_label                 │
│                          │  relevance_score                 │
├─────────────────────────────────────────────────────────────┤
│  alerts                  │  alert_history                   │
│  ──────                  │  ─────────────                   │
│  id (PK)                 │  id (PK)                         │
│  name                    │  alert_id (FK)                   │
│  alert_type              │  triggered_at                    │
│  threshold_value         │  trigger_value                   │
│  status                  │  message                         │
│  is_recurring            │                                  │
│  cooldown_minutes        │                                  │
│  user_id                 │                                  │
└─────────────────────────────────────────────────────────────┘
```

**Indices:**
- `ix_exchange_rates_currencies_timestamp` - Consultas por par de monedas
- `ix_news_published_at` - Ordenar noticias por fecha
- `ix_news_published_sentiment` - Filtrar por sentimiento
- `ix_alerts_status` - Filtrar alertas activas
- `ix_alert_history_alert_id` - Buscar historial por alerta

### 4. Sistema de Cache

```
┌─────────────────────────────────────────────────────────────┐
│                    CACHE LAYER                               │
├─────────────────────────────────────────────────────────────┤
│  exchange_rate_cache     │  TTL: 5 min   │  Max: 100       │
│  news_cache              │  TTL: 15 min  │  Max: 500       │
│  prediction_cache        │  TTL: 30 min  │  Max: 50        │
└─────────────────────────────────────────────────────────────┘

Estrategia:
1. Check cache → hit → return cached
2. Cache miss → fetch from source
3. Store in cache with TTL
4. Background cleanup de expired entries
```

### 5. Scheduler (Tareas Programadas)

```
┌─────────────────────────────────────────────────────────────┐
│                    SCHEDULED TASKS                           │
├─────────────────────────────────────────────────────────────┤
│  Task              │  Interval    │  Description            │
│  ─────────────────────────────────────────────────────────  │
│  refresh_rate      │  30 min      │  Actualizar tipo cambio │
│  check_alerts      │  5 min       │  Verificar alertas      │
│  cleanup_cache     │  1 hora      │  Limpiar cache expirado │
│  cleanup_data      │  24 horas    │  Eliminar datos viejos  │
└─────────────────────────────────────────────────────────────┘
```

## Flujos de Datos

### 1. Obtener Tipo de Cambio

```
Cliente → GET /api/exchange/rate
    │
    ▼
[Check Cache] ──hit──→ Return cached
    │
    miss
    ▼
[ExchangeRepository.get_latest()]
    │
    ▼
[Database Query]
    │
    ▼
Return ExchangeRate + Store in Cache
```

### 2. Generar Prediccion

```
Cliente → GET /api/prediction/forecast?days=7
    │
    ▼
[Check Prediction Cache] ──hit──→ Return cached
    │
    miss
    ▼
[Get Historical Data] → 60 dias de historia
    │
    ▼
[Get Sentiment Score] → Promedio ultimas 24h
    │
    ▼
[PredictionEngine.predict()]
    │
    ├──→ [Prophet Model] (si disponible)
    │
    └──→ [Fallback: Trend + EMA] (por defecto)
    │
    ▼
[Apply Sentiment Adjustment]
    │
    ▼
Return Predictions + Confidence Intervals
```

### 3. Verificar Alertas

```
[Scheduler: cada 5 min]
    │
    ▼
[AlertService.get_all_alerts(status=active)]
    │
    ▼
[Get Current Rate + Sentiment]
    │
    ▼
[AlertChecker.check_alerts()]
    │
    ├──→ PRICE_ABOVE: rate >= threshold
    ├──→ PRICE_BELOW: rate <= threshold
    ├──→ PERCENT_CHANGE: |change_24h| >= threshold
    └──→ SENTIMENT_SHIFT: sentiment <= threshold
    │
    ▼
[For each triggered alert]
    │
    ├──→ Update last_triggered_at
    ├──→ Log to AlertHistory
    └──→ Send Push Notification
```

## Decisiones de Arquitectura

### ADR-001: SQLite vs PostgreSQL

**Decision:** Usar SQLite para desarrollo y produccion inicial.

**Contexto:** Necesitamos una base de datos simple para almacenar tasas de cambio y alertas.

**Razones:**
- Zero configuration
- Suficiente para un solo usuario
- Facil backup (un solo archivo)
- Compatible con async via aiosqlite

**Consecuencias:**
- Migrar a PostgreSQL si se necesita multi-usuario
- No soporta conexiones concurrentes pesadas

### ADR-002: Cache In-Memory vs Redis

**Decision:** Usar cache in-memory simple.

**Contexto:** Queremos reducir llamadas a APIs externas.

**Razones:**
- Sin dependencias externas
- Suficiente para una instancia
- Configurable con TTL

**Consecuencias:**
- Cache se pierde al reiniciar
- Migrar a Redis si se escala horizontalmente

### ADR-003: Prophet vs Modelo Custom

**Decision:** Prophet opcional, fallback a modelo basado en tendencia.

**Contexto:** Prophet tiene dependencias pesadas pero es mas preciso.

**Razones:**
- Funciona sin Prophet instalado
- Usuario puede instalar Prophet para mejor precision
- Modelo fallback usa numpy (ya requerido)

**Consecuencias:**
- Dos paths de codigo a mantener
- Predicciones menos precisas sin Prophet

### ADR-004: Next.js App Router

**Decision:** Usar App Router de Next.js 14.

**Contexto:** Necesitamos un frontend moderno con buen SEO.

**Razones:**
- Server Components por defecto
- Mejor performance
- Layouts anidados
- Streaming y Suspense

**Consecuencias:**
- Curva de aprendizaje para Server vs Client Components
- Algunos paquetes no compatibles aun

## Seguridad

### Actual
- CORS configurado para origenes especificos
- Validacion de input con Pydantic
- SQL injection prevenido por SQLAlchemy ORM

### Pendiente
- Autenticacion JWT
- Rate limiting
- HTTPS en produccion
- Sanitizacion de datos de APIs externas

## Escalabilidad

### Actual (1 usuario)
- SQLite local
- Cache in-memory
- Single instance

### Futuro (multi-usuario)
```
                    ┌─────────────┐
                    │   Nginx     │
                    │   (LB)      │
                    └──────┬──────┘
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │  Backend 1  │ │  Backend 2  │ │  Backend 3  │
    └──────┬──────┘ └──────┬──────┘ └──────┬──────┘
           └───────────────┼───────────────┘
                           ▼
                    ┌─────────────┐
                    │    Redis    │
                    │   (Cache)   │
                    └──────┬──────┘
                           ▼
                    ┌─────────────┐
                    │ PostgreSQL  │
                    │    (DB)     │
                    └─────────────┘
```

## Monitoreo

### Metricas disponibles en /api/system/metrics
- Conteo de registros en BD
- Estadisticas de cache (hits, misses, hit rate)
- Estado del scheduler
- Alertas activas/disparadas

### Pendiente
- Integracion Prometheus
- Dashboard Grafana
- Alertas de sistema (errores, latencia)
