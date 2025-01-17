# src/lcseq/pipeline/components/standard_input.py
import logging
from dataclasses import dataclass
from typing import Dict, Any
import yaml
import numpy as np
from src.lcseq.pipeline.base import PipelineComponent
from src.lcseq.pipeline.input_types import SinglePeptideInput, PeptideSetInput, PeptideHierarchyInput
from src.lcseq.core.building_block import BuildingBlock, BuildingBlockRegistry
from src.lcseq.core.peptide import Peptide, PeptideEncoding
from src.lcseq.core.chromatogram import Chromatogram

logger = logging.getLogger(__name__)

class StandardInput(PipelineComponent):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def load_data(self, input_data: Dict[str, Any]) -> PeptideSetInput:
        """Load data from dictionary format into peptide objects."""
        # First register building blocks with their full information
        for bb_id, bb_data in input_data['building_blocks'].items():
            block = BuildingBlock(
                identifier=bb_id,
                properties={
                    'name': bb_data['name'],
                    'smiles': bb_data['smiles'],
                    'stereochem': bb_data['stereochem']
                }
            )
            BuildingBlockRegistry.register(block)

        # Create peptides
        peptides = []
        for peptide_data in input_data['peptides']:
            # Get sequence of building block names from the sequence field
            sequence_names = peptide_data['sequence']

            # Find corresponding building blocks by name
            sequence = []
            for name in sequence_names:
                # Find the building block with matching name
                matching_block = None
                for block in BuildingBlockRegistry.blocks.values():
                    if block.properties['name'] == name:
                        matching_block = block
                        break

                if matching_block:
                    sequence.append(matching_block)
                else:
                    self.logger.warning(f"Could not find building block for name: {name}")
                    continue

            # Only create peptide if we found all building blocks
            if len(sequence) == len(sequence_names):
                # Create chromatogram
                chromatogram = Chromatogram(
                    times=np.array(peptide_data['chromatogram']['times']),
                    intensities=np.array(peptide_data['chromatogram']['intensities'])
                )

                # Create peptide with properties and identifier
                properties = peptide_data['properties'].copy()
                properties['identifier'] = peptide_data['identifier']  # Include identifier in properties

                peptide = Peptide(
                    sequence=sequence,
                    properties=properties
                )

                # Add encoding with chromatogram
                encoding = PeptideEncoding(
                    blocks=sequence,
                    chromatogram=chromatogram
                )
                peptide.add_encoding(encoding)
                peptides.append(peptide)

        return PeptideSetInput(set(peptides))

    def process_peptide(self, input_data: SinglePeptideInput) -> SinglePeptideInput:
        """Process a single peptide input."""
        self.logger.info(f"Handling input for peptide: {input_data.peptide}")
        return input_data

    def process_peptide_set(self, input_data: PeptideSetInput) -> PeptideSetInput:
        """Process a set of peptides input."""
        self.logger.info(f"Handling input for peptide set: {len(input_data.peptides)} peptides")
        return input_data

    def process_hierarchy(self, input_data: PeptideHierarchyInput) -> PeptideHierarchyInput:
        """Process a hierarchy of peptides input."""
        self.logger.info(f"Handling input for peptide hierarchy: {input_data.hierarchy}")
        return input_data
