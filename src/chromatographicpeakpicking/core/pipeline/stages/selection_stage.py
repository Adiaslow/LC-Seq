from typing import List
from src.chromatographicpeakpicking.core.interfaces.selector import Selector
from src.chromatographicpeakpicking.core.interfaces.pipeline_stage import PipelineStage, PipelineStageResult
from src.chromatographicpeakpicking.core.pipeline.pipeline_config import PipelineConfig
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
