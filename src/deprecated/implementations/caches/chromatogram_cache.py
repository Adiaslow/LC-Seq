# src/chromatographicpeakpicking/implementations/caches/chromatogram_cache.py
"""
Module: chromatogram_cache

This module defines the ChromatogramCache class, which is a singleton cache for storing and
managing Chromatogram instances. It extends the CacheSingleton.
"""
from typing import Optional
from ...core.singletons.cache_singleton import CacheSingleton
from ...core.prototypes.chromatogram import Chromatogram

class ChromatogramCache(CacheSingleton):
    """
    A cache singleton for storing and managing Chromatogram instances.

    This class encapsulates the logic for caching Chromatogram instances,
    providing methods to get, set, remove, and clear cached objects.
    """
    _instance: Optional['ChromatogramCache'] = None  # Singleton instance

    def __new__(cls) -> 'ChromatogramCache':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    instance = super(ChromatogramCache, cls).__new__(cls)
                    instance.cache = {}  # Initialize cache on instance
                    cls._instance = instance
        if cls._instance is not None:
            return cls._instance
        raise RuntimeError("Failed to create singleton instance")

    def get(self, key: str) -> Chromatogram:
        """
        Retrieve a Chromatogram from the cache.

        Args:
            key (str): The key of the Chromatogram to retrieve.

        Returns:
            Chromatogram: The cached Chromatogram. Raises KeyError if key does not exist.

        Raises:
            KeyError: If the key does not exist in the cache.
        """
        return super().get(key)

    def set(self, key: str, value: Chromatogram) -> None:
        """
        Store a Chromatogram in the cache.

        Args:
            key (str): The key to store the Chromatogram under.
            value (Chromatogram): The Chromatogram to store in the cache.
        """
        super().set(key, value)

    def remove(self, key: str) -> None:
        """
        Remove a Chromatogram from the cache.

        Args:
            key (str): The key of the Chromatogram to remove.
        """
        super().remove(key)

    def clear(self) -> None:
        """Clear all Chromatograms from the cache."""
        super().clear()
