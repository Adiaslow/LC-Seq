# src/lcseq/core/hierarchy.py
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional
from .peptide import Peptide, PeptideEncoding
from .building_block import BuildingBlock, BuildingBlockRegistry

@dataclass
class PeptideHierarchy:
    """Represents a hierarchical relationship between peptides."""
    root: Peptide
    children: List['PeptideHierarchy'] = field(default_factory=list)
    properties: Dict = field(default_factory=dict)

    def __post_init__(self):
        """Validate the hierarchy structure."""
        self._validate_hierarchy()

    def _validate_hierarchy(self) -> None:
        """Ensure the hierarchy is valid."""
        if not self.root:
            raise ValueError("Root peptide cannot be None")

        # Ensure no circular references
        seen = set()
        self._check_circular_references(seen)

    def _check_circular_references(self, seen: Set[str]) -> None:
        """Check for circular references in the hierarchy."""
        current_sequence = self.root.sequence_str
        if current_sequence in seen:
            raise ValueError("Circular reference detected in hierarchy")

        seen.add(current_sequence)
        for child in self.children:
            child._check_circular_references(seen.copy())

    def add_child(self, child: 'PeptideHierarchy') -> None:
        """Add a child to the hierarchy."""
        self.children.append(child)
        self._validate_hierarchy()

class HierarchyBuilder:
    """Utility class for building peptide hierarchies."""

    @staticmethod
    def build_from_sequence(
        sequence: List[BuildingBlock],
        null_block: Optional[BuildingBlock] = None
    ) -> PeptideHierarchy:
        """Build a complete hierarchy from a sequence."""
        if null_block is None:
            null_block = BuildingBlockRegistry.get('N')

        # Create the root peptide
        root_peptide = Peptide(sequence)
        hierarchy = PeptideHierarchy(root_peptide)

        # Generate all possible sub-sequences
        for length in range(1, len(sequence)):
            for i in range(len(sequence) - length + 1):
                sub_sequence = sequence[i:i + length]
                sub_peptide = Peptide(sub_sequence)
                sub_hierarchy = PeptideHierarchy(sub_peptide)
                hierarchy.add_child(sub_hierarchy)

        return hierarchy

    @staticmethod
    def generate_null_variants(peptide: Peptide, null_block: BuildingBlock) -> List[PeptideEncoding]:
        """Generate all possible null variants for a peptide."""
        variants = []
        sequence_length = len(peptide.sequence)

        def generate_variants(current: List[BuildingBlock], position: int):
            if position == sequence_length:
                variants.append(PeptideEncoding(current.copy()))
                return

            # Try null block at this position
            current[position] = null_block
            generate_variants(current, position + 1)

            # Try original block at this position
            current[position] = peptide.sequence[position]
            generate_variants(current, position + 1)

        initial = [null_block] * sequence_length
        generate_variants(initial, 0)

        return variants
