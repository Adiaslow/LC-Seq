# src/lcseq/pipeline/components/validators/hierarchical_synthesis_validator.py
"""
This module provides a pipeline component for validating synthesis success based on retention time hierarchy.

Classes:
    HierarchicalSynthesisValidator: Validate synthesis success based on retention time hierarchy.
"""

# Standard library imports
import logging

from src.lcseq.core.hierarchy import PeptideHierarchyNode
from src.lcseq.core.synthesis_status import SynthesisStatus

# Local application imports
from src.lcseq.pipeline.base import PipelineComponent
from src.lcseq.pipeline.input_types import (
    PeptideHierarchyInput,
    SinglePeptideInput,
    PeptideSetInput,
)

logger: logging.Logger = logging.getLogger(__name__)


class HierarchicalSynthesisValidator(PipelineComponent):
    """Validates synthesis success based on retention time hierarchy.

    Attributes:
        logger (logging.Logger): The logger for logging messages.

    Methods:
        process_hierarchy: Validate synthesis across the hierarchy.
        _validate_node: Validate a single node's synthesis.
        process_peptide: Process a single peptide (not supported in hierarchical validator).
        process_peptide_set: Process a set of peptides (not supported in hierarchical validator).
    """

    def process_hierarchy(
        self, input_data: PeptideHierarchyInput
    ) -> PeptideHierarchyInput:
        """Validate synthesis across the hierarchy.

        Args:
            input_data (PeptideHierarchyInput): The input data to process.

        Returns:
            PeptideHierarchyInput: The processed input data.
        """
        for layer in sorted(input_data.hierarchy.layers.keys()):
            for node in input_data.hierarchy.layers[layer]:
                self._validate_node(node)
        return input_data

    def _validate_node(self, node: PeptideHierarchyNode) -> None:
        """Validate a single node's synthesis.

        Args:
            node (PeptideHierarchyNode): The node to validate.
        """
        if node.validate_retention_times():
            node.synthesis_status = SynthesisStatus.SUCCESS
        else:
            node.synthesis_status = SynthesisStatus.FAILURE

    def process_peptide(self, input_data: SinglePeptideInput) -> SinglePeptideInput:
        """Process a single peptide (not supported in hierarchical validator).

        Args:
            input_data: The single peptide input data.

        Returns:
            The unmodified input data.
        """
        self.logger.warning(
            "Single peptide processing not supported in hierarchical validator"
        )
        return input_data

    def process_peptide_set(self, input_data: PeptideSetInput) -> PeptideSetInput:
        """Process a set of peptides (not supported in hierarchical validator).

        Args:
            input_data: The peptide set input data.

        Returns:
            The unmodified input data.
        """
        self.logger.warning(
            "Peptide set processing not supported in hierarchical validator"
        )
        return input_data
