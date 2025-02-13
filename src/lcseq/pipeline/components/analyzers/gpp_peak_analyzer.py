# src/lcseq/pipeline/components/analyzers/gpp_peak_analyzer.py
"""
This module provides a pipeline component for analyzing GPP peaks in peptide chromatograms.
It includes a configuration class for specifying Gaussian fitting parameters and an analyzer
class for performing the analysis.

Classes:
    GPPPeakAnalyzerConfig: Configuration for Gaussian fitting parameters.
    GPPPeakAnalyzer: Analyzer for performing Gaussian peak fitting.
"""

# Standard library imports
import logging
from dataclasses import dataclass
from typing import List

import numpy as np
from scipy.optimize import curve_fit

# Local application imports
from src.lcseq.core.chromatogram import Chromatogram, Peak
from src.lcseq.pipeline.base import PipelineComponent
from src.lcseq.pipeline.input_types import (
    PeptideHierarchyInput,
    PeptideSetInput,
    SinglePeptideInput,
)
from src.lcseq.core.hierarchy import PeptideHierarchyNode

logger: logging.Logger = logging.getLogger(__name__)


@dataclass
class GPPPeakAnalyzerConfig:
    """Configuration for Gaussian fitting parameters.

    Attributes:
        min_std (float): Minimum standard deviation to avoid division by zero.
    """

    min_std: float = 1e-6  # Minimum standard deviation to avoid division by zero


class GPPPeakAnalyzer(PipelineComponent):
    """GPPPeakAnalyzer class for analyzing GPP peaks in peptide chromatograms.

    Attributes:
        config (GPPPeakAnalyzerConfig): Configuration for Gaussian fitting parameters.
        logger (logging.Logger): Logger for logging messages.

    Methods:
        __init__: Initialize the GPPPeakAnalyzer.
        _gaussian: Calculate Gaussian function values.
        analyze_peak: Analyze a single peak and fit a Gaussian to the corrected intensities.
        process_peptide: Analyze peaks for a single peptide
        process_peptide_set: Analyze peaks for a set of peptides
        process_hierarchy: Analyze peaks for a hierarchy of peptides
    """

    def __init__(self, config: GPPPeakAnalyzerConfig = None):  # type: ignore
        """Initialize the GPPPeakAnalyzer.

        Args:
            config (GPPPeakAnalyzerConfig, optional): Configuration for Gaussian fitting parameters.
                Default is None, which uses the default configuration.
        """
        self.config: GPPPeakAnalyzerConfig = config or GPPPeakAnalyzerConfig()
        self.logger: logging.Logger = logging.getLogger(__name__)

    @staticmethod
    def _gaussian(
        x: np.ndarray, amplitude: float, mean: float, std: float
    ) -> np.ndarray:
        """Calculate Gaussian function values.

        Args:
            x (np.ndarray): The x-values to evaluate the Gaussian function at.
            amplitude (float): The amplitude of the Gaussian function.
            mean (float): The mean of the Gaussian function.
            std (float): The standard deviation of the Gaussian function.

        Returns:
            np.ndarray: The values of the Gaussian function at the given x-values.
        """
        std = max(std, 1e-6)  # Ensure std is not zero
        return amplitude * np.exp(-((x - mean) ** 2) / (2 * std**2))

    def analyze_peak(self, peak: Peak, chrom: Chromatogram) -> Peak:
        """Analyze a single peak and fit a Gaussian to the corrected intensities.

        Args:
            peak (Peak): The peak to analyze.
            chrom (Chromatogram): The chromatogram containing the peak.

        Returns:
            Peak: The peak with the corrected Gaussian fit parameters.
        """
        try:
            peak_slice = slice(
                np.searchsorted(chrom.times, peak.start_time),
                np.searchsorted(chrom.times, peak.end_time) + 1,
            )
            times: np.ndarray = chrom.times[peak_slice]
            corrected_intensities: np.ndarray = chrom.properties.get(
                "corrected_intensities", chrom.intensities[peak_slice]
            )

            # Check if corrected_intensities are properly assigned
            if corrected_intensities is None or len(corrected_intensities) == 0:
                self.logger.error("Corrected intensities are not properly assigned.")
                raise ValueError("Corrected intensities are missing or empty.")

            # Improved Gaussian fitting
            try:
                window_extension: float = (
                    peak.end_time - peak.start_time
                )  # Extend by one peak width on each side
                extended_start: float = max(
                    peak.start_time - window_extension, chrom.times[0]
                )
                extended_end: float = min(
                    peak.end_time + window_extension, chrom.times[-1]
                )

                fit_slice = slice(
                    np.searchsorted(chrom.times, extended_start),
                    np.searchsorted(chrom.times, extended_end) + 1,
                )
                fit_times: np.ndarray = chrom.times[fit_slice]
                fit_intensities: np.ndarray = chrom.properties.get(
                    "corrected_intensities", chrom.intensities
                )[fit_slice]

                p0: List[float] = [
                    peak.apex_intensity,  # Amplitude
                    peak.apex_time,  # Mean
                    max(
                        (peak.end_time - peak.start_time) / 2.355, self.config.min_std
                    ),  # Sigma (FWHM/2.355)
                ]

                lower_bounds: List[float] = [
                    peak.apex_intensity * 0.5,  # Amplitude lower bound
                    peak.start_time,  # Mean lower bound
                    self.config.min_std,  # Sigma lower bound
                ]
                upper_bounds: List[float] = [
                    peak.apex_intensity * 1.5,  # Amplitude upper bound
                    peak.end_time,  # Mean upper bound
                    peak.end_time - peak.start_time,  # Sigma upper bound
                ]

                popt, _ = curve_fit(
                    self._gaussian,
                    fit_times,
                    fit_intensities,
                    p0=p0,
                    bounds=(lower_bounds, upper_bounds),
                    maxfev=1000,  # Increase max iterations
                )

                gaussian_residuals: float = (
                    np.sqrt(
                        np.mean(
                            (corrected_intensities - self._gaussian(times, *popt)) ** 2
                        )
                    )
                    / peak.apex_intensity
                )

            except (RuntimeError, ValueError) as e:
                self.logger.warning(f"Gaussian fitting failed: {str(e)}")
                gaussian_residuals: float = 1.0
                popt: List[float] = [0, 0, 0]

            self.logger.info(f"Found Gaussian fit parameters: {popt} for peak {peak}")

            # Update peak properties with corrected values
            peak.properties.update(
                {
                    "corrected_gaussian_residuals": gaussian_residuals,
                    "corrected_gaussian_fit_params": {
                        "amplitude": float(popt[0]),
                        "mean": float(popt[1]),
                        "sigma": float(popt[2]),
                    },
                }
            )

        except Exception as e:
            self.logger.error(f"Failed to analyze peak: {str(e)}")
            peak.properties["corrected_analysis_error"] = str(e)

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

        def process_node(node: PeptideHierarchyNode) -> None:
            """Process a single node in the hierarchy.

            Args:
                node (PeptideHierarchyNode): The node to process.
            """
            for encoding in node.peptide.encodings:
                if encoding.chromatogram is not None and encoding.chromatogram.peaks:
                    for i, peak in enumerate(encoding.chromatogram.peaks):
                        encoding.chromatogram.peaks[i] = self.analyze_peak(
                            peak, encoding.chromatogram
                        )
            for extension in node.extension_edges:
                process_node(extension)

        self.logger.info("Analyzing peaks for peptide hierarchy")
        for node in input_data.hierarchy.layers[1]:
            process_node(node)
        return input_data
