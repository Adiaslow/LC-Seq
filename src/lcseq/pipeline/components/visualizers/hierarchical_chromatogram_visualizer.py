# src/lcseq/pipeline/components/visualizers/hierarchical_chromatogram_visualizer.py
"""
This module provides a pipeline component for visualizing hierarchical chromatograms.
"""

# Standard library imports
import logging
from dataclasses import dataclass
import matplotlib.pyplot as plt
import numpy as np
from typing import Optional

# Local application imports
from src.lcseq.pipeline.base import PipelineComponent
from src.lcseq.pipeline.input_types import SinglePeptideInput, PeptideSetInput, PeptideHierarchyInput
from src.lcseq.core.chromatogram import Chromatogram

logger = logging.getLogger(__name__)

@dataclass
class HierarchicalChromatogramVisualizerConfig:
    """Configuration for hierarchical chromatogram visualization.

    Attributes:
        figure_size (tuple): The size of the figure.
        dpi (int): The resolution of the figure.
        line_width (float): The width of the lines.
        peak_line_style (str): The style of the peak lines.
    """
    figure_size: tuple = (10, 6)
    dpi: int = 100
    line_width: float = 1.5
    peak_line_style: str = '--'
    gaussian_line_style: str = ':'
    width_line_style: str = '-.'
    save_plots: bool = True
    output_dir: str = 'chromatogram_plots'
    plot_corrected_gaussians: bool = False  # New option to plot corrected Gaussians

class HierarchicalChromatogramVisualizer(PipelineComponent):
    ...
