# src/chromatographicpeakpicking/core/pipeline/stages/selection_stage.py
"""This module implements the SelectionStage class, which handles peak selection.

    Classes:
        SelectionStage: Handle peak selection.
"""
from typing import List
from src.chromatographicpeakpicking.core.interfaces.selector import Selector
from src.chromatographicpeakpicking.core.interfaces.pipeline_stage import (
    PipelineStage,
    PipelineStageResult
)
from src.chromatographicpeakpicking.core.pipeline.pipeline import PipelineConfig
from src.chromatographicpeakpicking.core.prototypes.peak import Peak

class SelectionStage(PipelineStage[PipelineConfig]):
    """Handle peak selection."""
    def __init__(self, name: str, selector: Selector):
        super().__init__(name)
        self.selector = selector

    def process(self, data: List[Peak]) -> PipelineStageResult:
        peaks = data
        try:
            result = self.selector.select(peaks)
            return PipelineStageResult(True, result.selected_peaks, result.metrics)
        except Exception as e:
            return PipelineStageResult(False, None, {}, str(e))
