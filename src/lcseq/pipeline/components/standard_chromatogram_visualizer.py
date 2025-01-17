# src/lcseq/pipeline/components/standard_chromatogram_visualizer.py
import logging
from dataclasses import dataclass
import matplotlib.pyplot as plt
import numpy as np
from typing import Optional

from src.lcseq.pipeline.base import PipelineComponent
from src.lcseq.pipeline.input_types import SinglePeptideInput, PeptideSetInput, PeptideHierarchyInput
from src.lcseq.core.chromatogram import Chromatogram

logger = logging.getLogger(__name__)

@dataclass
class StandardChromatogramVisualizerConfig:
    """Configuration for chromatogram visualization."""
    figure_size: tuple = (10, 6)
    dpi: int = 100
    line_width: float = 1.5
    peak_line_style: str = '--'
    gaussian_line_style: str = ':'
    width_line_style: str = '-.'
    save_plots: bool = True
    output_dir: str = 'chromatogram_plots'

class StandardChromatogramVisualizer(PipelineComponent):
    def __init__(self, config: StandardChromatogramVisualizerConfig = None, plot_chromatograms = False): # type: ignore
        self.config = config or StandardChromatogramVisualizerConfig()
        self.logger = logging.getLogger(__name__)
        self.plot_chromatograms = plot_chromatograms

        # Create output directory if saving plots
        if self.config.save_plots:
            import os
            os.makedirs(self.config.output_dir, exist_ok=True)

    @staticmethod
    def _gaussian(x: np.ndarray, amplitude: float, mean: float, std: float) -> np.ndarray:
        """Calculate Gaussian function values."""
        return amplitude * np.exp(-(x - mean) ** 2 / (2 * std ** 2))

    def visualize_chromatogram(self, chrom: Chromatogram, peptide_name: str) -> None:
            """Create visualization for a single chromatogram."""
            if self.plot_chromatograms == False:
                return
            if not chrom.peaks:
                self.logger.warning(f"No peaks found for {peptide_name}")
                return

            # Create figure
            plt.figure(figsize=self.config.figure_size, dpi=self.config.dpi)

            # Plot chromatogram
            plt.plot(chrom.times, chrom.intensities,
                    linewidth=self.config.line_width,
                    label='Chromatogram')

            # Get picked peak (first peak)
            peak = chrom.peaks[0]

            # Plot vertical lines for peak boundaries and apex
            plt.axvline(x=peak.start_time,
                       color='r',
                       linestyle=self.config.peak_line_style,
                       alpha=0.5,
                       label='Peak Boundaries')
            plt.axvline(x=peak.end_time,
                       color='r',
                       linestyle=self.config.peak_line_style,
                       alpha=0.5)
            plt.axvline(x=peak.apex_time,
                       color='r',
                       linestyle=self.config.peak_line_style,
                       label='Peak Apex')

            # Plot width line if width is in properties
            if 'width' in peak.properties:
                # Get half max intensity for width line
                half_max = (peak.apex_intensity + peak.start_intensity) / 2
                plt.hlines(y=half_max,
                          xmin=peak.start_time,
                          xmax=peak.end_time,
                          colors='g',
                          linestyles=self.config.width_line_style,
                          label='Peak Width')

            # Plot Gaussian fit if parameters are available
            if 'gaussian_fit_params' in peak.properties:
                params = peak.properties['gaussian_fit_params']
                x_fit = np.linspace(min(chrom.times), max(chrom.times), 1000)
                y_fit = self._gaussian(x_fit,
                                     params['amplitude'],
                                     params['mean'],
                                     params['sigma'])
                plt.plot(x_fit, y_fit,
                        linestyle=self.config.gaussian_line_style,
                        color='orange',
                        label='Gaussian Fit')

            # Add labels and title
            plt.xlabel('Time')
            plt.ylabel('Intensity')
            plt.title(f'Chromatogram for {peptide_name}')
            plt.legend()
            plt.grid(True, alpha=0.3)

            # Save or show plot
            if self.config.save_plots:
                import os
                filename = os.path.join(self.config.output_dir,
                                      f"{peptide_name.replace(' ', '_')}_chromatogram.png")
                plt.savefig(filename)
                plt.close()
                self.logger.info(f"Saved chromatogram plot to {filename}")
            else:
                plt.show()
                plt.close()

    def process_peptide(self, input_data: SinglePeptideInput) -> SinglePeptideInput:
        """Process a single peptide."""
        self.logger.info(f"Visualizing chromatogram for peptide: {input_data.peptide.sequence_str}")
        for encoding in input_data.peptide.encodings:
            if encoding.chromatogram is not None:
                self.visualize_chromatogram(encoding.chromatogram,
                                          input_data.peptide.sequence_str)
        return input_data

    def process_peptide_set(self, input_data: PeptideSetInput) -> PeptideSetInput:
        """Process a set of peptides."""
        self.logger.info(f"Visualizing chromatograms for peptide set: {len(input_data.peptides)} peptides")
        for peptide in input_data.peptides:
            for encoding in peptide.encodings:
                if encoding.chromatogram is not None:
                    self.visualize_chromatogram(encoding.chromatogram,
                                              peptide.sequence_str)
        return input_data

    def process_hierarchy(self, input_data: PeptideHierarchyInput) -> PeptideHierarchyInput:
        """Process a hierarchy of peptides."""
        def process_node(node):
            for encoding in node.root.encodings:
                if encoding.chromatogram is not None:
                    self.visualize_chromatogram(encoding.chromatogram,
                                              node.root.sequence_str)
            for child in node.children:
                process_node(child)

        self.logger.info(f"Visualizing chromatograms for peptide hierarchy")
        process_node(input_data.hierarchy)
        return input_data
