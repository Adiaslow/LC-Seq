# src/chromatographicpeakpicking/core/interfaces/selector.py
from abc import ABC, abstractmethod
from typing import Dict, Generic, List, TypeVar
from src.chromatographicpeakpicking.core.prototypes.peak import Peak
from src.chromatographicpeakpicking.core.types.config import BaseConfig
from src.chromatographicpeakpicking.core.types.validation import ValidationResult

C = TypeVar('C', bound=BaseConfig)

class SelectionResult:
    """Base class for selection results."""
    def __init__(self, selected_peaks: List[Peak], metrics: Dict[str, float]):
        self.selected_peaks = selected_peaks
        self.metrics = metrics

class Selector(Generic[C], ABC):
    """Base interface for peak selection algorithms.

    The Selector interface defines methods for filtering and selecting peaks
    based on various criteria (e.g., intensity threshold, signal-to-noise ratio,
    peak width, etc.).

    Type Parameters:
        C: Configuration type (must be a BaseConfig)
    """
    @abstractmethod
    def configure(self, config: C) -> ValidationResult:
        """Configure the selector with given parameters."""
        pass

    @abstractmethod
    def validate_config(self, config: C) -> ValidationResult:
        """Validate the configuration."""
        pass

    @abstractmethod
    def select(self, peaks: List[Peak]) -> SelectionResult:
        """Filter and select peaks based on configured criteria.

        Args:
            peaks: List of detected peaks to be filtered

        Returns:
            SelectionResult containing filtered peaks and selection metrics
        """
        pass
