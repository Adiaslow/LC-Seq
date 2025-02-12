# src/lcseq/pipelines/__init__.py
"""
This module provides the pipelines for the LC-seq project.
"""

# Local application imports
from src.lcseq.pipelines.gpp import GPP
from src.lcseq.pipelines.tpipe import TPipe
from src.lcseq.pipelines.standard import StandardPipe

__all__ = [
    # "CC",
    "GPP",
    "TPipe",
    "StandardPipe"
]
