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
from typing import Any, Dict, List, Optional

# Local application imports
from src.lcseq.core.building_block import BuildingBlock
from src.lcseq.core.chromatogram import Chromatogram


@dataclass(eq=True)
class PeptideEncoding:
    """Represents a specific encoding of a peptide with its associated chromatogram.

    An encoding represents a specific arrangement of building blocks, including null blocks.
    The canonical_sequence includes all blocks (including nulls), while the effective_sequence
    only includes non-null blocks.

    Attributes:
        blocks (List[BuildingBlock]): The blocks that make up the encoding
        chromatogram (Optional[Chromatogram]): The chromatogram associated with the encoding
        properties (Dict): The properties of the encoding, including retention_time if measured
    """

    blocks: List[BuildingBlock]
    chromatogram: Optional[Chromatogram] = None
    properties: Dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate encoding blocks.

        Raises:
            ValueError: If all blocks are not BuildingBlock instances.
        """
        if not all(isinstance(block, BuildingBlock) for block in self.blocks):
            raise ValueError("All blocks must be BuildingBlock instances")

    @property
    def canonical_sequence(self) -> List[str]:
        """Get the canonical sequence as a list of strings.

        Returns:
            List[str]: The canonical sequence including null blocks.
        """
        return [block.identifier for block in self.blocks]

    @property
    def canonical_sequence_str(self) -> str:
        """Get the canonical sequence as a hyphen-separated string.

        Returns:
            str: The canonical sequence string including null blocks.
        """
        return "-".join(self.canonical_sequence[::-1])

    @property
    def effective_sequence(self) -> List[str]:
        """Get the effective sequence as a list of strings.

        Returns:
            List[str]: The effective sequence without null blocks.
        """
        return [
            block.identifier for block in self.blocks if block.identifier != "AgxNull"
        ]

    @property
    def effective_sequence_str(self) -> str:
        """Get the effective sequence as a hyphen-separated string.

        Returns:
            str: The effective sequence string without null blocks.
        """
        return "-".join(self.effective_sequence[::-1])

    def __str__(self) -> str:
        """Get the sequence as a string.

        Returns:
            str: The sequence as a string.
        """
        return self.canonical_sequence_str

    def __hash__(self) -> int:
        """Get the hash of the encoding.

        Returns:
            int: The hash of the encoding.
        """
        return hash(self.canonical_sequence_str)


@dataclass
class Peptide:
    """Represents a peptide with its possible encodings.

    A peptide represents a sequence of building blocks with multiple possible encodings.
    Each encoding can include null blocks in different positions, but their effective
    sequences (non-null blocks) must match the peptide's sequence.

    Attributes:
        blocks (List[BuildingBlock]): The sequence of the peptide
        encodings (List[PeptideEncoding]): The possible encodings of the peptide
        properties (Dict): The properties of the peptide
    """

    blocks: List[BuildingBlock]
    encodings: List[PeptideEncoding] = field(default_factory=list)
    properties: Dict = field(default_factory=dict)

    @property
    def effective_sequence(self) -> List[str]:
        """Get the effective sequence as a list of strings.

        Returns:
            List[str]: The effective sequence without null blocks.
        """
        return [
            block.identifier for block in self.blocks if block.identifier != "AgxNull"
        ]

    @property
    def effective_sequence_str(self) -> str:
        """Get the effective sequence as a hyphen-separated string.

        Returns:
            str: The effective sequence string without null blocks.
        """
        return "-".join(self.effective_sequence[::-1])

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

    def get_encoding(self, sequence: List[str]) -> Optional[PeptideEncoding]:
        """Get a specific encoding by its canonical sequence.

        Args:
            sequence (List[str]): The canonical sequence to look for.

        Returns:
            Optional[PeptideEncoding]: The encoding if found, otherwise None.
        """
        for encoding in self.encodings:
            if encoding.canonical_sequence == sequence:
                return encoding
        return None

    def __eq__(self, other: Any) -> bool:
        """Check if two peptides are equal.

        Args:
            other: The other peptide to compare to.

        Returns:
            bool: True if the peptides are equal, False otherwise.
        """
        if not isinstance(other, Peptide):
            return False
        return self.effective_sequence == other.effective_sequence

    def __str__(self) -> str:
        """Get the sequence as a string.

        Returns:
            str: The sequence as a string.
        """
        return self.effective_sequence_str

    def __hash__(self) -> int:
        """Get the hash of the peptide.

        Returns:
            int: The hash of the peptide.
        """
        return hash(self.effective_sequence_str)

    def has_chromatogram(self) -> bool:
        """Check if the peptide has any encoding with a chromatogram.

        Returns:
            bool: True if any encoding has a chromatogram, False otherwise.
        """
        return any(encoding.chromatogram is not None for encoding in self.encodings)

    def get_chromatogram(self) -> Optional[Chromatogram]:
        """Get the chromatogram from the first encoding that has one.

        Returns:
            Optional[Chromatogram]: The chromatogram if found, otherwise None.
        """
        for encoding in self.encodings:
            if encoding.chromatogram is not None:
                return encoding.chromatogram
        return None
