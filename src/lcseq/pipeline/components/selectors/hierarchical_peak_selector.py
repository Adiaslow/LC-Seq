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
        """Select the peak with the lowest time value meeting criteria.

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

        # Find peak with lowest time (earliest peak)
        earliest_peak: Peak = min(valid_peaks, key=lambda p: p.apex_time)
        self.logger.info(f"Selected peak at {earliest_peak.apex_time}")
        return [earliest_peak]

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

        min_truncation_time = min(truncation_times)

        # A peak is valid if it's significantly lower than all truncation peaks
        # or if it's clearly a failed synthesis (significantly higher)
        if (
            peak.apex_time
            < min_truncation_time - self.config.min_retention_time_difference
        ):
            return True  # Valid synthesis peak

        # If the peak is close to or above truncation times, it's likely a failed synthesis
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

        For example, with Val-Phe-Leu:
        1. First process Val, Phe, and Leu (depth 1)
        2. Then process Val-Phe, Val-Leu, Phe-Leu (depth 2)
        3. Finally process Val-Phe-Leu (depth 3)

        Args:
            input_data (PeptideHierarchyInput): The input data to process.

        Returns:
            PeptideHierarchyInput: The processed input data.
        """
        hierarchy = input_data.hierarchy

        # Process nodes layer by layer
        for depth in range(1, 4):  # Process depths 1, 2, and 3
            nodes_at_depth = hierarchy.get_nodes_at_depth(depth)
            self.logger.info(f"Processing {len(nodes_at_depth)} nodes at depth {depth}")

            for node in nodes_at_depth:
                # Get precursors that have already been processed
                precursors = hierarchy.get_precursors(node)
                if depth > 1 and not all(
                    p.peptide.properties.get("retention_time") is not None
                    for p in precursors
                ):
                    self.logger.warning(
                        f"Not all precursors have been processed for {node.peptide.effective_sequence_str}"
                    )
                    continue

                # Process the node
                self._process_node_with_truncations(node)

                # Update node's retention time from the selected peak
                for encoding in node.peptide.encodings:
                    if encoding.chromatogram and encoding.chromatogram.peaks:
                        rt = encoding.chromatogram.peaks[0].apex_time
                        node.peptide.properties["retention_time"] = rt
                        break

                # Update synthesis status based on precursors and RT
                node.update_synthesis_status(precursors)

                self.logger.info(
                    f"Processed {node.peptide.effective_sequence_str}: "
                    f"RT = {node.peptide.properties.get('retention_time')}, "
                    f"Status = {node.peptide.properties.get('synthesis_status')}"
                )

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
                        min(synthesis_peaks, key=lambda p: p.apex_time)
                    ]
                else:
                    # If no valid synthesis peaks, take the lowest peak
                    # (will be marked as failed synthesis)
                    encoding.chromatogram.peaks = [
                        min(valid_peaks, key=lambda p: p.apex_time)
                    ]
