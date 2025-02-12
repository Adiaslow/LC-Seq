# src/lcseq/pipeline/components/selectors/basic_peak_selector.py
"""
This module provides a pipeline component for selecting peaks from chromatograms.
It includes a class for basic peak selection.
"""

# Standard library imports
import logging
from dataclasses import dataclass

# Local application imports
from src.lcseq.pipeline.base import PipelineComponent
from src.lcseq.pipeline.input_types import SinglePeptideInput, PeptideSetInput, PeptideHierarchyInput
from src.lcseq.core.chromatogram import Peak

logger = logging.getLogger(__name__)

@dataclass
class BasicPeakSelectorConfig:
    """Configuration for basic peak selection.

    Attributes:
        intensity_threshold (float): The intensity threshold for peak selection.
        min_duration (float): The minimum duration for peak selection.
    """
    intensity_threshold: float = 0.0
    min_duration: float = 0.0

class BasicPeakSelector(PipelineComponent):
    """BasicPeakSelector class for selecting peaks from chromatograms.

    Attributes:
        config (BasicPeakSelectorConfig): The configuration for basic peak selection.
        logger (logging.Logger): The logger for logging messages.

    Methods:
        select_peaks: Select the peak with the highest time value.
        process_peptide: Process a single peptide.
        process_peptide_set: Process a set of peptides.
        process_hierarchy: Process a hierarchy of peptides.
    """
    def __init__(self, config: BasicPeakSelectorConfig = None): # type: ignore
        """Initialize the BasicPeakSelector.

        Args:
            config (BasicPeakSelectorConfig, optional): The configuration for basic peak selection.
                Defaults to None, which uses the default configuration.
        """
        self.config = config or BasicPeakSelectorConfig()
        self.logger = logging.getLogger(__name__)

    def select_peaks(self, peaks: list[Peak]) -> list[Peak]:
        """Select the peak with the highest time value.

        Args:
            peaks (list[Peak]): The list of peaks to select from.

        Returns:
            list[Peak]: The list of selected peaks.
        """
        peak_info = [f"{peak.apex_time} ({peak.apex_intensity})" for peak in peaks]
        self.logger.info(f"Selecting peaks from: {', '.join(peak_info)}")
        if not peaks:
            self.logger.warning("No peaks found")
            return []

        # Filter peaks based on basic criteria
        valid_peaks = [
            peak for peak in peaks
            if peak.apex_intensity >= self.config.intensity_threshold
            and (peak.end_time - peak.start_time) >= self.config.min_duration
        ]

        if not valid_peaks:
            self.logger.warning("No valid peaks found")
            return []

        # Find peak with highest time
        latest_peak = max(valid_peaks, key=lambda p: p.apex_time)
        self.logger.info(f"Selected peak at {latest_peak.apex_time} with metrics:\n{latest_peak.properties}")
        return [latest_peak]

    def process_peptide(self, input_data: SinglePeptideInput) -> SinglePeptideInput:
        """Select peaks for a single peptide.

        Args:
            input_data (SinglePeptideInput): The input data to process.

        Returns:
            SinglePeptideInput: The processed input data.
        """
        self.logger.info(f"Selecting peaks for peptide: {input_data.peptide.sequence_str}")
        for encoding in input_data.peptide.encodings:
            if encoding.chromatogram is not None and encoding.chromatogram.peaks:
                encoding.chromatogram.peaks = self.select_peaks(encoding.chromatogram.peaks)
        return input_data

    def process_peptide_set(self, input_data: PeptideSetInput) -> PeptideSetInput:
        """Select peaks for a set of peptides.

        Args:
            input_data (PeptideSetInput): The input data to process.

        Returns:
            PeptideSetInput: The processed input data.
        """
        self.logger.info(f"Selecting peaks for peptide set: {len(input_data.peptides)} peptides")
        for peptide in input_data.peptides:
            for encoding in peptide.encodings:
                if encoding.chromatogram is not None and encoding.chromatogram.peaks:
                    encoding.chromatogram.peaks = self.select_peaks(encoding.chromatogram.peaks)
        return input_data

    def process_hierarchy(self, input_data: PeptideHierarchyInput) -> PeptideHierarchyInput:
        """Select peaks for a hierarchy of peptides.

        Args:
            input_data (PeptideHierarchyInput): The input data to process.

        Returns:
            PeptideHierarchyInput: The processed input data.
        """
        def process_node(node):
            for encoding in node.root.encodings:
                if encoding.chromatogram is not None and encoding.chromatogram.peaks:
                    encoding.chromatogram.peaks = self.select_peaks(encoding.chromatogram.peaks)
            for child in node.children:
                process_node(child)

        self.logger.info(f"Selecting peaks for peptide hierarchy")
        process_node(input_data.hierarchy)
        return input_data
