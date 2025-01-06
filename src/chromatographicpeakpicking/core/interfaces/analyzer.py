# src/chromatographicpeakpicking/core/interfaces/analyzer.py
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Dict
from src.chromatographicpeakpicking.core.prototypes.chromatogram import Chromatogram
from src.chromatographicpeakpicking.core.types.config import BaseConfig
from src.chromatographicpeakpicking.core.types.validation import ValidationResult

# Type variables for configuration, input data, and result
C = TypeVar('C', bound=BaseConfig)
D = TypeVar('D')  # Input data type
R = TypeVar('R')  # Result type

class AnalysisResult(Generic[R]):
    """Base class for analysis results."""
    def __init__(self, result: R, metadata: Dict[str, float]):
        self.result = result
        self.metadata = metadata

class Analyzer(Generic[C, D, R], ABC):
    """Generic interface for analysis algorithms.

    Type Parameters:
        C: Configuration type (must be a BaseConfig)
        D: Input data type
        R: Result type
    """

    @abstractmethod
    def configure(self, config: C) -> ValidationResult:
        """Configure the analyzer with given parameters."""
        pass

    @abstractmethod
    def validate_config(self, config: C) -> ValidationResult:
        """Validate the configuration."""
        pass

    @abstractmethod
    def analyze(self, data: D) -> AnalysisResult[R]:
        """Analyze the input data and return results with metrics."""
        pass
