# src/chromatographicpeakpicking/core/prototypes/peptide.py
"""This module defines the peptide prototype.

    Classes:
        Peptide: Represents a peptide sequence.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List
from src.chromatographicpeakpicking.core.prototypes.building_block import BuildingBlock
from src.chromatographicpeakpicking.core.interfaces.prototype import Prototype

@dataclass
class Peptide(Prototype['Peptide']):
    """Represents a peptide sequence."""
    sequence: List[BuildingBlock]
    properties: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def clone(self, **kwargs: Any) -> 'Peptide':
        return Peptide(
            sequence=kwargs.get('sequence', [b.clone() for b in self.sequence]),
            properties=kwargs.get('properties', self.properties.copy()),
            metadata=kwargs.get('metadata', self.metadata.copy())
        )

    def with_properties(self, **kwargs: Any) -> 'Peptide':
        new_properties = self.properties.copy()
        new_properties.update(kwargs)
        return self.clone(properties=new_properties)

    def with_metadata(self, **kwargs: Any) -> 'Peptide':
        new_metadata = self.metadata.copy()
        new_metadata.update(kwargs)
        return self.clone(metadata=new_metadata)

    def validate(self) -> List[str]:
        """Validate the peptide and return any errors."""
        errors = []
        if not self.sequence:
            errors.append("Peptide sequence cannot be empty")
        for i, block in enumerate(self.sequence):
            if not isinstance(block, BuildingBlock):
                errors.append(f"Invalid building block at position {i}")
            else:
                block_errors = block.validate()
                errors.extend(f"Block {i}: {error}" for error in block_errors)
        return errors

    def __hash__(self) -> int:
        """Calculate a hash value for the peptide.

        Args:
            None

        Returns:
            int: The hash value for

        Raises:
            None
        """
        return hash(tuple(hash(block) for block in self.sequence))
