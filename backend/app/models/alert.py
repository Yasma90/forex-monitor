from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean, Enum as SQLEnum, Index
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel
from typing import Optional
from enum import Enum

from .database import Base


class AlertType(str, Enum):
    PRICE_ABOVE = "price_above"      # Trigger when rate goes above threshold
    PRICE_BELOW = "price_below"      # Trigger when rate goes below threshold
    PERCENT_CHANGE = "percent_change" # Trigger on X% change in 24h
    SENTIMENT_SHIFT = "sentiment"     # Trigger on sentiment change
    NEWS_IMPACT = "news_impact"       # Trigger on high-impact news


class AlertStatus(str, Enum):
    ACTIVE = "active"
    TRIGGERED = "triggered"
    PAUSED = "paused"
    EXPIRED = "expired"


class Alert(Base):
    """SQLAlchemy model for user alerts"""
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Alert configuration
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    alert_type: Mapped[str] = mapped_column(String(20), nullable=False)
    base_currency: Mapped[str] = mapped_column(String(3), default="USD")
    target_currency: Mapped[str] = mapped_column(String(3), default="EUR")

    # Threshold values
    threshold_value: Mapped[float] = mapped_column(Float, nullable=False)
    threshold_direction: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)  # above/below

    # Status
    status: Mapped[str] = mapped_column(String(20), default="active")
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False)  # Trigger once or multiple times
    cooldown_minutes: Mapped[int] = mapped_column(Integer, default=60)  # Min time between triggers

    # Notification settings
    notify_push: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_sound: Mapped[bool] = mapped_column(Boolean, default=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_triggered_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # User identifier (for multi-user support later)
    user_id: Mapped[str] = mapped_column(String(100), default="default")

    __table_args__ = (
        Index('ix_alerts_status', 'status'),
        Index('ix_alerts_user_status', 'user_id', 'status'),
        Index('ix_alerts_expires', 'expires_at'),
    )


class AlertHistory(Base):
    """History of triggered alerts"""
    __tablename__ = "alert_history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    alert_id: Mapped[int] = mapped_column(Integer, nullable=False)
    triggered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    trigger_value: Mapped[float] = mapped_column(Float, nullable=False)
    message: Mapped[str] = mapped_column(String(500), nullable=False)

    __table_args__ = (
        Index('ix_alert_history_alert_id', 'alert_id'),
        Index('ix_alert_history_triggered_at', 'triggered_at'),
    )


# Pydantic schemas
class AlertCreate(BaseModel):
    name: str
    alert_type: AlertType
    base_currency: str = "USD"
    target_currency: str = "EUR"
    threshold_value: float
    is_recurring: bool = False
    cooldown_minutes: int = 60
    notify_push: bool = True
    notify_sound: bool = True
    expires_at: Optional[datetime] = None


class AlertUpdate(BaseModel):
    name: Optional[str] = None
    threshold_value: Optional[float] = None
    status: Optional[AlertStatus] = None
    is_recurring: Optional[bool] = None
    cooldown_minutes: Optional[int] = None
    notify_push: Optional[bool] = None
    notify_sound: Optional[bool] = None


class AlertResponse(BaseModel):
    id: int
    name: str
    alert_type: str
    base_currency: str
    target_currency: str
    threshold_value: float
    status: str
    is_recurring: bool
    cooldown_minutes: int
    notify_push: bool
    notify_sound: bool
    created_at: datetime
    last_triggered_at: Optional[datetime]
    expires_at: Optional[datetime]

    class Config:
        from_attributes = True


class AlertHistoryResponse(BaseModel):
    id: int
    alert_id: int
    triggered_at: datetime
    trigger_value: float
    message: str

    class Config:
        from_attributes = True


class TriggeredAlert(BaseModel):
    """Alert that was just triggered - for notification"""
    alert: AlertResponse
    current_value: float
    message: str
    triggered_at: datetime
