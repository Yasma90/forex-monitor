# Forex Monitor - USD/EUR

Monitor de tipo de cambio USD/EUR con predicciones ML, analisis de sentimiento y alertas.

## Caracteristicas

- **Tipo de cambio en tiempo real** - Datos del BCE actualizados cada 30 min
- **Grafico historico** - Visualiza tendencias de hasta 365 dias
- **Predicciones ML** - Pronostico a 7 y 30 dias con intervalo de confianza
- **Analisis de sentimiento** - Noticias financieras con scoring BULLISH/BEARISH/NEUTRAL
- **Senales de trading** - Indicadores basados en tendencia, momentum y sentimiento
- **PWA Ready** - Instalable en movil como app nativa

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
│   │   │   └── prediction.py  # /api/prediction/*
│   │   ├── models/            # SQLAlchemy + Pydantic
│   │   ├── services/
│   │   │   ├── exchange/      # Fetcher, Repository
│   │   │   ├── news/          # Fetcher, Sentiment, Keywords
│   │   │   └── prediction/    # Engine, Signals
│   │   └── main.py
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
│   │   │   └── SignalBadge.tsx
│   │   └── lib/api.ts         # API client
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
- [ ] **Fase 4:** Alertas + PWA completo
- [ ] **Fase 5:** Refinamiento y optimizacion

## Requisitos

- Python 3.10+
- Node.js 18+
- npm o yarn

## Disclaimer

Las predicciones son indicativas, no garantias. Los mercados forex son volatiles.
Use esta informacion como herramienta complementaria, no como unica referencia para decisiones financieras.
