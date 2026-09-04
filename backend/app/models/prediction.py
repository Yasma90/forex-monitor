from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class PredictionPoint(BaseModel):
    """A single prediction point"""
    date: str
    predicted_rate: float
    lower_bound: float  # 95% confidence interval
    upper_bound: float


class PredictionResponse(BaseModel):
    """Full prediction response"""
    base_currency: str
    target_currency: str
    current_rate: float
    predictions: list[PredictionPoint]

    # Signal
    signal: str  # BULLISH, BEARISH, NEUTRAL
    signal_strength: float  # 0 to 1
    signal_description: str

    # Sentiment adjustment
    sentiment_impact: float  # How much sentiment affected prediction
    sentiment_mood: str

    # Metadata
    model_type: str
    confidence_level: float
    generated_at: datetime

    # Predicted change
    predicted_change_7d: float  # Percentage change in 7 days
    predicted_change_30d: float  # Percentage change in 30 days


class SignalResponse(BaseModel):
    """Quick signal without full prediction"""
    signal: str
    strength: float
    description: str
    factors: list[str]
