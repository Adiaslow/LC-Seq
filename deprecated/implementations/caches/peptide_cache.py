# src/chromatographicpeakpicking/implementations/caches/peptide_cache.py
"""
Module: peptide_cache

This module defines the PeptideCache class, which is a singleton cache for storing and
managing Peptide instances. It extends the CacheSingleton.

Design Patterns:
    - Singleton Pattern: Ensures that a class has only one instance and provides a global point of access to it.
    - Prototype Pattern: Used to create new objects by copying an existing object (the prototype).

Rationale:
    - Efficiency: A single instance of the cache can be used throughout the application.
    - Consistency: Ensures that all parts of the application are using the same cache.
    - Simplicity: Simplifies access to the cache by providing a global point of access.
"""
from typing import Optional
from ...core.singletons.cache_singleton import CacheSingleton
from ...core.prototypes.peptide import Peptide

class PeptideCache(CacheSingleton):
    """
    A cache singleton for storing and managing Peptide instances.

    This class encapsulates the logic for caching Peptide instances,
    providing methods to get, set, remove, and clear cached objects.
    """
    _instance: Optional['PeptideCache'] = None  # Singleton instance

    def __new__(cls) -> 'PeptideCache':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    instance = super(PeptideCache, cls).__new__(cls)
                    instance.cache = {}  # Initialize cache on instance
                    cls._instance = instance
        if cls._instance is not None:
            return cls._instance
        raise RuntimeError("Failed to create singleton instance")

    def get(self, key: str) -> Peptide:
        """
        Retrieve a Peptide from the cache.

        Args:
            key (str): The key of the Peptide to retrieve.

        Returns:
            Peptide: The cached Peptide. Raises KeyError if key does not exist.

        Raises:
            KeyError: If the key does not exist in the cache.
        """
        return super().get(key)

    def set(self, key: str, value: Peptide) -> None:
        """
        Store a Peptide in the cache.

        Args:
            key (str): The key to store the Peptide under.
            value (Peptide): The Peptide to store in the cache.
        """
        super().set(key, value)

    def remove(self, key: str) -> None:
        """
        Remove a Peptide from the cache.

        Args:
            key (str): The key of the Peptide to remove.
        """
        super().remove(key)

    def clear(self) -> None:
        """Clear all Peptides from the cache."""
        super().clear()
