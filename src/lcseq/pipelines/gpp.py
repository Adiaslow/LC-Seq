# src/lcseq/pipelines/gpp.py
"""
This module defines the GPPPipeline class, which sets up a GPP pipeline for
processing chromatogram data. It includes various GPP components for analyzing,
visualizing, and outputting chromatogram data.

Classes:
    GPPPipe: A pipeline class that sets up a sequence of GPP components for
        chromatogram data processing.
"""

from ..pipeline.pipeline import Pipeline
from ..pipeline.components.io import StandardInput
from ..pipeline.components.analyzers import StandardChromatogramAnalyzer
from ..pipeline.components.correctors import SWMChromatogramCorrector
from ..pipeline.components.detectors import StandardPeakDetector
from ..pipeline.components.analyzers import GPPPeakAnalyzer
from ..pipeline.components.selectors import GPPPeakSelector
from ..pipeline.components.analyzers import StandardPeakAnalyzer
from ..pipeline.components.io import StandardOutput
from ..pipeline.components.visualizers import StandardChromatogramVisualizer
from ..pipeline.components.visualizers.standard_chromatogram_visualizer import StandardChromatogramVisualizerConfig

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

    def __init__(self, input_file_path: str, plot_chromatograms=False):
        """
        Initializes the GPP with the provided input file path and optional plotting flag.

        Args:
            input_file_path (str): The file path for the output component to write the
                results.
            plot_chromatograms (bool): Optional; Flag to determine whether to plot
                chromatograms. Default is False.
        """
        config = StandardChromatogramVisualizerConfig(plot_corrected_gaussians=True)
        visualizer = StandardChromatogramVisualizer(config=config, plot_chromatograms=plot_chromatograms)
        super().__init__([
            StandardInput(),
            StandardChromatogramAnalyzer(),
            SWMChromatogramCorrector(),
            StandardPeakDetector(),
            StandardPeakAnalyzer(),
            GPPPeakAnalyzer(),
            GPPPeakSelector(),
            visualizer,
            StandardOutput(input_file_path)
        ])
