# src/chromatographicpeakpicking/core/pipeline/pipeline.py
"""This

    Classes:
        PipelineConfig: Configuration for chromatogram pipeline.
        Pipeline: Pipeline for chromatogram peak picking.
"""
from dataclasses import dataclass
from typing import List
from src.chromatographicpeakpicking.core.pipeline.stages import preprocess_stage
from src.chromatographicpeakpicking.core.types.config import BaseConfig
from src.chromatographicpeakpicking.core.interfaces.pipeline_stage import PipelineStage

from src.chromatographicpeakpicking.core.pipeline.stages.input_stage import InputStage
from src.chromatographicpeakpicking.core.pipeline.stages.output_stage import OutputStage
@dataclass
class PipelineConfig(BaseConfig):
    """Configuration for chromatogram pipeline.

    Attributes:
        input_path: str
        output_path: str
        preprocessing_params: Dict[str, Any]
        analysis_params: Dict[str, Any]
        correction_params: Dict[str, Any]
        detection_params: Dict[str, Any]
        selection_params: Dict[str, Any]
    """

@dataclass
class Pipeline:
    """Pipeline
    """
    stages: List[PipelineStage]
