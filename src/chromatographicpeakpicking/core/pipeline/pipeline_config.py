from dataclasses import dataclass
from typing import Any, Dict
from src.chromatographicpeakpicking.core.types.config import BaseConfig

@dataclass
class PipelineConfig(BaseConfig):
    """Configuration for chromatogram pipeline."""
    input_path: str
    output_path: str
    preprocessing_params: Dict[str, Any]
    analysis_params: Dict[str, Any]
    correction_params: Dict[str, Any]
    detection_params: Dict[str, Any]
    selection_params: Dict[str, Any]
