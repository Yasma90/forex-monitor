# Forex Monitor - USD/EUR

Monitor de tipo de cambio USD/EUR con predicciones ML, analisis de sentimiento y alertas.

## Caracteristicas Implementadas

- **Tipo de cambio en tiempo real** - Datos del BCE actualizados cada 30 min
- **Grafico historico** - Visualiza tendencias de hasta 365 dias
- **Predicciones ML** - Pronostico a 7 y 30 dias con intervalo de confianza
- **Analisis de sentimiento** - Noticias financieras con scoring BULLISH/BEARISH/NEUTRAL
- **Senales de trading** - Indicadores basados en tendencia, momentum y sentimiento
- **Sistema de alertas** - 5 tipos de alertas con notificaciones push
- **PWA Ready** - Instalable en movil como app nativa
- **Backtesting** - Evaluacion de precision de predicciones
- **Cache inteligente** - Sistema de cache con TTL para optimizar rendimiento
- **Scheduler** - Tareas programadas para actualizacion automatica

## Inicio Rapido (Windows)

### Opcion 1: Script automatico
```bash
cd forex-monitor
start-dev.bat
```

### Opcion 2: Manual

**Terminal 1 - Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### URLs
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs (Swagger):** http://localhost:8000/docs

## Configuracion de APIs (Opcional)

Crear archivo `backend/.env`:

```env
# Noticias (opcional - mejora el analisis de sentimiento)
GNEWS_API_KEY=tu_key_de_gnews.io
NEWSDATA_API_KEY=tu_key_de_newsdata.io

# Exchange rate backup (opcional)
EXCHANGERATE_API_KEY=tu_key
```

**Sin API keys:** La app funciona con APIs gratuitas sin key (Frankfurter para cambio).

## Estructura del Proyecto

```
forex-monitor/
├── backend/                    # Python FastAPI
│   ├── app/
│   │   ├── api/routes/        # Endpoints REST
│   │   │   ├── exchange.py    # /api/exchange/*
│   │   │   ├── news.py        # /api/news/*
│   │   │   ├── prediction.py  # /api/prediction/*
│   │   │   ├── alerts.py      # /api/alerts/*
│   │   │   └── system.py      # /api/system/* (cache, scheduler, metrics)
│   │   ├── models/            # SQLAlchemy + Pydantic
│   │   │   ├── exchange.py    # Modelo de tasas de cambio
│   │   │   ├── news.py        # Modelo de noticias
│   │   │   ├── alert.py       # Modelo de alertas
│   │   │   └── database.py    # Configuracion BD
│   │   ├── services/
│   │   │   ├── exchange/      # Fetcher, Repository
│   │   │   ├── news/          # Fetcher, Sentiment, Keywords
│   │   │   ├── prediction/    # Engine, Signals, Backtesting
│   │   │   ├── alerts/        # Service, Checker
│   │   │   └── cache.py       # Sistema de cache en memoria
│   │   ├── jobs/
│   │   │   └── scheduler.py   # Tareas programadas
│   │   └── main.py
│   ├── tests/                 # Tests unitarios
│   │   ├── test_cache.py
│   │   ├── test_sentiment.py
│   │   ├── test_scheduler.py
│   │   └── test_alerts.py
│   └── requirements.txt
├── frontend/                   # Next.js + React
│   ├── src/
│   │   ├── app/               # Pages (App Router)
│   │   ├── components/        # React components
│   │   │   ├── ExchangeCard.tsx
│   │   │   ├── PredictionChart.tsx
│   │   │   ├── PredictionCard.tsx
│   │   │   ├── NewsFeed.tsx
│   │   │   ├── SentimentGauge.tsx
│   │   │   ├── SignalBadge.tsx
│   │   │   └── AlertsPanel.tsx
│   │   └── lib/
│   │       ├── api.ts         # API client
│   │       └── notifications.ts # Push notifications
│   ├── public/
│   │   ├── sw.js              # Service Worker
│   │   └── manifest.json      # PWA manifest
│   └── package.json
└── data/                       # SQLite database
```

## API Endpoints

### Exchange Rate
- `GET /api/exchange/rate` - Tasa actual con cambio 24h
- `GET /api/exchange/history?days=30` - Historico
- `POST /api/exchange/refresh` - Forzar actualizacion

### News
- `GET /api/news/feed` - Noticias con sentimiento
- `GET /api/news/sentiment-summary` - Resumen BULLISH/BEARISH/NEUTRAL

### Prediction
- `GET /api/prediction/forecast?days=30` - Prediccion completa con intervalos
- `GET /api/prediction/signal` - Senal rapida

### Alerts
- `GET /api/alerts` - Listar alertas
- `POST /api/alerts` - Crear alerta
- `PUT /api/alerts/{id}` - Actualizar alerta
- `DELETE /api/alerts/{id}` - Eliminar alerta
- `GET /api/alerts/history` - Historial de alertas disparadas

### System
- `GET /api/system/cache/stats` - Estadisticas de cache
- `POST /api/system/cache/clear` - Limpiar cache
- `GET /api/system/scheduler/status` - Estado del scheduler
- `GET /api/system/prediction/accuracy` - Precision de predicciones
- `POST /api/system/prediction/backtest` - Ejecutar backtesting
- `GET /api/system/metrics` - Metricas del sistema

## ML/Predicciones

