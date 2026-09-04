"""
Backtesting service for evaluating prediction accuracy.
Compares past predictions with actual values.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional
import numpy as np

logger = logging.getLogger(__name__)


class BacktestResult:
    """Results from a backtest run"""

    def __init__(
        self,
        predictions: list[dict],
        actuals: list[dict],
        metrics: dict
    ):
        self.predictions = predictions
        self.actuals = actuals
        self.metrics = metrics
        self.generated_at = datetime.utcnow()

    def to_dict(self) -> dict:
        return {
            "predictions_count": len(self.predictions),
            "actuals_count": len(self.actuals),
            "metrics": self.metrics,
            "generated_at": self.generated_at.isoformat()
        }


class PredictionBacktester:
    """
    Evaluates prediction accuracy by comparing past predictions
    with actual values that occurred.
    """

    async def run_backtest(
        self,
        historical_data: list[dict],
        lookback_days: int = 30,
        prediction_horizon: int = 7
    ) -> BacktestResult:
        """
        Run backtest on historical data.

        Args:
            historical_data: List of {date, rate} dicts
            lookback_days: How many days of history to use for each prediction
            prediction_horizon: How many days ahead to predict

        Returns:
            BacktestResult with metrics
        """
        if len(historical_data) < lookback_days + prediction_horizon + 10:
            raise ValueError("Insufficient data for backtesting")

        from .engine import PredictionEngine
        engine = PredictionEngine()

        predictions = []
        actuals = []
        errors = []

        # Slide through historical data
        for i in range(lookback_days, len(historical_data) - prediction_horizon):
            # Get training window
            train_data = historical_data[i - lookback_days:i]

            # Get actual future values
            actual_future = historical_data[i:i + prediction_horizon]

            try:
                # Generate prediction
                result = await engine.predict(
                    historical_data=train_data,
                    days_ahead=prediction_horizon,
                    sentiment_score=0  # No sentiment for backtest
                )

                # Compare prediction at horizon with actual
                if result['predictions'] and actual_future:
                    pred_value = result['predictions'][-1]['predicted_rate']
                    actual_value = actual_future[-1]['rate']

                    predictions.append({
                        'date': actual_future[-1]['date'],
                        'predicted': pred_value,
                        'lower': result['predictions'][-1]['lower_bound'],
                        'upper': result['predictions'][-1]['upper_bound']
                    })
                    actuals.append({
                        'date': actual_future[-1]['date'],
                        'actual': actual_value
                    })

                    error = pred_value - actual_value
                    errors.append(error)

            except Exception as e:
                logger.warning(f"Backtest prediction failed at index {i}: {e}")
                continue

        # Calculate metrics
        metrics = self._calculate_metrics(predictions, actuals, errors)

        return BacktestResult(predictions, actuals, metrics)

    def _calculate_metrics(
        self,
        predictions: list[dict],
        actuals: list[dict],
        errors: list[float]
    ) -> dict:
        """Calculate accuracy metrics"""
        if not errors:
            return {"error": "No valid predictions to evaluate"}

        errors_arr = np.array(errors)
        actual_values = np.array([a['actual'] for a in actuals])

        # Mean Absolute Error
        mae = np.mean(np.abs(errors_arr))

        # Root Mean Square Error
        rmse = np.sqrt(np.mean(errors_arr ** 2))

        # Mean Absolute Percentage Error
        mape = np.mean(np.abs(errors_arr / actual_values)) * 100

        # Direction accuracy (did we predict up/down correctly?)
        direction_correct = 0
        for i in range(1, len(predictions)):
            pred_direction = predictions[i]['predicted'] > predictions[i-1]['predicted']
            actual_direction = actuals[i]['actual'] > actuals[i-1]['actual']
            if pred_direction == actual_direction:
                direction_correct += 1
        direction_accuracy = (direction_correct / (len(predictions) - 1)) * 100 if len(predictions) > 1 else 0

        # Confidence interval accuracy
        in_bounds = sum(
            1 for p, a in zip(predictions, actuals)
            if p['lower'] <= a['actual'] <= p['upper']
        )
        ci_accuracy = (in_bounds / len(predictions)) * 100 if predictions else 0

        # Bias (systematic over/under prediction)
        bias = np.mean(errors_arr)

        return {
            "mae": round(mae, 6),
            "rmse": round(rmse, 6),
            "mape": round(mape, 2),
            "direction_accuracy": round(direction_accuracy, 1),
            "confidence_interval_accuracy": round(ci_accuracy, 1),
            "bias": round(bias, 6),
            "sample_size": len(predictions),
            "interpretation": self._interpret_metrics(mae, mape, direction_accuracy)
        }

    def _interpret_metrics(self, mae: float, mape: float, direction_acc: float) -> str:
        """Generate human-readable interpretation"""
        interpretations = []

        if mape < 1:
            interpretations.append("Predicciones muy precisas")
        elif mape < 2:
            interpretations.append("Predicciones razonablemente precisas")
        elif mape < 5:
            interpretations.append("Predicciones con precision moderada")
        else:
            interpretations.append("Predicciones con alta variabilidad")

        if direction_acc > 60:
            interpretations.append("buena prediccion de tendencia")
        elif direction_acc > 50:
            interpretations.append("prediccion de tendencia similar al azar")
        else:
            interpretations.append("tendencia dificil de predecir")

        return ", ".join(interpretations)


async def quick_accuracy_check(
    historical_data: list[dict],
    days_to_check: int = 7
) -> dict:
    """
    Quick accuracy check using recent data.
    Returns simple accuracy metrics.
    """
    if len(historical_data) < days_to_check + 14:
        return {"error": "Insufficient data"}

    from .engine import PredictionEngine
    engine = PredictionEngine()

    # Use data up to 'days_to_check' days ago to predict
    train_data = historical_data[:-days_to_check]
    actual_data = historical_data[-days_to_check:]

    try:
        result = await engine.predict(
            historical_data=train_data,
            days_ahead=days_to_check,
            sentiment_score=0
        )

        # Compare predictions with actuals
        errors = []
        comparisons = []
        for pred, actual in zip(result['predictions'], actual_data):
            error = pred['predicted_rate'] - actual['rate']
            errors.append(abs(error))
            comparisons.append({
                'date': actual['date'],
                'predicted': pred['predicted_rate'],
                'actual': actual['rate'],
                'error': round(error, 6),
                'in_bounds': pred['lower_bound'] <= actual['rate'] <= pred['upper_bound']
            })

        avg_error = sum(errors) / len(errors) if errors else 0
        in_bounds_pct = sum(1 for c in comparisons if c['in_bounds']) / len(comparisons) * 100

        return {
            "average_error": round(avg_error, 6),
            "max_error": round(max(errors), 6) if errors else 0,
            "in_bounds_percentage": round(in_bounds_pct, 1),
            "comparisons": comparisons[:5],  # First 5 for brevity
            "model_type": result['model_type'],
            "assessment": "bueno" if avg_error < 0.005 else "aceptable" if avg_error < 0.01 else "mejorable"
        }

    except Exception as e:
        return {"error": str(e)}
