# src/lcseq/pipeline/base.py
from abc import ABC, abstractmethod
from src.lcseq.pipeline.input_types import ProcessableInput, SinglePeptideInput, PeptideSetInput, PeptideHierarchyInput
from src.lcseq.core.peptide import Peptide
from src.lcseq.core.hierarchy import PeptideHierarchy

class PipelineComponent(ABC):
    @abstractmethod
    def process_peptide(self, input_data: SinglePeptideInput) -> SinglePeptideInput:
        """Process a single peptide."""
        pass

    @abstractmethod
    def process_peptide_set(self, input_data: PeptideSetInput) -> PeptideSetInput:
        """Process a set of peptides."""
        pass

    @abstractmethod
    def process_hierarchy(self, input_data: PeptideHierarchyInput) -> PeptideHierarchyInput:
        """Process a hierarchy of peptides."""
        pass

    def process(self, input_data: ProcessableInput) -> ProcessableInput:
        """Main entry point for processing any type of input."""
        return input_data.accept(self)
