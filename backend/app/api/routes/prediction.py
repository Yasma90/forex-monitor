from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from ...models.database import get_db
from ...models.prediction import PredictionResponse, SignalResponse
from ...services.prediction import PredictionEngine, SignalGenerator
from ...services.exchange import ExchangeRateRepository
from ...services.news import NewsRepository

router = APIRouter(prefix="/api/prediction", tags=["prediction"])


@router.get("/forecast", response_model=PredictionResponse)
async def get_forecast(
    base: str = Query(default="USD"),
    target: str = Query(default="EUR"),
    days: int = Query(default=30, ge=7, le=90),
    db: AsyncSession = Depends(get_db)
):
    """
    Get exchange rate forecast with confidence intervals.
    Combines historical trend analysis with news sentiment.
    """
    exchange_repo = ExchangeRateRepository(db)
    news_repo = NewsRepository(db)
    engine = PredictionEngine()

    # Get historical data (need at least 30 days for good prediction)
    history = await exchange_repo.get_history(base, target, days=60)

    if len(history) < 7:
        # Try to fetch historical data first
        from ...services.exchange import ExchangeRateFetcher
        fetcher = ExchangeRateFetcher()
        try:
            historical = await fetcher.fetch_historical(base, target, 60)
            if historical:
                from ...models.exchange import ExchangeRateCreate
                for rate_data in historical:
                    rate_create = ExchangeRateCreate(
                        base_currency=rate_data["base_currency"],
                        target_currency=rate_data["target_currency"],
                        rate=rate_data["rate"],
                        source="frankfurter"
                    )
                    await exchange_repo.save_rate(rate_create)
                history = await exchange_repo.get_history(base, target, days=60)
        finally:
            await fetcher.close()

    if len(history) < 7:
        raise HTTPException(
            status_code=400,
            detail="Insufficient historical data for prediction. Need at least 7 days."
        )

    # Get current sentiment
    avg_sentiment = await news_repo.get_avg_sentiment(hours=48)

    # Prepare historical data for prediction
    historical_data = [
        {'date': rate.timestamp.strftime('%Y-%m-%d'), 'rate': rate.rate}
        for rate in history
    ]

    # Remove duplicates (keep last per day)
    seen_dates = {}
    for item in historical_data:
        seen_dates[item['date']] = item['rate']
    historical_data = [{'date': d, 'rate': r} for d, r in sorted(seen_dates.items())]

    # Generate prediction
    try:
        result = await engine.predict(
            historical_data=historical_data,
            days_ahead=days,
            sentiment_score=avg_sentiment
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

    # Get current rate
    latest = await exchange_repo.get_latest(base, target)
    current_rate = latest.rate if latest else historical_data[-1]['rate']

    # Get sentiment mood
    sentiment_summary = await news_repo.get_sentiment_summary(hours=24)
    total = sum(sentiment_summary.values())
    if avg_sentiment > 0.15:
        mood = "BULLISH"
    elif avg_sentiment < -0.15:
        mood = "BEARISH"
    else:
        mood = "NEUTRAL"

    return PredictionResponse(
        base_currency=base,
        target_currency=target,
        current_rate=current_rate,
        predictions=[
            {
                'date': p['date'],
                'predicted_rate': p['predicted_rate'],
                'lower_bound': p['lower_bound'],
                'upper_bound': p['upper_bound']
            }
            for p in result['predictions']
        ],
        signal=result['signal'],
        signal_strength=result['signal_strength'],
        signal_description=result['signal_description'],
        sentiment_impact=result['sentiment_impact'],
        sentiment_mood=mood,
        model_type=result['model_type'],
        confidence_level=result['confidence_level'],
        generated_at=datetime.utcnow(),
        predicted_change_7d=result['predicted_change_7d'],
        predicted_change_30d=result['predicted_change_30d']
    )


@router.get("/signal", response_model=SignalResponse)
async def get_quick_signal(
    base: str = Query(default="USD"),
    target: str = Query(default="EUR"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a quick trading signal without full prediction.
    Faster endpoint for frequent checks.
    """
    exchange_repo = ExchangeRateRepository(db)
    news_repo = NewsRepository(db)
    signal_gen = SignalGenerator()

    # Get recent history
    history = await exchange_repo.get_history(base, target, days=14)

    if len(history) < 7:
        return SignalResponse(
            signal="NEUTRAL",
            strength=0.3,
            description="Datos insuficientes para generar senal confiable.",
            factors=["Necesita al menos 7 dias de historico"]
        )

    rates = [r.rate for r in history]

    # Get sentiment
    avg_sentiment = await news_repo.get_avg_sentiment(hours=24)

    # Get prediction change (simplified)
    if len(rates) >= 2:
        recent_change = ((rates[-1] - rates[-7]) / rates[-7]) * 100 if len(rates) >= 7 else 0
    else:
        recent_change = 0

    # Generate signal
    result = await signal_gen.generate_signal(
        current_rate=rates[-1],
        historical_rates=rates,
        sentiment_score=avg_sentiment,
        prediction_change=recent_change
    )

    return SignalResponse(
        signal=result['signal'],
        strength=result['strength'],
        description=result['description'],
        factors=result['factors']
    )
