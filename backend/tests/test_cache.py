"""
Tests for the cache service.
"""

import pytest
import time
from app.services.cache import (
    InMemoryCache,
    CacheEntry,
    cache_key,
    get_all_cache_stats
)


class TestCacheEntry:
    """Tests for CacheEntry class"""

    def test_entry_creation(self):
        """Test cache entry is created correctly"""
        entry = CacheEntry("test_value", ttl_seconds=60)
        assert entry.value == "test_value"
        assert not entry.is_expired()

    def test_entry_expiration(self):
        """Test cache entry expires after TTL"""
        entry = CacheEntry("test_value", ttl_seconds=0)
        time.sleep(0.01)
        assert entry.is_expired()

    def test_entry_age(self):
        """Test cache entry age calculation"""
        entry = CacheEntry("test_value", ttl_seconds=60)
        time.sleep(0.1)
        assert entry.age_seconds >= 0.1


class TestInMemoryCache:
    """Tests for InMemoryCache class"""

    def test_set_and_get(self, cache):
        """Test basic set and get operations"""
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_get_nonexistent(self, cache):
        """Test getting nonexistent key returns None"""
        assert cache.get("nonexistent") is None

    def test_get_expired(self, cache):
        """Test getting expired entry returns None"""
        cache.set("key1", "value1", ttl=0)
        time.sleep(0.01)
        assert cache.get("key1") is None

    def test_delete(self, cache):
        """Test deleting cache entry"""
        cache.set("key1", "value1")
        assert cache.delete("key1") is True
        assert cache.get("key1") is None

    def test_delete_nonexistent(self, cache):
        """Test deleting nonexistent key"""
        assert cache.delete("nonexistent") is False

    def test_clear(self, cache):
        """Test clearing all cache entries"""
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.clear()
        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_clear_expired(self, cache):
        """Test clearing only expired entries"""
        cache.set("key1", "value1", ttl=0)
        cache.set("key2", "value2", ttl=3600)
        time.sleep(0.01)
        removed = cache.clear_expired()
        assert removed == 1
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"

    def test_max_entries_eviction(self):
        """Test eviction when max entries reached"""
        cache = InMemoryCache(default_ttl=60, max_entries=5)
        for i in range(10):
            cache.set(f"key{i}", f"value{i}")
        # Should have evicted some entries
        assert len(cache._cache) <= 5

    def test_stats(self, cache):
        """Test cache statistics"""
        cache.set("key1", "value1")
        cache.get("key1")  # hit
        cache.get("key2")  # miss

        stats = cache.stats
        assert stats["entries"] == 1
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert "hit_rate" in stats

    def test_complex_values(self, cache):
        """Test caching complex objects"""
        data = {"nested": {"value": [1, 2, 3]}}
        cache.set("complex", data)
        assert cache.get("complex") == data


class TestCacheKey:
    """Tests for cache key generation"""

    def test_cache_key_same_args(self):
        """Test same args produce same key"""
        key1 = cache_key("arg1", "arg2", kwarg1="value1")
        key2 = cache_key("arg1", "arg2", kwarg1="value1")
        assert key1 == key2

    def test_cache_key_different_args(self):
        """Test different args produce different keys"""
        key1 = cache_key("arg1")
        key2 = cache_key("arg2")
        assert key1 != key2

    def test_cache_key_order_independent_kwargs(self):
        """Test kwargs order doesn't affect key"""
        key1 = cache_key(a="1", b="2")
        key2 = cache_key(b="2", a="1")
        assert key1 == key2


class TestGetAllCacheStats:
    """Tests for global cache stats function"""

    def test_returns_all_cache_stats(self):
        """Test get_all_cache_stats returns stats for all caches"""
        stats = get_all_cache_stats()
        assert "exchange_rate" in stats
        assert "news" in stats
        assert "prediction" in stats
        assert "entries" in stats["exchange_rate"]
