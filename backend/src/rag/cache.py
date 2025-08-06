"""
Simple in-memory cache for RAG queries to improve performance.
"""

import time
from typing import Dict, Any, Optional
import hashlib
import logging

logger = logging.getLogger(__name__)


class RAGCache:
    """Simple in-memory cache for RAG query results."""

    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        """
        Initialize the cache.

        Args:
            max_size: Maximum number of cached items
            ttl_seconds: Time to live for cached items in seconds
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.access_times: Dict[str, float] = {}

    def _generate_key(self, query: str) -> str:
        """Generate a cache key from the query."""
        return hashlib.md5(query.encode()).hexdigest()

    def get(self, query: str) -> Optional[list]:
        """
        Get cached result for a query.

        Args:
            query: The search query

        Returns:
            Cached result or None if not found/expired
        """
        key = self._generate_key(query)

        if key not in self.cache:
            return None

        # Check if expired
        if time.time() - self.access_times[key] > self.ttl_seconds:
            del self.cache[key]
            del self.access_times[key]
            return None

        # Update access time
        self.access_times[key] = time.time()

        logger.info(f"Cache hit for query: {query[:50]}...")
        return self.cache[key]["result"]

    def set(self, query: str, result: list):
        """
        Cache a query result.

        Args:
            query: The search query
            result: The search result
        """
        key = self._generate_key(query)
        current_time = time.time()

        # Remove oldest items if cache is full
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.access_times.keys(),
                             key=lambda k: self.access_times[k])
            del self.cache[oldest_key]
            del self.access_times[oldest_key]

        # Add new item
        self.cache[key] = {
            "result": result,
            "timestamp": current_time
        }
        self.access_times[key] = current_time

        logger.info(f"Cached result for query: {query[:50]}...")

    def clear(self):
        """Clear all cached items."""
        self.cache.clear()
        self.access_times.clear()
        logger.info("RAG cache cleared")

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "ttl_seconds": self.ttl_seconds
        }
