# src/chromatographicpeakpicking/core/prototypes/hierarchy.py

"""
Module: hierarchy

This module defines the Hierarchy class for managing hierarchical structures of null truncations
in null-encoded peptide libraries. The Hierarchy class follows the Prototype Pattern and is
designed to work with the Factory Pattern.
"""

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Set, Optional
from itertools import combinations
import copy
from .building_block import BuildingBlock
from .peptide import Peptide
from src.chromatographicpeakpicking.core.types.config import GlobalConfig

@dataclass
class Hierarchy:
    """
    Represents the hierarchical relational structure of null truncations in null-encoded peptide
    libraries.

    Attributes:
        global_config (GlobalConfig): Global configuration settings.
        levels (Dict[int, Set[Peptide]]): Dictionary mapping level to sets of peptides.
        descendants (Dict[Peptide, Set[Peptide]]): Dictionary mapping peptides to descendants.
        ancestors (Dict[Peptide, Set[Peptide]]): Dictionary mapping peptides to ancestors.
        id (str): Unique identifier for the hierarchy instance.
    """
    global_config: GlobalConfig = field(default_factory=GlobalConfig)
    levels: Dict[int, Set[Peptide]] = field(default_factory=lambda: defaultdict(set))
    descendants: Dict[Peptide, Set[Peptide]] = field(default_factory=lambda: defaultdict(set))
    ancestors: Dict[Peptide, Set[Peptide]] = field(default_factory=lambda: defaultdict(set))
    properties: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate hierarchy data after initialization."""
        if not isinstance(self.global_config, GlobalConfig):
            raise ValueError("global_config must be an instance of GlobalConfig")

    def count_non_null_blocks(self, peptide: Peptide) -> int:
        """
        Returns the number of non-null building blocks in the peptide.

        Args:
            peptide (Peptide): The peptide to count non-null building blocks in.

        Returns:
            int: The number of non-null building blocks.
        """
        null_building_block = self.global_config.null_building_block
        return sum(block != null_building_block for block in peptide.sequence)

    def get_direct_descendants(self, peptide: Peptide) -> Set[Peptide]:
        """
        Generate all direct descendants by replacing one non-null block with null.
        Each non-null block can be replaced, and the remaining blocks can be in any position.
        """
        null_bb = self.global_config.null_building_block
        length = len(peptide.sequence)

        # Get current non-null blocks
        non_null_blocks = self.get_non_null_blocks(peptide)
        current_level = len(non_null_blocks)

        if current_level <= 1:
            return set()

        descendants = set()
        # For each non-null block we could remove
        for i in range(len(non_null_blocks)):
            # Create the new set of blocks (removing one)
            remaining_blocks = non_null_blocks[:i] + non_null_blocks[i+1:]

            # Generate all possible positions for these blocks
            from itertools import permutations
            for perm in permutations(range(length), len(remaining_blocks)):
                # Create a new sequence with nulls
                new_sequence = [null_bb] * length
                # Place the blocks in the chosen positions
                for pos, block in zip(perm, remaining_blocks):
                    new_sequence[pos] = block
                descendants.add(Peptide(sequence=new_sequence))

        return descendants

    def generate_descendants_with_k_blocks(self, peptide: Peptide, k: int) -> Set[Peptide]:
        """
        Generate all peptides with exactly k non-null building blocks that preserve the relative order
        of building blocks.

        Args:
            peptide (Peptide): The peptide to generate descendants for.
            k (int): The number of non-null building blocks in the generated peptides.

        Returns:
            Set[Peptide]: A set of peptides with exactly k non-null building blocks.
        """
        result = set()
        null_building_block = self.global_config.null_building_block
        non_null_blocks = [block for block in peptide.sequence if block != null_building_block]
        length = len(peptide.sequence)

        if k > len(non_null_blocks):
            return result

        def place_blocks(curr_pos: int, block_idx: int, curr_peptide: List[BuildingBlock]) -> None:
            if block_idx == len(selected_blocks):
                result.add(Peptide(sequence=curr_peptide))
                return

            block = selected_blocks[block_idx]
            min_pos = curr_pos
            max_pos = length - (len(selected_blocks) - block_idx)

            for pos in range(min_pos, max_pos + 1):
                new_peptide = curr_peptide.copy()
                new_peptide[pos] = block
                place_blocks(pos + 1, block_idx + 1, new_peptide)

        for selected_indices in combinations(range(len(non_null_blocks)), k):
            selected_blocks = [non_null_blocks[i] for i in selected_indices]
            initial_peptide = [null_building_block] * length
            place_blocks(0, 0, initial_peptide)

        return result

    def generate_all_descendants(self, peptide: Peptide) -> List[Peptide]:
        """
        Generate all possible descendants of a peptide that preserve relative order.

        Args:
            peptide (Peptide): The peptide to generate descendants for.

        Returns:
            List[Peptide]: A list of all possible descendant peptides.
        """
        peptides = []
        non_null_count = self.count_non_null_blocks(peptide)

        for k in range(non_null_count + 1):
            peptides_with_k = self.generate_descendants_with_k_blocks(peptide, k)
            peptides.extend(peptides_with_k)

        return peptides

    def add_peptide(self, peptide: Peptide) -> None:
        """
        Add a peptide to the hierarchy and compute its relationships.
        """
        # Add to appropriate level
        level = self.count_non_null_blocks(peptide)
        self.levels[level].add(peptide)

        # Get all direct descendants
        direct_desc = self.get_direct_descendants(peptide)

        # For each descendant, find or create the canonical form
        for desc in direct_desc:
            level_desc = self.count_non_null_blocks(desc)

            # Find any existing equivalent form
            existing_equiv = None
            for existing in self.levels[level_desc]:
                if self.are_functionally_equivalent(existing, desc):
                    existing_equiv = existing
                    break

            # Use existing form if found, otherwise add new one
            target_desc = existing_equiv if existing_equiv else desc
            if not existing_equiv:
                self.levels[level_desc].add(target_desc)

            # Update relationships
            self.descendants[peptide].add(target_desc)
            self.ancestors[target_desc].add(peptide)

    def add_peptides(self, peptides: List[Peptide]) -> None:
        """Add multiple peptides to the hierarchy."""
        # Sort by level to ensure proper relationship building
        sorted_peptides = sorted(
            peptides,
            key=lambda p: self.count_non_null_blocks(p),
            reverse=True
        )
        for peptide in sorted_peptides:
            self.add_peptide(peptide)

    def get_peptides_by_level(self, level: int) -> Set[Peptide]:
        """
        Get all peptides with a specific number of non-null building blocks.

        Args:
            level (int): The level to get peptides for.

        Returns:
            Set[Peptide]: A set of peptides at the specified level.
        """
        return self.levels[level]

    def get_level(self, peptide: Peptide) -> int:
        """
        Get the level (number of non-null building blocks) of a peptide.

        Args:
            peptide (Peptide): The peptide to get the level for.

        Returns:
            int: The level of the peptide.
        """
        return self.count_non_null_blocks(peptide)

    def get_ancestors(self, peptide: Peptide) -> Set[Peptide]:
        """
        Get all peptides that can have building blocks replaced to get this peptide.

        Args:
            peptide (Peptide): The peptide to get ancestors for.

        Returns:
            Set[Peptide]: A set of ancestor peptides.
        """
        return self.ancestors[peptide]

    def get_descendants(self, peptide: Peptide) -> Set[Peptide]:
        """
        Get direct descendants of a peptide.

        Args:
            peptide (Peptide): The peptide to get descendants for.

        Returns:
            Set[Peptide]: A set of direct descendant peptides.
        """
        return self.descendants[peptide]

    def clone(self, **kwargs: Any) -> 'Hierarchy':
        """
        Clone the current hierarchy, allowing for optional overrides.

        Args:
            kwargs (Any): Attributes to override in the cloned instance.

        Returns:
            Hierarchy: A new Hierarchy instance with a new unique ID.
        """
        new_instance = copy.deepcopy(self)
        for key, value in kwargs.items():
            object.__setattr__(new_instance, key, value)
        return new_instance

    def organize_by_relationships(self) -> Dict[str, Any]:
        """
        Organize peptides by their relationships for visualization.
        Returns a structured representation of the hierarchy.
        """
        structure = {
            'levels': {},  # Organized by level
            'groups': {},  # Groups of related peptides
            'edges': []    # Edge connections with group information
        }

        # First, organize peptides into levels and groups
        for level, peptides in self.levels.items():
            structure['levels'][level] = []

            # Group peptides by their non-null components
            groups_at_level = {}
            for peptide in peptides:
                group_key = self._get_group_key(peptide)
                if group_key not in groups_at_level:
                    groups_at_level[group_key] = []
                groups_at_level[group_key].append(peptide)

            # Add groups to structure
            for group_key, group_peptides in groups_at_level.items():
                group_id = f"level{level}_group{len(structure['groups'])}"
                structure['groups'][group_id] = {
                    'peptides': group_peptides,
                    'level': level,
                    'key': group_key
                }
                structure['levels'][level].append(group_id)

        # Then, organize edges between groups
        for source_peptide, dest_peptides in self.descendants.items():
            source_group = self._find_group_for_peptide(source_peptide, structure['groups'])
            for dest_peptide in dest_peptides:
                dest_group = self._find_group_for_peptide(dest_peptide, structure['groups'])
                if source_group and dest_group:
                    edge = {
                        'source_group': source_group,
                        'target_group': dest_group,
                        'source': source_peptide,
                        'target': dest_peptide
                    }
                    structure['edges'].append(edge)

        return structure

    def _get_group_key(self, peptide: Peptide) -> str:
        """Generate a consistent key for grouping related peptides."""
        null_building_block = self.global_config.null_building_block
        components = [
            (i, block) for i, block in enumerate(peptide.sequence)
            if block != null_building_block
        ]
        return '_'.join(f"{i}:{block.name}" for i, block in sorted(components))

    def _find_group_for_peptide(self, peptide: Peptide, groups: Dict[str, Any]) -> Optional[str]:
        """Find the group ID containing a specific peptide."""
        for group_id, group_info in groups.items():
            if peptide in group_info['peptides']:
                return group_id
        return None

    def get_ordered_components(self, peptide: Peptide) -> List[BuildingBlock]:
        """
        Get the ordered list of non-null building blocks in a peptide.

        Args:
            peptide (Peptide): The peptide to analyze.

        Returns:
            List[BuildingBlock]: List of non-null building blocks in their original order.
        """
        return [block for block in peptide.sequence
                if block != self.global_config.null_building_block]

    def are_functionally_equivalent(self, peptide1: Peptide, peptide2: Peptide) -> bool:
        """
        Determine if two peptides are functionally equivalent (same non-null building blocks
        in the same order).

        Args:
            peptide1 (Peptide): First peptide to compare.
            peptide2 (Peptide): Second peptide to compare.

        Returns:
            bool: True if peptides are functionally equivalent.
        """
        blocks1 = set(self.get_non_null_blocks(peptide1))
        blocks2 = set(self.get_non_null_blocks(peptide2))
        return blocks1 == blocks2

    def get_non_null_blocks(self, peptide: Peptide) -> List[BuildingBlock]:
        """Get list of non-null building blocks in a peptide."""
        return [block for block in peptide.sequence
                if block != self.global_config.null_building_block]


    def with_peptides(self, peptides: List[Peptide]) -> 'Hierarchy':
        """
        Create a new hierarchy instance with updated peptides.

        Args:
            peptides (List[Peptide]): The list of peptides to add.

        Returns:
            Hierarchy: A new Hierarchy instance with updated peptides.
        """
        new_instance = self.clone()
        new_instance.add_peptides(peptides)
        return new_instance

    def with_properties(self, **kwargs: Any) -> 'Hierarchy':
            """Create a new hierarchy instance with updated properties."""
            new_properties = self.properties.copy()
            new_properties.update(kwargs)
            return self.clone(properties=new_properties)

    def with_metadata(self, **kwargs: Any) -> 'Hierarchy':
        """Create a new hierarchy instance with updated metadata."""
        new_metadata = self.metadata.copy()
        new_metadata.update(kwargs)
        return self.clone(metadata=new_metadata)
