"""
Background task scheduler for periodic operations.
Handles automatic data refresh, alert checking, and cache cleanup.
"""

import asyncio
import logging
from datetime import datetime
from typing import Callable, Dict, List, Optional
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


class ScheduledTask:
    """Represents a scheduled task"""

    def __init__(
        self,
        name: str,
        func: Callable,
        interval_seconds: int,
        enabled: bool = True
    ):
        self.name = name
        self.func = func
        self.interval_seconds = interval_seconds
        self.enabled = enabled
        self.last_run: Optional[datetime] = None
        self.run_count = 0
        self.error_count = 0
        self.last_error: Optional[str] = None

    async def run(self) -> bool:
        """Execute the task"""
        if not self.enabled:
            return False

        try:
            logger.info(f"Running scheduled task: {self.name}")
            await self.func()
            self.last_run = datetime.utcnow()
            self.run_count += 1
            return True
        except Exception as e:
            self.error_count += 1
            self.last_error = str(e)
            logger.error(f"Task {self.name} failed: {e}")
            return False

    @property
    def status(self) -> dict:
        return {
            "name": self.name,
            "interval_seconds": self.interval_seconds,
            "enabled": self.enabled,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "run_count": self.run_count,
            "error_count": self.error_count,
            "last_error": self.last_error
        }


class TaskScheduler:
    """
    Async task scheduler for background operations.
    """

    def __init__(self):
        self.tasks: Dict[str, ScheduledTask] = {}
        self._running = False
        self._task_handles: List[asyncio.Task] = []

    def add_task(
        self,
        name: str,
        func: Callable,
        interval_seconds: int,
        enabled: bool = True
    ) -> None:
        """Register a new scheduled task"""
        self.tasks[name] = ScheduledTask(name, func, interval_seconds, enabled)
        logger.info(f"Registered task: {name} (interval: {interval_seconds}s)")

    def remove_task(self, name: str) -> bool:
        """Remove a scheduled task"""
        if name in self.tasks:
            del self.tasks[name]
            return True
        return False

    def enable_task(self, name: str) -> bool:
        """Enable a task"""
        if name in self.tasks:
            self.tasks[name].enabled = True
            return True
        return False

    def disable_task(self, name: str) -> bool:
        """Disable a task"""
        if name in self.tasks:
            self.tasks[name].enabled = False
            return True
        return False

    async def start(self) -> None:
        """Start the scheduler"""
        if self._running:
            return

        self._running = True
        logger.info("Starting task scheduler")

        for name, task in self.tasks.items():
            if task.enabled:
                handle = asyncio.create_task(self._run_task_loop(task))
                self._task_handles.append(handle)

    async def stop(self) -> None:
        """Stop the scheduler"""
        self._running = False
        for handle in self._task_handles:
            handle.cancel()
        self._task_handles.clear()
        logger.info("Stopped task scheduler")

    async def _run_task_loop(self, task: ScheduledTask) -> None:
        """Run a task in a loop"""
        while self._running and task.enabled:
            await task.run()
            await asyncio.sleep(task.interval_seconds)

    @property
    def status(self) -> dict:
        """Get scheduler status"""
        return {
            "running": self._running,
            "task_count": len(self.tasks),
            "tasks": {name: task.status for name, task in self.tasks.items()}
        }


# Global scheduler instance
scheduler = TaskScheduler()


async def setup_default_tasks(db_session_factory) -> None:
    """Setup default scheduled tasks"""
    from ..services.exchange import ExchangeRateFetcher, ExchangeRateRepository
    from ..services.alerts import AlertService, AlertChecker
    from ..services.news import NewsRepository
    from ..services.cache import exchange_rate_cache, news_cache, prediction_cache

    async def refresh_exchange_rate():
        """Fetch latest exchange rate"""
        async with db_session_factory() as db:
            fetcher = ExchangeRateFetcher()
            repo = ExchangeRateRepository(db)
            try:
                data = await fetcher.fetch_rate("USD", "EUR")
                if data:
                    from ..models.exchange import ExchangeRateCreate
                    await repo.save_rate(ExchangeRateCreate(
                        base_currency=data["base_currency"],
                        target_currency=data["target_currency"],
                        rate=data["rate"],
                        source=data["source"]
                    ))
                    # Invalidate cache
                    exchange_rate_cache.clear()
            finally:
                await fetcher.close()

    async def check_alerts():
        """Check all active alerts"""
        async with db_session_factory() as db:
            alert_service = AlertService(db)
            exchange_repo = ExchangeRateRepository(db)
            news_repo = NewsRepository(db)
            checker = AlertChecker()

            alerts = await alert_service.get_all_alerts()
            latest = await exchange_repo.get_latest("USD", "EUR")
            old_rate = await exchange_repo.get_rate_24h_ago("USD", "EUR")
            sentiment = await news_repo.get_avg_sentiment(24)

            if latest:
                triggered = await checker.check_alerts(
                    alerts=alerts,
                    current_rate=latest.rate,
                    rate_24h_ago=old_rate.rate if old_rate else None,
                    sentiment_score=sentiment
                )
                for t in triggered:
                    await alert_service.mark_triggered(
                        t.alert.id, t.current_value, t.message
                    )

    async def cleanup_caches():
        """Clean up expired cache entries"""
        removed = 0
        removed += exchange_rate_cache.clear_expired()
        removed += news_cache.clear_expired()
        removed += prediction_cache.clear_expired()
        if removed > 0:
            logger.info(f"Cleaned up {removed} expired cache entries")

    async def cleanup_old_data():
        """Clean up old database records to optimize storage"""
        async with db_session_factory() as db:
            exchange_repo = ExchangeRateRepository(db)
            news_repo = NewsRepository(db)

            # Keep 1 year of exchange rates
            exchange_deleted = await exchange_repo.cleanup_old_rates(keep_days=365)
            # Keep 30 days of news
            news_deleted = await news_repo.cleanup_old_articles(keep_days=30)

            if exchange_deleted > 0 or news_deleted > 0:
                logger.info(
                    f"Data cleanup: removed {exchange_deleted} exchange rates, "
                    f"{news_deleted} news articles"
                )

    # Register tasks
    scheduler.add_task("refresh_rate", refresh_exchange_rate, 1800)  # 30 min
    scheduler.add_task("check_alerts", check_alerts, 300)  # 5 min
    scheduler.add_task("cleanup_cache", cleanup_caches, 3600)  # 1 hour
    scheduler.add_task("cleanup_data", cleanup_old_data, 86400)  # 24 hours


@asynccontextmanager
async def lifespan_scheduler(db_session_factory):
    """Context manager for scheduler lifecycle"""
    await setup_default_tasks(db_session_factory)
    await scheduler.start()
    yield
    await scheduler.stop()
