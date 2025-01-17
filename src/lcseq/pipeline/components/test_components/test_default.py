# src/lcseq/pipeline/TestDefault.py
from src.lcseq.pipeline.base import PipelineComponent
from src.lcseq.pipeline.input_types import SinglePeptideInput, PeptideSetInput, PeptideHierarchyInput

class TestDefault(PipelineComponent):
    def process_peptide(self, input_data: SinglePeptideInput) -> SinglePeptideInput:
        # Example processing of a single peptide
        print(f"Processing single peptide: {input_data.peptide}")
        return input_data

    def process_peptide_set(self, input_data: PeptideSetInput) -> PeptideSetInput:
        # Example processing of a set of peptides
        print(f"Processing peptide set: {input_data.peptides}")
        return input_data

    def process_hierarchy(self, input_data: PeptideHierarchyInput) -> PeptideHierarchyInput:
        # Example processing of a hierarchy of peptides
        print(f"Processing peptide hierarchy: {input_data.hierarchy}")
        return input_data
