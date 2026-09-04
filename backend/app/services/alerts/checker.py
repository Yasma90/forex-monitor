"""Alert checker - evaluates conditions and triggers alerts"""

from datetime import datetime, timedelta
from typing import Optional
import logging

from ...models.alert import Alert, AlertType, AlertStatus, TriggeredAlert, AlertResponse

logger = logging.getLogger(__name__)


class AlertChecker:
    """Checks alert conditions and determines which alerts should trigger"""

    def __init__(self):
        self.triggered_alerts: list[TriggeredAlert] = []

    async def check_alerts(
        self,
        alerts: list[Alert],
        current_rate: float,
        rate_24h_ago: Optional[float] = None,
        sentiment_score: Optional[float] = None
    ) -> list[TriggeredAlert]:
        """
        Check all alerts against current conditions.
        Returns list of alerts that should be triggered.
        """
        self.triggered_alerts = []

        for alert in alerts:
            if not self._should_check(alert):
                continue

            triggered = await self._check_single_alert(
                alert, current_rate, rate_24h_ago, sentiment_score
            )

            if triggered:
                self.triggered_alerts.append(triggered)

        return self.triggered_alerts

    def _should_check(self, alert: Alert) -> bool:
        """Determine if alert should be checked"""
        # Skip inactive alerts
        if alert.status != AlertStatus.ACTIVE.value:
            return False

        # Check expiration
        if alert.expires_at and alert.expires_at < datetime.utcnow():
            return False

        # Check cooldown
        if alert.last_triggered_at:
            cooldown_end = alert.last_triggered_at + timedelta(minutes=alert.cooldown_minutes)
            if datetime.utcnow() < cooldown_end:
                return False

        return True

    async def _check_single_alert(
        self,
        alert: Alert,
        current_rate: float,
        rate_24h_ago: Optional[float],
        sentiment_score: Optional[float]
    ) -> Optional[TriggeredAlert]:
        """Check a single alert condition"""

        alert_type = alert.alert_type
        threshold = alert.threshold_value

        triggered = False
        message = ""

        if alert_type == AlertType.PRICE_ABOVE.value:
            if current_rate >= threshold:
                triggered = True
                message = f"El tipo de cambio {alert.base_currency}/{alert.target_currency} ha superado {threshold:.4f}. Valor actual: {current_rate:.4f}"

        elif alert_type == AlertType.PRICE_BELOW.value:
            if current_rate <= threshold:
                triggered = True
                message = f"El tipo de cambio {alert.base_currency}/{alert.target_currency} ha caido por debajo de {threshold:.4f}. Valor actual: {current_rate:.4f}"

        elif alert_type == AlertType.PERCENT_CHANGE.value:
            if rate_24h_ago:
                change_percent = ((current_rate - rate_24h_ago) / rate_24h_ago) * 100
                if abs(change_percent) >= threshold:
                    direction = "subido" if change_percent > 0 else "bajado"
                    triggered = True
                    message = f"El {alert.base_currency}/{alert.target_currency} ha {direction} {abs(change_percent):.2f}% en las ultimas 24h"

        elif alert_type == AlertType.SENTIMENT_SHIFT.value:
            if sentiment_score is not None:
                # Threshold is sentiment score (-1 to 1)
                # Positive threshold = alert when sentiment goes above
                # Negative threshold = alert when sentiment goes below
                if threshold >= 0 and sentiment_score >= threshold:
                    triggered = True
                    message = f"Sentimiento del mercado muy positivo: {sentiment_score:.2f}"
                elif threshold < 0 and sentiment_score <= threshold:
                    triggered = True
                    message = f"Sentimiento del mercado muy negativo: {sentiment_score:.2f}"

        elif alert_type == AlertType.NEWS_IMPACT.value:
            # This would be triggered by news service when high-impact news arrives
            # For now, trigger on extreme sentiment
            if sentiment_score is not None and abs(sentiment_score) >= 0.5:
                triggered = True
                mood = "positivas" if sentiment_score > 0 else "negativas"
                message = f"Noticias de alto impacto detectadas. Tendencia {mood}."

        if triggered:
            logger.info(f"Alert triggered: {alert.name} - {message}")
            return TriggeredAlert(
                alert=AlertResponse(
                    id=alert.id,
                    name=alert.name,
                    alert_type=alert.alert_type,
                    base_currency=alert.base_currency,
                    target_currency=alert.target_currency,
                    threshold_value=alert.threshold_value,
                    status=alert.status,
                    is_recurring=alert.is_recurring,
                    cooldown_minutes=alert.cooldown_minutes,
                    notify_push=alert.notify_push,
                    notify_sound=alert.notify_sound,
                    created_at=alert.created_at,
                    last_triggered_at=alert.last_triggered_at,
                    expires_at=alert.expires_at
                ),
                current_value=current_rate,
                message=message,
                triggered_at=datetime.utcnow()
            )

        return None


def generate_alert_message(alert_type: str, threshold: float, current_value: float, currency_pair: str) -> str:
    """Generate human-readable alert message"""
    messages = {
        AlertType.PRICE_ABOVE.value: f"{currency_pair} supera {threshold:.4f} (actual: {current_value:.4f})",
        AlertType.PRICE_BELOW.value: f"{currency_pair} cae bajo {threshold:.4f} (actual: {current_value:.4f})",
        AlertType.PERCENT_CHANGE.value: f"{currency_pair} cambio >{threshold}% en 24h",
        AlertType.SENTIMENT_SHIFT.value: f"Cambio de sentimiento detectado",
        AlertType.NEWS_IMPACT.value: f"Noticias de alto impacto"
    }
    return messages.get(alert_type, "Alerta activada")
