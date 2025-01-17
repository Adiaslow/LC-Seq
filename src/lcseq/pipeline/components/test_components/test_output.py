# src/lcseq/pipeline/components/test_components/test_output.py
import logging
from src.lcseq.pipeline.base import PipelineComponent
from src.lcseq.pipeline.input_types import SinglePeptideInput, PeptideSetInput, PeptideHierarchyInput

logger = logging.getLogger(__name__)

class TestOutput(PipelineComponent):
    def process_peptide(self, input_data: SinglePeptideInput) -> SinglePeptideInput:
        # Output processing results for a single peptide
        logger.info(f"Outputting results for peptide: {input_data.peptide}")
        return input_data

    def process_peptide_set(self, input_data: PeptideSetInput) -> PeptideSetInput:
        # Output processing results for a set of peptides
        logger.info(f"Outputting results for peptide set: {input_data.peptides}")
        return input_data

    def process_hierarchy(self, input_data: PeptideHierarchyInput) -> PeptideHierarchyInput:
        # Output processing results for a hierarchy of peptides
        logger.info(f"Outputting results for peptide hierarchy: {input_data.hierarchy}")
        return input_data
