# src/lcseq/pipeline/components/standard_chromatogram_analyzer.py
"""
This module provides a pipeline component for analyzing standard chromatograms.
It includes a configuration class for specifying analysis parameters and an analyzer
class for performing the analysis.

Classes:
    StandardChromatogramAnalyzerConfig: Configuration for the StandardChromatogramAnalyzer.
    StandardChromatogramAnalyzer: Analyzer for performing the StandardChromatogramAnalysis.
"""

import logging
# Standard library imports
from dataclasses import dataclass, field
from typing import List, Tuple

import numpy as np
from scipy import signal, stats
from src.lcseq.core.chromatogram import Chromatogram, Peak
# Local application imports
from src.lcseq.pipeline.base import PipelineComponent
from src.lcseq.pipeline.input_types import (PeptideHierarchyInput,
                                            PeptideSetInput,
                                            SinglePeptideInput)

logger: logging.Logger = logging.getLogger(__name__)


@dataclass
class StandardChromatogramAnalyzerConfig:
    """Configuration for the StandardChromatogramAnalyzer.

    Attributes:
        window_width (int): The width of the moving window for calculating standard deviation.
        window_overlap (float): The overlap between windows.
        min_window_points (int): The minimum number of points in a window.
        variation_threshold (float): The threshold for minimal variation.
        min_region_width (int): The minimum width of a region of minimal variation.
        max_region_gap (int): The maximum gap between regions of minimal variation.
        noise_percentile (float): The percentile for noise calculation.
        min_regions_required (int): The minimum number of regions required for noise calculation.
        max_noise_variance (float): The maximum variance for noise calculation.
        edge_exclusion (float): The edge exclusion for noise calculation.
        baseline_percentile (float): The percentile for baseline calculation.
        drift_window (int): The window for drift calculation.
        smoothing_window (int): The window for smoothing the chromatogram.
        outlier_threshold (float): The threshold for outlier detection.
    """

    window_width: int = 15
    window_overlap: float = 0.5
    min_window_points: int = 5
    variation_threshold: float = 1.5
    min_region_width: int = 5
    max_region_gap: int = 20
    noise_percentile: float = 50.0
    min_regions_required: int = 3
    max_noise_variance: float = 2.0
    edge_exclusion: float = 0.05
    baseline_percentile: float = 10.0
    drift_window: int = 100
    smoothing_window: int = 5
    outlier_threshold: float = 3.0


