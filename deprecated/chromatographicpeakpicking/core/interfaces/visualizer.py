# src/chromatographicpeakpicking/core/interfaces/visualizer.py
"""This module defines the base interface for chromatogram and peak visualization.

    Classes:
        VisualizationResult: Base class for visualization results.
        Visualizer: Base interface for chromatogram and peak visualization.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, TypeVar
from src.chromatographicpeakpicking.core.prototypes.chromatogram import Chromatogram
from src.chromatographicpeakpicking.core.prototypes.peak import Peak
from src.chromatographicpeakpicking.core.types.config import BaseConfig
from src.chromatographicpeakpicking.core.types.validation import ValidationResult

C = TypeVar('C', bound=BaseConfig)

class VisualizationResult:
    """Base class for visualization results."""
    def __init__(self, figure_data: Dict[str, Any], metadata: Dict[str, float]):
        self.figure_data = figure_data
        self.metadata = metadata

class Visualizer(Generic[C], ABC):
    """Base interface for chromatogram and peak visualization.

    The Visualizer interface defines methods for creating visual representations
    of chromatograms and detected peaks. This can include interactive plots,
    static figures, or other visualization formats.

    Type Parameters:
        C: Configuration type (must be a BaseConfig)
    """
    @abstractmethod
    def configure(self, config: C) -> ValidationResult:
        """Configure the visualizer with given parameters."""
        raise NotImplementedError

    @abstractmethod
    def validate_config(self, config: C) -> ValidationResult:
        """Validate the configuration."""
        raise NotImplementedError

    @abstractmethod
    def visualize(
        self,
        chromatogram: Chromatogram,
        peaks: Optional[List[Peak]] = None
    ) -> VisualizationResult:
        """Create visualization of chromatogram and optionally detected peaks.

        Args:
            chromatogram: The chromatogram to visualize
            peaks: Optional list of detected peaks to overlay on the chromatogram

        Returns:
            VisualizationResult containing figure data and visualization metadata
        """
        raise NotImplementedError

    @abstractmethod
    def save(self, result: VisualizationResult, path: str) -> bool:
        """Save the visualization to a file.

        Args:
            result: The visualization result to save
            path: Target file path

        Returns:
            True if save was successful, False otherwise
        """
        raise NotImplementedError
