# src/lcseq/pipeline/components/correctors/aals_chromatogram_corrector.py
"""
This module defines the AALSChromatogramCorrector class, which is a pipeline component
for correcting chromatograms using the Asymmetric Least Squares (AALS) baseline correction
algorithm.

Classes:
    AALSChromatogramCorrectorConfig: Configuration for the AALS baseline correction.
    AALSChromatogramCorrector: A pipeline component for correcting chromatograms using AALS.
"""

# Standard library imports
import logging
from dataclasses import dataclass, field

import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve
from src.lcseq.core.chromatogram import Chromatogram
# Local application imports
from src.lcseq.pipeline.base import PipelineComponent
from src.lcseq.pipeline.input_types import (PeptideHierarchyInput,
                                            PeptideSetInput,
                                            SinglePeptideInput)

logger: logging.Logger = logging.getLogger(__name__)


@dataclass
class AALSChromatogramCorrectorConfig:
    """Configuration for the AALS baseline correction.

    Attributes:
        lambda_value (float): The lambda value for the AALS baseline correction.
        p_value (float): The p value for the AALS baseline correction.
        max_iterations (int): The maximum number of iterations for the AALS baseline correction.
    """

    lambda_value: float = 1e4
    p_value: float = 0.001
    max_iterations: int = 10


class AALSChromatogramCorrector(PipelineComponent):
    """AALSChromatogramCorrector class for correcting chromatograms using the Asymmetric Least Squares (AALS)
    baseline correction algorithm.

    This class inherits from the PipelineComponent class and provides methods to process and correct
    chromatograms for single peptides, sets of peptides, and peptide hierarchies.

    Attributes:
        config (AALSChromatogramCorrectorConfig): Configuration for the AALS baseline correction.
        logger (logging.Logger): Logger for logging messages.

    Methods:
        __init__: Initialize the AALSChromatogramCorrector.
        _correct_chromatogram: Apply AALS baseline correction to a single chromatogram.
        process_peptide: Process and correct a single peptide.
        process_peptide_set: Process and correct a set of peptides.
        process_hierarchy: Process and correct a peptide hierarchy.
    """

    def __init__(self, config: AALSChromatogramCorrectorConfig = None) -> None:  # type: ignore
        """
        Initializes the AALSChromatogramCorrector with the provided configuration.

        Args:
            config (AALSChromatogramCorrectorConfig, optional): Configuration for the AALS baseline correction.
                Default is None, which uses the default configuration.
        """
        self.config: AALSChromatogramCorrectorConfig = (
            config or AALSChromatogramCorrectorConfig()
        )
        self.logger: logging.Logger = logging.getLogger(__name__)

    def _correct_chromatogram(self, chrom: Chromatogram) -> Chromatogram:
        """Apply AALS baseline correction to a single chromatogram.

        Args:
            chrom (Chromatogram): The chromatogram to correct.

        Returns:
            Chromatogram: The corrected chromatogram.
        """
        y: np.ndarray = chrom.intensities
        length: int = len(y)
        diff_matrix: sparse.csr_matrix = sparse.diags(
            [1, -2, 1], [0, 1, 2], shape=(length, length)  # type: ignore
        )
        weights: np.ndarray = np.ones(length)
        baseline: np.ndarray = np.ones(length)

        for _ in range(self.config.max_iterations):
            weight_matrix: sparse.csr_matrix = sparse.spdiags(
                weights, 0, length, length  # type: ignore  # noqa: F821
            )
            z_matrix: np.ndarray = (
                weight_matrix
                + self.config.lambda_value * diff_matrix.T.dot(diff_matrix)
            )
            baseline: np.ndarray = spsolve(z_matrix, weights * y)
            weights: np.ndarray = self.config.p_value * (y > baseline) + (
                1 - self.config.p_value
            ) * (y <= baseline)

        corrected_intensities: np.ndarray = np.maximum(
            y - baseline, 0
        )  # Ensure non-negative values

        chrom.properties["corrected_intensities"] = corrected_intensities
        chrom.properties["baseline"] = baseline

        return chrom

    def process_peptide(self, input_data: SinglePeptideInput) -> SinglePeptideInput:
        """
        Correct the chromatogram for a single peptide.

        Args:
            input_data (SinglePeptideInput): The input data representing a single peptide.

        Returns:
            SinglePeptideInput: The corrected single peptide input.
        """
        self.logger.info(
            f"Correcting chromatogram for peptide: {input_data.peptide.sequence_str}"
        )
        for encoding in input_data.peptide.encodings:
            if encoding.chromatogram is not None:
                encoding.chromatogram = self._correct_chromatogram(
                    encoding.chromatogram
                )
                self.logger.info(
                    f"Chromatogram corrected for {encoding}: {encoding.chromatogram.properties}"
                )
        return input_data

    def process_peptide_set(self, input_data: PeptideSetInput) -> PeptideSetInput:
        """
        Correct chromatograms for a set of peptides.

        Args:
            input_data (PeptideSetInput): The input data representing a set of peptides.

        Returns:
            PeptideSetInput: The corrected set of peptides.
        """
        self.logger.info(
            f"Correcting chromatograms for peptide set: {len(input_data.peptides)} peptides"
        )
        for peptide in input_data.peptides:
            for encoding in peptide.encodings:
                if encoding.chromatogram is not None:
                    encoding.chromatogram = self._correct_chromatogram(
                        encoding.chromatogram
                    )
        return input_data

    def process_hierarchy(
        self, input_data: PeptideHierarchyInput
    ) -> PeptideHierarchyInput:
        """
        Correct chromatograms in a peptide hierarchy.

        Args:
            input_data (PeptideHierarchyInput): The input data representing a hierarchy of peptides.

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
