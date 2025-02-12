# src/lcseq/core/__init__.py
"""Core module initialization.

This module provides the core domain models and abstractions for the LC-Seq analysis package.
Exports fundamental classes for building blocks, chromatograms, peaks, peptides and hierarchies.
"""

# Local application imports
from src.lcseq.core.building_block import BuildingBlock, BuildingBlockRegistry
from src.lcseq.core.chromatogram import Chromatogram
from src.lcseq.core.hierarchy import PeptideHierarchy, PeptideHierarchyNode
from src.lcseq.core.peak import Peak
from src.lcseq.core.peptide import Peptide, PeptideEncoding
from src.lcseq.core.synthesis_status import SynthesisStatus

__all__ = [
    "BuildingBlock",
    "BuildingBlockRegistry",
    "Chromatogram",
    "Peak",
    "Peptide",
    "PeptideEncoding",
    "PeptideHierarchy",
    "PeptideHierarchyNode",
    "SynthesisStatus"
]
