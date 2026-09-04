# Forex Monitor — USD/EUR

> Real-time USD/EUR exchange rate monitor with ML predictions, sentiment analysis, and smart alerts.

[![CI](https://github.com/Yasma90/forex-monitor/actions/workflows/ci.yml/badge.svg)](https://github.com/Yasma90/forex-monitor/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](CHANGELOG.md)

---

## Features

- **Real-time exchange rate** — ECB data updated every 30 min via Frankfurter API
- **Historical chart** — Visualise trends up to 365 days
- **ML Predictions** — 7 and 30-day forecast with confidence intervals
- **Sentiment analysis** — Financial news scored as BULLISH / BEARISH / NEUTRAL
- **Trading signals** — Indicators based on trend, momentum and sentiment
- **Alert system** — 5 alert types with browser push notifications
- **PWA Ready** — Installable on mobile as a native app
- **Backtesting** — Evaluate prediction accuracy against historical data
- **Smart cache** — In-memory cache with configurable TTL
- **Scheduler** — Background tasks for automatic data refresh

---

## Quick Start (Windows)

### Option 1: Automatic script
```bash
cd forex-monitor
start-dev.bat
```

### Option 2: Manual

**Terminal 1 — Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### URLs
| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |

---

## API Configuration (Optional)

Create a `backend/.env` file:

```env
# News (optional — improves sentiment analysis)
GNEWS_API_KEY=your_gnews_key
NEWSDATA_API_KEY=your_newsdata_key

# Exchange rate backup (optional)
EXCHANGERATE_API_KEY=your_key
```

**Without API keys:** The app works out of the box using free APIs with no key required (Frankfurter for exchange rates).

---

## Project Structure

```
forex-monitor/
├── backend/                    # Python FastAPI
│   ├── app/
│   │   ├── api/routes/        # REST endpoints
│   │   │   ├── exchange.py    # /api/exchange/*
│   │   │   ├── news.py        # /api/news/*
│   │   │   ├── prediction.py  # /api/prediction/*
│   │   │   ├── alerts.py      # /api/alerts/*
│   │   │   └── system.py      # /api/system/*
│   │   ├── models/            # SQLAlchemy + Pydantic
│   │   │   ├── exchange.py
│   │   │   ├── news.py
│   │   │   ├── alert.py
│   │   │   └── database.py
│   │   ├── services/
│   │   │   ├── exchange/      # Fetcher, Repository
│   │   │   ├── news/          # Fetcher, Sentiment, Keywords
│   │   │   ├── prediction/    # Engine, Signals, Backtesting
│   │   │   ├── alerts/        # Service, Checker
│   │   │   └── cache.py       # In-memory cache
│   │   ├── jobs/
│   │   │   └── scheduler.py   # Scheduled tasks
│   │   └── main.py
│   ├── tests/                 # Unit tests
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
│   │       └── notifications.ts
│   ├── public/
│   │   ├── sw.js              # Service Worker
│   │   └── manifest.json      # PWA manifest
│   └── package.json
├── data/                       # SQLite database
├── docs/                       # Extended documentation
├── .github/
│   ├── workflows/ci.yml       # GitHub Actions CI
│   └── PULL_REQUEST_TEMPLATE.md
└── docker-compose.yml
```

---

## API Endpoints

### Exchange Rate
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/exchange/rate` | Current rate with 24h change |
| `GET` | `/api/exchange/history?days=30` | Historical data |
| `POST` | `/api/exchange/refresh` | Force data refresh |

### News
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/news/feed` | News with sentiment scores |
| `GET` | `/api/news/sentiment-summary` | BULLISH / BEARISH / NEUTRAL summary |

### Prediction
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/prediction/forecast?days=30` | Full forecast with confidence intervals |
| `GET` | `/api/prediction/signal` | Quick trading signal |

### Alerts
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/alerts` | List alerts |
| `POST` | `/api/alerts` | Create alert |
| `PUT` | `/api/alerts/{id}` | Update alert |
| `DELETE` | `/api/alerts/{id}` | Delete alert |
| `GET` | `/api/alerts/history` | Triggered alerts history |

### System
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/system/cache/stats` | Cache statistics |
| `POST` | `/api/system/cache/clear` | Clear cache |
| `GET` | `/api/system/scheduler/status` | Scheduler status |
| `GET` | `/api/system/prediction/accuracy` | Prediction accuracy |
| `POST` | `/api/system/prediction/backtest` | Run backtesting |
| `GET` | `/api/system/metrics` | System metrics |

---

## ML / Predictions

### Default model (no extra dependencies)
- Linear regression trend analysis
- Exponential smoothing for short-term
- News sentiment adjustment

### Advanced model (optional)
```bash
pip install prophet
```
- Facebook Prophet for time series
- Better seasonality detection
- Higher prediction accuracy

---

## Free APIs Used

| API | Purpose | Limit |
|---|---|---|
| [Frankfurter](https://www.frankfurter.app/) | Exchange rate (ECB) | Unlimited |
| [ExchangeRate-API](https://www.exchangerate-api.com/) | Backup | 1 500/month |
| [GNews](https://gnews.io/) | News | 100/day |
| [NewsData](https://newsdata.io/) | News backup | 200/day |

---

## Alert System

### Alert types
| Type | Trigger |
|---|---|
| Price rises to... | Rate exceeds a threshold |
| Price falls to... | Rate drops below a threshold |
| % change in 24h | Movement greater than X% in a day |
| Sentiment change | News sentiment shifts |
| High-impact news | High-impact news detected |

### Features
- Recurring or one-shot alerts
- Configurable cooldown between triggers
- Browser push notifications
- Automatic check every 5 minutes

---

## PWA (Progressive Web App)

Install as a native app:
- **Chrome / Edge:** Click "Install" in the address bar or the purple button
- **Safari iOS:** Share → Add to Home Screen
- Works offline with cached data
- Receives push notifications

---

## Tests

Run unit tests:
```bash
cd backend
pytest tests/ -v
```

With coverage report:
```bash
pytest tests/ --cov=app --cov-report=html
```

Coverage: 63 tests covering cache, sentiment, scheduler and alerts.

---

## Requirements

| Dependency | Version |
|---|---|
| Python | 3.10+ |
| Node.js | 18+ |
| npm | 9+ |

---

## Completed Phases

- [x] **Phase 1:** MVP — Exchange rate + Chart
- [x] **Phase 2:** News + Sentiment analysis
- [x] **Phase 3:** ML Predictions + Signals
- [x] **Phase 4:** Alerts + Full PWA
- [x] **Phase 5:** Refinement & optimisation
  - [x] In-memory cache with TTL
  - [x] Prediction backtesting
  - [x] Background task scheduler
  - [x] 63 unit tests
  - [x] Optimised DB indexes
  - [x] Automatic cleanup of old data

---

## Roadmap

### High Priority
- [ ] **Currency swap** — View EUR/USD in addition to USD/EUR with one click
- [ ] **Pair selector** — Choose between multiple pairs (USD/EUR default)
- [ ] **Multi-currency support** — EUR/GBP, USD/JPY, GBP/USD, etc.
- [ ] **User authentication** — JWT/OAuth login for personalised alerts
- [ ] **Email notifications** — Alerts via email in addition to push

### Medium Priority
- [ ] **Improved ML model** — LSTM or Transformer integration
- [ ] **Economic calendar** — Display scheduled Fed/ECB events
- [ ] **Correlations** — Analyse correlation with other assets (gold, S&P500)
- [ ] **Data export** — Download history as CSV/Excel
- [ ] **Alert webhooks** — Send notifications to external URLs

### Low Priority
- [ ] **Native app** — React Native or Flutter for iOS/Android
- [ ] **Public API** — Third-party integration documentation
- [ ] **Widgets** — Mini-widgets to embed in other sites
- [ ] **Historical comparison** — Compare periods (this month vs previous)

### Technical Debt
- [ ] **Integration tests** — E2E tests with Playwright
- [x] **CI/CD** — GitHub Actions pipeline
- [ ] **Monitoring** — Prometheus/Grafana integration
- [ ] **Rate limiting** — API abuse protection
- [ ] **PostgreSQL** — Migrate from SQLite for production
- [ ] **Redis** — Distributed cache for multiple instances
- [ ] **WebSockets** — Real-time updates without polling

---

## Documentation

| File | Description |
|---|---|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | System architecture and technical decisions |
| [API.md](docs/API.md) | Full REST API documentation |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contributor guide |
| [CHANGELOG.md](CHANGELOG.md) | Version history |

---

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to submit pull requests, report bugs, and suggest features. We follow [Git Flow](https://nvie.com/posts/a-successful-git-branching-model/) and [Conventional Commits](https://www.conventionalcommits.org/).

---

## License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

Copyright (c) 2026 Yasmany Reyes González

---

## Disclaimer

Predictions are indicative, not guaranteed. Forex markets are volatile.
Use this tool as a complementary reference, not as the sole basis for financial decisions.
