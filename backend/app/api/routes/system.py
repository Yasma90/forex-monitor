"""System and monitoring endpoints"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.database import get_db
from ...services.cache import get_all_cache_stats
from ...services.prediction.backtesting import PredictionBacktester, quick_accuracy_check
from ...services.exchange import ExchangeRateRepository
from ...jobs.scheduler import scheduler

router = APIRouter(prefix="/api/system", tags=["system"])


@router.get("/cache/stats")
async def get_cache_stats():
    """Get cache statistics"""
    return get_all_cache_stats()


@router.post("/cache/clear")
async def clear_cache():
    """Clear all caches"""
    from ...services.cache import exchange_rate_cache, news_cache, prediction_cache
    exchange_rate_cache.clear()
    news_cache.clear()
    prediction_cache.clear()
    return {"message": "All caches cleared"}


@router.get("/scheduler/status")
async def get_scheduler_status():
    """Get scheduler status and task info"""
    return scheduler.status


@router.post("/scheduler/task/{task_name}/enable")
async def enable_task(task_name: str):
    """Enable a scheduled task"""
    if scheduler.enable_task(task_name):
        return {"message": f"Task {task_name} enabled"}
    return {"error": f"Task {task_name} not found"}


@router.post("/scheduler/task/{task_name}/disable")
async def disable_task(task_name: str):
    """Disable a scheduled task"""
    if scheduler.disable_task(task_name):
        return {"message": f"Task {task_name} disabled"}
    return {"error": f"Task {task_name} not found"}


@router.get("/prediction/accuracy")
async def check_prediction_accuracy(
    days: int = Query(default=7, ge=3, le=30),
    db: AsyncSession = Depends(get_db)
):
    """
    Quick check of prediction accuracy against recent actual data.
    """
    repo = ExchangeRateRepository(db)
    history = await repo.get_history("USD", "EUR", days=60)

    if len(history) < 20:
        return {"error": "Insufficient historical data for accuracy check"}

    historical_data = [
        {"date": r.timestamp.strftime("%Y-%m-%d"), "rate": r.rate}
        for r in history
    ]

    # Remove duplicates
    seen = {}
    for item in historical_data:
        seen[item["date"]] = item["rate"]
    historical_data = [{"date": d, "rate": r} for d, r in sorted(seen.items())]

    return await quick_accuracy_check(historical_data, days)


@router.post("/prediction/backtest")
async def run_backtest(
    lookback_days: int = Query(default=30, ge=14, le=90),
    prediction_horizon: int = Query(default=7, ge=3, le=30),
    db: AsyncSession = Depends(get_db)
):
    """
    Run full backtest of prediction model.
    This evaluates how well predictions would have performed historically.
    """
    repo = ExchangeRateRepository(db)
    history = await repo.get_history("USD", "EUR", days=120)

    if len(history) < lookback_days + prediction_horizon + 20:
        return {"error": "Insufficient historical data for backtesting"}

    historical_data = [
        {"date": r.timestamp.strftime("%Y-%m-%d"), "rate": r.rate}
        for r in history
    ]

    # Remove duplicates
    seen = {}
    for item in historical_data:
        seen[item["date"]] = item["rate"]
    historical_data = [{"date": d, "rate": r} for d, r in sorted(seen.items())]

    backtester = PredictionBacktester()
    result = await backtester.run_backtest(
        historical_data,
        lookback_days=lookback_days,
        prediction_horizon=prediction_horizon
    )

    return result.to_dict()


@router.get("/metrics")
async def get_system_metrics(db: AsyncSession = Depends(get_db)):
    """Get comprehensive system metrics"""
    from ...services.exchange import ExchangeRateRepository
    from ...services.news import NewsRepository
    from ...services.alerts import AlertService

    exchange_repo = ExchangeRateRepository(db)
    news_repo = NewsRepository(db)
    alert_service = AlertService(db)

    # Get counts
    exchange_stats = await exchange_repo.get_stats("USD", "EUR", 30)
    sentiment_summary = await news_repo.get_sentiment_summary(24)
    alerts = await alert_service.get_all_alerts(include_inactive=True)

    active_alerts = len([a for a in alerts if a.status == "active"])
    triggered_alerts = len([a for a in alerts if a.status == "triggered"])

    return {
        "exchange": {
            "data_points_30d": exchange_stats.get("count", 0),
            "min_rate": exchange_stats.get("min_rate"),
            "max_rate": exchange_stats.get("max_rate"),
            "avg_rate": exchange_stats.get("avg_rate")
        },
        "news": {
            "sentiment_24h": sentiment_summary,
            "total_articles_24h": sum(sentiment_summary.values())
        },
        "alerts": {
            "total": len(alerts),
            "active": active_alerts,
            "triggered": triggered_alerts
        },
        "cache": get_all_cache_stats(),
        "scheduler": scheduler.status
    }
