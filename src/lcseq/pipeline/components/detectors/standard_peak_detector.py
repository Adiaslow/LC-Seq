# src/lcseq/pipeline/components/detectors/standard_peak_detector.py
"""
This module provides a standard peak detector for peptide chromatograms.
It includes a configuration class for specifying detection parameters and a
class for performing peak detection.

Classes:
    StandardPeakDetectorConfig: Configuration parameters for peak detection.
    PeakDetectionStats: Statistics about peak detection and threshold adjustments.
    StandardPeakDetector: Class for performing peak detection.
"""

import logging
from dataclasses import dataclass
from typing import List

import numpy as np
from scipy.signal import find_peaks as sp_find_peaks
from src.lcseq.core.chromatogram import Chromatogram, Peak
from src.lcseq.pipeline.base import PipelineComponent
from src.lcseq.pipeline.input_types import (
    PeptideHierarchyInput,
    PeptideSetInput,
    SinglePeptideInput,
)

logger: logging.Logger = logging.getLogger(__name__)


@dataclass
class StandardPeakDetectorConfig:
    """Configuration parameters for peak detection.

    Attributes:
        min_snr_factor (float): The minimum SNR factor.
        max_snr_factor (float): The maximum SNR factor.
        snr_scale (float): The SNR scale.
        noise_prominence_factor (float): The noise prominence factor.
        min_prominence_ratio (float): The minimum prominence ratio.
        min_roughness_factor (float): The minimum roughness factor.
        max_roughness_factor (float): The maximum roughness factor.
        roughness_scale (float): The roughness scale.
        peak_separation_factor (float): The peak separation factor.
        min_window_points (int): The minimum window points.
        min_window_roughness_factor (float): The minimum window roughness factor.
        max_window_roughness_factor (float): The maximum window roughness factor.
        window_roughness_scale (float): The window roughness scale.
        relative_height (float): The relative height.
        max_threshold_iterations (int): The maximum threshold iterations.
        threshold_relaxation_factor (float): The threshold relaxation factor.
    """

    min_snr_factor: float = 3.0
    max_snr_factor: float = 10.0
    snr_scale: float = 0.5
    noise_prominence_factor: float = 2.0
    min_prominence_ratio: float = 0.01
    min_roughness_factor: float = 1.0
    max_roughness_factor: float = 5.0
    roughness_scale: float = 2.0
    peak_separation_factor: float = 2.0
    min_window_points: int = 5
    min_window_roughness_factor: float = 1.0
    max_window_roughness_factor: float = 10.0
    window_roughness_scale: float = 3.0
    relative_height: float = 0.5

    # Threshold relaxation parameters
    max_threshold_iterations: int = 5
    threshold_relaxation_factor: float = 0.5


@dataclass
class PeakDetectionStats:
    """Statistics about peak detection and threshold adjustments.

    Attributes:
        initial_thresholds (dict): The initial thresholds.
        final_thresholds (dict): The final thresholds.
        iterations (int): The number of iterations.
        excluded_by_height (int): The number of peaks excluded by height.
        excluded_by_prominence (int): The number of peaks excluded by prominence.
        excluded_by_width (int): The number of peaks excluded by width.
        excluded_by_distance (int): The number of peaks excluded by distance.
    """

    initial_thresholds: dict
    final_thresholds: dict
    iterations: int
    excluded_by_height: int = 0
    excluded_by_width: int = 0
    excluded_by_distance: int = 0


