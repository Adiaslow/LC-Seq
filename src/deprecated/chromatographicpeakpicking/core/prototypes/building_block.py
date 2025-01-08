# src/chromatographicpeakpicking/core/prototypes/building_block.py
"""This module defines the building block prototype.

    Classes:
        BuildingBlock: Represents a building block in a peptide sequence.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List
from src.chromatographicpeakpicking.core.interfaces.prototype import Prototype

@dataclass
class BuildingBlock(Prototype['BuildingBlock']):
    """Represents a building block in a peptide sequence."""
    name: str
    smiles: str
    properties: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def clone(self, **kwargs: Any) -> 'BuildingBlock':
        """Create a copy with optional overrides."""
        new_instance = BuildingBlock(
            name=kwargs.get('name', self.name),
            smiles=kwargs.get('smiles', self.smiles),
            properties=kwargs.get('properties', self.properties.copy()),
            metadata=kwargs.get('metadata', self.metadata.copy())
        )
        return new_instance

    def with_properties(self, **kwargs: Any) -> 'BuildingBlock':
        """Create a new instance with updated properties."""
        new_properties = self.properties.copy()
        new_properties.update(kwargs)
        return self.clone(properties=new_properties)

    def with_metadata(self, **kwargs: Any) -> 'BuildingBlock':
        """Create a new instance with updated metadata."""
        new_metadata = self.metadata.copy()
        new_metadata.update(kwargs)
        return self.clone(metadata=new_metadata)

    def validate(self) -> List[str]:
        """Validate the building block and return any errors."""
        errors = []
        if not self.name:
            errors.append("Building block name cannot be empty")
        return errors

    def __hash__(self) -> int:
        """Calculate a hash value for the building block."""
        return hash(self.name)
