# src/lcseq/core/peptide.py
"""
This module defines the Peptide and PeptideEncoding classes,
which represent the basic structure of peptides and their encodings.

Classes:
    PeptideEncoding: Represents a specific encoding of a peptide with its associated chromatogram.
    Peptide: Represents a peptide with its possible encodings.
"""

# Standard library imports
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional

# Local application imports
from src.lcseq.core.building_block import BuildingBlock
from src.lcseq.core.chromatogram import Chromatogram

@dataclass(eq=True)
class PeptideEncoding:
    """Represents a specific encoding of a peptide with its associated chromatogram.
    
    Attributes:
        blocks (List[BuildingBlock]): The blocks that make up the encoding.
        chromatogram (Optional[Chromatogram]): The chromatogram associated with the encoding.
        properties (Dict): The properties of the encoding.

    Methods:
        __post_init__: Validate encoding blocks.
        sequence: Get the sequence as a string.
        sequence_str: Get the canonical sequence as a string.
        __str__: Get the sequence as a string.
    """
    blocks: List[BuildingBlock]
    chromatogram: Optional[Chromatogram] = None
    properties: Dict = field(default_factory=dict)

    def __post_init__(self):
        """Validate encoding blocks.

        Raises:
            ValueError: If all blocks are not BuildingBlock instances.
        """
        if not all(isinstance(block, BuildingBlock) for block in self.blocks):
            raise ValueError("All blocks must be BuildingBlock instances")

    @property
    def sequence(self) -> str:
        """Get the sequence as a string.

        Returns:
            str: The sequence as a string.
        """
        return self.sequence_str

    @property
    def sequence_str(self) -> str:
        """Get the canonical sequence as a string.

        Returns:
            str: The canonical sequence as a string.
        """
        return '-'.join([block.identifier for block in self.blocks][::-1])

    def __str__(self) -> str:
        """Get the sequence as a string.

        Returns:
            str: The sequence as a string.
        """
        return self.sequence_str

@dataclass
class Peptide:
    """Represents a peptide with its possible encodings.
    
    Attributes:
        sequence (List[BuildingBlock]): The sequence of the peptide.
        encodings (List[PeptideEncoding]): The possible encodings of the peptide.
        properties (Dict): The properties of the peptide.

    Methods:
        __post_init__: Validate the peptide sequence.
        sequence_str: Get the canonical sequence as a string.
        add_encoding: Add a new encoding to the peptide.
        remove_encoding: Remove an encoding from the peptide.
        get_encoding: Get a specific encoding by its sequence.
    """
    sequence: List[BuildingBlock]
    encodings: List[PeptideEncoding] = field(default_factory=list)
    properties: Dict = field(default_factory=dict)

    def __post_init__(self):
        """Validate the peptide sequence.

        Raises:
            ValueError: If the sequence is empty or contains non-BuildingBlock instances.
        """
        if not self.sequence:
            raise ValueError("Peptide sequence cannot be empty")

        if not all(isinstance(block, BuildingBlock) for block in self.sequence):
            raise ValueError("All sequence items must be BuildingBlock instances")

    @property
    def sequence_str(self) -> str:
        """Get the canonical sequence as a string.

        Returns:
            str: The canonical sequence as a string.
        """
        return '-'.join([block.identifier for block in self.sequence][::-1])

    def add_encoding(self, encoding: PeptideEncoding) -> None:
        """Add a new encoding to the peptide.
        
        Args:
            encoding (PeptideEncoding): The encoding to add.
        """
        if not isinstance(encoding, PeptideEncoding):
            raise ValueError("Encoding must be a PeptideEncoding instance")
        self.encodings.append(encoding)

    def remove_encoding(self, encoding: PeptideEncoding) -> None:
        """Remove an encoding from the peptide.

        Args:
            encoding (PeptideEncoding): The encoding to remove.
        """
        if encoding in self.encodings:
            self.encodings.remove(encoding)

    def get_encoding(self, sequence: str) -> Optional[PeptideEncoding]:
        """Get a specific encoding by its sequence.

        Args:
            sequence (str): The sequence of the encoding to get.

        Returns:
            Optional[PeptideEncoding]: The encoding if found, otherwise None.
        """
        for encoding in self.encodings:
            if encoding.sequence == sequence:
                return encoding
        return None

    def __eq__(self, other):
        """Check if two peptides are equal.

        Args:
            other: The other peptide to compare to.

        Returns:
            bool: True if the peptides are equal, False otherwise.
        """
        if not isinstance(other, Peptide):
            return False
        return self.sequence_str == other.sequence_str

    def __str__(self) -> str:
        """Get the sequence as a string.

        Returns:
            str: The sequence as a string.
        """
        return self.sequence_str

    def __hash__(self) -> int:
        """Get the hash of the peptide.

        Returns:
            int: The hash of the peptide.
        """
        return hash(self.sequence_str)
