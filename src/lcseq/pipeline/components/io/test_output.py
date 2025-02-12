# src/lcseq/pipeline/components/io/test_output.py
"""
This module provides a pipeline component for handling test output data.
It includes a class for processing test output data.

Classes:
    TestOutput: Pipeline component for handling test output data.
"""

# Standard library imports
import logging
from typing import Optional

# Local application imports
from src.lcseq.pipeline.base import PipelineComponent
from src.lcseq.pipeline.input_types import (PeptideHierarchyInput,
                                            PeptideSetInput,
                                            SinglePeptideInput)

logger: logging.Logger = logging.getLogger(__name__)


class TestOutput(PipelineComponent):
    """TestOutput class for handling test output data.

    Methods:
        process_peptide: Process a single peptide output.
        process_peptide_set: Process a set of peptides output.
        process_hierarchy: Process a hierarchy of peptides output.
    """

    def __init__(self, input_file_path: Optional[str] = None) -> None:
        """Initialize the TestOutput.

        Args:
            input_file_path (Optional[str], optional): The path to the input file.
                Defaults to None.
        """
        super().__init__()
        self.input_file_path: Optional[str] = input_file_path

    def process_peptide(self, input_data: SinglePeptideInput) -> SinglePeptideInput:
        """Process a single peptide output.

        Args:
            input_data (SinglePeptideInput): The input data to process.

        Returns:
            SinglePeptideInput: The processed input data.
        """
        logger.info(f"Outputting results for peptide: {input_data.peptide}")
        return input_data

    def process_peptide_set(self, input_data: PeptideSetInput) -> PeptideSetInput:
        """Process a set of peptides output.

        Args:
            input_data (PeptideSetInput): The input data to process.

        Returns:
            PeptideSetInput: The processed input data.
        """
        logger.info(f"Outputting results for peptide set: {input_data.peptides}")
        return input_data

    def process_hierarchy(
        self, input_data: PeptideHierarchyInput
    ) -> PeptideHierarchyInput:
        """Process a hierarchy of peptides output.

        Args:
            input_data (PeptideHierarchyInput): The input data to process.

        Returns:
            PeptideHierarchyInput: The processed input data.
        """
        logger.info(f"Outputting results for peptide hierarchy: {input_data.hierarchy}")
        return input_data
