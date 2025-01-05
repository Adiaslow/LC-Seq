# src/chromatographicpeakpicking/implementations/caches/hierarchy_cache.py
"""
Module: hierarchy_cache

This module defines the HierarchyCache class, which is a singleton cache for storing and
managing Hierarchy instances. It extends the CacheSingleton.
"""
from typing import Optional
from ...core.singletons.cache_singleton import CacheSingleton
from ...core.prototypes.hierarchy import Hierarchy

class HierarchyCache(CacheSingleton):
    """
    A cache singleton for storing and managing Hierarchy instances.

    This class encapsulates the logic for caching Hierarchy instances,
    providing methods to get, set, remove, and clear cached objects.
    """
    _instance: Optional['HierarchyCache'] = None  # Singleton instance

    def __new__(cls) -> 'HierarchyCache':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    instance = super(HierarchyCache, cls).__new__(cls)
                    instance.cache = {}  # Initialize cache on instance
                    cls._instance = instance
        if cls._instance is not None:
            return cls._instance
        raise RuntimeError("Failed to create singleton instance")

    def get(self, key: str) -> Hierarchy:
        """
        Retrieve a Hierarchy from the cache.

        Args:
            key (str): The key of the Hierarchy to retrieve.

        Returns:
            Hierarchy: The cached Hierarchy. Raises KeyError if key does not exist.

        Raises:
            KeyError: If the key does not exist in the cache.
        """
        return super().get(key)

    def set(self, key: str, value: Hierarchy) -> None:
        """
        Store a Hierarchy in the cache.

        Args:
            key (str): The key to store the Hierarchy under.
            value (Hierarchy): The Hierarchy to store in the cache.
        """
        super().set(key, value)

    def remove(self, key: str) -> None:
        """
        Remove a Hierarchy from the cache.

        Args:
            key (str): The key of the Hierarchy to remove.
        """
        super().remove(key)

    def clear(self) -> None:
        """Clear all Hierarchies from the cache."""
        super().clear()
