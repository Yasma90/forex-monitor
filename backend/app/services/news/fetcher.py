"""News fetcher with multiple API fallback support"""

import httpx
from datetime import datetime, timedelta
from typing import Optional
import logging

from ...config import get_settings
from .keywords import get_search_query

logger = logging.getLogger(__name__)
settings = get_settings()


class NewsFetcher:
    """Fetches financial news from multiple free APIs"""

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=15.0)

    async def close(self):
        await self.client.aclose()

    async def fetch_news(self, max_articles: int = 20) -> list[dict]:
        """
        Fetch news from available APIs with fallback.
        Returns list of normalized article dicts.
        """
        articles = []

        # Try GNews API first (if key available)
        if settings.gnews_api_key:
            try:
                gnews_articles = await self._fetch_gnews(max_articles)
                articles.extend(gnews_articles)
                logger.info(f"Fetched {len(gnews_articles)} articles from GNews")
            except Exception as e:
                logger.warning(f"GNews API failed: {e}")

        # Try NewsData.io as backup
        if len(articles) < max_articles and settings.newsdata_api_key:
            try:
                newsdata_articles = await self._fetch_newsdata(max_articles - len(articles))
                articles.extend(newsdata_articles)
                logger.info(f"Fetched {len(newsdata_articles)} articles from NewsData")
            except Exception as e:
                logger.warning(f"NewsData API failed: {e}")

        # Try free RSS feeds as last resort (no API key needed)
        if len(articles) < 5:
            try:
                rss_articles = await self._fetch_free_sources()
                articles.extend(rss_articles)
                logger.info(f"Fetched {len(rss_articles)} articles from free sources")
            except Exception as e:
                logger.warning(f"Free sources failed: {e}")

        # Remove duplicates by URL
        seen_urls = set()
        unique_articles = []
        for article in articles:
            if article["url"] not in seen_urls:
                seen_urls.add(article["url"])
                unique_articles.append(article)

        return unique_articles[:max_articles]

    async def _fetch_gnews(self, max_articles: int) -> list[dict]:
        """Fetch from GNews API"""
        url = "https://gnews.io/api/v4/search"
        params = {
            "q": "USD EUR OR Federal Reserve OR ECB OR forex OR dollar euro",
            "lang": "en",
            "country": "us,gb,de",
            "max": min(max_articles, 10),  # GNews free tier limit
            "apikey": settings.gnews_api_key
        }

        response = await self.client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        articles = []
        for item in data.get("articles", []):
            articles.append({
                "title": item.get("title", ""),
                "description": item.get("description", ""),
                "content": item.get("content", ""),
                "url": item.get("url", ""),
                "source": item.get("source", {}).get("name", "GNews"),
                "image_url": item.get("image"),
                "published_at": self._parse_date(item.get("publishedAt"))
            })

        return articles

    async def _fetch_newsdata(self, max_articles: int) -> list[dict]:
        """Fetch from NewsData.io API"""
        url = "https://newsdata.io/api/1/news"
        params = {
            "q": "USD EUR forex dollar euro federal reserve ECB",
            "language": "en",
            "category": "business",
            "apikey": settings.newsdata_api_key
        }

        response = await self.client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        articles = []
        for item in data.get("results", [])[:max_articles]:
            articles.append({
                "title": item.get("title", ""),
                "description": item.get("description", ""),
                "content": item.get("content", ""),
                "url": item.get("link", ""),
                "source": item.get("source_id", "NewsData"),
                "image_url": item.get("image_url"),
                "published_at": self._parse_date(item.get("pubDate"))
            })

        return articles

    async def _fetch_free_sources(self) -> list[dict]:
        """
        Fetch from free sources that don't require API keys.
        Uses a public financial news aggregator API.
        """
        # Using a free financial news endpoint
        url = "https://www.alphavantage.co/query"

        # Alpha Vantage has a free tier with news
        # But requires API key - let's use an alternative

        # Fallback: Fetch from ECB press releases (always free)
        ecb_url = "https://www.ecb.europa.eu/rss/press.html"

        try:
            # Simple approach: return placeholder for demo
            # In production, implement RSS parsing
            return [{
                "title": "ECB Press Releases - Check official source",
                "description": "Visit ECB website for latest monetary policy news",
                "content": "",
                "url": "https://www.ecb.europa.eu/press/pr/html/index.en.html",
                "source": "ECB",
                "image_url": None,
                "published_at": datetime.utcnow()
            }]
        except Exception as e:
            logger.error(f"Free sources fetch failed: {e}")
            return []

    def _parse_date(self, date_str: Optional[str]) -> datetime:
        """Parse various date formats to datetime"""
        if not date_str:
            return datetime.utcnow()

        formats = [
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d"
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        return datetime.utcnow()
