# src/chromatographicpeakpicking/core/pipeline/__init__.py
"""This module aggregates and re-exports key components related to the chromatogram pipeline.
"""

from src.chromatographicpeakpicking.core.pipeline.pipeline import (
    PipelineConfig,
    Pipeline
)

__all__ = [
    "PipelineConfig",
    "Pipeline"
]
