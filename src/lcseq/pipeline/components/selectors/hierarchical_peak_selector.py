# src/lcseq/pipeline/components/selectors/hierarchical_peak_selector.py
"""
This module provides a pipeline component for selecting peaks from chromatograms.
It includes a class for hierarchical peak selection.
"""

import logging

# Standard library imports
from dataclasses import dataclass

from src.lcseq.core.chromatogram import Peak
from src.lcseq.core.hierarchy import PeptideHierarchyNode

# Local application imports
from src.lcseq.pipeline.base import PipelineComponent
from src.lcseq.pipeline.input_types import (
    PeptideHierarchyInput,
    PeptideSetInput,
    SinglePeptideInput,
)

logger: logging.Logger = logging.getLogger(__name__)


@dataclass
class HierarchicalPeakSelectorConfig:
    """Configuration for hierarchical peak selection.

    Attributes:
        intensity_threshold (float): The intensity threshold for peak selection.
        min_duration (float): The minimum duration for peak selection.
        min_retention_time_difference (float): The minimum retention time difference from truncation times.
    """

    intensity_threshold: float = 0.0
    min_duration: float = 0.0
    min_retention_time_difference: float = (
        0.5  # Minimum difference from truncation times
    )


class HierarchicalPeakSelector(PipelineComponent):
    """Selects peaks considering hierarchical relationships between peptides."""

    def __init__(self, config: HierarchicalPeakSelectorConfig = None) -> None:  # type: ignore
        """Initialize the HierarchicalPeakSelector.

        Args:
            config (HierarchicalPeakSelectorConfig, optional): The configuration for hierarchical peak selection.
                Defaults to None, which uses the default configuration.
        """
        super().__init__()
        self.config: HierarchicalPeakSelectorConfig = (
            config or HierarchicalPeakSelectorConfig()
        )

    def select_peaks(self, peaks: list[Peak]) -> list[Peak]:
        """Select the peak with the highest time value meeting criteria.

        Args:
            peaks (list[Peak]): The list of peaks to select from.

        Returns:
            list[Peak]: The list of selected peaks.
        """
        self.logger.info(f"Selecting from {len(peaks)} peaks")
        if not peaks:
            self.logger.warning("No peaks found")
            return []

        # Filter peaks based on basic criteria
        valid_peaks: list[Peak] = [
            peak
            for peak in peaks
            if peak.apex_intensity >= self.config.intensity_threshold
            and (peak.end_time - peak.start_time) >= self.config.min_duration
        ]

        if not valid_peaks:
            self.logger.warning("No valid peaks found")
            return []

        # Find peak with highest time
        latest_peak: Peak = max(valid_peaks, key=lambda p: p.apex_time)
        self.logger.info(f"Selected peak at {latest_peak.apex_time}")
        return [latest_peak]

    def _validates_against_truncations(
        self, peak: Peak, node: PeptideHierarchyNode
    ) -> bool:
        """Check if peak retention time is valid against truncation peaks.

        Args:
            peak (Peak): The peak to check.
            node (PeptideHierarchyNode): The node to check against.

        Returns:
            bool: True if the peak is valid, False otherwise.
        """
        # Get all truncation peak times
        truncation_times = []
        for truncation in node.truncation_edges:
            for encoding in truncation.peptide.encodings:
                if encoding.chromatogram and encoding.chromatogram.peaks:
                    truncation_times.extend(
                        peak.apex_time for peak in encoding.chromatogram.peaks
                    )

        if not truncation_times:
            return True  # No truncations to validate against

        max_truncation_time = max(truncation_times)

        # A peak is valid if it's significantly higher than all truncation peaks
        # or if it's clearly a failed synthesis (significantly lower)
        if (
            peak.apex_time
            > max_truncation_time + self.config.min_retention_time_difference
        ):
            return True  # Valid synthesis peak

        # If the peak is close to or below truncation times, it's likely a failed synthesis
        # We'll still keep these peaks but they'll be marked as failures later
        return False

    def process_peptide(self, input_data: SinglePeptideInput) -> SinglePeptideInput:
        """Process a single peptide (treat as non-hierarchical).

        Args:
            input_data (SinglePeptideInput): The input data to process.

        Returns:
            SinglePeptideInput: The processed input data.
        """
        for encoding in input_data.peptide.encodings:
            if encoding.chromatogram and encoding.chromatogram.peaks:
                encoding.chromatogram.peaks = self.select_peaks(
                    encoding.chromatogram.peaks
                )
        return input_data

    def process_peptide_set(self, input_data: PeptideSetInput) -> PeptideSetInput:
        """Process a set of peptides (treat as non-hierarchical).

        Args:
            input_data (PeptideSetInput): The input data to process.

        Returns:
            PeptideSetInput: The processed input data.
        """
        for peptide in input_data.peptides:
            for encoding in peptide.encodings:
                if encoding.chromatogram and encoding.chromatogram.peaks:
                    encoding.chromatogram.peaks = self.select_peaks(
                        encoding.chromatogram.peaks
                    )
        return input_data

    def process_hierarchy(
        self, input_data: PeptideHierarchyInput
    ) -> PeptideHierarchyInput:
        """Process hierarchy layer by layer.

        Args:
            input_data (PeptideHierarchyInput): The input data to process.

        Returns:
            PeptideHierarchyInput: The processed input data.
        """
        # Process from shortest to longest peptides
        max_layer = max(input_data.hierarchy.layers.keys())

        # First process single building blocks (layer 1)
        for node in input_data.hierarchy.layers[1]:
            for encoding in node.peptide.encodings:
                if encoding.chromatogram and encoding.chromatogram.peaks:
                    # For single blocks, just take the highest peak
                    encoding.chromatogram.peaks = self.select_peaks(
                        encoding.chromatogram.peaks
                    )
                    if encoding.chromatogram.peaks:
                        node.retention_time = encoding.chromatogram.peaks[0].apex_time

        # Then process each subsequent layer
        for layer in range(2, max_layer + 1):
            for node in input_data.hierarchy.layers[layer]:
                self._process_node_with_truncations(node)

                # Update node's retention time and synthesis status
                for encoding in node.peptide.encodings:
                    if encoding.chromatogram and encoding.chromatogram.peaks:
                        node.retention_time = encoding.chromatogram.peaks[0].apex_time
                        break

                # Update synthesis status based on RT relationships
                node.update_synthesis_status()

        return input_data

    def _process_node_with_truncations(self, node: PeptideHierarchyNode) -> None:
        """Select peaks considering truncation retention times.

        Args:
            node (PeptideHierarchyNode): The node to process.
        """
        for encoding in node.peptide.encodings:
            if encoding.chromatogram and encoding.chromatogram.peaks:
                # First filter by basic criteria
                valid_peaks = [
                    peak
                    for peak in encoding.chromatogram.peaks
                    if peak.apex_intensity >= self.config.intensity_threshold
                    and (peak.end_time - peak.start_time) >= self.config.min_duration
                ]

                if not valid_peaks:
                    continue

                # Then validate against truncations
                synthesis_peaks = [
                    peak
                    for peak in valid_peaks
                    if self._validates_against_truncations(peak, node)
                ]

                # If we found valid synthesis peaks, use those
                if synthesis_peaks:
                    encoding.chromatogram.peaks = [
                        max(synthesis_peaks, key=lambda p: p.apex_time)
                    ]
                else:
                    # If no valid synthesis peaks, take the highest peak
                    # (will be marked as failed synthesis)
                    encoding.chromatogram.peaks = [
                        max(valid_peaks, key=lambda p: p.apex_time)
                    ]
