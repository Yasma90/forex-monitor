"""Keywords and relevance scoring for forex news filtering"""

# Keywords that indicate news relevant to USD/EUR exchange rate
FOREX_KEYWORDS = {
    # High impact - Central banks and monetary policy
    "high": [
        "federal reserve", "fed", "fomc", "jerome powell",
        "ecb", "european central bank", "christine lagarde",
        "interest rate", "rate hike", "rate cut",
        "monetary policy", "quantitative easing", "qe",
        "tightening", "dovish", "hawkish",
        "inflation", "cpi", "consumer price",
        "usd", "eur", "dollar", "euro",
        "forex", "exchange rate", "currency"
    ],

    # Medium impact - Economic indicators
    "medium": [
        "gdp", "gross domestic product",
        "unemployment", "jobs report", "nonfarm payroll", "employment",
        "trade balance", "trade deficit", "trade surplus",
        "treasury", "bond yield", "yield curve",
        "economic growth", "recession",
        "pmi", "manufacturing", "services",
        "retail sales", "consumer spending",
        "bundesbank", "deutsche bank"
    ],

    # Lower impact but still relevant - Geopolitical
    "low": [
        "tariff", "trade war", "sanctions",
        "election", "government", "policy",
        "debt ceiling", "stimulus", "fiscal",
        "oil price", "energy", "commodity",
        "stock market", "wall street", "dax",
        "brexit", "eurozone", "eu"
    ]
}

# All keywords flattened for quick matching
ALL_KEYWORDS = (
    FOREX_KEYWORDS["high"] +
    FOREX_KEYWORDS["medium"] +
    FOREX_KEYWORDS["low"]
)


def calculate_relevance(text: str) -> tuple[float, list[str]]:
    """
    Calculate relevance score based on keyword matches.
    Returns (score 0-1, list of matched keywords)
    """
    if not text:
        return 0.0, []

    text_lower = text.lower()
    matched = []
    score = 0.0

    # Check high impact keywords (weight: 0.5 each, max 1.0)
    for keyword in FOREX_KEYWORDS["high"]:
        if keyword in text_lower:
            matched.append(keyword)
            score += 0.15

    # Check medium impact keywords (weight: 0.1 each)
    for keyword in FOREX_KEYWORDS["medium"]:
        if keyword in text_lower:
            matched.append(keyword)
            score += 0.08

    # Check low impact keywords (weight: 0.05 each)
    for keyword in FOREX_KEYWORDS["low"]:
        if keyword in text_lower:
            matched.append(keyword)
            score += 0.03

    # Cap at 1.0
    score = min(score, 1.0)

    return score, list(set(matched))  # Remove duplicates


def get_search_query() -> str:
    """
    Generate a search query for news APIs.
    Uses most important keywords.
    """
    priority_terms = [
        "USD EUR",
        "Federal Reserve",
        "ECB",
        "dollar euro",
        "forex",
        "interest rate"
    ]
    return " OR ".join(priority_terms)
