# src/chromatographicpeakpicking/core/factories/chromatogram_factory.py
"""
Module: chromatogram_factory

This module defines the ChromatogramFactory class for creating Chromatogram instances.
"""

from typing import Dict, Any
import numpy as np
from ..prototypes.chromatogram import Chromatogram
from ...implementations.caches.chromatogram_cache import ChromatogramCache

class ChromatogramFactory:
    """
    Responsible for creating Chromatogram instances.

    This class encapsulates the logic for creating new Chromatogram instances,
    including the creation of chromatograms with specific data and properties.
    """

    def __init__(self):
        """Initialize the ChromatogramFactory with a singleton cache."""
        self.cache = ChromatogramCache()

    def register_prototype(self, name: str, chromatogram: Chromatogram) -> None:
        """Register a prototype chromatogram in the cache."""
        if self.cache is None:
            raise AttributeError("Cache has not been initialized")
        self.cache.set(name, chromatogram)

    def create_chromatogram(self, prototype_name: str, **kwargs: Any) -> Chromatogram:
        """Create a new Chromatogram instance based on a registered prototype."""
        if self.cache is None:
            raise AttributeError("Cache has not been initialized")
        prototype = self.cache.get(prototype_name)
        if prototype is None:
            raise ValueError(f"Prototype '{prototype_name}' is not registered.")
        return prototype.clone(**kwargs)

    def create_chromatogram_from_data(
        self,
        time: np.ndarray,
        intensity: np.ndarray,
        **kwargs: Any
    ) -> Chromatogram:
        """
        Create a new Chromatogram instance directly from time and intensity data.

        Args:
            time (np.ndarray): Time points of the chromatogram.
            intensity (np.ndarray): Intensity values of the chromatogram.
            kwargs (Any): Additional attributes for the chromatogram.

        Returns:
            Chromatogram: A new Chromatogram instance.
        """
        return Chromatogram(time=time, intensity=intensity, **kwargs)

    def list_prototypes(self) -> Dict[str, Chromatogram]:
        """List all registered prototype chromatograms."""
        return self.cache.cache

    def unregister_prototype(self, name: str) -> None:
        """Unregister a prototype chromatogram from the cache."""
        if self.cache.get(name) is None:
            raise ValueError(f"Prototype '{name}' is not registered.")
        self.cache.remove(name)
