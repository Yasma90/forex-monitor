"""Database operations for news articles"""

from datetime import datetime, timedelta
from sqlalchemy import select, func, or_, exists, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from ...models.news import NewsArticle, NewsArticleCreate


class NewsRepository:
    """Database operations for news articles"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def save_article(
        self,
        article_data: NewsArticleCreate,
        sentiment_score: Optional[float] = None,
        sentiment_label: Optional[str] = None,
        relevance_score: Optional[float] = None,
        keywords_matched: Optional[list[str]] = None
    ) -> Optional[NewsArticle]:
        """Save a news article to the database"""

        # Check if article already exists (by URL) - optimized with exists()
        exists_query = select(exists().where(NewsArticle.url == article_data.url))
        result = await self.db.execute(exists_query)
        if result.scalar():
            return await self.get_by_url(article_data.url)

        article = NewsArticle(
            title=article_data.title,
            description=article_data.description,
            content=article_data.content,
            url=article_data.url,
            source=article_data.source,
            image_url=article_data.image_url,
            published_at=article_data.published_at,
            fetched_at=datetime.utcnow(),
            sentiment_score=sentiment_score,
            sentiment_label=sentiment_label,
            relevance_score=relevance_score,
            keywords_matched=",".join(keywords_matched) if keywords_matched else None
        )

        self.db.add(article)
        await self.db.commit()
        await self.db.refresh(article)
        return article

    async def save_articles_batch(
        self,
        articles: list[tuple[NewsArticleCreate, Optional[float], Optional[str], Optional[float], Optional[list[str]]]]
    ) -> int:
        """
        Save multiple articles in a single transaction (batch insert).
        Returns count of newly inserted articles.
        """
        if not articles:
            return 0

        # Get existing URLs to avoid duplicates
        urls = [a[0].url for a in articles]
        existing_result = await self.db.execute(
            select(NewsArticle.url).where(NewsArticle.url.in_(urls))
        )
        existing_urls = set(row[0] for row in existing_result)

        # Filter out existing articles
        new_articles = []
        for article_data, sentiment_score, sentiment_label, relevance_score, keywords_matched in articles:
            if article_data.url not in existing_urls:
                new_articles.append(NewsArticle(
                    title=article_data.title,
                    description=article_data.description,
                    content=article_data.content,
                    url=article_data.url,
                    source=article_data.source,
                    image_url=article_data.image_url,
                    published_at=article_data.published_at,
                    fetched_at=datetime.utcnow(),
                    sentiment_score=sentiment_score,
                    sentiment_label=sentiment_label,
                    relevance_score=relevance_score,
                    keywords_matched=",".join(keywords_matched) if keywords_matched else None
                ))

        if new_articles:
            self.db.add_all(new_articles)
            await self.db.commit()

        return len(new_articles)

    async def get_by_url(self, url: str) -> Optional[NewsArticle]:
        """Get article by URL"""
        result = await self.db.execute(
            select(NewsArticle).where(NewsArticle.url == url)
        )
        return result.scalar_one_or_none()

    async def get_recent(
        self,
        limit: int = 20,
        hours: int = 48,
        min_relevance: float = 0.0,
        sentiment_filter: Optional[str] = None
    ) -> list[NewsArticle]:
        """Get recent articles with optional filtering"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)

        query = (
            select(NewsArticle)
            .where(NewsArticle.published_at >= cutoff)
        )

        if min_relevance > 0:
            query = query.where(
                or_(
                    NewsArticle.relevance_score >= min_relevance,
                    NewsArticle.relevance_score.is_(None)  # Include unscored
                )
            )

        if sentiment_filter:
            query = query.where(NewsArticle.sentiment_label == sentiment_filter)

        query = (
            query
            .order_by(NewsArticle.published_at.desc())
            .limit(limit)
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_sentiment_summary(self, hours: int = 24) -> dict:
        """Get sentiment distribution for recent articles"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)

        result = await self.db.execute(
            select(
                NewsArticle.sentiment_label,
                func.count(NewsArticle.id).label("count")
            )
            .where(NewsArticle.published_at >= cutoff)
            .where(NewsArticle.sentiment_label.isnot(None))
            .group_by(NewsArticle.sentiment_label)
        )

        summary = {"positive": 0, "negative": 0, "neutral": 0}
        for row in result:
            if row.sentiment_label in summary:
                summary[row.sentiment_label] = row.count

        return summary

    async def get_avg_sentiment(self, hours: int = 24) -> float:
        """Get average sentiment score for recent articles"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)

        result = await self.db.execute(
            select(func.avg(NewsArticle.sentiment_score))
            .where(NewsArticle.published_at >= cutoff)
            .where(NewsArticle.sentiment_score.isnot(None))
        )

        avg = result.scalar()
        return float(avg) if avg else 0.0

    async def cleanup_old_articles(self, keep_days: int = 30) -> int:
        """
        Remove news articles older than keep_days.
        Returns count of deleted records.
        """
        cutoff = datetime.utcnow() - timedelta(days=keep_days)

        result = await self.db.execute(
            delete(NewsArticle).where(NewsArticle.published_at < cutoff)
        )
        await self.db.commit()

        return result.rowcount

    async def get_article_count(self, hours: int = 24) -> int:
        """Get count of articles in the specified period"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)

        result = await self.db.execute(
            select(func.count(NewsArticle.id))
            .where(NewsArticle.published_at >= cutoff)
        )

        return result.scalar() or 0
