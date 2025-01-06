# src/chromatographicpeakpicking/core/pipeline/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Generic, List, TypeVar, Any
from src.chromatographicpeakpicking.core.types.config import BaseConfig
from src.chromatographicpeakpicking.core.types.validation import ValidationResult
from src.chromatographicpeakpicking.core.prototypes.chromatogram import Chromatogram
from src.chromatographicpeakpicking.core.prototypes.peak import Peak

C = TypeVar('C', bound=BaseConfig)

@dataclass
class PipelineStageResult:
    """Base class for pipeline stage results."""
    success: bool
    data: Any
    metrics: Dict[str, float]
    error_message: str = ""

class PipelineStage(Generic[C], ABC):
    """Base class for pipeline stages."""
    def __init__(self, name: str):
        self.name = name
        self._next_stage = None
        self._config = None

    @abstractmethod
    def configure(self, config: C) -> ValidationResult:
        """Configure the pipeline stage."""
        pass

    @abstractmethod
    def process(self, data: Any) -> PipelineStageResult:
        """Process input data and return result."""
        pass

    def set_next(self, stage: 'PipelineStage') -> 'PipelineStage':
        """Set the next stage in the pipeline."""
        self._next_stage = stage
        return stage
