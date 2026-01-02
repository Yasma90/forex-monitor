from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel
from typing import Optional

from .database import Base


class ExchangeRate(Base):
    """SQLAlchemy model for exchange rate records"""
    __tablename__ = "exchange_rates"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    base_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    target_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    rate: Mapped[float] = mapped_column(Float, nullable=False)
    source: Mapped[str] = mapped_column(String(50), nullable=False)  # API source
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('ix_exchange_rates_currencies_timestamp',
              'base_currency', 'target_currency', 'timestamp'),
    )


# Pydantic schemas
class ExchangeRateCreate(BaseModel):
    base_currency: str
    target_currency: str
    rate: float
    source: str


class ExchangeRateResponse(BaseModel):
    id: int
    base_currency: str
    target_currency: str
    rate: float
    source: str
    timestamp: datetime
    change_24h: Optional[float] = None
    change_percent_24h: Optional[float] = None

    class Config:
        from_attributes = True


class ExchangeRateHistoryResponse(BaseModel):
    rates: list[ExchangeRateResponse]
    min_rate: float
    max_rate: float
    avg_rate: float
    period_days: int
