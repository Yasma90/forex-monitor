# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

---

## [0.1.0] - 2026-09-04

First structured release under Git Flow. Establishes baseline documentation,
CI pipeline, and correct branching conventions.


### Added
- MIT License with correct copyright holder (Yasmany Reyes González)
- GitHub Actions CI pipeline (backend pytest + frontend lint/build)
- Pull Request template (`.github/PULL_REQUEST_TEMPLATE.md`)
- Bug report and feature request issue templates
- Git Flow branching model documentation in CONTRIBUTING.md
- Version badges and License badge in README.md

### Changed
- Full translation of README, CONTRIBUTING and CHANGELOG to English
- Updated CONTRIBUTING to reference `develop` as the base branch for feature work
- Production branch renamed from `master` to `main`
- Copyright year updated to 2026

### Fixed
- `.gitignore` now correctly excludes `.claude/` directory

---

## Historical Versions (pre-Git Flow)

> The following entries predate the Git Flow workflow and are kept for historical reference.

## [1.0.0] - 2024-12-21

### Added — Phase 5: Refinement
- In-memory cache with configurable TTL
- Backtesting service to evaluate prediction accuracy
- Background task scheduler (rate refresh, alert checker, cleanup)
- 63 unit tests (cache, sentiment, scheduler, alerts)
- Optimised database indexes
- Automatic cleanup of old data
- System endpoints (`/api/system/*`) for monitoring
- Professional documentation (README, CONTRIBUTING, CHANGELOG)

### Changed
- Database queries optimised with composite indexes
- Batch insert for news articles
- `get_daily_rates()` method for efficient long-range queries

## [0.4.0] - 2024-12-20

### Added — Phase 4: Alerts + PWA
- Alert system with 5 types:
  - Price rises/falls to threshold
  - Percentage change in 24h
  - Sentiment change
  - High-impact news
- Alert model with cooldown and recurrence support
- AlertChecker for automatic verification
- Triggered alert history
- Browser push notifications (Web Push API)
- Service Worker for PWA
- `manifest.json` for app installation
- AlertsPanel frontend component
- Offline support with asset cache

## [0.3.0] - 2024-12-19

### Added — Phase 3: ML Predictions
- Prediction engine with optional Prophet support
- Fallback model based on trend + exponential smoothing
- Sentiment-adjusted predictions
- Trading signal generator (BULLISH / BEARISH / NEUTRAL)
- Confidence intervals in predictions
- `/api/prediction/forecast` and `/api/prediction/signal` endpoints
- PredictionChart and PredictionCard components
- SignalBadge with visual indicators

## [0.2.0] - 2024-12-18

### Added — Phase 2: News + Sentiment
- Multi-source news fetcher (GNews, NewsData)
- Lexicon-based sentiment analyser
- 100+ financial keywords (Fed, ECB, inflation, etc.)
- Forex-relevance news filtering
- NewsArticle model with sentiment scores
- `/api/news/feed` and `/api/news/sentiment-summary` endpoints
- NewsFeed and SentimentGauge components

## [0.1.0-alpha] - 2024-12-17

### Added — Phase 1: MVP
- FastAPI backend with async SQLAlchemy
- Exchange rate fetcher (Frankfurter API as primary source)
- Backup APIs (ExchangeRate-API)
- SQLite database with ExchangeRate model
- Exchange rate history
- Statistics (min, max, avg per period)
- Next.js 14 frontend with App Router
- ExchangeCard component with current rate
- Historical chart with Recharts
- Responsive design with Tailwind CSS
- Typed TypeScript API client

---

## Planned Versions

### [0.2.0] — Planned
- Currency swap (EUR/USD in addition to USD/EUR)
- Currency pair selector
- Support for EUR/GBP, USD/JPY, etc.

### [0.3.0] — Planned
- User authentication
- User-specific alerts
- Cross-device synchronisation

### [1.0.0] — Future
- Improved ML model (LSTM/Transformer)
- Integrated economic calendar
- Native mobile app

[Unreleased]: https://github.com/Yasma90/forex-monitor/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Yasma90/forex-monitor/releases/tag/v0.1.0
