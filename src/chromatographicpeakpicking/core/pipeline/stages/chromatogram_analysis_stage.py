# src/chromatographicpeakpicking/core/pipeline/stages/chromatogram_analysis_stage.py
"""This module implements the ChromatogramAnalysisStage class, which handles chromatogram analysis.

    Classes:
        ChromatogramAnalysisStage: Handle chromatogram analysis.
"""
from src.chromatographicpeakpicking.core.interfaces.analyzer import Analyzer
from src.chromatographicpeakpicking.core.interfaces.pipeline_stage import (
    PipelineStage,
    PipelineStageResult
)
from src.chromatographicpeakpicking.core.pipeline.pipeline_config import PipelineConfig
from src.chromatographicpeakpicking.core.prototypes import chromatogram
from src.chromatographicpeakpicking.core.prototypes.chromatogram import Chromatogram

class ChromatogramAnalysisStage(PipelineStage[PipelineConfig]):
    """Handle chromatogram analysis."""
    def __init__(self, name: str, analyzer: Analyzer):
        super().__init__(name)
        self.analyzer = analyzer

    def process(self, data: Chromatogram) -> PipelineStageResult:
        chromatogram = data
        try:
            result = self.analyzer.analyze(chromatogram)
            return PipelineStageResult(True, result.result, result.metadata)
        except Exception as e:
            return PipelineStageResult(False, None, {}, str(e))
