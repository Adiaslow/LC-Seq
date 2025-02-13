# src/lcseq/pipelines/hierarchical.py
"""
This module defines the HierarchicalPipe class, which sets up a pipeline specifically
designed for processing hierarchical peptide data. It includes components for analyzing
relationships between peptides and their truncations.

Classes:
    HierarchicalPipe: A pipeline class that sets up a sequence of hierarchical components
        for processing peptide data.
"""

# Local application imports
from src.lcseq.pipeline.components.analyzers import (
    StandardChromatogramAnalyzer,
    StandardPeakAnalyzer,
)

from src.lcseq.pipeline.components.detectors import StandardPeakDetector
from src.lcseq.pipeline.components.io import StandardInput, StandardOutput
from src.lcseq.pipeline.components.selectors import HierarchicalPeakSelector
from src.lcseq.pipeline.components.validators import HierarchicalSynthesisValidator
from src.lcseq.pipeline.components.visualizers import (
    HierarchicalChromatogramVisualizer,
    HierarchyVisualizer,
)
from src.lcseq.pipeline.pipeline import Pipeline, PipelineConfig
from src.lcseq.pipeline.input_types import PeptideHierarchyInput
import os
import warnings


class HierarchicalPipe(Pipeline):
    """
    HierarchicalPipe class for processing peptide hierarchies with retention time
    validation and truncation analysis.
    """

    def __init__(self, input_file_path: str, plot_chromatograms: bool = False) -> None:
        """
        Initialize the hierarchical pipeline.

        Args:
            input_file_path (str): Path to input file containing peptide data
            plot_chromatograms (bool): Whether to generate visualization plots

        Raises:
            FileNotFoundError: If input file does not exist.
        """
        if not os.path.exists(input_file_path):
            raise FileNotFoundError(f"Input file not found: {input_file_path}")

        self.input_file_path = input_file_path
        self.plot_chromatograms = plot_chromatograms

        # Initialize visualizers with correct plot flags
        self.hierarchy_visualizer = HierarchyVisualizer(plot_results=plot_chromatograms)
        self.chromatogram_visualizer = HierarchicalChromatogramVisualizer(
            plot_chromatograms=plot_chromatograms
        )

        config = PipelineConfig(
            hierarchical=True,
            plot_chromatograms=plot_chromatograms,
            input_file_path=input_file_path,
        )

        # Base components that are always included
        components = [
            StandardInput(),
            StandardChromatogramAnalyzer(),
            StandardPeakDetector(),
            StandardPeakAnalyzer(),
            HierarchicalPeakSelector(),
            HierarchicalSynthesisValidator(),
        ]

        # Add visualization components only if plotting is enabled
        if plot_chromatograms:
            components.extend(
                [
                    self.chromatogram_visualizer,
                    self.hierarchy_visualizer,
                ]
            )

        # Always add output component last
        components.append(StandardOutput(input_file_path))

        # Initialize pipeline with components and config
        super().__init__(components, config=config)

    def run(self, input_data: PeptideHierarchyInput) -> PeptideHierarchyInput:
        """Run the pipeline.

        Args:
            input_data: Input data to process.

        Returns:
            Processed input data.

        Warns:
            UserWarning: If input data contains no peptides.
        """
        if not input_data.hierarchy or not input_data.hierarchy.peptides:
            warnings.warn("No peptides found in input data", UserWarning)
            return input_data

        # Call the parent class's run method instead of directly calling visualizers
        return super().run(input_data)  # type: ignore
