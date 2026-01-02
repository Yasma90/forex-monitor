import httpx
from datetime import datetime
from typing import Optional
import logging

from ...config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class ExchangeRateFetcher:
    """Fetches exchange rates from multiple APIs with fallback support"""

    # Free API endpoints
    APIS = {
        "exchangerate-api": {
            "url": "https://v6.exchangerate-api.com/v6/{api_key}/pair/{base}/{target}",
            "requires_key": True,
            "rate_path": ["conversion_rate"]
        },
        "frankfurter": {
            # Frankfurter API - completely free, no key required, uses ECB data
            "url": "https://api.frankfurter.app/latest?from={base}&to={target}",
            "requires_key": False,
            "rate_path": ["rates", "{target}"]
        },
        "fawazahmed0": {
            # Another free API with no key required
            "url": "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/{base_lower}.json",
            "requires_key": False,
            "rate_path": ["{base_lower}", "{target_lower}"]
        }
    }

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=10.0)

    async def close(self):
        await self.client.aclose()

    async def fetch_rate(
        self,
        base: str = "USD",
        target: str = "EUR"
    ) -> Optional[dict]:
        """
        Fetch exchange rate with automatic fallback to backup APIs.
        Returns dict with rate, source, and timestamp.
        """
        base = base.upper()
        target = target.upper()

        # Try APIs in order until one succeeds
        for api_name, api_config in self.APIS.items():
            try:
                result = await self._fetch_from_api(api_name, api_config, base, target)
                if result:
                    logger.info(f"Successfully fetched {base}/{target} from {api_name}: {result['rate']}")
                    return result
            except Exception as e:
                logger.warning(f"Failed to fetch from {api_name}: {e}")
                continue

        logger.error(f"All APIs failed for {base}/{target}")
        return None

    async def _fetch_from_api(
        self,
        api_name: str,
        config: dict,
        base: str,
        target: str
    ) -> Optional[dict]:
        """Fetch from a specific API"""

        # Build URL
        url = config["url"].format(
            api_key=settings.exchangerate_api_key,
            base=base,
            target=target,
            base_lower=base.lower(),
            target_lower=target.lower()
        )

        # Skip APIs that require key if no key is configured
        if config["requires_key"] and not settings.exchangerate_api_key:
            return None

        response = await self.client.get(url)
        response.raise_for_status()
        data = response.json()

        # Extract rate using the path defined for this API
        rate = data
        for key in config["rate_path"]:
            key = key.format(
                base=base,
                target=target,
                base_lower=base.lower(),
                target_lower=target.lower()
            )
            rate = rate[key]

        return {
            "rate": float(rate),
            "source": api_name,
            "timestamp": datetime.utcnow(),
            "base_currency": base,
            "target_currency": target
        }

    async def fetch_historical(
        self,
        base: str = "USD",
        target: str = "EUR",
        days: int = 30
    ) -> Optional[list[dict]]:
        """
        Fetch historical rates using Frankfurter API (free, no key).
        Returns list of {date, rate} dicts.
        """
        from datetime import timedelta

        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)

        url = f"https://api.frankfurter.app/{start_date}..{end_date}?from={base}&to={target}"

        try:
            response = await self.client.get(url)
            response.raise_for_status()
            data = response.json()

            rates = []
            for date_str, rate_data in data.get("rates", {}).items():
                rates.append({
                    "date": date_str,
                    "rate": rate_data.get(target),
                    "base_currency": base,
                    "target_currency": target
                })

            return sorted(rates, key=lambda x: x["date"])

        except Exception as e:
            logger.error(f"Failed to fetch historical data: {e}")
            return None
