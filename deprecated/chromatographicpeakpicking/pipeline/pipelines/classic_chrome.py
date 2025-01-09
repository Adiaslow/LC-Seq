# src/chromatographicpeakpicking/pipelines/classic_chrome.py
"""This module defines the classic chrome peak picking algorithm.

"""
from dataclasses import dataclass
from src.chromatographicpeakpicking.core.pipeline import Pipeline, PipelineConfig
from src.chromatographicpeakpicking.analysis.implementations.chromatogram_analyzer import (
    ChromatogramAnalyzer
)
from src.chromatographicpeakpicking.analysis.implementations.peak_analyzer import PeakAnalyzer
from src.chromatographicpeakpicking.core.pipeline.stages import (
    ChromatogramAnalysisStage,
    CorrectionStage,
    DetectionStage,
    InputStage,
    OutputStage,
    PeakAnalysisStage,
    PreprocessStage,
    ProcessStage,
    SelectionStage
)

@dataclass
class ClassicChromeConfig(PipelineConfig):
    """Configuration for the classic Chrome peak picking pipeline.

    """
    input_stage: InputStage = InputStage(

    )
    preprocess_stage: PreprocessStage
    chromatogram_analysis_stage: ChromatogramAnalysisStage
    correction_stage: CorrectionStage
    detection_stage: DetectionStage
    peak_analysis_stage: PeakAnalysisStage
    process_stage: ProcessStage
    selection_state: SelectionStage
    output_stage: OutputStage


class ClassicChrome(Pipeline):
    """A pipeline that implements the classic Chrome peak picking algorithm.

    """

    def __init__(self, config: PipelineConfig):
        """Initializes a new instance of the ClassicChromePipeline class.

        Args:
            config (PipelineConfig): The configuration for the pipeline.

        """
        super().__init__(config)

        self.add_stage(InputStage())
        self.add_stage(PreprocessStage())
        self.add_stage(DetectionStage())
        self.add_stage(SelectionStage())
        self.add_stage(CorrectionStage())
        self.add_stage(PeakAnalysisStage())
        self.add_stage(ChromatogramAnalysisStage())
        self.add_stage(OutputStage())

    def run(self, input_data: Any) -> Any:
        """Runs the pipeline on the given input data.

        Args:
            input_data (Any): The input data to process.

        Returns:
            Any: The result of processing the input data.

        """
        return super().run(input_data)
