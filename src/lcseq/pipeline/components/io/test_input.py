# src/lcseq/pipeline/components/io/test_input.py
"""
This module provides a pipeline component for handling test input data.
It includes a class for processing test input data.

Classes:
    TestInput: Pipeline component for handling test input data.
"""

# Standard library imports
import logging

# Local application imports
from src.lcseq.pipeline.base import PipelineComponent
from src.lcseq.pipeline.input_types import (
    PeptideHierarchyInput,
    PeptideSetInput,
    SinglePeptideInput,
)

logger: logging.Logger = logging.getLogger(__name__)


class TestInput(PipelineComponent):
    """TestInput class for handling test input data.

    Methods:
        process_peptide: Process a single peptide input.
        process_peptide_set: Process a set of peptides input.
        process_hierarchy: Process a hierarchy of peptides input.
    """

    def process_peptide(self, input_data: SinglePeptideInput) -> SinglePeptideInput:
        """Process a single peptide input.

        Args:
            input_data (SinglePeptideInput): The input data to process.

        Returns:
            SinglePeptideInput: The processed input data.
        """
        logger.info(f"Handling input for peptide: {input_data.peptide}")
        return input_data

    def process_peptide_set(self, input_data: PeptideSetInput) -> PeptideSetInput:
        """Process a set of peptides input.

        Args:
            input_data (PeptideSetInput): The input data to process.

        Returns:
            PeptideSetInput: The processed input data.
        """
        logger.info(f"Handling input for peptide set: {input_data.peptides}")
        return input_data

    def process_hierarchy(
        self, input_data: PeptideHierarchyInput
    ) -> PeptideHierarchyInput:
        """Process a hierarchy of peptides input.

        Args:
            input_data (PeptideHierarchyInput): The input data to process.

        Returns:
            PeptideHierarchyInput: The processed input data.
        """
        logger.info(f"Handling input for peptide hierarchy: {input_data.hierarchy}")
        return input_data
