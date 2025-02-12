# src/lcseq/pipeline/components/standard_input.py
"""
This module provides a pipeline component for handling standard input data.
It includes a class for detecting hierarchy in input peptides and a method for
loading data from a dictionary format into appropriate input types.

Classes:
    StandardInput: Pipeline component for handling standard input data.
"""

# Standard library imports
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import numpy as np
import yaml

from ....core import (BuildingBlock, BuildingBlockRegistry, Chromatogram,
                      Peptide, PeptideEncoding, PeptideHierarchy)
from ....pipeline import (PeptideHierarchyInput, PeptideSetInput,
                          SinglePeptideInput)
# Local application imports
from ...pipeline import PipelineComponent

logger: logging.Logger = logging.getLogger(__name__)


class StandardInput(PipelineComponent):
    """StandardInput class for handling standard input data.

    Methods:
        __init__: Initialize the StandardInput.
        detect_hierarchy: Detect if the input peptides likely form a hierarchical structure.
        build_hierarchy: Build a hierarchy from the input peptides.
        load_data: Load data from a dictionary format into appropriate input types.
        process_peptide: Process a single peptide input.
        process_peptide_set: Process a set of peptides input.
        process_hierarchy: Process a hierarchy of peptides input.
    """

    def __init__(self) -> None:
        """Initialize the StandardInput.

        Args:
            config (StandardInputConfig, optional): Configuration for the StandardInput.
                Default is None, which uses the default configuration.
        """
        super().__init__()
        self.logger: logging.Logger = logging.getLogger(__name__)

    def detect_hierarchy(self, peptides: Set[Peptide]) -> bool:
        """Detect if the input peptides likely form a hierarchical structure.

        Args:
            peptides (Set[Peptide]): The set of peptides to detect hierarchy in.

        Returns:
            bool: True if the peptides likely form a hierarchical structure, False otherwise.
        """
        # Count peptides of different lengths
        length_counts: dict = {}
        for peptide in peptides:
            length: int = len(peptide.sequence)
            length_counts[length] = length_counts.get(length, 0) + 1

        # Check if we have peptides of different lengths
        if len(length_counts) <= 1:
            return False

        # Look for potential truncation relationships
        for peptide in peptides:
            if len(peptide.sequence) > 1:
                # Check if potential truncations exist
                for i in range(len(peptide.sequence)):
                    truncated_seq = peptide.sequence[:i] + peptide.sequence[i + 1 :]
                    truncated_str = "-".join(
                        [block.identifier for block in truncated_seq][::-1]
                    )

                    # Look for matching truncation
                    for potential_truncation in peptides:
                        if potential_truncation.sequence_str == truncated_str:
                            return True

        return False

    def build_hierarchy(
        self, peptides: Set[Peptide]
    ) -> Tuple[PeptideHierarchy, Set[Peptide]]:
        """Build hierarchy from peptides, returning both hierarchy and orphaned peptides."""
        hierarchy = PeptideHierarchy()
        orphaned = set()

        # First pass: add all single-block peptides
        single_block = {p for p in peptides if len(p.sequence) == 1}
        for peptide in single_block:
            hierarchy.add_node(peptide)

        # Second pass: try to build up multi-block peptides
        remaining = peptides - single_block
        for peptide in remaining:
            # Check if all possible truncations exist
            has_all_truncations = True
            truncation_sequences = set()

            # Generate all possible truncation sequences
            for i in range(len(peptide.sequence)):
                truncated_seq = peptide.sequence[:i] + peptide.sequence[i + 1 :]
                truncation_sequences.add(
                    "-".join([block.identifier for block in truncated_seq][::-1])
                )

            # Check if truncations exist in hierarchy
            for truncation_seq in truncation_sequences:
                if truncation_seq not in hierarchy.nodes:
                    has_all_truncations = False
                    break

            if has_all_truncations:
                hierarchy.add_node(peptide)
            else:
                orphaned.add(peptide)

        return hierarchy, orphaned

    def load_data(
        self, input_data: Dict[str, Any]
    ) -> Union[PeptideSetInput, PeptideHierarchyInput]:
        """Load data from dictionary format into appropriate input type."""
        peptides = set()

        # Load building blocks
        for bb_id, bb_data in input_data["building_blocks"].items():
            block = BuildingBlock(
                identifier=bb_id,
                properties={
                    "name": bb_data["name"],
                    "smiles": bb_data["smiles"],
                    "stereochem": bb_data["stereochem"],
                },
            )
            BuildingBlockRegistry.register(block)

        # Create peptides
        for peptide_data in input_data["peptides"]:
            sequence = self._create_sequence(peptide_data["sequence"])
            if sequence:
                peptide = self._create_peptide(sequence, peptide_data)
                peptides.add(peptide)

        # Determine processing type
        if self.pipeline.config.hierarchical or self.detect_hierarchy(peptides):  # type: ignore
            hierarchy, orphaned = self.build_hierarchy(peptides)
            return PeptideHierarchyInput(hierarchy=hierarchy, orphaned_peptides=orphaned)  # type: ignore

        return PeptideSetInput(peptides=peptides)

    def _create_sequence(
        self, sequence_names: List[str]
    ) -> Optional[List[BuildingBlock]]:
        """Create sequence of building blocks from names."""
        sequence = []
        for name in sequence_names:
            matching_block = next(
                (
                    block
                    for block in BuildingBlockRegistry.blocks.values()  # type: ignore
                    if block.properties["name"] == name
                ),
                None,
            )
            if matching_block:
                sequence.append(matching_block)
            else:
                self.logger.warning(f"Could not find building block for name: {name}")
                return None
        return sequence if len(sequence) == len(sequence_names) else None

    def _create_peptide(
        self, sequence: List[BuildingBlock], peptide_data: Dict
    ) -> Peptide:
        """Create peptide with chromatogram from sequence and data."""
        chromatogram = Chromatogram(
            times=np.array(peptide_data["chromatogram"]["times"]),
            intensities=np.array(peptide_data["chromatogram"]["intensities"]),
        )

        properties = peptide_data["properties"].copy()
        properties["identifier"] = peptide_data["identifier"]

        peptide = Peptide(sequence=sequence, properties=properties)
        encoding = PeptideEncoding(blocks=sequence, chromatogram=chromatogram)
        peptide.add_encoding(encoding)

        return peptide

    def process_peptide(self, input_data: SinglePeptideInput) -> SinglePeptideInput:
        """Process a single peptide input."""
        self.logger.info(f"Handling input for peptide: {input_data.peptide}")
        return input_data

    def process_peptide_set(self, input_data: PeptideSetInput) -> PeptideSetInput:
        """Process a set of peptides input."""
        self.logger.info(
            f"Handling input for peptide set: {len(input_data.peptides)} peptides"
        )
        return input_data

    def process_hierarchy(
        self, input_data: PeptideHierarchyInput
    ) -> PeptideHierarchyInput:
        """Process a hierarchy of peptides input."""
        self.logger.info(
            f"Handling input for peptide hierarchy: {input_data.hierarchy}"
        )
        return input_data
