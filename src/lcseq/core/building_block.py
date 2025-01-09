# src/lcseq/core/building_block.py
from dataclasses import dataclass
from typing import Any, Dict, Optional
from copy import deepcopy

@dataclass
class BuildingBlock:
    """Represents a fundamental building block of a peptide."""
    identifier: str
    properties: Dict[str, Any]

    def __eq__(self, other):
        if not isinstance(other, BuildingBlock):
            return False
        return self.identifier == other.identifier

    def __hash__(self):
        return hash(self.identifier)

class BuildingBlockRegistry:
    """Singleton registry for managing BuildingBlock instances."""
    _blocks: Dict[str, BuildingBlock] = {}

    @classmethod
    def register(cls, block: BuildingBlock) -> None:
        """Register a new building block type."""
        cls._blocks[block.identifier] = block

    @classmethod
    def get(cls, identifier: str) -> BuildingBlock:
        """Retrieve a copy of a registered building block."""
        if identifier not in cls._blocks:
            raise KeyError(f"BuildingBlock {identifier} not found in registry")
        return deepcopy(cls._blocks[identifier])

    @classmethod
    def clear(cls) -> None:
        """Clear all registered building blocks."""
        cls._blocks.clear()
