# src/lcseq/pipeline/components/visualizers/test_chromatogram_visualizer.py
"""
This module defines the TestChromatogramVisualizer class, which is a test component for
visualizing chromatograms in various peptide inputs.

Classes:
    TestChromatogramVisualizer: A pipeline component for visualizing chromatograms.
"""

import logging

from src.lcseq.pipeline.base import PipelineComponent
from src.lcseq.pipeline.input_types import (PeptideHierarchyInput,
                                            PeptideSetInput,
                                            SinglePeptideInput)

logger: logging.Logger = logging.getLogger(__name__)


class TestChromatogramVisualizer(PipelineComponent):
    """
    TestChromatogramVisualizer class for visualizing chromatograms in various peptide
    inputs.

    This class inherits from the PipelineComponent class and provides methods to
    process and visualize chromatograms for single peptides, sets of peptides, and
    peptide hierarchies.
    """

    def process_peptide(self, input_data: SinglePeptideInput) -> SinglePeptideInput:
        """
        Visualize chromatogram for a single peptide.

        Args:
            input_data (SinglePeptideInput): The input data representing a single
            peptide.

        Returns:
            SinglePeptideInput: The visualized single peptide input.
        """
        logger.info(f"Visualizing chromatogram for peptide: {input_data.peptide}")
        return input_data

    def process_peptide_set(self, input_data: PeptideSetInput) -> PeptideSetInput:
        """
        Visualize chromatogram for a set of peptides.

        Args:
            input_data (PeptideSetInput): The input data representing a set of peptides.

        Returns:
            PeptideSetInput: The visualized set of peptides.
        """
        logger.info(f"Visualizing chromatogram for peptide set: {input_data.peptides}")
        return input_data

    def process_hierarchy(
        self, input_data: PeptideHierarchyInput
    ) -> PeptideHierarchyInput:
        """
        Visualize chromatogram for a hierarchy of peptides.

        Args:
            input_data (PeptideHierarchyInput): The input data representing a hierarchy
            of peptides.

        Returns:
            PeptideHierarchyInput: The visualized hierarchy of peptides.
        """
        logger.info(
            "Visualizing chromatogram for peptide hierarchy:"
            + f"{input_data.hierarchy}"
        )
        return input_data
