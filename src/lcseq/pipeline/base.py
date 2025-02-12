# src/lcseq/pipeline/base.py
"""
This module contains the definition of the PipelineComponent abstract base class, which
is used to define components that can process different types of peptide inputs in a pipeline.

Classes:
    PipelineComponent: Abstract base class for pipeline components.
"""

# Standard library imports
from abc import ABC, abstractmethod
import logging

# Local application imports
from src.lcseq.pipeline.input_types import (
    ProcessableInput,
    SinglePeptideInput,
    PeptideSetInput,
    PeptideHierarchyInput
)
from src.lcseq.core.peptide import Peptide
from src.lcseq.core.hierarchy import PeptideHierarchy

class PipelineComponent(ABC):
    """Abstract base class for pipeline components.

    This class defines the interface for components that can process different types of
    peptide inputs in a pipeline. Subclasses must implement the abstract methods to
    handle specific input types.

    Methods:
        process_peptide: Process a single peptide.
        process_peptide_set: Process a set of peptides.
        process_hierarchy: Process a hierarchy of peptides.
        process: Main entry point for processing any type of input.
    """
    def __init__(self):
        self._pipeline = None
        self.logger = logging.getLogger(__name__)


    @abstractmethod
    def process_peptide(self, input_data: SinglePeptideInput) -> SinglePeptideInput:
        """Process a single peptide.

        Args:
            input_data (SinglePeptideInput): The input data representing a single
            peptide.

        Returns:
            SinglePeptideInput: The processed single peptide.
        """
        pass

    @abstractmethod
    def process_peptide_set(self, input_data: PeptideSetInput) -> PeptideSetInput:
        """Process a set of peptides.

        Args:
            input_data (PeptideSetInput): The input data representing a set of peptides.

        Returns:
            PeptideSetInput: The processed set of peptides.
        """
        pass

    @abstractmethod
    def process_hierarchy(self, input_data: PeptideHierarchyInput) -> PeptideHierarchyInput:
        """Process a hierarchy of peptides.

        Args:
            input_data (PeptideHierarchyInput): The input data representing a hierarchy
            of peptides.

        Returns:
            PeptideHierarchyInput: The processed hierarchy of peptides.
        """
        pass

    def process(self, input_data: ProcessableInput) -> ProcessableInput:
        """Main entry point for processing any type of input.

        This method delegates the processing to the appropriate method based on the
        type of input.

        Args:
            input_data (ProcessableInput): The input data to be processed.

        Returns:
            ProcessableInput: The processed data.
        """
        return input_data.accept(self)

    @property
    def pipeline(self):
        """Get the pipeline this component belongs to."""
        return self._pipeline

    @pipeline.setter
    def pipeline(self, pipeline):
        """Set the pipeline this component belongs to."""
        self._pipeline = pipeline
