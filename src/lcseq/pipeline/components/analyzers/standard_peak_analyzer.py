# src/lcseq/pipeline/components/standard_peak_analyzer.py
"""
This module provides a pipeline component for analyzing standard peaks in peptide chromatograms.
It includes a configuration class for specifying analysis parameters and an analyzer
class for performing the analysis.

Classes:
    StandardPeakAnalyzerConfig: Configuration for peak analysis parameters.
    StandardPeakAnalyzer: Analyzer for performing the StandardPeakAnalysis.
"""

# Standard library imports
import logging
from dataclasses import dataclass, field
from typing import Dict, List

import numpy as np
from scipy.optimize import curve_fit
from scipy.signal import peak_widths
from src.lcseq.core.chromatogram import Chromatogram, Peak
# Local application imports
from src.lcseq.pipeline.base import PipelineComponent
from src.lcseq.pipeline.input_types import (PeptideHierarchyInput,
                                            PeptideSetInput,
                                            SinglePeptideInput)

logger: logging.Logger = logging.getLogger(__name__)


@dataclass
class StandardPeakAnalyzerConfig:
    """Configuration for peak analysis parameters.

    Attributes:
        threshold (float): The threshold for peak detection.
        min_prominence (float): The minimum prominence for peak detection.
        min_width (float): The minimum width for peak detection.
        max_width (float): The maximum width for peak detection.
        min_resolution (float): The minimum resolution for peak detection.
        min_symmetry (float): The minimum symmetry for peak detection.
    """

    threshold: float = 0.5
    min_prominence: float = 0.1
    min_width: float = 0.1
    max_width: float = 10.0
    min_resolution: float = 1.0
    min_symmetry: float = 0.5


