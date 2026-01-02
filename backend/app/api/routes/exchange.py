from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from ...models.database import get_db
from ...models.exchange import ExchangeRateResponse, ExchangeRateCreate, ExchangeRateHistoryResponse
from ...services.exchange import ExchangeRateFetcher, ExchangeRateRepository

router = APIRouter(prefix="/api/exchange", tags=["exchange"])


@router.get("/rate", response_model=ExchangeRateResponse)
async def get_current_rate(
    base: str = Query(default="USD", description="Base currency code"),
    target: str = Query(default="EUR", description="Target currency code"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the current exchange rate for a currency pair.
    Includes 24h change if historical data is available.
    """
    repo = ExchangeRateRepository(db)

    # Get latest rate from DB
    latest = await repo.get_latest(base, target)

    # If no recent rate (older than 30 min), fetch fresh
    if not latest or _is_stale(latest.timestamp):
        fetcher = ExchangeRateFetcher()
        try:
            fresh_data = await fetcher.fetch_rate(base, target)
            if fresh_data:
                rate_create = ExchangeRateCreate(
                    base_currency=fresh_data["base_currency"],
                    target_currency=fresh_data["target_currency"],
                    rate=fresh_data["rate"],
                    source=fresh_data["source"]
                )
                latest = await repo.save_rate(rate_create)
        finally:
            await fetcher.close()

    if not latest:
        raise HTTPException(status_code=503, detail="Unable to fetch exchange rate")

    # Calculate 24h change
    rate_24h_ago = await repo.get_rate_24h_ago(base, target)
    change_24h = None
    change_percent_24h = None

    if rate_24h_ago:
        change_24h = latest.rate - rate_24h_ago.rate
        change_percent_24h = (change_24h / rate_24h_ago.rate) * 100

    return ExchangeRateResponse(
        id=latest.id,
        base_currency=latest.base_currency,
        target_currency=latest.target_currency,
        rate=latest.rate,
        source=latest.source,
        timestamp=latest.timestamp,
        change_24h=change_24h,
        change_percent_24h=change_percent_24h
    )


@router.get("/history", response_model=ExchangeRateHistoryResponse)
async def get_rate_history(
    base: str = Query(default="USD", description="Base currency code"),
    target: str = Query(default="EUR", description="Target currency code"),
    days: int = Query(default=30, ge=1, le=365, description="Number of days of history"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get historical exchange rates for a currency pair.
    """
    repo = ExchangeRateRepository(db)

    # Get historical rates from DB
    rates = await repo.get_history(base, target, days)

    # If no data, try to fetch historical data
    if not rates:
        fetcher = ExchangeRateFetcher()
        try:
            historical = await fetcher.fetch_historical(base, target, days)
            if historical:
                # Save to DB for future use
                for rate_data in historical:
                    rate_create = ExchangeRateCreate(
                        base_currency=rate_data["base_currency"],
                        target_currency=rate_data["target_currency"],
                        rate=rate_data["rate"],
                        source="frankfurter"
                    )
                    await repo.save_rate(rate_create)
                rates = await repo.get_history(base, target, days)
        finally:
            await fetcher.close()

    if not rates:
        raise HTTPException(status_code=404, detail="No historical data available")

    # Calculate stats
    stats = await repo.get_stats(base, target, days)

    return ExchangeRateHistoryResponse(
        rates=[ExchangeRateResponse(
            id=r.id,
            base_currency=r.base_currency,
            target_currency=r.target_currency,
            rate=r.rate,
            source=r.source,
            timestamp=r.timestamp
        ) for r in rates],
        min_rate=stats["min_rate"],
        max_rate=stats["max_rate"],
        avg_rate=stats["avg_rate"],
        period_days=stats["period_days"]
    )


@router.post("/refresh")
async def refresh_rate(
    base: str = Query(default="USD"),
    target: str = Query(default="EUR"),
    db: AsyncSession = Depends(get_db)
):
    """
    Force refresh the exchange rate (bypasses cache).
    """
    fetcher = ExchangeRateFetcher()
    repo = ExchangeRateRepository(db)

    try:
        fresh_data = await fetcher.fetch_rate(base, target)
        if fresh_data:
            rate_create = ExchangeRateCreate(
                base_currency=fresh_data["base_currency"],
                target_currency=fresh_data["target_currency"],
                rate=fresh_data["rate"],
                source=fresh_data["source"]
            )
            rate = await repo.save_rate(rate_create)
            return {"message": "Rate refreshed", "rate": rate.rate, "source": rate.source}
    finally:
        await fetcher.close()

    raise HTTPException(status_code=503, detail="Failed to refresh rate")


def _is_stale(timestamp, max_age_minutes: int = 30) -> bool:
    """Check if a timestamp is older than max_age_minutes"""
    from datetime import datetime, timedelta
    return datetime.utcnow() - timestamp > timedelta(minutes=max_age_minutes)
