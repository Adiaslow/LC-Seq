# src/lcseq/pipeline/components/gpp_peak_selector.py
"""
GPPPeakSelector module for selecting chromatographic peaks based on corrected Gaussian mean time.

This module defines the GPPPeakSelector class which inherits from PipelineComponent.
The GPPPeakSelector class is used to select peaks from chromatographic data based on the
corrected Gaussian mean time, with configurable intensity threshold and minimum duration for peaks.

Classes:
    GPPPeakSelectorConfig: Configuration class for GPP peak selection.
    GPPPeakSelector: Pipeline component for selecting peaks based on corrected Gaussian mean time.
"""

# Standard library imports
import logging
from dataclasses import dataclass

from src.lcseq.core.chromatogram import Peak
from src.lcseq.core.hierarchy import PeptideHierarchyNode
# Local application imports
from src.lcseq.pipeline.base import PipelineComponent
from src.lcseq.pipeline.input_types import (PeptideHierarchyInput,
                                            PeptideSetInput,
                                            SinglePeptideInput)

logger: logging.Logger = logging.getLogger(__name__)


@dataclass
class GPPPeakSelectorConfig:
    """Configuration for GPP peak selection.

    Attributes:
        intensity_threshold (float): The intensity threshold for peak selection.
        min_duration (float): The minimum duration for peak selection.
    """

    intensity_threshold: float = 0.0
    min_duration: float = 0.0


class GPPPeakSelector(PipelineComponent):
    """Pipeline component for selecting peaks based on corrected Gaussian mean time.

    Attributes:
        config (GPPPeakSelectorConfig): The configuration for GPP peak selection.
        logger (logging.Logger): The logger for logging messages.

    Methods:
        select_peaks: Select the peak with the highest corrected Gaussian mean time value.
        process_peptide: Process a single peptide.
        process_peptide_set: Process a set of peptides.
        process_hierarchy: Process a hierarchy of peptides.
    """

    def __init__(self, config: GPPPeakSelectorConfig = None):  # type: ignore
        """Initialize GPPPeakSelector with the given configuration.

        Args:
            config: An optional GPPPeakSelectorConfig object. If not provided,
                a default configuration will be used.
        """
        self.config = config or GPPPeakSelectorConfig()
        self.logger = logging.getLogger(__name__)

    def select_peaks(self, peaks: list[Peak]) -> list[Peak]:
        """Select the peak with the highest corrected Gaussian mean time value.

        Args:
            peaks: A list of Peak objects to select from.

        Returns:
            A list containing the selected Peak object with the highest corrected Gaussian
            mean time value. If no valid peaks are found, an empty list is returned.
        """
        peak_info = [
            f"{peak.properties.get('corrected_gaussian_fit_params', {}).get('mean', 'N/A')} ({peak.apex_intensity})"
            for peak in peaks
        ]
        self.logger.info(f"Selecting peaks from: {', '.join(peak_info)}")

        if not peaks:
            self.logger.warning("No peaks found")
            return []

        # Filter peaks based on basic criteria
        valid_peaks = [
            peak
            for peak in peaks
            if peak.apex_intensity >= self.config.intensity_threshold
            and (peak.end_time - peak.start_time) >= self.config.min_duration
        ]

        if not valid_peaks:
            self.logger.warning("No valid peaks found")
            return []

        # Find peak with highest corrected Gaussian mean time
        latest_peak = max(
            valid_peaks,
            key=lambda p: p.properties.get("corrected_gaussian_fit_params", {}).get(
                "mean", float("-inf")
            ),
        )
        self.logger.info(
            f"Selected peak at {latest_peak.properties.get('corrected_gaussian_fit_params', {}).get('mean', 'N/A')} with metrics:\n{latest_peak.properties}"
        )
        return [latest_peak]

    def process_peptide(self, input_data: SinglePeptideInput) -> SinglePeptideInput:
        """Select peaks for a single peptide.

        Args:
            input_data: A SinglePeptideInput object containing the peptide data.

        Returns:
            The SinglePeptideInput object with selected peaks.
        """
        self.logger.info(
            f"Selecting peaks for peptide: {input_data.peptide.sequence_str}"
        )
        for encoding in input_data.peptide.encodings:
            if encoding.chromatogram is not None and encoding.chromatogram.peaks:
                encoding.chromatogram.peaks = self.select_peaks(
                    encoding.chromatogram.peaks
                )
        return input_data

    def process_peptide_set(self, input_data: PeptideSetInput) -> PeptideSetInput:
        """Select peaks for a set of peptides.

        Args:
            input_data: A PeptideSetInput object containing the set of peptides.

        Returns:
            The PeptideSetInput object with selected peaks for each peptide.
        """
        self.logger.info(
            f"Selecting peaks for peptide set: {len(input_data.peptides)} peptides"
        )
        for peptide in input_data.peptides:
            for encoding in peptide.encodings:
                if encoding.chromatogram is not None and encoding.chromatogram.peaks:
                    encoding.chromatogram.peaks = self.select_peaks(
                        encoding.chromatogram.peaks
                    )
        return input_data

    def process_hierarchy(
        self, input_data: PeptideHierarchyInput
    ) -> PeptideHierarchyInput:
        """Select peaks for a hierarchy of peptides.

        Args:
            input_data: A PeptideHierarchyInput object containing the peptide hierarchy.

        Returns:
            The PeptideHierarchyInput object with selected peaks for each peptide in the hierarchy.
        """

        def process_node(node: PeptideHierarchyNode) -> None:
            for encoding in node.peptide.encodings:
                if encoding.chromatogram is not None and encoding.chromatogram.peaks:
                    encoding.chromatogram.peaks = self.select_peaks(
                        encoding.chromatogram.peaks
                    )
            for child in node.children:
                process_node(child)

        self.logger.info(f"Selecting peaks for peptide hierarchy")
        process_node(input_data.hierarchy.root)
        return input_data
