# src/chromatographicpeakpicking/core/interfaces/prototype.py
"""This module defines the base interface for all prototypes.

    Classes:
        Prototype: Base interface for all prototypes.
"""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Any

T = TypeVar('T')  # Type for the object being cloned

class Prototype(Generic[T], ABC):
    """Base interface for all prototypes."""

    @abstractmethod
    def clone(self, **kwargs: Any) -> T:
        """Create a copy of the object with optional overrides."""
        raise NotImplementedError

    @abstractmethod
    def with_properties(self, **kwargs: Any) -> T:
        """Create a new instance with updated properties."""
        raise NotImplementedError

    @abstractmethod
    def with_metadata(self, **kwargs: Any) -> T:
        """Create a new instance with updated metadata."""
        raise NotImplementedError
