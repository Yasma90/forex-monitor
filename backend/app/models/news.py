from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, Text, Index
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel
from typing import Optional

from .database import Base


class NewsArticle(Base):
    """SQLAlchemy model for news articles"""
    __tablename__ = "news_articles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    url: Mapped[str] = mapped_column(String(1000), nullable=False, unique=True)
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    image_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    published_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Sentiment analysis
    sentiment_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # -1 to 1
    sentiment_label: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # positive, negative, neutral

    # Relevance
    relevance_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 0 to 1
    keywords_matched: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # comma-separated

    __table_args__ = (
        Index('ix_news_published_at', 'published_at'),
        Index('ix_news_sentiment', 'sentiment_label'),
    )


# Pydantic schemas
class NewsArticleCreate(BaseModel):
    title: str
    description: Optional[str] = None
    content: Optional[str] = None
    url: str
    source: str
    image_url: Optional[str] = None
    published_at: datetime


class NewsArticleResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    url: str
    source: str
    image_url: Optional[str]
    published_at: datetime
    sentiment_score: Optional[float]
    sentiment_label: Optional[str]
    relevance_score: Optional[float]
    keywords_matched: Optional[str]

    class Config:
        from_attributes = True


class NewsFeedResponse(BaseModel):
    articles: list[NewsArticleResponse]
    total: int
    sentiment_summary: dict  # {positive: n, negative: n, neutral: n}
    avg_sentiment: float
