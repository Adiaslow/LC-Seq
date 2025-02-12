# src/lcseq/pipeline/components/correctors/swm_chromatogram_corrector.py
"""
This module defines the SWMChromatogramCorrector class, which is a pipeline component
for correcting chromatograms using the Sliding Window Minimum (SWM) baseline correction
algorithm.

Classes:
    SWMChromatogramCorrector: A pipeline component for correcting chromatograms using
        SWM.
"""

# Standard library imports
import logging
import numpy as np
from dataclasses import dataclass

# Local application imports
from src.lcseq.pipeline.base import PipelineComponent
from src.lcseq.pipeline.input_types import SinglePeptideInput, PeptideSetInput, PeptideHierarchyInput
from src.lcseq.core.chromatogram import Chromatogram

logger = logging.getLogger(__name__)

@dataclass
class SWMChromatogramCorrectorConfig:
    """
    Configuration for the SWM baseline correction.
    """
    window_length: int = 3
    padding_mode: str = 'edge'

class SWMChromatogramCorrector(PipelineComponent):
    """
    SWMChromatogramCorrector class for correcting chromatograms using the Sliding
    Window Minimum (SWM) baseline correction algorithm.

    This class inherits from the PipelineComponent class and provides methods to
    process and correct chromatograms for single peptides, sets of peptides, and
    peptide hierarchies.

    Attributes:
        config (SWMChromatogramCorrectorConfig): Configuration for the SWM baseline
            correction.
    """

    def __init__(self, config: SWMChromatogramCorrectorConfig = None): # type: ignore
        """
        Initializes the SWMChromatogramCorrector with the provided configuration.

        Args:
            config (SWMChromatogramCorrectorConfig, optional): Configuration for the
                SWM baseline correction. Default is None, which uses the default
                configuration.
        """
        self.config = config or SWMChromatogramCorrectorConfig()
        self.logger = logging.getLogger(__name__)

    def _correct_chromatogram(self, chrom: Chromatogram) -> Chromatogram:
        """Apply SWM baseline correction to a single chromatogram."""
        x = chrom.times
        y = chrom.intensities

        # Validate inputs
        self._validate_inputs(y)

        # Calculate window parameters
        half_window = self.config.window_length // 2

        # Pad signal and times
        y_pad = self._pad_signal(y, half_window)
        x_pad = self._pad_signal(x, half_window)

        # Calculate baseline
        y_min = self._compute_baseline(y_pad)

        # Trim y_min to match the length of y
        y_min_trimmed = y_min[half_window: -half_window or None]

        # Ensure y_min_trimmed has the correct length
        if len(y_min_trimmed) != len(y):
            y_min_trimmed = y_min[:len(y)]

        # Subtract baseline
        y_diff = y - y_min_trimmed

        # Set non-zero values back to their original amplitudes
        y_corrected = np.where(y_diff > 0, y, 0)

        # Filter out zero points
        non_zero_mask = y_corrected != 0
        if not np.any(non_zero_mask):
            raise ValueError("No non-zero points remain after baseline correction")

        chrom.properties['corrected_intensities'] = y_corrected
        chrom.properties['baseline'] = y_min_trimmed
        return chrom

    def process_peptide(self, input_data: SinglePeptideInput) -> SinglePeptideInput:
        """
        Correct the chromatogram for a single peptide.

        Args:
            input_data (SinglePeptideInput): The input data representing a single peptide.

        Returns:
            SinglePeptideInput: The corrected single peptide input.
        """
        self.logger.info(f"Correcting chromatogram for peptide: {input_data.peptide.sequence_str}")
        for encoding in input_data.peptide.encodings:
            if encoding.chromatogram is not None:
                encoding.chromatogram = self._correct_chromatogram(
                    encoding.chromatogram
                )
                self.logger.info(f"Chromatogram corrected for {encoding}:" +
                    f"{encoding.chromatogram.properties}")
        return input_data

    def process_peptide_set(
        self,
        input_data: PeptideSetInput
    ) -> PeptideSetInput:
        """
        Correct chromatograms for a set of peptides.

        Args:
            input_data (PeptideSetInput): The input data representing a set of peptides.

        Returns:
            PeptideSetInput: The corrected set of peptides.
        """
        self.logger.info("Correcting chromatograms for peptide set:" +
            f"{len(input_data.peptides)} peptides")
        for peptide in input_data.peptides:
            for encoding in peptide.encodings:
                if encoding.chromatogram is not None:
                    encoding.chromatogram = self._correct_chromatogram(
                        encoding.chromatogram
                    )
        return input_data

    def process_hierarchy(
        self,
        input_data: PeptideHierarchyInput
    ) -> PeptideHierarchyInput:
        """
        Correct chromatograms in a peptide hierarchy.

        Args:
            input_data (PeptideHierarchyInput): The input data representing a hierarchy
                of peptides.

        Returns:
            PeptideHierarchyInput: The corrected hierarchy of peptides.
        """
        def process_node(node):
            for encoding in node.root.encodings:
                if encoding.chromatogram is not None:
                    encoding.chromatogram = self._correct_chromatogram(
                        encoding.chromatogram
                    )
            for child in node.children:
                process_node(child)

        self.logger.info(f"Correcting chromatograms for peptide hierarchy")
        process_node(input_data.hierarchy)
        return input_data

    def _validate_inputs(self, y: np.ndarray) -> None:
        """Validate input parameters and signal."""
        if not isinstance(self.config.window_length, int):
            raise TypeError("Window length must be an integer.")
        if self.config.window_length <= 0:
            raise ValueError("Window length must be positive.")
        if self.config.window_length % 2 == 0:
            raise ValueError("Window length must be an odd integer.")
        if len(y) == 0:
            raise ValueError("Input signal is empty.")
        if not np.all(np.isfinite(y)):
            raise ValueError("Input signal contains NaN or infinite values.")
        if len(y) < self.config.window_length:
            raise ValueError(
                f"Signal length ({len(y)}) must be >= window length "
                f"({self.config.window_length})"
            )

    def _pad_signal(self, y: np.ndarray, half_window: int) -> np.ndarray:
        """Pad the input signal according to config."""
        try:
            return np.pad(
                y,
                (half_window, half_window),
                mode=self.config.padding_mode
            )
        except ValueError as e:
            raise ValueError("Invalid padding mode: " + \
                f"{self.config.padding_mode}") from e

    def _compute_baseline(self, y_padded: np.ndarray) -> np.ndarray:
        """Compute the baseline using sliding window minimum."""
        try:
            window_view = np.lib.stride_tricks.sliding_window_view(
                y_padded, self.config.window_length
            )
            return np.min(window_view, axis=1)
        except Exception as e:
            raise RuntimeError("Failed to compute sliding window minimum") from e
