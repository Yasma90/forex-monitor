from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from ...models.database import get_db
from ...models.news import NewsArticleResponse, NewsFeedResponse, NewsArticleCreate
from ...services.news import NewsFetcher, NewsRepository, calculate_relevance
from ...services.news.sentiment import get_analyzer

router = APIRouter(prefix="/api/news", tags=["news"])


@router.get("/feed", response_model=NewsFeedResponse)
async def get_news_feed(
    limit: int = Query(default=20, ge=1, le=50),
    hours: int = Query(default=48, ge=1, le=168),
    min_relevance: float = Query(default=0.0, ge=0.0, le=1.0),
    sentiment: Optional[str] = Query(default=None, description="Filter: positive, negative, neutral"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the latest forex-related news with sentiment analysis.
    """
    repo = NewsRepository(db)

    # Get articles from database
    articles = await repo.get_recent(
        limit=limit,
        hours=hours,
        min_relevance=min_relevance,
        sentiment_filter=sentiment
    )

    # If no articles or too few, try fetching fresh
    if len(articles) < 5:
        await _refresh_news(db)
        articles = await repo.get_recent(
            limit=limit,
            hours=hours,
            min_relevance=min_relevance,
            sentiment_filter=sentiment
        )

    # Get sentiment summary
    sentiment_summary = await repo.get_sentiment_summary(hours=hours)
    avg_sentiment = await repo.get_avg_sentiment(hours=hours)

    return NewsFeedResponse(
        articles=[NewsArticleResponse(
            id=a.id,
            title=a.title,
            description=a.description,
            url=a.url,
            source=a.source,
            image_url=a.image_url,
            published_at=a.published_at,
            sentiment_score=a.sentiment_score,
            sentiment_label=a.sentiment_label,
            relevance_score=a.relevance_score,
            keywords_matched=a.keywords_matched
        ) for a in articles],
        total=len(articles),
        sentiment_summary=sentiment_summary,
        avg_sentiment=avg_sentiment
    )


@router.post("/refresh")
async def refresh_news(db: AsyncSession = Depends(get_db)):
    """
    Manually refresh news from APIs.
    """
    count = await _refresh_news(db)
    return {"message": f"Fetched and analyzed {count} articles"}


@router.get("/sentiment-summary")
async def get_sentiment_summary(
    hours: int = Query(default=24, ge=1, le=168),
    db: AsyncSession = Depends(get_db)
):
    """
    Get sentiment distribution for recent news.
    """
    repo = NewsRepository(db)
    summary = await repo.get_sentiment_summary(hours=hours)
    avg = await repo.get_avg_sentiment(hours=hours)

    total = sum(summary.values())

    # Determine market mood
    if avg > 0.15:
        mood = "BULLISH"
        mood_description = "Noticias predominantemente positivas para USD/EUR"
    elif avg < -0.15:
        mood = "BEARISH"
        mood_description = "Noticias predominantemente negativas para USD/EUR"
    else:
        mood = "NEUTRAL"
        mood_description = "Sentimiento mixto en las noticias"

    return {
        "summary": summary,
        "total_articles": total,
        "avg_sentiment": round(avg, 3),
        "mood": mood,
        "mood_description": mood_description,
        "period_hours": hours
    }


async def _refresh_news(db: AsyncSession) -> int:
    """Internal function to fetch and process news"""
    fetcher = NewsFetcher()
    analyzer = get_analyzer()
    repo = NewsRepository(db)

    try:
        raw_articles = await fetcher.fetch_news(max_articles=20)

        saved_count = 0
        for article_data in raw_articles:
            # Skip invalid articles
            if not article_data.get("title") or not article_data.get("url"):
                continue

            # Calculate relevance
            text = f"{article_data.get('title', '')} {article_data.get('description', '')}"
            relevance_score, keywords = calculate_relevance(text)

            # Skip low relevance articles
            if relevance_score < 0.1:
                continue

            # Analyze sentiment
            sentiment = await analyzer.analyze(text)

            # Save to database
            article_create = NewsArticleCreate(
                title=article_data["title"],
                description=article_data.get("description"),
                content=article_data.get("content"),
                url=article_data["url"],
                source=article_data.get("source", "Unknown"),
                image_url=article_data.get("image_url"),
                published_at=article_data.get("published_at")
            )

            saved = await repo.save_article(
                article_create,
                sentiment_score=sentiment["score"],
                sentiment_label=sentiment["label"],
                relevance_score=relevance_score,
                keywords_matched=keywords
            )

            if saved:
                saved_count += 1

        return saved_count

    finally:
        await fetcher.close()
