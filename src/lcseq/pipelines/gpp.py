# src/lcseq/pipelines/gpp.py
"""
This module defines the GPPPipeline class, which sets up a GPP pipeline for
processing chromatogram data. It includes various GPP components for analyzing,
visualizing, and outputting chromatogram data.

Classes:
    GPPPipe: A pipeline class that sets up a sequence of GPP components for
        chromatogram data processing.
"""

# Local application imports
from src.lcseq.pipeline.components.analyzers import (
    GPPPeakAnalyzer,
    StandardChromatogramAnalyzer,
    StandardPeakAnalyzer,
)
from src.lcseq.pipeline.components.correctors import SWMChromatogramCorrector
from src.lcseq.pipeline.components.detectors import StandardPeakDetector
from src.lcseq.pipeline.components.io import StandardInput, StandardOutput
from src.lcseq.pipeline.components.selectors import GPPPeakSelector
from src.lcseq.pipeline.components.visualizers import StandardChromatogramVisualizer
from src.lcseq.pipeline.components.visualizers.standard_chromatogram_visualizer import (
    StandardChromatogramVisualizerConfig,
)
from src.lcseq.pipeline.pipeline import Pipeline


class GPPPipe(Pipeline):
    """
    GPPPipe class for setting up a pipeline with a sequence of GPP components.

    This class inherits from the Pipeline class and initializes it with a specific
    sequence of GPP components to process chromatogram data.

    Attributes:
        input_file_path (str): The file path for the output component to write the
            results.
        plot_chromatograms (bool): Flag to determine whether to plot chromatograms.
    """

    def __init__(self, input_file_path: str, plot_chromatograms: bool = False) -> None:
        """
        Initializes the GPP with the provided input file path and optional plotting flag.

        Args:
            input_file_path (str): The file path for the output component to write the
                results.
            plot_chromatograms (bool): Optional; Flag to determine whether to plot
                chromatograms. Default is False.
        """
        config = StandardChromatogramVisualizerConfig(plot_corrected_gaussians=True)
        visualizer = StandardChromatogramVisualizer(
            config=config, plot_chromatograms=plot_chromatograms
        )
        super().__init__(
            [
                StandardInput(),
                StandardChromatogramAnalyzer(),
                SWMChromatogramCorrector(),
                StandardPeakDetector(),
                StandardPeakAnalyzer(),
                GPPPeakAnalyzer(),
                GPPPeakSelector(),
                visualizer,
                StandardOutput(input_file_path),
            ]
        )
