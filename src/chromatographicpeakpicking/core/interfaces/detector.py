from abc import ABC, abstractmethod
from typing import Dict, Generic, List, TypeVar
from src.chromatographicpeakpicking.core.interfaces.pipeline_stage import PipelineStage
from src.chromatographicpeakpicking.core.prototypes.chromatogram import Chromatogram
from src.chromatographicpeakpicking.core.prototypes.peak import Peak
from src.chromatographicpeakpicking.core.types.config import BaseConfig
from src.chromatographicpeakpicking.core.types.validation import ValidationResult

C = TypeVar('C', bound=BaseConfig)

class DetectionResult:
    """Base class for detection results."""
    def __init__(self, peaks: List[Peak], metrics: Dict[str, float]):
        self.peaks = peaks
        self.metrics = metrics

class Detector(Generic[C], ABC):
    """Base interface for peak detection algorithms."""

    @abstractmethod
    def configure(self, config: C) -> ValidationResult:
        """Configure the detector with given parameters."""
        pass

    @abstractmethod
    def validate_config(self, config: C) -> ValidationResult:
        """Validate the configuration."""
        pass

    @abstractmethod
    def detect(self, chromatogram: Chromatogram) -> DetectionResult:
        """Detect peaks in the chromatogram."""
        pass
