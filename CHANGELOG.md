# Changelog

Todos los cambios notables en este proyecto seran documentados aqui.

El formato esta basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [1.0.0] - 2024-12-21

### Agregado - Fase 5: Refinamiento
- Sistema de cache en memoria con TTL configurable
- Servicio de backtesting para evaluar precision de predicciones
- Scheduler de tareas en background (refresh rate, check alerts, cleanup)
- 63 tests unitarios (cache, sentiment, scheduler, alerts)
- Indices optimizados en base de datos
- Limpieza automatica de datos antiguos
- Endpoints de sistema (`/api/system/*`) para monitoreo
- Documentacion profesional (README, CONTRIBUTING, CHANGELOG)

### Mejorado
- Queries de base de datos optimizadas con indices compuestos
- Insercion batch de articulos de noticias
- Metodo `get_daily_rates()` para consultas eficientes de largo plazo

## [0.4.0] - 2024-12-20

### Agregado - Fase 4: Alertas + PWA
- Sistema de alertas con 5 tipos:
  - Precio sube/baja a umbral
  - Cambio porcentual en 24h
  - Cambio de sentimiento
  - Noticias de alto impacto
- Modelo de alertas con cooldown y recurrencia
- AlertChecker para verificacion automatica
- Historial de alertas disparadas
- Notificaciones push en navegador (Web Push API)
- Service Worker para PWA
- Manifest.json para instalacion como app
- Componente AlertsPanel en frontend
- Soporte offline con cache de assets

## [0.3.0] - 2024-12-19

### Agregado - Fase 3: Predicciones ML
- Motor de predicciones con soporte Prophet (opcional)
- Modelo fallback basado en tendencia + suavizado exponencial
- Ajuste de predicciones por sentimiento de noticias
- Generador de senales de trading (BULLISH/BEARISH/NEUTRAL)
- Intervalos de confianza en predicciones
- Endpoints `/api/prediction/forecast` y `/api/prediction/signal`
- Componentes PredictionChart y PredictionCard
- SignalBadge con indicadores visuales

## [0.2.0] - 2024-12-18

### Agregado - Fase 2: Noticias + Sentimiento
- Fetcher de noticias multi-fuente (GNews, NewsData)
- Analizador de sentimiento basado en lexico financiero
- 100+ palabras clave financieras (Fed, BCE, inflation, etc.)
- Filtrado de noticias por relevancia forex
- Modelo NewsArticle con scores de sentimiento
- Endpoints `/api/news/feed` y `/api/news/sentiment-summary`
- Componentes NewsFeed y SentimentGauge

## [0.1.0] - 2024-12-17

### Agregado - Fase 1: MVP
- Backend FastAPI con SQLAlchemy async
- Fetcher de tipo de cambio (Frankfurter API como principal)
- APIs de backup (ExchangeRate-API)
- Base de datos SQLite con modelo ExchangeRate
- Historico de tasas de cambio
- Estadisticas (min, max, avg por periodo)
- Frontend Next.js 14 con App Router
- Componente ExchangeCard con tasa actual
- Grafico historico con Recharts
- Diseno responsive con Tailwind CSS
- API client TypeScript tipado

---

## Proximas Versiones

### [1.1.0] - Planificado
- Invertir monedas (EUR/USD ademas de USD/EUR)
- Selector de pares de divisas
- Soporte para EUR/GBP, USD/JPY, etc.

### [1.2.0] - Planificado
- Autenticacion de usuarios
- Alertas personalizadas por usuario
- Sincronizacion entre dispositivos

### [2.0.0] - Futuro
- Modelo ML mejorado (LSTM/Transformer)
- Calendario economico integrado
- App movil nativa
