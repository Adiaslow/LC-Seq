# src/lcseq/pipeline/components/validators/hierarchical_synthesis_validator.py
"""
This module provides a pipeline component for validating synthesis success based on retention time hierarchy.
"""

# Standard library imports
import logging

# Local application imports
from ... import PipelineComponent
from ...input_types import PeptideHierarchyInput
from ....core import PeptideHierarchyNode, SynthesisStatus

logger = logging.getLogger(__name__)

class HierarchicalSynthesisValidator(PipelineComponent):
    """Validates synthesis success based on retention time hierarchy.

    Attributes:
        logger (logging.Logger): The logger for logging messages.

    Methods:
        process_hierarchy: Validate synthesis across the hierarchy.
        _validate_node: Validate a single node's synthesis.
    """
    def process_hierarchy(self, input_data: PeptideHierarchyInput) -> PeptideHierarchyInput:
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
