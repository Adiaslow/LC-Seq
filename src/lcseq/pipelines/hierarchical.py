# src/lcseq/pipelines/hierarchical.py
"""
This module defines the HierarchicalPipe class, which sets up a pipeline specifically
designed for processing hierarchical peptide data. It includes components for analyzing
relationships between peptides and their truncations.

Classes:
    HierarchicalPipe: A pipeline class that sets up a sequence of hierarchical components
        for processing peptide data.
"""

from ..pipeline.components.analyzers import (HierarchicalPeakAnalyzer,
                                             StandardChromatogramAnalyzer,
                                             StandardPeakAnalyzer)
from ..pipeline.components.detectors import StandardPeakDetector
from ..pipeline.components.io import StandardInput, StandardOutput
from ..pipeline.components.selectors import HierarchicalPeakSelector
from ..pipeline.components.validators import HierarchicalSynthesisValidator
from ..pipeline.components.visualizers import (
    HierarchicalChromatogramVisualizer, HierarchyVisualizer)
# Local application imports
from ..pipeline.pipeline import Pipeline


class HierarchicalPipe(Pipeline):
    """
    HierarchicalPipe class for processing peptide hierarchies with retention time
    validation and truncation analysis.
    """

    def __init__(self, input_file_path: str, plot_results=False):
        """
        Initialize the hierarchical pipeline.

        Args:
            input_file_path (str): Path to input file containing peptide data
            plot_results (bool): Whether to generate visualization plots
        """
        super().__init__(
            [
                StandardInput(),
                StandardChromatogramAnalyzer(),
                StandardPeakDetector(),
                StandardPeakAnalyzer(),
                HierarchicalPeakSelector(),
                HierarchicalPeakAnalyzer(),
                HierarchicalSynthesisValidator(),
                HierarchyVisualizer(plot_results=plot_results),
                StandardOutput(input_file_path),
            ]
        )
