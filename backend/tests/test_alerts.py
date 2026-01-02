"""
Tests for the alerts service.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

from app.models.alert import Alert, AlertType, AlertStatus
from app.services.alerts.checker import AlertChecker


def create_mock_alert(
    id: int,
    alert_type: str,
    threshold: float,
    status: str = "active",
    is_recurring: bool = False,
    cooldown_minutes: int = 60,
    last_triggered_at: datetime = None
) -> MagicMock:
    """Create a mock alert for testing"""
    alert = MagicMock(spec=Alert)
    alert.id = id
    alert.name = f"Test Alert {id}"
    alert.alert_type = alert_type
    alert.threshold_value = threshold
    alert.base_currency = "USD"
    alert.target_currency = "EUR"
    alert.status = status
    alert.is_recurring = is_recurring
    alert.cooldown_minutes = cooldown_minutes
    alert.last_triggered_at = last_triggered_at
    alert.expires_at = None
    alert.notify_push = True
    alert.notify_sound = True
    alert.created_at = datetime.utcnow()
    return alert


class TestAlertChecker:
    """Tests for AlertChecker class"""

    @pytest.fixture
    def checker(self):
        """Create alert checker instance"""
        return AlertChecker()

    @pytest.fixture
    def price_above_alert(self):
        """Create a price above alert"""
        return create_mock_alert(
            id=1,
            alert_type=AlertType.PRICE_ABOVE.value,
            threshold=1.10
        )

    @pytest.fixture
    def price_below_alert(self):
        """Create a price below alert"""
        return create_mock_alert(
            id=2,
            alert_type=AlertType.PRICE_BELOW.value,
            threshold=1.05
        )

    @pytest.fixture
    def percent_change_alert(self):
        """Create a percent change alert"""
        return create_mock_alert(
            id=3,
            alert_type=AlertType.PERCENT_CHANGE.value,
            threshold=2.0,
            is_recurring=True
        )

    @pytest.fixture
    def sentiment_alert(self):
        """Create a sentiment change alert"""
        return create_mock_alert(
            id=4,
            alert_type=AlertType.SENTIMENT_SHIFT.value,
            threshold=-0.5,
            is_recurring=True,
            cooldown_minutes=120
        )

    @pytest.mark.asyncio
    async def test_price_above_triggered(self, checker, price_above_alert):
        """Test price above alert triggers correctly"""
        triggered = await checker.check_alerts(
            alerts=[price_above_alert],
            current_rate=1.12,
            rate_24h_ago=1.08,
            sentiment_score=0
        )

        assert len(triggered) == 1
        assert triggered[0].alert.id == 1
        assert triggered[0].current_value == 1.12

    @pytest.mark.asyncio
    async def test_price_above_not_triggered(self, checker, price_above_alert):
        """Test price above alert doesn't trigger when below threshold"""
        triggered = await checker.check_alerts(
            alerts=[price_above_alert],
            current_rate=1.08,
            rate_24h_ago=1.07,
            sentiment_score=0
        )

        assert len(triggered) == 0

    @pytest.mark.asyncio
    async def test_price_below_triggered(self, checker, price_below_alert):
        """Test price below alert triggers correctly"""
        triggered = await checker.check_alerts(
            alerts=[price_below_alert],
            current_rate=1.03,
            rate_24h_ago=1.08,
            sentiment_score=0
        )

        assert len(triggered) == 1
        assert triggered[0].alert.id == 2

    @pytest.mark.asyncio
    async def test_price_below_not_triggered(self, checker, price_below_alert):
        """Test price below alert doesn't trigger when above threshold"""
        triggered = await checker.check_alerts(
            alerts=[price_below_alert],
            current_rate=1.08,
            rate_24h_ago=1.07,
            sentiment_score=0
        )

        assert len(triggered) == 0

    @pytest.mark.asyncio
    async def test_percent_change_triggered(self, checker, percent_change_alert):
        """Test percent change alert triggers correctly"""
        # ~2.8% change should trigger 2% threshold
        triggered = await checker.check_alerts(
            alerts=[percent_change_alert],
            current_rate=1.10,
            rate_24h_ago=1.07,
            sentiment_score=0
        )

        assert len(triggered) == 1
        assert triggered[0].alert.id == 3

    @pytest.mark.asyncio
    async def test_percent_change_not_triggered(self, checker, percent_change_alert):
        """Test percent change alert doesn't trigger below threshold"""
        # ~0.9% change should not trigger 2% threshold
        triggered = await checker.check_alerts(
            alerts=[percent_change_alert],
            current_rate=1.08,
            rate_24h_ago=1.07,
            sentiment_score=0
        )

        assert len(triggered) == 0

    @pytest.mark.asyncio
    async def test_sentiment_alert_triggered(self, checker, sentiment_alert):
        """Test sentiment alert triggers correctly"""
        triggered = await checker.check_alerts(
            alerts=[sentiment_alert],
            current_rate=1.08,
            rate_24h_ago=1.07,
            sentiment_score=-0.7
        )

        assert len(triggered) == 1
        assert triggered[0].alert.id == 4

    @pytest.mark.asyncio
    async def test_sentiment_alert_not_triggered(self, checker, sentiment_alert):
        """Test sentiment alert doesn't trigger above threshold"""
        triggered = await checker.check_alerts(
            alerts=[sentiment_alert],
            current_rate=1.08,
            rate_24h_ago=1.07,
            sentiment_score=-0.3
        )

        assert len(triggered) == 0

    @pytest.mark.asyncio
    async def test_multiple_alerts(
        self, checker, price_above_alert, price_below_alert, percent_change_alert
    ):
        """Test checking multiple alerts at once"""
        triggered = await checker.check_alerts(
            alerts=[price_above_alert, price_below_alert, percent_change_alert],
            current_rate=1.12,
            rate_24h_ago=1.08,
            sentiment_score=0
        )

        # Should trigger price_above and percent_change (~3.7%)
        assert len(triggered) == 2
        triggered_ids = [t.alert.id for t in triggered]
        assert 1 in triggered_ids
        assert 3 in triggered_ids

    @pytest.mark.asyncio
    async def test_inactive_alert_not_checked(self, checker, price_above_alert):
        """Test inactive alerts are not checked"""
        price_above_alert.status = "triggered"
        triggered = await checker.check_alerts(
            alerts=[price_above_alert],
            current_rate=1.12,
            rate_24h_ago=1.08,
            sentiment_score=0
        )

        assert len(triggered) == 0

    @pytest.mark.asyncio
    async def test_cooldown_prevents_trigger(self, checker, price_above_alert):
        """Test cooldown prevents re-triggering"""
        price_above_alert.is_recurring = True
        price_above_alert.last_triggered_at = datetime.utcnow() - timedelta(minutes=30)

        triggered = await checker.check_alerts(
            alerts=[price_above_alert],
            current_rate=1.12,
            rate_24h_ago=1.08,
            sentiment_score=0
        )

        # Should not trigger due to cooldown (60 min)
        assert len(triggered) == 0

    @pytest.mark.asyncio
    async def test_cooldown_expired_allows_trigger(self, checker, price_above_alert):
        """Test expired cooldown allows re-triggering"""
        price_above_alert.is_recurring = True
        price_above_alert.last_triggered_at = datetime.utcnow() - timedelta(minutes=90)

        triggered = await checker.check_alerts(
            alerts=[price_above_alert],
            current_rate=1.12,
            rate_24h_ago=1.08,
            sentiment_score=0
        )

        assert len(triggered) == 1

    @pytest.mark.asyncio
    async def test_expired_alert_not_checked(self, checker, price_above_alert):
        """Test expired alerts are not checked"""
        price_above_alert.expires_at = datetime.utcnow() - timedelta(hours=1)

        triggered = await checker.check_alerts(
            alerts=[price_above_alert],
            current_rate=1.12,
            rate_24h_ago=1.08,
            sentiment_score=0
        )

        assert len(triggered) == 0

    @pytest.mark.asyncio
    async def test_news_impact_triggered(self, checker):
        """Test news impact alert triggers on extreme sentiment"""
        news_alert = create_mock_alert(
            id=5,
            alert_type=AlertType.NEWS_IMPACT.value,
            threshold=0.5
        )

        triggered = await checker.check_alerts(
            alerts=[news_alert],
            current_rate=1.08,
            rate_24h_ago=1.07,
            sentiment_score=0.7
        )

        assert len(triggered) == 1
        assert triggered[0].alert.id == 5

    @pytest.mark.asyncio
    async def test_empty_alerts_list(self, checker):
        """Test handling empty alerts list"""
        triggered = await checker.check_alerts(
            alerts=[],
            current_rate=1.08,
            rate_24h_ago=1.07,
            sentiment_score=0
        )

        assert len(triggered) == 0
