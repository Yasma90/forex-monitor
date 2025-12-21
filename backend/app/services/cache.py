"""
In-memory cache service for reducing API calls and improving performance.
Simple TTL-based cache without external dependencies.
"""

import time
from typing import Any, Optional, Dict
from functools import wraps
import logging
import hashlib
import json

logger = logging.getLogger(__name__)


class CacheEntry:
    """Single cache entry with TTL"""
    def __init__(self, value: Any, ttl_seconds: int):
        self.value = value
        self.expires_at = time.time() + ttl_seconds
        self.created_at = time.time()

    def is_expired(self) -> bool:
        return time.time() > self.expires_at

    @property
    def age_seconds(self) -> float:
        return time.time() - self.created_at


class InMemoryCache:
    """
    Simple in-memory cache with TTL support.
    Thread-safe for single-process applications.
    """

    def __init__(self, default_ttl: int = 300, max_entries: int = 1000):
        self._cache: Dict[str, CacheEntry] = {}
        self._default_ttl = default_ttl
        self._max_entries = max_entries
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if exists and not expired"""
        entry = self._cache.get(key)

        if entry is None:
            self._misses += 1
            return None

        if entry.is_expired():
            del self._cache[key]
            self._misses += 1
            return None

        self._hits += 1
        return entry.value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with optional TTL override"""
        # Evict oldest entries if at capacity
        if len(self._cache) >= self._max_entries:
            self._evict_oldest()

        ttl = ttl if ttl is not None else self._default_ttl
        self._cache[key] = CacheEntry(value, ttl)

    def delete(self, key: str) -> bool:
        """Delete entry from cache"""
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def clear(self) -> None:
        """Clear all cache entries"""
        self._cache.clear()

    def clear_expired(self) -> int:
        """Remove all expired entries, return count of removed"""
        expired_keys = [k for k, v in self._cache.items() if v.is_expired()]
        for key in expired_keys:
            del self._cache[key]
        return len(expired_keys)

    def _evict_oldest(self, count: int = 100) -> None:
        """Evict oldest entries to make room"""
        sorted_entries = sorted(
            self._cache.items(),
            key=lambda x: x[1].created_at
        )
        for key, _ in sorted_entries[:count]:
            del self._cache[key]

    @property
    def stats(self) -> dict:
        """Get cache statistics"""
        total = self._hits + self._misses
        hit_rate = (self._hits / total * 100) if total > 0 else 0
        return {
            "entries": len(self._cache),
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": f"{hit_rate:.1f}%",
            "max_entries": self._max_entries,
            "default_ttl": self._default_ttl
        }


# Global cache instances with different TTLs
exchange_rate_cache = InMemoryCache(default_ttl=300, max_entries=100)  # 5 min
news_cache = InMemoryCache(default_ttl=900, max_entries=500)  # 15 min
prediction_cache = InMemoryCache(default_ttl=1800, max_entries=50)  # 30 min


def cache_key(*args, **kwargs) -> str:
    """Generate cache key from arguments"""
    key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
    return hashlib.md5(key_data.encode()).hexdigest()


def cached(cache: InMemoryCache, ttl: Optional[int] = None):
    """
    Decorator for caching function results.

    Usage:
        @cached(exchange_rate_cache, ttl=300)
        async def get_rate(base, target):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = f"{func.__name__}:{cache_key(*args, **kwargs)}"
            cached_value = cache.get(key)

            if cached_value is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_value

            result = await func(*args, **kwargs)
            cache.set(key, result, ttl)
            logger.debug(f"Cache miss for {func.__name__}, stored result")
            return result

        return wrapper
    return decorator


def get_all_cache_stats() -> dict:
    """Get stats from all cache instances"""
    return {
        "exchange_rate": exchange_rate_cache.stats,
        "news": news_cache.stats,
        "prediction": prediction_cache.stats
    }
