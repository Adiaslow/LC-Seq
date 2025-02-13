# src/lcseq/core/building_block.py
"""
This module defines the BuildingBlock class and its registry for managing building blocks.
Building blocks are fundamental units of peptide sequences that can be used to build larger peptides.

Classes:
    BuildingBlock: Represents a fundamental building block of a peptide.
    BuildingBlockRegistry: Singleton registry for managing BuildingBlock instances.
"""

# Standard library imports
from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class BuildingBlock:
    """Represents a fundamental building block of a peptide.

    Attributes:
        identifier (str): The identifier of the building block.
        properties (Dict[str, Any]): The properties of the building block.

    Methods:
        __post_init__: Validate building block attributes after initialization.
        __eq__: Check if two building blocks are equal.
        __hash__: Get the hash of the building block.
    """

    identifier: str
    properties: Dict[str, Any]

    def __post_init__(self) -> None:
        """Validate building block attributes after initialization.

        Raises:
            ValueError: If the building block identifier is empty or the properties
                are not a dictionary or are None.
        """
        if not self.identifier:
            raise ValueError("Building block identifier cannot be empty")

        if self.properties is None:
            raise ValueError("Building block properties cannot be None")

        if not isinstance(self.properties, dict):
            raise ValueError("Building block properties must be a dictionary")

        if not self.properties:
            raise ValueError("Building block properties cannot be empty")

    def __eq__(self, other: Any) -> bool:
        """Check if two building blocks are equal.

        Args:
            other: The other building block to compare to.

        Returns:
            bool: True if the building blocks are equal, False otherwise.
        """
        if not isinstance(other, BuildingBlock):
            return False
        return self.identifier == other.identifier

    def __hash__(self) -> int:
        """Get the hash of the building block.

        Returns:
            int: The hash of the building block.
        """
        return hash(self.identifier)


class BuildingBlockRegistry:
    """Singleton registry for managing BuildingBlock instances.

    Attributes:
        _blocks (Dict[str, BuildingBlock]): A dictionary of registered building blocks.

    Methods:
        register: Register a new building block type.
        get: Retrieve a copy of a registered building block.
    """

    _blocks: Dict[str, BuildingBlock] = {}

    @classmethod
    def register(cls, block: BuildingBlock) -> None:
        """Register a new building block type.

        Args:
            block (BuildingBlock): The building block to register.

        Raises:
            ValueError: If the building block identifier is already registered.
        """
        if block.identifier in cls._blocks:
            pass
        else:
            cls._blocks[block.identifier] = block

    @classmethod
    def get(cls, identifier: str) -> BuildingBlock:
        """Retrieve a copy of a registered building block.

        Args:
            identifier (str): The identifier of the building block to retrieve.
        Returns:
            BuildingBlock: A copy of the requested building block.
        Raises:
            KeyError: If the building block is not found.
        """
        if identifier not in cls._blocks:
            raise KeyError(f"BuildingBlock {identifier} not found in registry")
        return deepcopy(cls._blocks[identifier])

    @classmethod
    def clear(cls) -> None:
        """Clear all registered building blocks.

        Raises:
            ValueError: If the registry is empty.
        """
        if not cls._blocks:
            raise ValueError("Registry is empty")
        cls._blocks.clear()