class StandardPeakDetector(PipelineComponent):
    """Class for performing peak detection.

    Attributes:
        config (StandardPeakDetectorConfig): The configuration for peak detection.
    """

    def __init__(self, config: StandardPeakDetectorConfig = None) -> None:  # type: ignore
        self.config: StandardPeakDetectorConfig = config or StandardPeakDetectorConfig()
        self.logger: logging.Logger = logging.getLogger(__name__)

    def find_peaks(self, chrom: Chromatogram) -> Chromatogram:
        """Find peaks in a single chromatogram with adaptive threshold adjustment."""
        self.logger.info(f"Finding peaks in chromatogram")

        # Initialize tracking of threshold adjustments
        stats = PeakDetectionStats(
            initial_thresholds={}, final_thresholds={}, iterations=0
        )

        # Initial thresholds
        thresholds: dict = {
            "height": self._calculate_height_threshold(chrom),
            "prominence": self._calculate_prominence_threshold(chrom),
            "width": self._calculate_width_threshold(chrom),
            "distance": self._calculate_distance_threshold(chrom),
            "wlen": self._calculate_window_length(chrom),
        }
        stats.initial_thresholds = thresholds.copy()

        peaks: list[Peak] = []
        iteration: int = 0

        while iteration < self.config.max_threshold_iterations:
            # Find peaks with current thresholds
            peak_indices, peak_properties = sp_find_peaks(
                chrom.intensities,
                height=thresholds["height"],
                prominence=thresholds["prominence"],
                width=thresholds["width"],
                distance=thresholds["distance"],
                wlen=thresholds["wlen"],
                rel_height=self.config.relative_height,
            )

            # Update exclusion statistics
            if len(peak_indices) == 0:
                # Count excluded peaks by each criterion
                trial_peaks, _ = sp_find_peaks(chrom.intensities)
                height_peaks, _ = sp_find_peaks(
                    chrom.intensities, height=thresholds["height"]
                )
                prominence_peaks, _ = sp_find_peaks(
                    chrom.intensities, prominence=thresholds["prominence"]
                )
                width_peaks, _ = sp_find_peaks(
                    chrom.intensities, width=thresholds["width"]
                )
                distance_peaks, _ = sp_find_peaks(
                    chrom.intensities, distance=thresholds["distance"]
                )

                stats.excluded_by_height = len(trial_peaks) - len(height_peaks)
                stats.excluded_by_width = len(trial_peaks) - len(width_peaks)
                stats.excluded_by_distance = len(trial_peaks) - len(distance_peaks)

                # Relax thresholds based on what's excluding the most peaks
                relaxation = self.config.threshold_relaxation_factor
                max_exclusions = max(
                    stats.excluded_by_height,
                    stats.excluded_by_width,
                    stats.excluded_by_distance,
                )

                if max_exclusions == stats.excluded_by_height:
                    thresholds["height"] *= 1 - relaxation
                    self.logger.info(
                        f"Relaxing height threshold to {thresholds['height']}"
                    )
                elif max_exclusions == stats.excluded_by_width:
                    thresholds["width"] *= 1 - relaxation
                    self.logger.info(
                        f"Relaxing width threshold to {thresholds['width']}"
                    )
                elif max_exclusions == stats.excluded_by_distance:
                    thresholds["distance"] = max(
                        1, int(thresholds["distance"] * (1 - relaxation))
                    )
                    self.logger.info(
                        f"Relaxing distance threshold to {thresholds['distance']}"
                    )

                iteration += 1
                continue

            # If peaks were found, create Peak objects
            peaks = []
            for i, idx in enumerate(peak_indices):
                peak = Peak(
                    start_time=float(
                        chrom.times[int(peak_properties["left_bases"][i])]
                    ),
                    apex_time=float(chrom.times[idx]),
                    end_time=float(chrom.times[int(peak_properties["right_bases"][i])]),
                    start_intensity=float(
                        chrom.intensities[int(peak_properties["left_bases"][i])]
                    ),
                    apex_intensity=float(chrom.intensities[idx]),
                    end_intensity=float(
                        chrom.intensities[int(peak_properties["right_bases"][i])]
                    ),
                    properties={
                        "height": float(peak_properties["peak_heights"][i]),
                        "prominence": float(peak_properties["prominences"][i]),
                        "width": float(peak_properties["widths"][i]),
                        "width_height": float(peak_properties["width_heights"][i]),
                    },
                )
                peaks.append(peak)
            break

        # Update final statistics
        stats.final_thresholds = thresholds
        stats.iterations = iteration + 1

        # Store statistics in chromatogram properties
        chrom.properties["peak_detection_stats"] = stats

        # Update chromatogram with peaks
        chrom.peaks = peaks
        peak_times = [peak.apex_time for peak in peaks]
        self.logger.info(f"Found {len(peaks)} peaks at times: {peak_times}")
        self.logger.info(
            f"Peak detection completed after {stats.iterations} iterations"
        )
        if stats.iterations > 1:
            self.logger.info(
                f"Thresholds were adjusted from {stats.initial_thresholds} to {stats.final_thresholds}"
            )

        return chrom

    def process_peptide(self, input_data: SinglePeptideInput) -> SinglePeptideInput:
        """Process a single peptide."""
        self.logger.info(
            f"Detecting peaks for peptide: {input_data.peptide.sequence_str}"
        )
        for encoding in input_data.peptide.encodings:
            if encoding.chromatogram is not None:
                encoding.chromatogram = self.find_peaks(encoding.chromatogram)
        return input_data

    def process_peptide_set(self, input_data: PeptideSetInput) -> PeptideSetInput:
        """Process a set of peptides."""
        self.logger.info(
            f"Detecting peaks for peptide set: {len(input_data.peptides)} peptides"
        )
        for peptide in input_data.peptides:
            for encoding in peptide.encodings:
                if encoding.chromatogram is not None:
                    encoding.chromatogram = self.find_peaks(encoding.chromatogram)
        return input_data

    def process_hierarchy(
        self, input_data: PeptideHierarchyInput
    ) -> PeptideHierarchyInput:
        """Process a hierarchy of peptides.

        Processes each node in the hierarchy, starting with the longest peptides
        and working down to shorter ones to ensure proper peak detection order.
        """
        self.logger.info(f"Detecting peaks for peptide hierarchy")

        # Process nodes layer by layer, starting with the highest layer
        hierarchy = input_data.hierarchy
        max_layer = max(hierarchy.layers.keys())

        for layer in range(max_layer, 0, -1):  # Process from highest to lowest layer
            nodes = hierarchy.get_layer(layer)
            for node in nodes:
                # Process all encodings for this node
                for encoding in node.encodings:
                    if encoding.chromatogram is not None:
                        encoding.chromatogram = self.find_peaks(encoding.chromatogram)

                # Process equivalent encodings if they exist
                equivalent_nodes = hierarchy.get_equivalent_encodings(node)
                for equiv_node in equivalent_nodes:
                    for encoding in equiv_node.encodings:
                        if encoding.chromatogram is not None:
                            encoding.chromatogram = self.find_peaks(
                                encoding.chromatogram
                            )

        return input_data

    def _calculate_height_threshold(self, chrom: Chromatogram) -> float:
        """Calculate adaptive height threshold."""
        baseline_mean = chrom.properties.get("baseline_mean", 0)
        noise_level = chrom.properties.get("noise_level", 0)
        snr = chrom.properties.get("signal_to_noise", self.config.min_snr_factor)

        snr_factor = max(
            self.config.min_snr_factor,
            min(snr * self.config.snr_scale, self.config.max_snr_factor),
        )
        return baseline_mean + (noise_level * snr_factor)

    def _calculate_prominence_threshold(self, chrom: Chromatogram) -> float:
        """Calculate adaptive prominence threshold."""
        noise_level = chrom.properties.get("noise_level", 0)
        dynamic_range = chrom.properties.get("dynamic_range", 0)

        noise_based = noise_level * self.config.noise_prominence_factor
        range_based = dynamic_range * self.config.min_prominence_ratio
        return max(noise_based, range_based)

    def _calculate_width_threshold(self, chrom: Chromatogram) -> float:
        """Calculate adaptive width threshold."""
        sampling_rate = (chrom.times[-1] - chrom.times[0]) / len(chrom.times)
        roughness = chrom.properties.get(
            "baseline_roughness", self.config.min_roughness_factor
        )

        roughness_factor = max(
            self.config.min_roughness_factor,
            min(
                roughness * self.config.roughness_scale,
                self.config.max_roughness_factor,
            ),
        )
        return roughness_factor * sampling_rate

    def _calculate_distance_threshold(self, chrom: Chromatogram) -> int:
        """Calculate minimum distance between peaks."""
        width_threshold = self._calculate_width_threshold(chrom)
        return int(width_threshold * self.config.peak_separation_factor)

    def _calculate_window_length(self, chrom: Chromatogram) -> int:
        """Calculate window length for peak property calculations."""
        sampling_rate = (chrom.times[-1] - chrom.times[0]) / len(chrom.times)
        roughness = chrom.properties.get(
            "baseline_roughness", self.config.min_window_roughness_factor
        )

        roughness_factor = max(
            self.config.min_window_roughness_factor,
            min(
                roughness * self.config.window_roughness_scale,
                self.config.max_window_roughness_factor,
            ),
        )
        window_length = max(
            int(roughness_factor / sampling_rate), self.config.min_window_points
        )
        return window_length
