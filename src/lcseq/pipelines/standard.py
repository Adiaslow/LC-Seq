# src/lcseq/pipelines/standard.py
"""
This module defines the StandardPipe class, which sets up a standard pipeline for
processing chromatogram data. It includes various standard components for analyzing,
visualizing, and outputting chromatogram data.

Classes:
    StandardPipe: A pipeline class that sets up a sequence of standard components for
        chromatogram data processing.
"""

from src.lcseq.pipeline.components.standard_components.standard_chromatogram_analyzer \
    import StandardChromatogramAnalyzer
from src.lcseq.pipeline.components.standard_components.standard_chromatogram_visualizer\
    import StandardChromatogramVisualizer
from src.lcseq.pipeline.components.standard_components.standard_input \
    import StandardInput
from src.lcseq.pipeline.components.standard_components.standard_output \
    import StandardOutput
from src.lcseq.pipeline.components.standard_components.standard_peak_analyzer \
    import StandardPeakAnalyzer
from src.lcseq.pipeline.components.standard_components.standard_peak_detector \
    import StandardPeakDetector
from src.lcseq.pipeline.components.basic_peak_selector import BasicPeakSelector
from src.lcseq.pipeline.pipeline import Pipeline

class StandardPipe(Pipeline):
    """
    StandardPipe class for setting up a standard pipeline with a sequence of standard components.

    This class inherits from the Pipeline class and initializes it with a specific sequence of standard
    components to process chromatogram data.

    Attributes:
        input_file_path (str): The file path for the output component to write the results.
        plot_chromatograms (bool): Flag to determine whether to plot chromatograms.
    """

    def __init__(self, input_file_path: str, plot_chromatograms=False):
        """
        Initializes the StandardPipe with the provided input file path and optional plotting flag.

        Args:
            input_file_path (str): The file path for the output component to write the results.
            plot_chromatograms (bool): Optional; Flag to determine whether to plot chromatograms.
                Default is False.
        """
        super().__init__([
            StandardInput(),
            StandardChromatogramAnalyzer(),
            StandardPeakDetector(),
            StandardPeakAnalyzer(),
            BasicPeakSelector(),
            StandardChromatogramVisualizer(plot_chromatograms=plot_chromatograms),
            StandardOutput(input_file_path)
        ])
