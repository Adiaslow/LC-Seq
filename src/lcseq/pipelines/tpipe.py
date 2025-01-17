# src/lcseq/pipelines/test_pipeline.py
"""
This module defines the TPipe class, which is a specialized pipeline for testing
purposes.
It includes various test components for analyzing chromatograms, detecting peaks, and
selecting peaks, among other tasks.

Classes:
    TPipe: A pipeline class that sets up a sequence of test components.
"""

from src.lcseq.pipeline.components.test_components.test_chromatogram_analyzer import TestChromatogramAnalyzer
from src.lcseq.pipeline.components.test_components.test_input import TestInput
from src.lcseq.pipeline.components.test_components.test_output import TestOutput
from src.lcseq.pipeline.components.test_components.test_peak_analyzer import TestPeakAnalyzer
from src.lcseq.pipeline.components.test_components.test_peak_detector import TestPeakDetector
from src.lcseq.pipeline.components.test_components.test_peak_selector import TestPeakSelector
from src.lcseq.pipeline.pipeline import Pipeline

class TPipe(Pipeline):
    """
    TPipe class for setting up a test pipeline with a sequence of test components.

    This class inherits from the Pipeline class and initializes it with a specific
    sequence of test components to process input data.

    Attributes:
        input_file_path (str): The file path for the output component to write the
        results.
    """

    def __init__(self, input_file_path: str):
        """
        Initializes the TPipe with the provided input file path.

        Args:
            input_file_path (str): The file path for the output component to write the
            results.
        """
        super().__init__([
            TestInput(),
            TestChromatogramAnalyzer(),
            TestPeakDetector(),
            TestPeakAnalyzer(),
            TestPeakSelector(),
            TestOutput(input_file_path)
        ])
