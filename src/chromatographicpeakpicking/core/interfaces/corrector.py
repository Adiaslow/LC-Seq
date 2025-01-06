from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from src.chromatographicpeakpicking.core.interfaces.pipeline_stage import PipelineStage
from src.chromatographicpeakpicking.core.prototypes.chromatogram import Chromatogram
from src.chromatographicpeakpicking.core.types.config import BaseConfig
from src.chromatographicpeakpicking.core.types.validation import ValidationResult

C = TypeVar('C', bound=BaseConfig)

class Corrector(Generic[C], ABC):
    """Base interface for chromatographic correction algorithms."""

    @abstractmethod
    def configure(self, config: C) -> ValidationResult:
        """Configure the corrector with given parameters."""
        pass

    @abstractmethod
    def validate_config(self, config: C) -> ValidationResult:
        """Validate the configuration."""
        pass

    @abstractmethod
    def correct(self, chromatogram: Chromatogram) -> Chromatogram:
        """Apply correction to the chromatogram."""
        pass
