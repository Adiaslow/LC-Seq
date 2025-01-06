from src.chromatographicpeakpicking.core.interfaces.detector import Detector
from src.chromatographicpeakpicking.core.prototypes.chromatogram import Chromatogram
from src.chromatographicpeakpicking.core.interfaces.pipeline_stage import (
    PipelineStage,
    PipelineStageResult
)
from src.chromatographicpeakpicking.core.pipeline.pipeline_config import PipelineConfig

class DetectionStage(PipelineStage[PipelineConfig]):
    """Handle peak detection."""
    def __init__(self, name: str, detector: Detector):
        super().__init__(name)
        self.detector = detector

    def process(self, data: Chromatogram) -> PipelineStageResult:
        chromatogram = data
        try:
            result = self.detector.detect(chromatogram)
            return PipelineStageResult(True, result.peaks, result.metrics)
        except Exception as e:
            return PipelineStageResult(False, None, {}, str(e))
