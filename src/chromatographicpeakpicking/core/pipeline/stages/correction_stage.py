from src.chromatographicpeakpicking.core.interfaces.corrector import Corrector
from src.chromatographicpeakpicking.core.interfaces.pipeline_stage import (
    PipelineStage,
    PipelineStageResult
)
from src.chromatographicpeakpicking.core.pipeline.pipeline_config import PipelineConfig
from src.chromatographicpeakpicking.core.prototypes.chromatogram import Chromatogram

class CorrectionStage(PipelineStage[PipelineConfig]):
    """Handle chromatogram correction."""
    def __init__(self, name: str, corrector: Corrector):
        super().__init__(name)
        self.corrector = corrector

    def process(self, data: Chromatogram) -> PipelineStageResult:
        chromatogram = data
        try:
            corrected = self.corrector.correct(chromatogram)
            return PipelineStageResult(True, corrected, {})
        except Exception as e:
            return PipelineStageResult(False, None, {}, str(e))
