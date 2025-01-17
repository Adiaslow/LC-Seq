# src/lcseq/pipelines/test_pipeline.py
from src.lcseq.pipeline.components.test_components.test_chromatogram_analyzer import TestChromatogramAnalyzer
from src.lcseq.pipeline.components.test_components.test_input import TestInput
from src.lcseq.pipeline.components.test_components.test_output import TestOutput
from src.lcseq.pipeline.components.test_components.test_peak_analyzer import TestPeakAnalyzer
from src.lcseq.pipeline.components.test_components.test_peak_detector import TestPeakDetector
from src.lcseq.pipeline.components.test_components.test_peak_selector import TestPeakSelector
from src.lcseq.pipeline.pipeline import Pipeline

class TPipe(Pipeline):
    def __init__(self):
        super().__init__([
            TestInput(),
            TestChromatogramAnalyzer(),
            TestPeakDetector(),
            TestPeakAnalyzer(),
            TestPeakSelector(),
            TestOutput()
        ])
