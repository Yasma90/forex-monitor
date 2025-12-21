"""
Signal generator combining multiple factors for trading signals.
"""

from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class SignalGenerator:
    """
    Generates trading signals based on multiple factors:
    - Technical analysis (trend, momentum)
    - Sentiment analysis
    - Volatility
    - Economic calendar events
    """

    # Known high-impact events (simplified calendar)
    HIGH_IMPACT_EVENTS = {
        # Federal Reserve meetings 2024-2025 (approximate)
        'fed_meeting': [
            '2025-01-29', '2025-03-19', '2025-05-07', '2025-06-18',
            '2025-07-30', '2025-09-17', '2025-11-05', '2025-12-17'
        ],
        # ECB meetings 2024-2025 (approximate)
        'ecb_meeting': [
            '2025-01-30', '2025-03-06', '2025-04-17', '2025-06-05',
            '2025-07-17', '2025-09-11', '2025-10-30', '2025-12-18'
        ]
    }

    async def generate_signal(
        self,
        current_rate: float,
        historical_rates: list[float],
        sentiment_score: float = 0.0,
        prediction_change: float = 0.0
    ) -> dict:
        """
        Generate comprehensive trading signal.

        Args:
            current_rate: Current exchange rate
            historical_rates: List of recent rates (at least 14 days)
            sentiment_score: News sentiment (-1 to 1)
            prediction_change: Predicted change percentage

        Returns:
            Signal dict with recommendation and factors
        """
        factors = []
        scores = []

        # 1. Trend Analysis
        trend_signal, trend_score = self._analyze_trend(historical_rates)
        factors.append(f"Tendencia: {trend_signal}")
        scores.append(trend_score)

        # 2. Momentum (Rate of Change)
        momentum_signal, momentum_score = self._analyze_momentum(historical_rates)
        factors.append(f"Momentum: {momentum_signal}")
        scores.append(momentum_score)

        # 3. Volatility
        volatility_signal, vol_score = self._analyze_volatility(historical_rates)
        factors.append(f"Volatilidad: {volatility_signal}")
        scores.append(vol_score * 0.5)  # Lower weight for volatility

        # 4. Sentiment
        sentiment_signal = self._interpret_sentiment(sentiment_score)
        factors.append(f"Sentimiento: {sentiment_signal}")
        scores.append(sentiment_score * 0.3)

        # 5. Prediction
        if abs(prediction_change) > 0.1:
            pred_signal = "alcista" if prediction_change > 0 else "bajista"
            factors.append(f"Prediccion {abs(prediction_change):.1f}% {pred_signal}")
            scores.append(prediction_change / 5)  # Normalize

        # 6. Calendar Events
        event_warning = self._check_calendar_events()
        if event_warning:
            factors.append(event_warning)

        # Calculate combined signal
        avg_score = sum(scores) / len(scores) if scores else 0

        if avg_score > 0.15:
            signal = 'BULLISH'
            strength = min(0.9, 0.5 + avg_score)
        elif avg_score < -0.15:
            signal = 'BEARISH'
            strength = min(0.9, 0.5 + abs(avg_score))
        else:
            signal = 'NEUTRAL'
            strength = 0.5

        description = self._generate_description(signal, factors, strength)

        return {
            'signal': signal,
            'strength': round(strength, 2),
            'description': description,
            'factors': factors,
            'score': round(avg_score, 3)
        }

    def _analyze_trend(self, rates: list[float]) -> tuple[str, float]:
        """Analyze price trend using moving averages"""
        if len(rates) < 14:
            return "insuficiente data", 0

        # Short-term MA (7 days)
        ma_short = sum(rates[-7:]) / 7

        # Long-term MA (14 days)
        ma_long = sum(rates[-14:]) / 14

        # Current vs MAs
        current = rates[-1]

        if current > ma_short > ma_long:
            return "alcista fuerte", 0.4
        elif current > ma_short:
            return "alcista", 0.2
        elif current < ma_short < ma_long:
            return "bajista fuerte", -0.4
        elif current < ma_short:
            return "bajista", -0.2
        else:
            return "lateral", 0

    def _analyze_momentum(self, rates: list[float]) -> tuple[str, float]:
        """Analyze price momentum (rate of change)"""
        if len(rates) < 7:
            return "insuficiente data", 0

        # 7-day rate of change
        roc_7d = (rates[-1] - rates[-7]) / rates[-7] * 100

        # 3-day rate of change
        roc_3d = (rates[-1] - rates[-3]) / rates[-3] * 100 if len(rates) >= 3 else 0

        # Combine
        momentum = roc_7d * 0.6 + roc_3d * 0.4

        if momentum > 1.5:
            return "fuerte positivo", 0.35
        elif momentum > 0.5:
            return "positivo", 0.15
        elif momentum < -1.5:
            return "fuerte negativo", -0.35
        elif momentum < -0.5:
            return "negativo", -0.15
        else:
            return "neutral", 0

    def _analyze_volatility(self, rates: list[float]) -> tuple[str, float]:
        """Analyze price volatility"""
        if len(rates) < 7:
            return "insuficiente data", 0

        import numpy as np
        returns = np.diff(rates) / rates[:-1]
        volatility = np.std(returns) * 100

        if volatility > 1.5:
            return "muy alta - precaucion", 0
        elif volatility > 1.0:
            return "alta", 0
        elif volatility > 0.5:
            return "moderada", 0.1
        else:
            return "baja - estable", 0.2

    def _interpret_sentiment(self, score: float) -> str:
        """Interpret sentiment score"""
        if score > 0.3:
            return "muy positivo"
        elif score > 0.1:
            return "positivo"
        elif score < -0.3:
            return "muy negativo"
        elif score < -0.1:
            return "negativo"
        else:
            return "neutral"

    def _check_calendar_events(self) -> Optional[str]:
        """Check for upcoming high-impact events"""
        from datetime import timedelta

        today = datetime.now().date()
        next_week = today + timedelta(days=7)

        for event_type, dates in self.HIGH_IMPACT_EVENTS.items():
            for date_str in dates:
                event_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                if today <= event_date <= next_week:
                    if event_type == 'fed_meeting':
                        return f"ALERTA: Reunion Fed el {date_str}"
                    elif event_type == 'ecb_meeting':
                        return f"ALERTA: Reunion BCE el {date_str}"

        return None

    def _generate_description(
        self,
        signal: str,
        factors: list[str],
        strength: float
    ) -> str:
        """Generate human-readable description"""

        if signal == 'BULLISH':
            if strength > 0.7:
                return "Multiples indicadores senalan fortaleza del EUR. Considere posiciones a favor del EUR."
            else:
                return "Tendencia ligeramente alcista para EUR/USD. Monitorear para confirmacion."

        elif signal == 'BEARISH':
            if strength > 0.7:
                return "Multiples indicadores senalan debilidad del EUR. Considere posiciones a favor del USD."
            else:
                return "Tendencia ligeramente bajista para EUR/USD. Monitorear para confirmacion."

        else:
            return "Mercado en consolidacion. Esperar ruptura de rango para tomar posiciones."
