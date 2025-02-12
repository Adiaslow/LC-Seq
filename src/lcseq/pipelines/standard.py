# src/lcseq/pipelines/standard.py
"""
This module defines the StandardPipe class, which sets up a standard pipeline for
processing chromatogram data. It includes various standard components for analyzing,
visualizing, and outputting chromatogram data.

Classes:
    StandardPipe: A pipeline class that sets up a sequence of standard components for
        chromatogram data processing.
"""

from ..pipeline.components.analyzers import (StandardChromatogramAnalyzer,
                                             StandardPeakAnalyzer)
from ..pipeline.components.detectors import StandardPeakDetector
from ..pipeline.components.io import StandardInput, StandardOutput
from ..pipeline.components.selectors import BasicPeakSelector
from ..pipeline.components.visualizers import StandardChromatogramVisualizer
# Local application imports
from ..pipeline.pipeline import Pipeline


class StandardPipe(Pipeline):
    """
    StandardPipe class for setting up a standard pipeline with a sequence of standard components.

    This class inherits from the Pipeline class and initializes it with a specific
    sequence of standard components to process chromatogram data.

    Attributes:
        input_file_path (str): The file path for the output component to write the
            results.
        plot_chromatograms (bool): Flag to determine whether to plot chromatograms.
    """

    def __init__(self, input_file_path: str, plot_chromatograms=False):
        """
        Initializes the StandardPipe with the provided input file path and optional plotting flag.

        Args:
            input_file_path (str): The file path for the output component to write the
                results.
            plot_chromatograms (bool): Optional; Flag to determine whether to plot
                chromatograms. Default is False.
        """
        super().__init__(
            [
                StandardInput(),
                StandardChromatogramAnalyzer(),
                StandardPeakDetector(),
                StandardPeakAnalyzer(),
                BasicPeakSelector(),
                StandardChromatogramVisualizer(plot_chromatograms=plot_chromatograms),
                StandardOutput(input_file_path),
            ]
        )
