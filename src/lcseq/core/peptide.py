# src/lcseq/core/peptide.py
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional
from .building_block import BuildingBlock
from .chromatogram import Chromatogram

@dataclass
class PeptideEncoding:
    """Represents a specific encoding of a peptide with its associated chromatogram."""
    blocks: List[BuildingBlock]
    chromatogram: Optional[Chromatogram] = None
    properties: Dict = field(default_factory=dict)

    @property
    def sequence(self) -> str:
        """Get the sequence as a string."""
        return ''.join(block.identifier for block in self.blocks)

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

    @property
    def sequence_str(self) -> str:
        """Get the canonical sequence as a string."""
        return ''.join(block.identifier for block in self.sequence)

    def add_encoding(self, encoding: PeptideEncoding) -> None:
        """Add a new encoding to the peptide."""
        self.encodings.append(encoding)

    def get_encoding(self, sequence: str) -> Optional[PeptideEncoding]:
        """Get a specific encoding by its sequence."""
        for encoding in self.encodings:
            if encoding.sequence == sequence:
                return encoding
        return None
