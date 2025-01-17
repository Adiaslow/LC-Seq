# src/lcseq/pipeline/components/test_components/test_peak_selector.py
import logging
from src.lcseq.pipeline.base import PipelineComponent
from src.lcseq.pipeline.input_types import SinglePeptideInput, PeptideSetInput, PeptideHierarchyInput

logger = logging.getLogger(__name__)

class TestPeakSelector(PipelineComponent):
    def __init__(self, intensity_threshold: float = 100.0, min_duration: float = 0.1):
        self.intensity_threshold = intensity_threshold
        self.min_duration = min_duration

    def process_peptide(self, input_data: SinglePeptideInput) -> SinglePeptideInput:
        # Select peaks for a single peptide
        logger.info(f"Selecting peaks for peptide: {input_data.peptide}")
        return input_data

    def process_peptide_set(self, input_data: PeptideSetInput) -> PeptideSetInput:
        # Select peaks for a set of peptides
        logger.info(f"Selecting peaks for peptide set: {input_data.peptides}")
        return input_data

    def process_hierarchy(self, input_data: PeptideHierarchyInput) -> PeptideHierarchyInput:
        # Select peaks for a hierarchy of peptides
        logger.info(f"Selecting peaks for peptide hierarchy: {input_data.hierarchy}")
        return input_data
