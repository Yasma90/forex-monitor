"""Sentiment analysis for financial news using lightweight approach"""

import re
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """
    Lightweight sentiment analyzer for financial news.
    Uses keyword-based approach for fast, no-dependency analysis.
    Can be upgraded to HuggingFace transformers for better accuracy.
    """

    # Financial sentiment lexicon
    POSITIVE_WORDS = {
        # Economic growth
        "growth", "growing", "surge", "surging", "rise", "rising", "gain", "gains",
        "increase", "increasing", "boost", "boosting", "improve", "improving",
        "recovery", "recovering", "rebound", "rebounding", "expansion", "expanding",
        "strong", "stronger", "strength", "positive", "optimism", "optimistic",
        "bullish", "rally", "rallying", "upbeat", "upgrade", "upgraded",

        # Market positive
        "profit", "profitable", "earnings", "beat", "beats", "exceed", "exceeds",
        "outperform", "success", "successful", "confidence", "confident",
        "stable", "stability", "support", "supporting", "steady",

        # Policy positive (context-dependent)
        "stimulus", "easing", "accommodative", "dovish", "cut", "cutting"
    }

    NEGATIVE_WORDS = {
        # Economic decline
        "fall", "falling", "drop", "dropping", "decline", "declining", "decrease",
        "plunge", "plunging", "crash", "crashing", "collapse", "collapsing",
        "loss", "losses", "losing", "weak", "weaker", "weakness", "negative",
        "recession", "recessionary", "contraction", "contracting", "slowdown",
        "bearish", "slump", "slumping", "downgrade", "downgraded", "pessimism",

        # Market negative
        "miss", "misses", "disappoint", "disappointing", "underperform",
        "volatile", "volatility", "uncertainty", "uncertain", "risk", "risky",
        "concern", "concerns", "worried", "worry", "fear", "fears", "panic",

        # Crisis indicators
        "crisis", "turmoil", "default", "bankruptcy", "inflation", "inflationary",
        "hawkish", "tightening", "hike", "hiking", "warning", "warns"
    }

    # Intensifiers
    INTENSIFIERS = {
        "very", "extremely", "significantly", "sharply", "dramatically",
        "strongly", "heavily", "massively", "substantially", "considerably"
    }

    NEGATORS = {
        "not", "no", "never", "neither", "nobody", "nothing", "nowhere",
        "hardly", "barely", "scarcely", "doesn't", "don't", "didn't",
        "won't", "wouldn't", "couldn't", "shouldn't", "isn't", "aren't"
    }

    def __init__(self):
        self._model = None  # Placeholder for HuggingFace model

    async def analyze(self, text: str) -> dict:
        """
        Analyze sentiment of text.
        Returns dict with score (-1 to 1) and label.
        """
        if not text:
            return {"score": 0.0, "label": "neutral", "confidence": 0.0}

        # Try HuggingFace model if available
        if self._model:
            return await self._analyze_with_model(text)

        # Fallback to keyword-based analysis
        return self._analyze_keywords(text)

    def _analyze_keywords(self, text: str) -> dict:
        """Keyword-based sentiment analysis"""
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)

        positive_count = 0
        negative_count = 0
        intensifier_next = False

        for i, word in enumerate(words):
            # Check for negation (affects next sentiment word)
            if word in self.NEGATORS:
                intensifier_next = True
                continue

            multiplier = 1.5 if words[i-1] in self.INTENSIFIERS if i > 0 else 1.0

            if word in self.POSITIVE_WORDS:
                if intensifier_next:
                    negative_count += multiplier  # Negated positive = negative
                else:
                    positive_count += multiplier
                intensifier_next = False

            elif word in self.NEGATIVE_WORDS:
                if intensifier_next:
                    positive_count += multiplier * 0.5  # Negated negative = slightly positive
                else:
                    negative_count += multiplier
                intensifier_next = False

        total = positive_count + negative_count
        if total == 0:
            return {"score": 0.0, "label": "neutral", "confidence": 0.3}

        # Calculate score between -1 and 1
        score = (positive_count - negative_count) / total

        # Determine label
        if score > 0.1:
            label = "positive"
        elif score < -0.1:
            label = "negative"
        else:
            label = "neutral"

        # Confidence based on number of sentiment words found
        confidence = min(0.9, 0.3 + (total * 0.05))

        return {
            "score": round(score, 3),
            "label": label,
            "confidence": round(confidence, 2)
        }

    async def _analyze_with_model(self, text: str) -> dict:
        """
        Analyze using HuggingFace model (if loaded).
        Placeholder for Phase 3 upgrade.
        """
        # This would use transformers library:
        # from transformers import pipeline
        # classifier = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
        # result = classifier(text[:512])[0]

        return self._analyze_keywords(text)

    def load_model(self, model_name: str = "distilbert-base-uncased-finetuned-sst-2-english"):
        """
        Load HuggingFace model for better sentiment analysis.
        Call this to upgrade from keyword-based to ML-based.
        """
        try:
            from transformers import pipeline
            self._model = pipeline("sentiment-analysis", model=model_name)
            logger.info(f"Loaded sentiment model: {model_name}")
        except ImportError:
            logger.warning("transformers not installed, using keyword-based sentiment")
        except Exception as e:
            logger.error(f"Failed to load sentiment model: {e}")


# Global analyzer instance
_analyzer: Optional[SentimentAnalyzer] = None


def get_analyzer() -> SentimentAnalyzer:
    """Get or create sentiment analyzer singleton"""
    global _analyzer
    if _analyzer is None:
        _analyzer = SentimentAnalyzer()
    return _analyzer
