# src/lcseq/pipelines/__init__.py
"""
This module provides the pipelines for the LC-seq project.
"""

# Local application imports
from src.lcseq.pipelines.gpp import GPPPipe
from src.lcseq.pipelines.hierarchical import HierarchicalPipe
from src.lcseq.pipelines.standard import StandardPipe
from src.lcseq.pipelines.tpipe import TPipe

__all__: list[str] = [
    # "CC",
    "GPPPipe",
    "HierarchicalPipe",
    "TPipe",
    "StandardPipe",
]
