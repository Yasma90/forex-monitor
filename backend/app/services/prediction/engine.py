"""
Prediction engine using Prophet (or fallback to simple methods).
Prophet is optional - if not installed, uses ARIMA-like approach.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional
import numpy as np

logger = logging.getLogger(__name__)

# Try to import Prophet, fall back to simple methods if not available
try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
    logger.info("Prophet is available for predictions")
except ImportError:
    PROPHET_AVAILABLE = False
    logger.warning("Prophet not installed, using fallback prediction method")


class PredictionEngine:
    """
    Exchange rate prediction engine.
    Uses Prophet if available, otherwise falls back to trend-based prediction.
    """

    def __init__(self):
        self.model = None
        self.last_trained = None

    async def predict(
        self,
        historical_data: list[dict],
        days_ahead: int = 30,
        sentiment_score: float = 0.0
    ) -> dict:
        """
        Generate predictions based on historical data and sentiment.

        Args:
            historical_data: List of {date, rate} dicts
            days_ahead: How many days to predict
            sentiment_score: Current sentiment (-1 to 1) to adjust prediction

        Returns:
            Dict with predictions, signal, and metadata
        """
        if len(historical_data) < 7:
            raise ValueError("Need at least 7 days of historical data")

        if PROPHET_AVAILABLE:
            return await self._predict_prophet(historical_data, days_ahead, sentiment_score)
        else:
            return await self._predict_fallback(historical_data, days_ahead, sentiment_score)

    async def _predict_prophet(
        self,
        historical_data: list[dict],
        days_ahead: int,
        sentiment_score: float
    ) -> dict:
        """Prediction using Facebook Prophet"""
        import pandas as pd

        # Prepare data for Prophet
        df = pd.DataFrame(historical_data)
        df.columns = ['ds', 'y']  # Prophet requires these column names
        df['ds'] = pd.to_datetime(df['ds'])

        # Train model
        model = Prophet(
            daily_seasonality=False,
            weekly_seasonality=True,
            yearly_seasonality=True,
            changepoint_prior_scale=0.05,  # More conservative
            interval_width=0.95
        )
        model.fit(df)

        # Generate future dates
        future = model.make_future_dataframe(periods=days_ahead)
        forecast = model.predict(future)

        # Get only future predictions
        future_forecast = forecast[forecast['ds'] > df['ds'].max()]

        # Apply sentiment adjustment
        sentiment_adjustment = self._calculate_sentiment_adjustment(sentiment_score)

        predictions = []
        for _, row in future_forecast.iterrows():
            adjusted_rate = row['yhat'] * (1 + sentiment_adjustment)
            adjusted_lower = row['yhat_lower'] * (1 + sentiment_adjustment)
            adjusted_upper = row['yhat_upper'] * (1 + sentiment_adjustment)

            predictions.append({
                'date': row['ds'].strftime('%Y-%m-%d'),
                'predicted_rate': round(adjusted_rate, 4),
                'lower_bound': round(adjusted_lower, 4),
                'upper_bound': round(adjusted_upper, 4)
            })

        # Calculate signal
        current_rate = historical_data[-1]['rate']
        predicted_7d = predictions[6]['predicted_rate'] if len(predictions) > 6 else predictions[-1]['predicted_rate']
        predicted_30d = predictions[-1]['predicted_rate'] if predictions else current_rate

        signal_info = self._generate_signal(current_rate, predicted_7d, predicted_30d, sentiment_score)

        return {
            'predictions': predictions,
            'signal': signal_info['signal'],
            'signal_strength': signal_info['strength'],
            'signal_description': signal_info['description'],
            'sentiment_impact': sentiment_adjustment,
            'model_type': 'prophet',
            'confidence_level': 0.75,
            'predicted_change_7d': ((predicted_7d - current_rate) / current_rate) * 100,
            'predicted_change_30d': ((predicted_30d - current_rate) / current_rate) * 100
        }

    async def _predict_fallback(
        self,
        historical_data: list[dict],
        days_ahead: int,
        sentiment_score: float
    ) -> dict:
        """
        Fallback prediction using exponential smoothing and trend analysis.
        Works without Prophet dependency.
        """
        rates = [d['rate'] for d in historical_data]
        dates = [d['date'] for d in historical_data]

        # Calculate trend using linear regression
        n = len(rates)
        x = np.arange(n)
        y = np.array(rates)

        # Simple linear regression
        x_mean = np.mean(x)
        y_mean = np.mean(y)
        slope = np.sum((x - x_mean) * (y - y_mean)) / np.sum((x - x_mean) ** 2)
        intercept = y_mean - slope * x_mean

        # Calculate volatility for confidence intervals
        residuals = y - (slope * x + intercept)
        volatility = np.std(residuals)

        # Apply exponential smoothing to recent data for short-term trend
        alpha = 0.3  # Smoothing factor
        smoothed = rates[-1]
        for rate in reversed(rates[-7:]):
            smoothed = alpha * rate + (1 - alpha) * smoothed

        # Sentiment adjustment
        sentiment_adjustment = self._calculate_sentiment_adjustment(sentiment_score)

        # Generate predictions
        predictions = []
        last_date = datetime.strptime(dates[-1], '%Y-%m-%d') if isinstance(dates[-1], str) else dates[-1]
        current_rate = rates[-1]

        for i in range(1, days_ahead + 1):
            future_date = last_date + timedelta(days=i)

            # Combine trend with exponential smoothing
            trend_prediction = slope * (n + i) + intercept
            smoothed_prediction = smoothed + (slope * i * 0.5)  # Dampened trend

            # Weighted average favoring smoothed for short-term
            weight = min(i / 30, 1)  # More weight to trend for longer horizons
            base_prediction = (1 - weight) * smoothed_prediction + weight * trend_prediction

            # Apply sentiment
            adjusted_prediction = base_prediction * (1 + sentiment_adjustment)

            # Confidence interval widens with time
            interval_width = volatility * np.sqrt(i) * 1.96

            predictions.append({
                'date': future_date.strftime('%Y-%m-%d'),
                'predicted_rate': round(adjusted_prediction, 4),
                'lower_bound': round(adjusted_prediction - interval_width, 4),
                'upper_bound': round(adjusted_prediction + interval_width, 4)
            })

        # Calculate signal
        predicted_7d = predictions[6]['predicted_rate'] if len(predictions) > 6 else predictions[-1]['predicted_rate']
        predicted_30d = predictions[-1]['predicted_rate'] if predictions else current_rate

        signal_info = self._generate_signal(current_rate, predicted_7d, predicted_30d, sentiment_score)

        return {
            'predictions': predictions,
            'signal': signal_info['signal'],
            'signal_strength': signal_info['strength'],
            'signal_description': signal_info['description'],
            'sentiment_impact': sentiment_adjustment,
            'model_type': 'trend_smoothing',
            'confidence_level': 0.60,  # Lower confidence for simpler model
            'predicted_change_7d': ((predicted_7d - current_rate) / current_rate) * 100,
            'predicted_change_30d': ((predicted_30d - current_rate) / current_rate) * 100
        }

    def _calculate_sentiment_adjustment(self, sentiment_score: float) -> float:
        """
        Calculate how much to adjust prediction based on sentiment.
        Sentiment affects prediction by up to ±1.5%
        """
        # Clip sentiment to valid range
        sentiment = max(-1, min(1, sentiment_score))

        # Non-linear adjustment - stronger effect at extremes
        adjustment = sentiment * 0.015 * (1 + abs(sentiment) * 0.5)

        return round(adjustment, 4)

    def _generate_signal(
        self,
        current_rate: float,
        predicted_7d: float,
        predicted_30d: float,
        sentiment: float
    ) -> dict:
        """Generate trading signal based on predictions and sentiment"""

        change_7d = ((predicted_7d - current_rate) / current_rate) * 100
        change_30d = ((predicted_30d - current_rate) / current_rate) * 100

        # Combine short and long term outlook
        combined_outlook = change_7d * 0.4 + change_30d * 0.4 + sentiment * 20 * 0.2

        if combined_outlook > 1.0:
            signal = 'BULLISH'
            if combined_outlook > 2.5:
                strength = 0.9
                desc = 'Fuerte tendencia alcista prevista. El EUR podria fortalecerse frente al USD.'
            else:
                strength = 0.6
                desc = 'Tendencia alcista moderada. El EUR muestra senales de fortaleza.'
        elif combined_outlook < -1.0:
            signal = 'BEARISH'
            if combined_outlook < -2.5:
                strength = 0.9
                desc = 'Fuerte tendencia bajista prevista. El USD podria fortalecerse frente al EUR.'
            else:
                strength = 0.6
                desc = 'Tendencia bajista moderada. El USD muestra senales de fortaleza.'
        else:
            signal = 'NEUTRAL'
            strength = 0.5
            desc = 'Mercado estable. No se esperan cambios significativos a corto plazo.'

        return {
            'signal': signal,
            'strength': strength,
            'description': desc
        }
