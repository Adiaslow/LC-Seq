# src/chromatographicpeakpicking/core/prototypes/hierarchy.py
"""This module defines the Hierarchy prototype.

"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Set, Optional
from collections import defaultdict
import copy
from src.chromatographicpeakpicking.core.interfaces.prototype import Prototype
from src.chromatographicpeakpicking.core.prototypes.building_block import BuildingBlock
from src.chromatographicpeakpicking.core.prototypes.peptide import Peptide

@dataclass
class Hierarchy(Prototype['Hierarchy']):
    """
    Represents the hierarchical structure of null truncations in peptide libraries.

    Manages relationships between peptides at different levels, where each level
    represents the number of non-null building blocks in the peptides.

    Attributes:
        null_block (BuildingBlock): The null building block used for truncations.
        levels (Dict[int, Set[Peptide]]): Peptides grouped by number of non-null blocks.
        descendants (Dict[Peptide, Set[Peptide]]): Direct descendants of each peptide.
        ancestors (Dict[Peptide, Set[Peptide]]): Direct ancestors of each peptide.
        properties (Dict[str, Any]): Additional properties for the hierarchy.
        metadata (Dict[str, Any]): Additional metadata for the hierarchy.

    Methods:
        clone: Create a copy of the hierarchy with optional overrides.
        with_properties: Create a new hierarchy with updated properties.
        with_metadata: Create a new hierarchy with updated metadata.
        validate: Validate the hierarchy and return any errors.
        count_non_null_blocks: Count number of non-null building blocks in a peptide.
        add_peptide: Add a peptide to the hierarchy and compute its relationships.
        _get_direct_descendants: Generate direct descendants by replacing one non-null block with
            null.
        _find_canonical_form: Find existing functionally equivalent peptide at given level.
        _are_functionally_equivalent: Check if two peptides have the same non-null blocks in the
            same order.
        get_level: Get the level (number of non-null blocks) of a peptide.
        get_peptides_at_level: Get all peptides at a specific level.
        get_ancestors: Get all ancestors of a peptide.
        get_descendants: Get all descendants of a peptide.
    """
    null_block: BuildingBlock
    levels: Dict[int, Set[Peptide]] = field(default_factory=lambda: defaultdict(set))
    descendants: Dict[Peptide, Set[Peptide]] = field(default_factory=lambda: defaultdict(set))
    ancestors: Dict[Peptide, Set[Peptide]] = field(default_factory=lambda: defaultdict(set))
    properties: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def clone(self, **kwargs: Any) -> 'Hierarchy':
        """Create a copy of the hierarchy with optional overrides.

        Args:
            **kwargs (Any): Optional overrides for the hierarchy attributes.

        Returns:
            Hierarchy: A new hierarchy instance with the specified overrides.

        Raises:
            None
        """
        return Hierarchy(
            null_block=kwargs.get('null_block', self.null_block),
            levels=kwargs.get(
                'levels',
                defaultdict(set, {k: s.copy() for k, s in self.levels.items()})
            ),
            descendants=kwargs.get(
                'descendants',
                defaultdict(set, {k: s.copy() for k, s in self.descendants.items()})
            ),
            ancestors=kwargs.get(
                'ancestors',
                defaultdict(set, {k: s.copy() for k, s in self.ancestors.items()})
            ),
            properties=kwargs.get(
                'properties',
                self.properties.copy()
            ),
            metadata=kwargs.get(
                'metadata',
                self.metadata.copy()
            )
        )

    def with_properties(self, **kwargs: Any) -> 'Hierarchy':
        """Create a new hierarchy with updated properties."""
        new_properties = self.properties.copy()
        new_properties.update(kwargs)
        return self.clone(properties=new_properties)

    def with_metadata(self, **kwargs: Any) -> 'Hierarchy':
        """Create a new hierarchy with updated metadata."""
        new_metadata = self.metadata.copy()
        new_metadata.update(kwargs)
        return self.clone(metadata=new_metadata)

    def validate(self) -> List[str]:
        """Validate the hierarchy and return any errors."""
        errors = []
        if not isinstance(self.null_block, BuildingBlock):
            errors.append("Null block must be a BuildingBlock instance")

        # Validate level consistency
        for level, peptides in self.levels.items():
            for peptide in peptides:
                actual_level = self.count_non_null_blocks(peptide)
                if actual_level != level:
                    errors.append(f"Peptide at level {level} has {actual_level} non-null blocks")

        # Validate relationship consistency
        for peptide, desc in self.descendants.items():
            for d in desc:
                if peptide not in self.ancestors[d]:
                    errors.append(f"Inconsistent ancestor relationship for {peptide} and {d}")

        for peptide, anc in self.ancestors.items():
            for a in anc:
                if peptide not in self.descendants[a]:
                    errors.append(f"Inconsistent descendant relationship for {peptide} and {a}")

        return errors

    def count_non_null_blocks(self, peptide: Peptide) -> int:
        """Count number of non-null building blocks in a peptide."""
        return sum(block != self.null_block for block in peptide.sequence)

    def add_peptide(self, peptide: Peptide) -> None:
        """Add a peptide to the hierarchy and compute its relationships."""
        level = self.count_non_null_blocks(peptide)
        self.levels[level].add(peptide)

        # Generate and add direct descendants
        for desc in self._get_direct_descendants(peptide):
            desc_level = self.count_non_null_blocks(desc)

            # Find or create canonical form
            canonical = self._find_canonical_form(desc, desc_level)
            if not canonical:
                canonical = desc
                self.levels[desc_level].add(canonical)

            # Update relationships
            self.descendants[peptide].add(canonical)
            self.ancestors[canonical].add(peptide)

    def _get_direct_descendants(self, peptide: Peptide) -> Set[Peptide]:
        """Generate direct descendants by replacing one non-null block with null."""
        length = len(peptide.sequence)
        non_null_positions = [
            i for i, block in enumerate(peptide.sequence)
            if block != self.null_block
        ]

        descendants = set()
        for pos in non_null_positions:
            new_sequence = [b.clone() for b in peptide.sequence]
            new_sequence[pos] = self.null_block
            descendants.add(Peptide(sequence=new_sequence))

        return descendants

    def _find_canonical_form(self, peptide: Peptide, level: int) -> Optional[Peptide]:
        """Find existing functionally equivalent peptide at given level."""
        for existing in self.levels[level]:
            if self._are_functionally_equivalent(existing, peptide):
                return existing
        return None

    def _are_functionally_equivalent(self, peptide1: Peptide, peptide2: Peptide) -> bool:
        """Check if two peptides have the same non-null blocks in the same order."""
        blocks1 = [b for b in peptide1.sequence if b != self.null_block]
        blocks2 = [b for b in peptide2.sequence if b != self.null_block]
        if len(blocks1) != len(blocks2):
            return False
        return all(b1.name == b2.name for b1, b2 in zip(blocks1, blocks2))

    def get_level(self, peptide: Peptide) -> int:
        """Get the level (number of non-null blocks) of a peptide."""
        return self.count_non_null_blocks(peptide)

    def get_peptides_at_level(self, level: int) -> Set[Peptide]:
        """Get all peptides at a specific level."""
        return self.levels[level]

    def get_ancestors(self, peptide: Peptide) -> Set[Peptide]:
        """Get all ancestors of a peptide."""
        return self.ancestors[peptide]

    def get_descendants(self, peptide: Peptide) -> Set[Peptide]:
        """Get all descendants of a peptide."""
        return self.descendants[peptide]
