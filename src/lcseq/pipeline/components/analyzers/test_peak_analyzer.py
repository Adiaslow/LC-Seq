# src/lcseq/pipeline/components/analyzers/test_peak_analyzer.py
"""
This module provides a pipeline component for analyzing test peaks in peptide chromatograms.
It includes a configuration class for specifying analysis parameters and an analyzer
class for performing the analysis.
"""

# Standard library imports
import logging

# Local application imports
from src.lcseq.pipeline.base import PipelineComponent
from src.lcseq.pipeline.input_types import (PeptideHierarchyInput,
                                            PeptideSetInput,
                                            SinglePeptideInput)

logger: logging.Logger = logging.getLogger(__name__)


class TestPeakAnalyzer(PipelineComponent):
    """Pipeline component for analyzing test peaks in peptide chromatograms.

    Methods:
        process_peptide: Analyze peaks for a single peptide
        process_peptide_set: Analyze peaks for a set of peptides
        process_hierarchy: Analyze peaks for a hierarchy of peptides
    """

    def process_peptide(self, input_data: SinglePeptideInput) -> SinglePeptideInput:
        """Analyze peaks for a single peptide.

        Args:
            input_data (SinglePeptideInput): The input data representing a single
                peptide.

        Returns:
            SinglePeptideInput: The input data with the peaks analyzed.
        """
        logger.info(f"Analyzing peaks for peptide: {input_data.peptide}")
        return input_data

    def process_peptide_set(self, input_data: PeptideSetInput) -> PeptideSetInput:
        """Analyze peaks for a set of peptides.

        Args:
            input_data (PeptideSetInput): The input data representing a set of
                peptides.
        """
        logger.info(f"Analyzing peaks for peptide set: {input_data.peptides}")
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
        # Analyze peaks for a hierarchy of peptides
        logger.info(f"Analyzing peaks for peptide hierarchy: {input_data.hierarchy}")
        return input_data