class StandardChromatogramAnalyzer(PipelineComponent):
    """Pipeline component for analyzing standard chromatograms.

    Methods:
        process_peptide: Process a single peptide's chromatogram
        process_peptide_set: Process a set of peptides' chromatograms
        process_hierarchy: Process a hierarchy of peptides' chromatograms
    """

    def __init__(self, config: StandardChromatogramAnalyzerConfig = None):  # type: ignore
        self.config = config or StandardChromatogramAnalyzerConfig()
        self.logger: logging.Logger = logging.getLogger(__name__)

    def _analyze_single_chromatogram(self, chrom: Chromatogram) -> Chromatogram:
        """Core analysis logic for a single chromatogram

        Args:
            chrom (Chromatogram): The chromatogram to analyze.

        Returns:
            Chromatogram: The analyzed chromatogram.
        """
        try:
            self._validate_chromatogram(chrom)
            chrom.properties["times_count"] = len(chrom.times)
            chrom.properties["intensities_count"] = len(chrom.intensities)
            chrom.properties["scaled_intensities_count"] = len(chrom.intensities)
            chrom.properties["duration"] = float(chrom.times[-1] - chrom.times[0])
            self._calculate_noise_metrics(chrom)
            self._calculate_baseline_metrics(chrom)
            self._calculate_area_metrics(chrom)
            self._calculate_distribution_metrics(chrom)
            self._calculate_quality_metrics(chrom)
        except Exception as e:
            self.logger.error(f"Analysis failed: {str(e)}")
            raise

        return chrom

    def process_peptide(self, input_data: SinglePeptideInput) -> SinglePeptideInput:
        """Process a single peptide's chromatogram.

        Args:
            input_data (SinglePeptideInput): The input data representing a single
                peptide.

        Returns:
            SinglePeptideInput: The input data with the chromatogram analyzed.
        """
        self.logger.info(
            f"Analyzing chromatogram for peptide: {input_data.peptide.sequence_str}"
        )
        for encoding in input_data.peptide.encodings:
            if encoding.chromatogram is not None:
                encoding.chromatogram = self._analyze_single_chromatogram(
                    encoding.chromatogram
                )
                self.logger.info(
                    f"Chromatogram metrics for {encoding}: {encoding.chromatogram.properties}"
                )
        return input_data

    def process_peptide_set(self, input_data: PeptideSetInput) -> PeptideSetInput:
        """Process chromatograms for a set of peptides.

        Args:
            input_data (PeptideSetInput): The input data representing a set of
                peptides.

        Returns:
            PeptideSetInput: The input data with the chromatograms analyzed.
        """
        self.logger.info(
            f"Analyzing chromatograms for peptide set: {len(input_data.peptides)} peptides"
        )
        for peptide in input_data.peptides:
            for encoding in peptide.encodings:
                if encoding.chromatogram is not None:
                    encoding.chromatogram = self._analyze_single_chromatogram(
                        encoding.chromatogram
                    )
        return input_data

    def process_hierarchy(
        self, input_data: PeptideHierarchyInput
    ) -> PeptideHierarchyInput:
        """Process chromatograms in a peptide hierarchy.

        Args:
            input_data (PeptideHierarchyInput): The input data representing a hierarchy
                of peptides.

        Returns:
            PeptideHierarchyInput: The input data with the chromatograms analyzed.
        """

        def process_node(node):
            for encoding in node.root.encodings:
                if encoding.chromatogram is not None:
                    encoding.chromatogram = self._analyze_single_chromatogram(
                        encoding.chromatogram
                    )
            for child in node.children:
                process_node(child)

        self.logger.info(f"Analyzing chromatograms for peptide hierarchy")
        process_node(input_data.hierarchy)
        return input_data

    def _validate_chromatogram(self, chrom: Chromatogram) -> None:
        """Validate chromatogram data.

        Args:
            chrom (Chromatogram): The chromatogram to validate.

        Raises:
            ValueError: If the chromatogram is invalid.
        """
        if chrom.times is None or chrom.intensities is None:
            raise ValueError("Chromatogram contains no signal data")

        if not isinstance(chrom.times, np.ndarray) or not isinstance(
            chrom.intensities, np.ndarray
        ):
            raise ValueError("Chromatogram signals must be numpy arrays")

        if len(chrom.times) == 0 or len(chrom.intensities) == 0:
            raise ValueError("Chromatogram signals are empty")

        if len(chrom.times) != len(chrom.intensities):
            raise ValueError("Times and intensities must have same length")

        if not np.all(np.isfinite(chrom.times)) or not np.all(
            np.isfinite(chrom.intensities)
        ):
            raise ValueError("Chromatogram signals contain NaN or infinite values")

    def _calculate_moving_std(self, intensity: np.ndarray) -> np.ndarray:
        """Calculate moving standard deviation.

        Args:
            intensity (np.ndarray): The intensity data.

        Returns:
            np.ndarray: The moving standard deviation.
        """
        pad_width = self.config.window_width // 2
        intensity_padded = np.pad(intensity, pad_width, mode="edge")
        window = np.ones(self.config.window_width) / self.config.window_width
        moving_mean = signal.convolve(intensity_padded, window, mode="valid")
        intensity_squared = intensity_padded**2
        moving_mean_squared = signal.convolve(intensity_squared, window, mode="valid")
        moving_var = np.maximum(moving_mean_squared - moving_mean**2, 0)
        return np.sqrt(moving_var)

    def _find_minimal_variation_regions(
        self, moving_std: np.ndarray
    ) -> List[Tuple[int, int]]:
        """Find regions of minimal variation.

        Args:
            moving_std (np.ndarray): The moving standard deviation.

        Returns:
            List[Tuple[int, int]]: The regions of minimal variation.
        """
        min_std = np.min(moving_std)
        threshold = min_std * self.config.variation_threshold
        start_idx = int(len(moving_std) * self.config.edge_exclusion)
        end_idx = len(moving_std) - start_idx

        below_threshold = moving_std[start_idx:end_idx] < threshold
        regions = []
        current_start = None

        for i, is_quiet in enumerate(below_threshold, start=start_idx):
            if is_quiet and current_start is None:
                current_start = i
            elif not is_quiet and current_start is not None:
                if i - current_start >= self.config.min_region_width:
                    regions.append((current_start, i))
                current_start = None

        if (
            current_start is not None
            and end_idx - current_start >= self.config.min_region_width
        ):
            regions.append((current_start, end_idx))

        return self._merge_regions(regions)

    def _merge_regions(self, regions: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """Merge nearby regions.

        Args:
            regions (List[Tuple[int, int]]): The regions to merge.

        Returns:
            List[Tuple[int, int]]: The merged regions.
        """
        if not regions:
            return []

        merged = []
        current_start, current_end = regions[0]

        for start, end in regions[1:]:
            if start - current_end <= self.config.max_region_gap:
                current_end = end
            else:
                merged.append((current_start, current_end))
                current_start, current_end = start, end

        merged.append((current_start, current_end))
        return merged

    def _calculate_noise_metrics(self, chrom: Chromatogram) -> None:
        """Calculate noise-related metrics.

        Args:
            chrom (Chromatogram): The chromatogram to analyze.
        """
        moving_std = self._calculate_moving_std(chrom.intensities)
        quiet_regions = self._find_minimal_variation_regions(moving_std)

        if len(quiet_regions) < self.config.min_regions_required:
            noise_level = float(np.std(chrom.intensities))
        else:
            quiet_stds = []
            for start, end in quiet_regions:
                quiet_stds.extend(moving_std[start:end])
            noise_level = float(np.percentile(quiet_stds, self.config.noise_percentile))

        signal_range = float(np.max(chrom.intensities) - np.min(chrom.intensities))
        snr = float("inf") if noise_level == 0 else signal_range / noise_level

        chrom.properties["noise_level"] = noise_level
        chrom.properties["signal_to_noise"] = snr
        chrom.properties["quiet_regions"] = quiet_regions

    def _calculate_baseline_metrics(self, chrom: Chromatogram) -> None:
        """Calculate baseline-related metrics.

        Args:
            chrom (Chromatogram): The chromatogram to analyze.
        """
        baseline_mean = float(
            np.percentile(chrom.intensities, self.config.baseline_percentile)
        )
        try:
            coefficients = np.polyfit(chrom.times, chrom.intensities, 1)
            drift = float(coefficients[0])
        except np.exceptions.RankWarning:
            drift = float(np.nan)

        chrom.properties["baseline_mean"] = baseline_mean
        chrom.properties["baseline_drift"] = drift

    def _calculate_area_metrics(self, chrom: Chromatogram) -> None:
        """Calculate area-related metrics.

        Args:
            chrom (Chromatogram): The chromatogram to analyze.
        """
        zeros = np.zeros_like(chrom.intensities)
        positive_y = np.where(chrom.intensities > zeros, chrom.intensities, zeros)
        negative_y = np.where(chrom.intensities < zeros, chrom.intensities, zeros)

        total_area = float(np.trapezoid(chrom.intensities, chrom.times))
        positive_area = float(np.trapezoid(positive_y, chrom.times))
        negative_area = float(np.trapezoid(negative_y, chrom.times))

        chrom.properties["total_area"] = total_area
        chrom.properties["positive_area"] = positive_area
        chrom.properties["negative_area"] = negative_area

    def _calculate_distribution_metrics(self, chrom: Chromatogram) -> None:
        """Calculate distribution-related metrics.

        Args:
            chrom (Chromatogram): The chromatogram to analyze.
        """
        chrom.properties.update(
            {
                "skewness": float(stats.skew(chrom.intensities)),
                "kurtosis": float(stats.kurtosis(chrom.intensities)),
                "dynamic_range": float(
                    np.max(chrom.intensities) - np.min(chrom.intensities)
                ),
            }
        )

    def _calculate_quality_metrics(self, chrom: Chromatogram) -> None:
        """Calculate quality-related metrics.

        Args:
            chrom (Chromatogram): The chromatogram to analyze.
        """
        chrom.properties.update(
            {
                "signal_smoothness": float(np.mean(np.abs(np.diff(chrom.intensities)))),
                "baseline_roughness": float(np.std(np.diff(chrom.intensities))),
            }
        )
