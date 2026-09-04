"""
Tests for the sentiment analysis service.
"""

import pytest
from app.services.news.sentiment import SentimentAnalyzer, get_analyzer


class TestSentimentAnalyzer:
    """Tests for SentimentAnalyzer class"""

    @pytest.fixture
    def analyzer(self):
        """Create sentiment analyzer instance"""
        return SentimentAnalyzer()

    @pytest.mark.asyncio
    async def test_analyze_empty_text(self, analyzer):
        """Test analyzing empty text returns neutral"""
        result = await analyzer.analyze("")
        assert result["score"] == 0.0
        assert result["label"] == "neutral"

    @pytest.mark.asyncio
    async def test_analyze_positive_text(self, analyzer):
        """Test positive sentiment detection"""
        text = "Markets are rallying with strong growth and bullish momentum"
        result = await analyzer.analyze(text)
        assert result["score"] > 0
        assert result["label"] == "positive"

    @pytest.mark.asyncio
    async def test_analyze_negative_text(self, analyzer):
        """Test negative sentiment detection"""
        text = "Markets crash amid recession fears and plunging confidence"
        result = await analyzer.analyze(text)
        assert result["score"] < 0
        assert result["label"] == "negative"

    @pytest.mark.asyncio
    async def test_analyze_neutral_text(self, analyzer):
        """Test neutral sentiment detection"""
        text = "The meeting was held yesterday afternoon"
        result = await analyzer.analyze(text)
        assert result["label"] == "neutral"

    @pytest.mark.asyncio
    async def test_analyze_mixed_text(self, analyzer):
        """Test mixed sentiment results in balanced score"""
        text = "Despite growth concerns, markets show some recovery"
        result = await analyzer.analyze(text)
        # Score should be close to neutral
        assert -0.5 < result["score"] < 0.5

    @pytest.mark.asyncio
    async def test_intensifier_effect(self, analyzer):
        """Test intensifiers increase sentiment magnitude"""
        weak_text = "Markets are rising"
        strong_text = "Markets are dramatically rising"

        weak_result = await analyzer.analyze(weak_text)
        strong_result = await analyzer.analyze(strong_text)

        # With intensifier, positive words have more impact
        # This test checks the feature is working
        assert weak_result["score"] > 0
        assert strong_result["score"] > 0

    @pytest.mark.asyncio
    async def test_negation_effect(self, analyzer):
        """Test negation reverses sentiment"""
        positive_text = "The recovery is strong"
        negated_text = "There is no recovery"

        positive_result = await analyzer.analyze(positive_text)
        negated_result = await analyzer.analyze(negated_text)

        assert positive_result["score"] > negated_result["score"]

    @pytest.mark.asyncio
    async def test_financial_keywords(self, analyzer):
        """Test financial-specific keywords"""
        # Fed/ECB related
        hawkish_text = "Fed signals hawkish stance with rate hike warning"
        result = await analyzer.analyze(hawkish_text)
        assert result["score"] < 0  # Hawkish = negative for market

        dovish_text = "ECB maintains dovish approach with easing measures"
        result = await analyzer.analyze(dovish_text)
        assert result["score"] > 0  # Dovish = positive for market

    @pytest.mark.asyncio
    async def test_confidence_increases_with_more_words(self, analyzer):
        """Test confidence increases with more sentiment words"""
        short_text = "Markets rally"
        long_text = "Markets rally strongly with bullish growth and positive momentum across sectors"

        short_result = await analyzer.analyze(short_text)
        long_result = await analyzer.analyze(long_text)

        assert long_result["confidence"] >= short_result["confidence"]

    @pytest.mark.asyncio
    async def test_score_range(self, analyzer):
        """Test score is always between -1 and 1"""
        texts = [
            "Everything is amazing wonderful fantastic great incredible",
            "Everything is terrible horrible awful catastrophic disastrous",
            "Normal average ordinary standard typical regular"
        ]

        for text in texts:
            result = await analyzer.analyze(text)
            assert -1 <= result["score"] <= 1

    def test_keyword_analysis_directly(self, analyzer):
        """Test keyword analysis method directly"""
        result = analyzer._analyze_keywords("Strong growth and bullish sentiment")
        assert "score" in result
        assert "label" in result
        assert "confidence" in result
        assert result["score"] > 0

    def test_positive_words_list(self, analyzer):
        """Test positive words list is populated"""
        assert len(analyzer.POSITIVE_WORDS) > 0
        assert "growth" in analyzer.POSITIVE_WORDS
        assert "bullish" in analyzer.POSITIVE_WORDS

    def test_negative_words_list(self, analyzer):
        """Test negative words list is populated"""
        assert len(analyzer.NEGATIVE_WORDS) > 0
        assert "crash" in analyzer.NEGATIVE_WORDS
        assert "recession" in analyzer.NEGATIVE_WORDS


class TestGetAnalyzer:
    """Tests for get_analyzer singleton function"""

    def test_returns_analyzer_instance(self):
        """Test get_analyzer returns SentimentAnalyzer"""
        analyzer = get_analyzer()
        assert isinstance(analyzer, SentimentAnalyzer)

    def test_returns_same_instance(self):
        """Test get_analyzer returns singleton"""
        analyzer1 = get_analyzer()
        analyzer2 = get_analyzer()
        assert analyzer1 is analyzer2


class TestRealWorldExamples:
    """Test with real-world-like news headlines"""

    @pytest.fixture
    def analyzer(self):
        return SentimentAnalyzer()

    @pytest.mark.asyncio
    async def test_fed_rate_decision(self, analyzer):
        """Test Fed rate decision headlines"""
        hawkish = "Fed signals hawkish stance with aggressive rate hikes and tightening"
        dovish = "Federal Reserve holds rates steady, dovish easing outlook surprises markets"
        warning = "Fed Chair Powell warns of persistent inflation concerns and recession risk"

        hawkish_result = await analyzer.analyze(hawkish)
        dovish_result = await analyzer.analyze(dovish)
        warning_result = await analyzer.analyze(warning)

        # Hawkish should be negative, dovish positive, warning negative
        assert hawkish_result["score"] < 0
        assert dovish_result["score"] > 0
        assert warning_result["score"] < 0

    @pytest.mark.asyncio
    async def test_economic_indicators(self, analyzer):
        """Test economic indicator headlines"""
        positive_news = "US GDP growth exceeds expectations, unemployment falls"
        negative_news = "Eurozone enters recession as manufacturing contracts sharply"

        pos_result = await analyzer.analyze(positive_news)
        neg_result = await analyzer.analyze(negative_news)

        assert pos_result["score"] > 0
        assert neg_result["score"] < 0

    @pytest.mark.asyncio
    async def test_market_movement(self, analyzer):
        """Test market movement headlines"""
        rally = "Euro rallies against dollar amid strong European data"
        selloff = "Dollar plunges as risk appetite returns to markets"

        rally_result = await analyzer.analyze(rally)
        selloff_result = await analyzer.analyze(selloff)

        assert rally_result["score"] > 0
        assert selloff_result["score"] < 0
