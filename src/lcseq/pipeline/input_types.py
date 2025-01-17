# src/lcseq/pipeline/input_types.py
from abc import ABC, abstractmethod
from typing import Set
from src.lcseq.core.peptide import Peptide
from src.lcseq.core.hierarchy import PeptideHierarchy

class ProcessableInput(ABC):
    """Base class for all inputs that can be processed by pipeline components."""

    @abstractmethod
    def accept(self, processor: 'PipelineComponent') -> 'ProcessableInput': # type: ignore
        """Accept a pipeline component for processing using visitor pattern."""
        pass

class SinglePeptideInput(ProcessableInput):
    """Wrapper for processing a single peptide."""
    def __init__(self, peptide: 'Peptide'):
        self.peptide = peptide

    def accept(self, processor: 'PipelineComponent') -> 'SinglePeptideInput': # type: ignore
        return processor.process_peptide(self)

class PeptideSetInput(ProcessableInput):
    """Wrapper for processing a set of peptides."""
    def __init__(self, peptides: Set['Peptide']):
        self.peptides = peptides

    def accept(self, processor: 'PipelineComponent') -> 'PeptideSetInput': # type: ignore
        return processor.process_peptide_set(self)

class PeptideHierarchyInput(ProcessableInput):
    """Wrapper for processing a hierarchy of peptides."""
    def __init__(self, hierarchy: 'PeptideHierarchy'):
        self.hierarchy = hierarchy

    def accept(self, processor: 'PipelineComponent') -> 'PeptideHierarchyInput': # type: ignore
        return processor.process_hierarchy(self)
