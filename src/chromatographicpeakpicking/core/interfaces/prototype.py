# src/chromatographicpeakpicking/core/interfaces/prototype.py
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Any, Dict

T = TypeVar('T')  # Type for the object being cloned

class Prototype(Generic[T], ABC):
    """Base interface for all prototypes."""

    @abstractmethod
    def clone(self, **kwargs: Any) -> T:
        """Create a copy of the object with optional overrides."""
        pass

    @abstractmethod
    def with_properties(self, **kwargs: Any) -> T:
        """Create a new instance with updated properties."""
        pass

    @abstractmethod
    def with_metadata(self, **kwargs: Any) -> T:
        """Create a new instance with updated metadata."""
        pass
