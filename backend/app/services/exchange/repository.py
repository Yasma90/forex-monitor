from datetime import datetime, timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from ...models.exchange import ExchangeRate, ExchangeRateCreate


class ExchangeRateRepository:
    """Database operations for exchange rates"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def save_rate(self, rate_data: ExchangeRateCreate) -> ExchangeRate:
        """Save a new exchange rate to the database"""
        rate = ExchangeRate(
            base_currency=rate_data.base_currency,
            target_currency=rate_data.target_currency,
            rate=rate_data.rate,
            source=rate_data.source,
            timestamp=datetime.utcnow()
        )
        self.db.add(rate)
        await self.db.commit()
        await self.db.refresh(rate)
        return rate

    async def get_latest(
        self,
        base: str = "USD",
        target: str = "EUR"
    ) -> Optional[ExchangeRate]:
        """Get the most recent exchange rate"""
        result = await self.db.execute(
            select(ExchangeRate)
            .where(ExchangeRate.base_currency == base)
            .where(ExchangeRate.target_currency == target)
            .order_by(ExchangeRate.timestamp.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_rate_24h_ago(
        self,
        base: str = "USD",
        target: str = "EUR"
    ) -> Optional[ExchangeRate]:
        """Get the rate from approximately 24 hours ago"""
        target_time = datetime.utcnow() - timedelta(hours=24)

        result = await self.db.execute(
            select(ExchangeRate)
            .where(ExchangeRate.base_currency == base)
            .where(ExchangeRate.target_currency == target)
            .where(ExchangeRate.timestamp <= target_time)
            .order_by(ExchangeRate.timestamp.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_history(
        self,
        base: str = "USD",
        target: str = "EUR",
        days: int = 30
    ) -> list[ExchangeRate]:
        """Get historical rates for the specified period"""
        start_date = datetime.utcnow() - timedelta(days=days)

        result = await self.db.execute(
            select(ExchangeRate)
            .where(ExchangeRate.base_currency == base)
            .where(ExchangeRate.target_currency == target)
            .where(ExchangeRate.timestamp >= start_date)
            .order_by(ExchangeRate.timestamp.asc())
        )
        return list(result.scalars().all())

    async def get_stats(
        self,
        base: str = "USD",
        target: str = "EUR",
        days: int = 30
    ) -> dict:
        """Get statistics for the period"""
        start_date = datetime.utcnow() - timedelta(days=days)

        result = await self.db.execute(
            select(
                func.min(ExchangeRate.rate).label("min_rate"),
                func.max(ExchangeRate.rate).label("max_rate"),
                func.avg(ExchangeRate.rate).label("avg_rate"),
                func.count(ExchangeRate.id).label("count")
            )
            .where(ExchangeRate.base_currency == base)
            .where(ExchangeRate.target_currency == target)
            .where(ExchangeRate.timestamp >= start_date)
        )
        row = result.one()

        return {
            "min_rate": row.min_rate,
            "max_rate": row.max_rate,
            "avg_rate": row.avg_rate,
            "count": row.count,
            "period_days": days
        }
