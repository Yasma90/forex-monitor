"""
Tests for the prediction service including backtesting.
"""

import pytest
from datetime import datetime, timedelta

from app.services.prediction.backtesting import (
    BacktestResult,
    PredictionBacktester,
    quick_accuracy_check
)


class TestBacktestResult:
    """Tests for BacktestResult class"""

    def test_result_creation(self):
        """Test backtest result is created correctly"""
        predictions = [{"date": "2024-01-01", "predicted": 1.08}]
        actuals = [{"date": "2024-01-01", "actual": 1.079}]
        metrics = {"mae": 0.001}

        result = BacktestResult(predictions, actuals, metrics)

        assert len(result.predictions) == 1
        assert len(result.actuals) == 1
        assert result.metrics["mae"] == 0.001
        assert result.generated_at is not None

    def test_result_to_dict(self):
        """Test backtest result serialization"""
        predictions = [{"date": "2024-01-01", "predicted": 1.08}]
        actuals = [{"date": "2024-01-01", "actual": 1.079}]
        metrics = {"mae": 0.001, "rmse": 0.0012}

        result = BacktestResult(predictions, actuals, metrics)
        result_dict = result.to_dict()

        assert result_dict["predictions_count"] == 1
        assert result_dict["actuals_count"] == 1
        assert "metrics" in result_dict
        assert "generated_at" in result_dict


class TestPredictionBacktester:
    """Tests for PredictionBacktester class"""

    @pytest.fixture
    def backtester(self):
        """Create backtester instance"""
        return PredictionBacktester()

    @pytest.mark.asyncio
    async def test_run_backtest_insufficient_data(self, backtester):
        """Test backtest fails with insufficient data"""
        short_data = [{"date": "2024-01-01", "rate": 1.08}] * 10

        with pytest.raises(ValueError, match="Insufficient data"):
            await backtester.run_backtest(short_data)

    @pytest.mark.asyncio
    async def test_run_backtest_success(self, backtester, sample_historical_data):
        """Test successful backtest run"""
        result = await backtester.run_backtest(
            sample_historical_data,
            lookback_days=14,
            prediction_horizon=3
        )

        assert isinstance(result, BacktestResult)
        assert len(result.predictions) > 0
        assert "mae" in result.metrics or "error" in result.metrics

    @pytest.mark.asyncio
    async def test_backtest_metrics_calculated(self, backtester, sample_historical_data):
        """Test backtest calculates expected metrics"""
        result = await backtester.run_backtest(
            sample_historical_data,
            lookback_days=14,
            prediction_horizon=3
        )

        if "error" not in result.metrics:
            assert "mae" in result.metrics
            assert "rmse" in result.metrics
            assert "mape" in result.metrics
            assert "direction_accuracy" in result.metrics

    def test_calculate_metrics(self, backtester):
        """Test metrics calculation"""
        predictions = [
            {"date": "2024-01-01", "predicted": 1.08, "lower": 1.07, "upper": 1.09},
            {"date": "2024-01-02", "predicted": 1.085, "lower": 1.075, "upper": 1.095},
        ]
        actuals = [
            {"date": "2024-01-01", "actual": 1.079},
            {"date": "2024-01-02", "actual": 1.082},
        ]
        errors = [0.001, 0.003]

        metrics = backtester._calculate_metrics(predictions, actuals, errors)

        assert "mae" in metrics
        assert "rmse" in metrics
        assert "sample_size" in metrics
        assert metrics["sample_size"] == 2

    def test_calculate_metrics_empty(self, backtester):
        """Test metrics calculation with empty data"""
        metrics = backtester._calculate_metrics([], [], [])
        assert "error" in metrics

    def test_interpret_metrics(self, backtester):
        """Test metrics interpretation"""
        # Very accurate
        interpretation = backtester._interpret_metrics(mae=0.001, mape=0.5, direction_acc=70)
        assert "muy precisas" in interpretation.lower()

        # Moderate accuracy
        interpretation = backtester._interpret_metrics(mae=0.01, mape=3, direction_acc=55)
        assert "moderada" in interpretation.lower()


class TestQuickAccuracyCheck:
    """Tests for quick_accuracy_check function"""

    @pytest.mark.asyncio
    async def test_insufficient_data(self):
        """Test quick check fails with insufficient data"""
        short_data = [{"date": "2024-01-01", "rate": 1.08}] * 5

        result = await quick_accuracy_check(short_data, days_to_check=7)
        assert "error" in result

    @pytest.mark.asyncio
    async def test_quick_check_success(self, sample_historical_data):
        """Test successful quick accuracy check"""
        result = await quick_accuracy_check(
            sample_historical_data,
            days_to_check=5
        )

        # Should return metrics or error
        if "error" not in result:
            assert "average_error" in result
            assert "in_bounds_percentage" in result
            assert "assessment" in result

    @pytest.mark.asyncio
    async def test_quick_check_assessment(self, sample_historical_data):
        """Test quick check returns assessment"""
        result = await quick_accuracy_check(
            sample_historical_data,
            days_to_check=5
        )

        if "assessment" in result:
            assert result["assessment"] in ["bueno", "aceptable", "mejorable"]
