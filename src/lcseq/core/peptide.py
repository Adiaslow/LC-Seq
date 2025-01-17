# src/lcseq/core/peptide.py
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional
from .building_block import BuildingBlock
from .chromatogram import Chromatogram

@dataclass(eq=True)
class PeptideEncoding:
    """Represents a specific encoding of a peptide with its associated chromatogram."""
    blocks: List[BuildingBlock]
    chromatogram: Optional[Chromatogram] = None
    properties: Dict = field(default_factory=dict)

    def __post_init__(self):
        """Validate encoding blocks."""
        if not all(isinstance(block, BuildingBlock) for block in self.blocks):
            raise ValueError("All blocks must be BuildingBlock instances")

    @property
    def sequence(self) -> str:
        """Get the sequence as a string."""
        return self.sequence_str

    @property
    def sequence_str(self) -> str:
        """Get the canonical sequence as a string."""
        return '-'.join([block.identifier for block in self.blocks][::-1])

    def __str__(self) -> str:
        return self.sequence_str

@dataclass
class Peptide:
    """Represents a peptide with its possible encodings."""
    sequence: List[BuildingBlock]
    encodings: List[PeptideEncoding] = field(default_factory=list)
    properties: Dict = field(default_factory=dict)

    def __post_init__(self):
        """Validate the peptide sequence."""
        if not self.sequence:
            raise ValueError("Peptide sequence cannot be empty")

        if not all(isinstance(block, BuildingBlock) for block in self.sequence):
            raise ValueError("All sequence items must be BuildingBlock instances")

    @property
    def sequence_str(self) -> str:
        """Get the canonical sequence as a string."""
        return '-'.join([block.identifier for block in self.sequence][::-1])

    def add_encoding(self, encoding: PeptideEncoding) -> None:
        """Add a new encoding to the peptide."""
        if not isinstance(encoding, PeptideEncoding):
            raise ValueError("Encoding must be a PeptideEncoding instance")
        self.encodings.append(encoding)

    def remove_encoding(self, encoding: PeptideEncoding) -> None:
        """Remove an encoding from the peptide."""
        if encoding in self.encodings:
            self.encodings.remove(encoding)

    def get_encoding(self, sequence: str) -> Optional[PeptideEncoding]:
        """Get a specific encoding by its sequence."""
        for encoding in self.encodings:
            if encoding.sequence == sequence:
                return encoding
        return None

    def __eq__(self, other):
        if not isinstance(other, Peptide):
            return False
        return self.sequence_str == other.sequence_str

    def __str__(self) -> str:
        return self.sequence_str

    def __hash__(self) -> int:
        return hash(self.sequence_str)
