# src/lcseq/pipeline/components/visualizers/standard_chromatogram_visualizer.py
"""
This module provides a pipeline component for visualizing standard chromatograms.

Classes:
    StandardChromatogramVisualizer: Pipeline component for visualizing standard chromatograms.
    StandardChromatogramVisualizerConfig: Configuration for chromatogram visualization.
"""

# Standard library imports
import logging
from dataclasses import dataclass
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
from src.lcseq.core.chromatogram import Chromatogram
from src.lcseq.core.hierarchy import PeptideHierarchyNode
from src.lcseq.core.peak import Peak
# Local application imports
from src.lcseq.pipeline.base import PipelineComponent
from src.lcseq.pipeline.input_types import (PeptideHierarchyInput,
                                            PeptideSetInput,
                                            SinglePeptideInput)

logger: logging.Logger = logging.getLogger(__name__)


@dataclass
class StandardChromatogramVisualizerConfig:
    """Configuration for chromatogram visualization.

    Attributes:
        figure_size (tuple): The size of the figure.
        dpi (int): The resolution of the figure.
        line_width (float): The width of the lines.
        peak_line_style (str): The style of the peak lines.
        gaussian_line_style (str): The style of the gaussian lines.
        width_line_style (str): The style of the width lines.
        save_plots (bool): Whether to save the plots.
        output_dir (str): The directory to save the plots.
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
    plot_corrected_gaussians: bool = False  # New option to plot corrected Gaussians


class StandardChromatogramVisualizer(PipelineComponent):
    """Visualize standard chromatograms.

    Attributes:
        config (StandardChromatogramVisualizerConfig): The configuration for chromatogram visualization.
        logger (logging.Logger): The logger for logging messages.
        plot_chromatograms (bool): Whether to plot chromatograms.

    Methods:
        visualize_chromatogram: Create visualization for a single chromatogram.
        process_peptide: Process a single peptide.
        process_peptide_set: Process a set of peptides.
        process_hierarchy: Process a hierarchy of peptides.
    """

    def __init__(
        self,
        config: StandardChromatogramVisualizerConfig = None,  # type: ignore
        plot_chromatograms: bool = False,
    ) -> None:
        """Initialize the StandardChromatogramVisualizer.

        Args:
            config (StandardChromatogramVisualizerConfig, optional): The configuration for chromatogram visualization.
                Defaults to None, which uses the default configuration.
            plot_chromatograms (bool, optional): Whether to plot chromatograms.
                Defaults to False.
        """
        self.config: StandardChromatogramVisualizerConfig = (
            config or StandardChromatogramVisualizerConfig()
        )
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.plot_chromatograms: bool = plot_chromatograms

        # Create output directory if saving plots
        if self.config.save_plots:
            import os

            os.makedirs(self.config.output_dir, exist_ok=True)

    @staticmethod
    def _gaussian(
        x: np.ndarray, amplitude: float, mean: float, std: float
    ) -> np.ndarray:
        """Calculate Gaussian function values.

        Args:
            x (np.ndarray): The x values.
            amplitude (float): The amplitude of the Gaussian.
            mean (float): The mean of the Gaussian.
            std (float): The standard deviation of the Gaussian.

        Returns:
            np.ndarray: The y values of the Gaussian.
        """
        std = max(std, 1e-6)  # Ensure std is not zero
        return amplitude * np.exp(-((x - mean) ** 2) / (2 * std**2))

    def visualize_chromatogram(self, chrom: Chromatogram, peptide_name: str) -> None:
        """Create visualization for a single chromatogram.

        Args:
            chrom (Chromatogram): The chromatogram to visualize.
            peptide_name (str): The name of the peptide.

        Returns:
            None
        """
        if not self.plot_chromatograms:
            return
        if not chrom.peaks:
            self.logger.warning(f"No peaks found for {peptide_name}")
            return

        # Create figure
        plt.figure(figsize=self.config.figure_size, dpi=self.config.dpi)

        # Plot chromatogram
        plt.plot(
            chrom.times,
            chrom.intensities,
            linewidth=self.config.line_width,
            label="Chromatogram",
        )

        if "corrected_intensities" in chrom.properties:
            plt.plot(
                chrom.times,
                chrom.properties["corrected_intensities"],
                linewidth=self.config.line_width,
                label="Corrected Chromatogram",
            )

        # Get picked peak (first peak)
        peak: Peak = chrom.peaks[0]

        # Plot vertical lines for peak boundaries and apex
        plt.axvline(
            x=peak.start_time,
            color="r",
            linestyle=self.config.peak_line_style,
            alpha=0.5,
            label="Peak Boundaries",
        )
        plt.axvline(
            x=peak.end_time, color="r", linestyle=self.config.peak_line_style, alpha=0.5
        )
        plt.axvline(
            x=peak.apex_time,
            color="r",
            linestyle=self.config.peak_line_style,
            label="Retention Time",
        )

        # Plot width line if width is in properties
        if "width" in peak.properties:
            # Get half max intensity for width line
            half_max = (peak.apex_intensity + peak.start_intensity) / 2
            plt.hlines(
                y=half_max,
                xmin=peak.start_time,
                xmax=peak.end_time,
                colors="g",
                linestyles=self.config.width_line_style,
                label="Peak Width",
            )

        # Plot Gaussian fit if parameters are available
        gaussian_fit_key = (
            "corrected_gaussian_fit_params"
            if self.config.plot_corrected_gaussians
            else "gaussian_fit_params"
        )
        if gaussian_fit_key in peak.properties:
            params: dict[str, float] = peak.properties[gaussian_fit_key]
            x_fit: np.ndarray = np.linspace(min(chrom.times), max(chrom.times), 1000)
            y_fit: np.ndarray = self._gaussian(
                x_fit, params["amplitude"], params["mean"], params["sigma"]
            )
            plt.plot(
                x_fit,
                y_fit,
                linestyle=self.config.gaussian_line_style,
                color="orange",
                label=(
                    "Corrected Gaussian Fit"
                    if self.config.plot_corrected_gaussians
                    else "Gaussian Fit"
                ),
            )

        # Add labels and title
        plt.xlabel("Time")
        plt.ylabel("Intensity")
        plt.title(f"Chromatogram for {peptide_name}")
        plt.legend()
        plt.grid(True, alpha=0.3)

        # Save or show plot
        if self.config.save_plots:
            import os

            filename: str = os.path.join(
                self.config.output_dir,
                f"{peptide_name.replace(' ', '_')}_chromatogram.png",
            )
            plt.savefig(filename)
            plt.close()
            self.logger.info(f"Saved chromatogram plot to {filename}")
        else:
            plt.show()
            plt.close()

    def process_peptide(self, input_data: SinglePeptideInput) -> SinglePeptideInput:
        """Process a single peptide.

        Args:
            input_data (SinglePeptideInput): The input data to process.

        Returns:
            SinglePeptideInput: The processed input data.
        """
        self.logger.info(
            f"Visualizing chromatogram for peptide: {input_data.peptide.sequence_str}"
        )
        for encoding in input_data.peptide.encodings:
            if encoding.chromatogram is not None:
                self.visualize_chromatogram(
                    encoding.chromatogram, input_data.peptide.sequence_str
                )
        return input_data

    def process_peptide_set(self, input_data: PeptideSetInput) -> PeptideSetInput:
        """Process a set of peptides.

        Args:
            input_data (PeptideSetInput): The input data to process.

        Returns:
            PeptideSetInput: The processed input data.
        """
        self.logger.info(
            f"Visualizing chromatograms for peptide set: {len(input_data.peptides)} peptides"
        )
        for peptide in input_data.peptides:
            for encoding in peptide.encodings:
                if encoding.chromatogram is not None:
                    self.visualize_chromatogram(
                        encoding.chromatogram, peptide.sequence_str
                    )
        return input_data

    def process_hierarchy(
        self, input_data: PeptideHierarchyInput
    ) -> PeptideHierarchyInput:
        """Process a hierarchy of peptides.

        Args:
            input_data (PeptideHierarchyInput): The input data to process.

        Returns:
            PeptideHierarchyInput: The processed input data.
        """

        def process_node(node: PeptideHierarchyNode) -> None:
            for encoding in node.peptide.encodings:
                if encoding.chromatogram is not None:
                    self.visualize_chromatogram(
                        encoding.chromatogram, node.peptide.sequence_str
                    )
            for child in node.children:
                process_node(child)

        self.logger.info(f"Visualizing chromatograms for peptide hierarchy")
        process_node(input_data.hierarchy.root)
        return input_data