### Modelo por defecto (sin dependencias extras)
- Analisis de tendencia con regresion lineal
- Suavizado exponencial para corto plazo
- Ajuste por sentimiento de noticias

### Modelo avanzado (opcional)
```bash
pip install prophet
```
- Facebook Prophet para series temporales
- Mejor deteccion de estacionalidad
- Mayor precision en predicciones

## APIs Gratuitas Utilizadas

| API | Uso | Limite |
|-----|-----|--------|
| Frankfurter | Tipo de cambio (BCE) | Ilimitado |
| ExchangeRate-API | Backup | 1500/mes |
| GNews | Noticias | 100/dia |
| NewsData | Noticias backup | 200/dia |

## Fases Completadas

- [x] **Fase 1:** MVP - Tipo de cambio + Grafico
- [x] **Fase 2:** Noticias + Analisis de sentimiento
- [x] **Fase 3:** Predicciones ML + Senales
- [x] **Fase 4:** Alertas + PWA completo
- [x] **Fase 5:** Refinamiento y optimizacion
  - [x] Sistema de cache con TTL
  - [x] Backtesting de predicciones
  - [x] Scheduler para tareas automaticas
  - [x] Tests unitarios (63 tests)
  - [x] Indices de BD optimizados
  - [x] Limpieza automatica de datos antiguos

## Sistema de Alertas

### Tipos de alertas disponibles
- **Precio sube a...** - Se activa cuando el tipo de cambio supera un umbral
- **Precio baja a...** - Se activa cuando el tipo de cambio cae bajo un umbral
- **Cambio % en 24h** - Se activa si hay un movimiento mayor al X% en el dia
- **Cambio de sentimiento** - Se activa ante cambios en el sentimiento de noticias
- **Noticias de impacto** - Se activa ante noticias de alto impacto

### Caracteristicas
- Alertas recurrentes o de una sola vez
- Cooldown configurable entre activaciones
- Notificaciones push en el navegador
- Verificacion automatica cada 5 minutos

## PWA (Progressive Web App)

La aplicacion se puede instalar como app nativa:
- En Chrome/Edge: Clic en "Instalar" en la barra de direcciones o boton morado
- En Safari iOS: Compartir > Agregar a pantalla de inicio
- Funciona offline con datos en cache
- Recibe notificaciones push

## Tests

Ejecutar tests unitarios:
```bash
cd backend
pytest tests/ -v
```

Cobertura: 63 tests cubriendo cache, sentiment, scheduler y alerts.

## Requisitos

- Python 3.10+
- Node.js 18+
- npm o yarn

---

## Documentacion

- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - Arquitectura del sistema y decisiones tecnicas
- [API.md](docs/API.md) - Documentacion completa de la API REST
- [CONTRIBUTING.md](CONTRIBUTING.md) - Guia para contribuidores
- [CHANGELOG.md](CHANGELOG.md) - Historial de cambios por version

---

## Mejoras Futuras y Features Pendientes

### Alta Prioridad
- [ ] **Invertir monedas** - Ver EUR/USD ademas de USD/EUR con un click
- [ ] **Selector de pares** - Elegir entre multiples pares (USD/EUR por defecto)
- [ ] **Soporte multi-divisa** - Agregar EUR/GBP, USD/JPY, GBP/USD, etc.
- [ ] **Autenticacion de usuarios** - Login con JWT/OAuth para alertas personalizadas
- [ ] **Notificaciones por email** - Alertas via correo ademas de push
- [ ] **Dashboard de metricas** - Panel visual de precision de predicciones

### Media Prioridad
- [ ] **Modelo ML mejorado** - Integrar LSTM o Transformer para predicciones
- [ ] **Calendario economico** - Mostrar eventos Fed/BCE programados
- [ ] **Correlaciones** - Analizar correlacion con otros activos (oro, S&P500)
- [ ] **Modo oscuro** - Theme switcher en la interfaz
- [ ] **Exportar datos** - Descargar historico en CSV/Excel
- [ ] **Webhook para alertas** - Enviar notificaciones a URLs externas

### Baja Prioridad
- [ ] **App nativa** - React Native o Flutter para iOS/Android
- [ ] **API publica** - Documentacion para integraciones de terceros
- [ ] **Widgets** - Mini-widgets para embeber en otras webs
- [ ] **Comparativa historica** - Comparar periodos (este mes vs anterior)
- [ ] **Machine Learning en tiempo real** - Reentrenamiento automatico del modelo

### Deuda Tecnica
- [ ] **Tests de integracion** - Tests E2E con Playwright
- [ ] **CI/CD** - Pipeline con GitHub Actions
- [ ] **Docker Compose** - Despliegue simplificado
- [ ] **Monitoreo** - Integracion con Prometheus/Grafana
- [ ] **Rate limiting** - Proteccion contra abuso de API
- [ ] **Actualizacion Next.js** - Actualizar a version con parche de seguridad

### Optimizaciones
- [ ] **PostgreSQL** - Migrar de SQLite para produccion
- [ ] **Redis** - Cache distribuido para multiples instancias
- [ ] **CDN** - Assets estaticos en CDN
- [ ] **WebSockets** - Actualizaciones en tiempo real sin polling

---

## Disclaimer

Las predicciones son indicativas, no garantias. Los mercados forex son volatiles.
Use esta informacion como herramienta complementaria, no como unica referencia para decisiones financieras.
