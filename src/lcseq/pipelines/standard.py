# src/lcseq/pipelines/standard.py
from src.lcseq.pipeline.components.standard_chromatogram_analyzer import StandardChromatogramAnalyzer
from src.lcseq.pipeline.components.standard_chromatogram_visualizer import StandardChromatogramVisualizer
from src.lcseq.pipeline.components.standard_input import StandardInput
from src.lcseq.pipeline.components.standard_output import StandardOutput
from src.lcseq.pipeline.components.standard_peak_analyzer import StandardPeakAnalyzer
from src.lcseq.pipeline.components.standard_peak_detector import StandardPeakDetector
from src.lcseq.pipeline.components.basic_peak_selector import BasicPeakSelector
from src.lcseq.pipeline.pipeline import Pipeline

class StandardPipe(Pipeline):
    def __init__(self, input_file_path: str, plot_chromatograms=False):
        super().__init__([
            StandardInput(),
            StandardChromatogramAnalyzer(),
            StandardPeakDetector(),
            StandardPeakAnalyzer(),
            BasicPeakSelector(),
            StandardChromatogramVisualizer(plot_chromatograms=plot_chromatograms),
            StandardOutput(input_file_path)
        ])