class StandardPeakAnalyzer(PipelineComponent):
    """Pipeline component for analyzing standard peaks in peptide chromatograms.

    Methods:
        process_peptide: Process a single peptide's chromatogram
        process_peptide_set: Process a set of peptides' chromatograms
        process_hierarchy: Process a hierarchy of peptides' chromatograms
    """

    def __init__(self, config: StandardPeakAnalyzerConfig = None) -> None:  # type: ignore
        self.config: StandardPeakAnalyzerConfig = config or StandardPeakAnalyzerConfig()
        self.logger: logging.Logger = logging.getLogger(__name__)

    @staticmethod
    def _gaussian(
        x: np.ndarray, amplitude: float, mean: float, std: float
    ) -> np.ndarray:
        """Calculate Gaussian function values."""
        return amplitude * np.exp(-((x - mean) ** 2) / (2 * std**2))

    def analyze_peak(self, peak: Peak, chrom: Chromatogram) -> Peak:
        """Analyze a single peak and calculate its characteristics.

        Args:
            peak (Peak): The peak to analyze.
            chrom (Chromatogram): The chromatogram to analyze.

        Returns:
            Peak: The analyzed peak.
        """
        try:
            peak_slice = slice(
                np.searchsorted(chrom.times, peak.start_time),
                np.searchsorted(chrom.times, peak.end_time) + 1,
            )
            times = chrom.times[peak_slice]
            intensities = chrom.intensities[peak_slice]

            # Calculate peak width at half maximum
            half_max = (peak.apex_intensity + peak.start_intensity) / 2
            width_indices = np.where(intensities >= half_max)[0]
            if len(width_indices) >= 2:
                width = times[width_indices[-1]] - times[width_indices[0]]
            else:
                width = peak.end_time - peak.start_time

            # Calculate area using trapezoidal rule
            area = np.trapezoid(intensities, times)

            # Calculate symmetry
            apex_idx = np.searchsorted(times, peak.apex_time)
            left = intensities[: apex_idx + 1]
            right = intensities[apex_idx:][::-1]
            min_len = min(len(left), len(right))
            symmetry = 1 - np.mean(
                np.abs(left[-min_len:] - right[-min_len:]) / peak.apex_intensity
            )

            # Improved Gaussian fitting
            try:
                # Use a wider window for fitting
                window_extension = width  # Extend by one peak width on each side
                extended_start = max(peak.start_time - window_extension, chrom.times[0])
                extended_end = min(peak.end_time + window_extension, chrom.times[-1])

                fit_slice = slice(
                    np.searchsorted(chrom.times, extended_start),
                    np.searchsorted(chrom.times, extended_end) + 1,
                )
                fit_times = chrom.times[fit_slice]
                fit_intensities = chrom.intensities[fit_slice]

                # Better initial parameter estimates
                p0 = [
                    peak.apex_intensity,  # Amplitude
                    peak.apex_time,  # Mean
                    width / 2.355,  # Sigma (FWHM/2.355)
                ]

                # Add bounds to constrain the fit
                lower_bounds = [
                    peak.apex_intensity * 0.5,  # Amplitude lower bound
                    peak.start_time,  # Mean lower bound
                    width / 4,  # Sigma lower bound
                ]
                upper_bounds = [
                    peak.apex_intensity * 1.5,  # Amplitude upper bound
                    peak.end_time,  # Mean upper bound
                    width,  # Sigma upper bound
                ]

                # Perform fit with bounds and better initial guesses
                popt, _ = curve_fit(
                    self._gaussian,
                    fit_times,
                    fit_intensities,
                    p0=p0,
                    bounds=(lower_bounds, upper_bounds),
                    maxfev=1000,  # Increase max iterations
                )

                # Calculate residuals using the original peak region
                gaussian_residuals = (
                    np.sqrt(np.mean((intensities - self._gaussian(times, *popt)) ** 2))
                    / peak.apex_intensity
                )

            except (RuntimeError, ValueError) as e:
                self.logger.warning(f"Gaussian fitting failed: {str(e)}")
                gaussian_residuals = 1.0
                popt = [0, 0, 0]

            # Update peak properties
            peak.properties.update(
                {
                    "width": width,
                    "area": area,
                    "symmetry": symmetry,
                    "gaussian_residuals": gaussian_residuals,
                    "gaussian_fit_params": {
                        "amplitude": float(popt[0]),
                        "mean": float(popt[1]),
                        "sigma": float(popt[2]),
                    },
                }
            )

        except Exception as e:
            self.logger.error(f"Failed to analyze peak: {str(e)}")
            peak.properties["analysis_error"] = str(e)

        return peak

    def process_peptide(self, input_data: SinglePeptideInput) -> SinglePeptideInput:
        """Analyze peaks for a single peptide.

        Args:
            input_data (SinglePeptideInput): The input data representing a single
                peptide.

        Returns:
            SinglePeptideInput: The input data with the peaks analyzed.
        """
        self.logger.info(
            f"Analyzing peaks for peptide: {input_data.peptide.sequence_str}"
        )
        for encoding in input_data.peptide.encodings:
            if encoding.chromatogram is not None and encoding.chromatogram.peaks:
                for i, peak in enumerate(encoding.chromatogram.peaks):
                    encoding.chromatogram.peaks[i] = self.analyze_peak(
                        peak, encoding.chromatogram
                    )
        return input_data

    def process_peptide_set(self, input_data: PeptideSetInput) -> PeptideSetInput:
        """Analyze peaks for a set of peptides.

        Args:
            input_data (PeptideSetInput): The input data representing a set of
                peptides.

        Returns:
            PeptideSetInput: The input data with the peaks analyzed.
        """
        self.logger.info(
            f"Analyzing peaks for peptide set: {len(input_data.peptides)} peptides"
        )
        for peptide in input_data.peptides:
            for encoding in peptide.encodings:
                if encoding.chromatogram is not None and encoding.chromatogram.peaks:
                    for i, peak in enumerate(encoding.chromatogram.peaks):
                        encoding.chromatogram.peaks[i] = self.analyze_peak(
                            peak, encoding.chromatogram
                        )
        return input_data

    def process_hierarchy(
        self, input_data: PeptideHierarchyInput
    ) -> PeptideHierarchyInput:
        """Analyze peaks for a hierarchy of peptides.

        Args:
            input_data (PeptideHierarchyInput): The input data representing a hierarchy
                of peptides.

        Returns:
            PeptideHierarchyInput: The input data with the peaks analyzed.
        """

        def process_node(node):
            for encoding in node.root.encodings:
                if encoding.chromatogram is not None and encoding.chromatogram.peaks:
                    for i, peak in enumerate(encoding.chromatogram.peaks):
                        encoding.chromatogram.peaks[i] = self.analyze_peak(
                            peak, encoding.chromatogram
                        )
            for child in node.children:
                process_node(child)

        self.logger.info(f"Analyzing peaks for peptide hierarchy")
        process_node(input_data.hierarchy)
        return input_data
