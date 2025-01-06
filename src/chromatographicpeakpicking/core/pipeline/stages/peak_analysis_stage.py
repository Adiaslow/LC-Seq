from typing import List
from src.chromatographicpeakpicking.core.interfaces.analyzer import Analyzer
from src.chromatographicpeakpicking.core.interfaces.pipeline_stage import (
    PipelineStage,
    PipelineStageResult
)
from src.chromatographicpeakpicking.core.pipeline.pipeline_config import PipelineConfig
from src.chromatographicpeakpicking.core.prototypes.peak import Peak


class PeakAnalysisStage(PipelineStage[PipelineConfig]):
    """Handle peak analysis."""
    def __init__(self, name: str, analyzer: Analyzer):
        super().__init__(name)
        self.analyzer = analyzer

    def process(self, data: List[Peak]) -> PipelineStageResult:
        peaks = data
        try:
            result = self.analyzer.analyze(peaks)
            return PipelineStageResult(True, result.result, result.metadata)
        except Exception as e:
            return PipelineStageResult(False, None, {}, str(e))
