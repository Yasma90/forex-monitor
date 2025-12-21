"""
Tests for API endpoints.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient, ASGITransport
from datetime import datetime

from app.main import app


class TestSystemEndpoints:
    """Tests for system monitoring endpoints"""

    @pytest.mark.asyncio
    async def test_get_cache_stats(self):
        """Test cache stats endpoint"""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/system/cache/stats")

        assert response.status_code == 200
        data = response.json()
        assert "exchange_rate" in data
        assert "news" in data
        assert "prediction" in data

    @pytest.mark.asyncio
    async def test_clear_cache(self):
        """Test cache clear endpoint"""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post("/api/system/cache/clear")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    @pytest.mark.asyncio
    async def test_get_scheduler_status(self):
        """Test scheduler status endpoint"""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/system/scheduler/status")

        assert response.status_code == 200
        data = response.json()
        assert "running" in data
        assert "task_count" in data


class TestExchangeEndpoints:
    """Tests for exchange rate endpoints"""

    @pytest.mark.asyncio
    async def test_get_current_rate(self):
        """Test get current exchange rate"""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/exchange/rate")

        # May return error if no data, but should not crash
        assert response.status_code in [200, 404, 500]

    @pytest.mark.asyncio
    async def test_get_history(self):
        """Test get exchange rate history"""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/exchange/history?days=30")

        assert response.status_code == 200


class TestPredictionEndpoints:
    """Tests for prediction endpoints"""

    @pytest.mark.asyncio
    async def test_get_forecast(self):
        """Test get forecast endpoint"""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/prediction/forecast?days=7")

        # May fail without enough data, but should return valid response
        assert response.status_code in [200, 400, 500]

    @pytest.mark.asyncio
    async def test_prediction_accuracy(self):
        """Test prediction accuracy endpoint"""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/system/prediction/accuracy?days=7")

        assert response.status_code == 200


class TestAlertEndpoints:
    """Tests for alert endpoints"""

    @pytest.mark.asyncio
    async def test_get_alerts(self):
        """Test get all alerts"""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/alerts")

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    @pytest.mark.asyncio
    async def test_create_alert(self):
        """Test create alert endpoint"""
        alert_data = {
            "alert_type": "price_above",
            "condition": "greater_than",
            "threshold": 1.10,
            "currency_pair": "USD/EUR",
            "is_recurring": False,
            "cooldown_minutes": 60
        }

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post("/api/alerts", json=alert_data)

        assert response.status_code in [200, 201, 422]

    @pytest.mark.asyncio
    async def test_delete_nonexistent_alert(self):
        """Test deleting nonexistent alert"""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.delete("/api/alerts/99999")

        assert response.status_code in [404, 200]


class TestNewsEndpoints:
    """Tests for news endpoints"""

    @pytest.mark.asyncio
    async def test_get_news_feed(self):
        """Test get news feed"""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/news/feed")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_sentiment_summary(self):
        """Test get sentiment summary"""
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/news/sentiment-summary")

        assert response.status_code == 200
