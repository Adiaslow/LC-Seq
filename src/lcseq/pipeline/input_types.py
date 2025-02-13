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
from dataclasses import dataclass
from typing import Protocol, Set

# Local application imports
from src.lcseq.core.hierarchy import PeptideHierarchy
from src.lcseq.core.peptide import Peptide
from src.lcseq.pipeline.base import PipelineComponent


class ProcessableInput(Protocol):
    """Protocol for input types that can be processed by pipeline components."""

    def accept(self, component: "PipelineComponent") -> "ProcessableInput":
        """Accept a pipeline component for processing."""
        ...


@dataclass
class SinglePeptideInput:
    """Input type for processing a single peptide."""

    peptide: Peptide

    def accept(self, component: "PipelineComponent") -> "SinglePeptideInput":
        """Accept a pipeline component for processing."""
        return component.process_peptide(self)


@dataclass
class PeptideSetInput:
    """Input type for processing a set of peptides."""

    peptides: Set[Peptide]

    def accept(self, component: "PipelineComponent") -> "PeptideSetInput":
        """Accept a pipeline component for processing."""
        return component.process_peptide_set(self)


@dataclass
class PeptideHierarchyInput:
    """Input type for processing a hierarchy of peptides."""

    hierarchy: PeptideHierarchy

    def accept(self, component: "PipelineComponent") -> "PeptideHierarchyInput":
        """Accept a pipeline component for processing."""
        return component.process_hierarchy(self)
