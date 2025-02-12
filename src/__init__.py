# src/__init__.py
"""
This module provides the root package for the LC-seq project.

This is the main entry point for the LC-seq package, which provides tools for
analyzing liquid chromatography sequencing data. Rather than using wildcard imports,
we explicitly import and expose the public API.
"""

from .lcseq import (  # Core data structures; I/O utilities; Pipeline components; Pre-configured pipelines
    BuildingBlock, BuildingBlockRegistry, Chromatogram, ChromatogramDataParser,
    ColumnMapping, CompactChromDumper, GPPPipe, HierarchicalPipe, Peak,
    Peptide, PeptideDataReader, PeptideDataWriter, PeptideEncoding,
    PeptideHierarchy, PeptideHierarchyInput, PeptideHierarchyNode,
    PeptideSetInput, Pipeline, PipelineComponent, ProcessableInput,
    SinglePeptideInput, StandardPipe, SynthesisStatus, TPipe)

__all__: list[str] = [
    # Core data structures
    "Peptide",
    "PeptideHierarchy",
    "PeptideHierarchyNode",
    "PeptideEncoding",
    "Chromatogram",
    "Peak",
    "BuildingBlock",
    "BuildingBlockRegistry",
    "SynthesisStatus",
    # I/O utilities
    "ColumnMapping",
    "ChromatogramDataParser",
    "CompactChromDumper",
    "PeptideDataReader",
    "PeptideDataWriter",
    # Pipeline components
    "ProcessableInput",
    "SinglePeptideInput",
    "PeptideSetInput",
    "PeptideHierarchyInput",
    "PipelineComponent",
    "Pipeline",
    # Pre-configured pipelines
    "GPPPipe",
    "HierarchicalPipe",
    "StandardPipe",
    "TPipe",
]
