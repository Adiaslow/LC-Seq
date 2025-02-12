# src/lcseq/pipeline/input_types.py
"""
This module provides various classes that represent different types of inputs
that can be processed by pipeline components. These classes implement the visitor
pattern to allow pipeline components to process them.

Classes:
    ProcessableInput: Base class for all inputs that can be processed by pipeline components.
    SinglePeptideInput: Wrapper for processing a single peptide.
    PeptideSetInput: Wrapper for processing a set of peptides.
    PeptideHierarchyInput: Wrapper for processing a hierarchy of peptides.
"""

# Standard library imports
from abc import ABC, abstractmethod
from typing import Set

from src.lcseq.core.hierarchy import PeptideHierarchy
# Local application imports
from src.lcseq.core.peptide import Peptide
from src.lcseq.pipeline.base import PipelineComponent


class ProcessableInput(ABC):
    """Base class for all inputs that can be processed by pipeline components."""

    @abstractmethod
    def accept(
        self, processor: "PipelineComponent"  # type: ignore
    ) -> "ProcessableInput":
        """Accept a pipeline component for processing using the visitor pattern.

        Args:
            processor (PipelineComponent): The pipeline component to process the input.

        Returns:
            ProcessableInput: The processed input.
        """
        ...


class SinglePeptideInput(ProcessableInput):
    """Wrapper for processing a single peptide.

    Attributes:
        peptide (Peptide): The peptide to be processed.
    """

    def __init__(self, peptide: Peptide) -> None:
        """Initializes the SinglePeptideInput with a single peptide.

        Args:
            peptide (Peptide): The peptide to be processed.
        """
        self.peptide: Peptide = peptide

    def accept(
        self, processor: "PipelineComponent"  # type: ignore
    ) -> "SinglePeptideInput":
        """Accept a pipeline component for processing using the visitor pattern.

        Args:
            processor (PipelineComponent): The pipeline component to process the input.

        Returns:
            SinglePeptideInput: The processed single peptide input.
        """
        return processor.process_peptide(self)


class PeptideSetInput(ProcessableInput):
    """Wrapper for processing a set of peptides.

    Attributes:
        peptides (Set[Peptide]): The set of peptides to be processed.
    """

    def __init__(self, peptides: Set[Peptide]) -> None:
        """Initializes the PeptideSetInput with a set of peptides.

        Args:
            peptides (Set[Peptide]): The set of peptides to be processed.
        """
        self.peptides: Set[Peptide] = peptides

    def accept(
        self, processor: "PipelineComponent"  # type: ignore
    ) -> "PeptideSetInput":
        """Accept a pipeline component for processing using the visitor pattern.

        Args:
            processor (PipelineComponent): The pipeline component to process the input.

        Returns:
            PeptideSetInput: The processed set of peptides.
        """
        return processor.process_peptide_set(self)


class PeptideHierarchyInput(ProcessableInput):
    """Wrapper for processing a hierarchy of peptides.

    Attributes:
        hierarchy (PeptideHierarchy): The hierarchy of peptides to be processed.
    """

    def __init__(self, hierarchy: PeptideHierarchy) -> None:
        """Initializes the PeptideHierarchyInput with a hierarchy of peptides.

        Args:
            hierarchy (PeptideHierarchy): The hierarchy of peptides to be processed.
        """
        self.hierarchy: PeptideHierarchy = hierarchy

    def accept(
        self, processor: "PipelineComponent"  # type: ignore
    ) -> "PeptideHierarchyInput":
        """Accept a pipeline component for processing using the visitor pattern.

        Args:
            processor (PipelineComponent): The pipeline component to process the input.

        Returns:
            PeptideHierarchyInput: The processed hierarchy of peptides.
        """
        return processor.process_hierarchy(self)
