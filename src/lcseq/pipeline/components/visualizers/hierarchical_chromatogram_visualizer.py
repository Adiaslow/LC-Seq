# src/lcseq/pipeline/components/visualizers/hierarchical_chromatogram_visualizer.py
"""
This module provides a pipeline component for visualizing hierarchical chromatograms.
"""

# Standard library imports
import logging
from dataclasses import dataclass
from typing import Optional
import os
import warnings

import matplotlib.pyplot as plt
import numpy as np

# Local application imports
from src.lcseq.core.chromatogram import Chromatogram
from src.lcseq.pipeline.base import PipelineComponent
from src.lcseq.pipeline.input_types import (
    PeptideHierarchyInput,
    PeptideSetInput,
    SinglePeptideInput,
)

logger: logging.Logger = logging.getLogger(__name__)


@dataclass
class HierarchicalChromatogramVisualizerConfig:
    """Configuration for hierarchical chromatogram visualization.

    Attributes:
        figure_size (tuple): The size of the figure.
        dpi (int): The resolution of the figure.
        line_width (float): The width of the lines.
        peak_line_style (str): The style of the peak lines.
        gaussian_line_style (str): The style of the gaussian lines.
        width_line_style (str): The style of the width lines.
        save_plots (bool): Whether to save the plots.
        output_dir (str): Directory to save output plots.
        plot_corrected_gaussians (bool): Whether to plot corrected Gaussians.
    """

    figure_size: tuple = (10, 6)
    dpi: int = 100
    line_width: float = 1.5
    peak_line_style: str = "--"
    gaussian_line_style: str = ":"
    width_line_style: str = "-."
    save_plots: bool = True
    output_dir: str = "chromatogram_plots"
    plot_corrected_gaussians: bool = False


class HierarchicalChromatogramVisualizer(PipelineComponent):
    """Visualizes hierarchical chromatograms.

    Attributes:
        config (HierarchicalChromatogramVisualizerConfig): The configuration for the visualizer.
        plot_chromatograms (bool): Whether to plot chromatograms.
    """

    def __init__(
        self,
        config: Optional[HierarchicalChromatogramVisualizerConfig] = None,
        plot_chromatograms: bool = False,
    ) -> None:
        """Initialize the visualizer.

        Args:
            config: The configuration for the visualizer.
            plot_chromatograms: Whether to plot chromatograms.
        """
        super().__init__()
        self.config = config or HierarchicalChromatogramVisualizerConfig()
        self.plot_chromatograms = plot_chromatograms
        self.logger = logging.getLogger(__name__)

        # Only create output directory if plotting is enabled
        if self.plot_chromatograms and self.config.save_plots:
            os.makedirs(self.config.output_dir, exist_ok=True)

    def process_hierarchy(
        self, input_data: PeptideHierarchyInput
    ) -> PeptideHierarchyInput:
        """Process the hierarchical input data.

        Args:
            input_data: The input data to process.

        Returns:
            PeptideHierarchyInput: The processed input data.
        """
        if not input_data.hierarchy or not input_data.hierarchy.peptides:
            warnings.warn("No peptides found in input data", UserWarning)
            return input_data

        self.logger.info("Visualizing hierarchical chromatograms")
        self._visualize_hierarchy(input_data)
        return input_data

    def process_peptide(self, input_data: SinglePeptideInput) -> SinglePeptideInput:
        """Process a single peptide (not supported in hierarchical visualizer).

        Args:
            input_data (SinglePeptideInput): The input data to process.

        Returns:
            SinglePeptideInput: The unmodified input data.
        """
        self.logger.warning(
            "Single peptide processing not supported in hierarchical visualizer"
        )
        return input_data

    def process_peptide_set(self, input_data: PeptideSetInput) -> PeptideSetInput:
        """Process a set of peptides (not supported in hierarchical visualizer).

        Args:
            input_data (PeptideSetInput): The input data to process.

        Returns:
            PeptideSetInput: The unmodified input data.
        """
        self.logger.warning(
            "Peptide set processing not supported in hierarchical visualizer"
        )
        return input_data

    def _visualize_hierarchy(self, input_data: PeptideHierarchyInput) -> None:
        """Visualize the hierarchical chromatogram.

        Args:
            input_data: The input data to visualize.
        """
        if not self.plot_chromatograms:
            return

        has_chromatograms = False
        for peptide in input_data.hierarchy.peptides:
            if peptide.has_chromatogram():
                has_chromatograms = True
                chromatogram = peptide.get_chromatogram()
                if chromatogram is not None:
                    self._visualize_chromatogram(chromatogram, peptide.sequence_str)

        if not has_chromatograms:
            warnings.warn("No chromatograms found in peptides", UserWarning)

    def _visualize_chromatogram(self, chrom: Chromatogram, peptide_name: str) -> None:
        """Visualize a single chromatogram.

        Args:
            chrom: The chromatogram to visualize.
            peptide_name: Name of the peptide.
        """
        plt.figure(figsize=self.config.figure_size, dpi=self.config.dpi)

        # Plot raw data
        plt.plot(
            chrom.times,
            chrom.intensities,
            label="Raw Data",
            linewidth=self.config.line_width,
        )

        plt.xlabel("Time (min)")
        plt.ylabel("Intensity")
        plt.title(f"Chromatogram for {peptide_name}")
        plt.legend()
        plt.grid(True)

        if self.config.save_plots:
            filename = os.path.join(
                self.config.output_dir,
                f"{peptide_name.replace(' ', '_')}_chromatogram.png",
            )
            plt.savefig(filename, bbox_inches="tight")
            self.logger.info(f"Saved chromatogram plot to {filename}")
            plt.close()
        else:
            plt.show()
            plt.close()
