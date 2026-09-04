from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from ...models.database import get_db
from ...models.alert import (
    AlertCreate, AlertUpdate, AlertResponse, AlertHistoryResponse,
    TriggeredAlert, AlertStatus
)
from ...services.alerts import AlertService, AlertChecker
from ...services.exchange import ExchangeRateRepository
from ...services.news import NewsRepository

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.post("/", response_model=AlertResponse)
async def create_alert(
    alert_data: AlertCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new alert"""
    service = AlertService(db)
    alert = await service.create_alert(alert_data)
    return AlertResponse.model_validate(alert)


@router.get("/", response_model=list[AlertResponse])
async def get_alerts(
    include_inactive: bool = Query(default=False),
    db: AsyncSession = Depends(get_db)
):
    """Get all alerts"""
    service = AlertService(db)
    alerts = await service.get_all_alerts(include_inactive=include_inactive)
    return [AlertResponse.model_validate(a) for a in alerts]


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific alert"""
    service = AlertService(db)
    alert = await service.get_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return AlertResponse.model_validate(alert)


@router.put("/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: int,
    update_data: AlertUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an alert"""
    service = AlertService(db)
    alert = await service.update_alert(alert_id, update_data)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return AlertResponse.model_validate(alert)


@router.delete("/{alert_id}")
async def delete_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete an alert"""
    service = AlertService(db)
    success = await service.delete_alert(alert_id)
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"message": "Alert deleted successfully"}


@router.post("/{alert_id}/pause", response_model=AlertResponse)
async def pause_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Pause an alert"""
    service = AlertService(db)
    alert = await service.pause_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return AlertResponse.model_validate(alert)


@router.post("/{alert_id}/resume", response_model=AlertResponse)
async def resume_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Resume a paused alert"""
    service = AlertService(db)
    alert = await service.resume_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return AlertResponse.model_validate(alert)


@router.get("/history/all", response_model=list[AlertHistoryResponse])
async def get_alert_history(
    alert_id: Optional[int] = Query(default=None),
    limit: int = Query(default=50, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get alert trigger history"""
    service = AlertService(db)
    history = await service.get_alert_history(alert_id=alert_id, limit=limit)
    return [AlertHistoryResponse.model_validate(h) for h in history]


@router.post("/check", response_model=list[TriggeredAlert])
async def check_alerts_now(
    db: AsyncSession = Depends(get_db)
):
    """
    Manually check all active alerts against current conditions.
    Returns list of triggered alerts.
    """
    alert_service = AlertService(db)
    exchange_repo = ExchangeRateRepository(db)
    news_repo = NewsRepository(db)
    checker = AlertChecker()

    # Get current data
    alerts = await alert_service.get_all_alerts()
    latest_rate = await exchange_repo.get_latest("USD", "EUR")
    rate_24h_ago = await exchange_repo.get_rate_24h_ago("USD", "EUR")
    sentiment = await news_repo.get_avg_sentiment(hours=24)

    if not latest_rate:
        return []

    current_rate = latest_rate.rate
    old_rate = rate_24h_ago.rate if rate_24h_ago else None

    # Check alerts
    triggered = await checker.check_alerts(
        alerts=alerts,
        current_rate=current_rate,
        rate_24h_ago=old_rate,
        sentiment_score=sentiment
    )

    # Mark triggered alerts
    for t in triggered:
        await alert_service.mark_triggered(
            alert_id=t.alert.id,
            trigger_value=t.current_value,
            message=t.message
        )

    return triggered


@router.get("/templates/common")
async def get_alert_templates():
    """Get common alert templates for quick setup"""
    return [
        {
            "name": "EUR sube a 0.95",
            "description": "Alerta cuando 1 USD = 0.95 EUR o mas",
            "config": {
                "alert_type": "price_above",
                "threshold_value": 0.95,
                "is_recurring": False
            }
        },
        {
            "name": "EUR baja a 0.90",
            "description": "Alerta cuando 1 USD = 0.90 EUR o menos",
            "config": {
                "alert_type": "price_below",
                "threshold_value": 0.90,
                "is_recurring": False
            }
        },
        {
            "name": "Cambio >1% diario",
            "description": "Alerta si el cambio supera 1% en 24h",
            "config": {
                "alert_type": "percent_change",
                "threshold_value": 1.0,
                "is_recurring": True,
                "cooldown_minutes": 240
            }
        },
        {
            "name": "Sentimiento muy negativo",
            "description": "Alerta si las noticias son muy negativas",
            "config": {
                "alert_type": "sentiment",
                "threshold_value": -0.3,
                "is_recurring": True,
                "cooldown_minutes": 360
            }
        },
        {
            "name": "Noticias de alto impacto",
            "description": "Alerta ante noticias importantes",
            "config": {
                "alert_type": "news_impact",
                "threshold_value": 0.5,
                "is_recurring": True,
                "cooldown_minutes": 120
            }
        }
    ]
