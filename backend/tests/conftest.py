"""
Pytest fixtures for forex-monitor tests.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.models.database import Base
from app.services.cache import InMemoryCache


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def async_db() -> AsyncGenerator[AsyncSession, None]:
    """Create in-memory database for testing"""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session

    await engine.dispose()


@pytest.fixture
def cache() -> InMemoryCache:
    """Create fresh cache instance for testing"""
    return InMemoryCache(default_ttl=60, max_entries=100)


@pytest.fixture
def sample_historical_data() -> list[dict]:
    """Generate sample historical exchange rate data"""
    base_rate = 1.08
    data = []
    for i in range(60):
        date = (datetime.now() - timedelta(days=60-i)).strftime("%Y-%m-%d")
        # Add some variation
        rate = base_rate + (i % 10 - 5) * 0.001
        data.append({"date": date, "rate": rate})
    return data


@pytest.fixture
def sample_news_data() -> list[dict]:
    """Generate sample news data"""
    return [
        {
            "title": "Fed raises interest rates by 0.25%",
            "description": "The Federal Reserve announced a rate hike today",
            "source": "Reuters",
            "url": "https://example.com/1",
            "published_at": datetime.now().isoformat()
        },
        {
            "title": "Euro strengthens against dollar",
            "description": "EUR/USD pair shows bullish momentum",
            "source": "Bloomberg",
            "url": "https://example.com/2",
            "published_at": datetime.now().isoformat()
        }
    ]


@pytest.fixture
def mock_exchange_fetcher():
    """Mock exchange rate fetcher"""
    fetcher = AsyncMock()
    fetcher.fetch_rate.return_value = {
        "base_currency": "USD",
        "target_currency": "EUR",
        "rate": 0.92,
        "source": "test"
    }
    fetcher.close = AsyncMock()
    return fetcher


@pytest.fixture
def mock_news_fetcher():
    """Mock news fetcher"""
    fetcher = AsyncMock()
    fetcher.fetch_news.return_value = [
        {
            "title": "Test News",
            "description": "Test description",
            "source": "Test Source",
            "url": "https://test.com",
            "published_at": datetime.now()
        }
    ]
    fetcher.close = AsyncMock()
    return fetcher
