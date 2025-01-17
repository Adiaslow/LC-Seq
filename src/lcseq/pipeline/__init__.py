# src/lcseq/pipeline/__init__.py
"""
This module initializes the lcseq.pipeline package, making key classes and types
available for easy import. It includes classes and types for processing different
types of peptide inputs through a pipeline.

Classes and types:
    ProcessableInput: Base class for all processable inputs.
    SinglePeptideInput: Represents a single peptide input.
    PeptideSetInput: Represents a set of peptide inputs.
    PeptideHierarchyInput: Represents a hierarchy of peptide inputs.
    PipelineComponent: Abstract base class for pipeline components.
    Pipeline: Defines a pipeline of processing components.
"""

from src.lcseq.pipeline.input_types import (
    ProcessableInput,
    SinglePeptideInput,
    PeptideSetInput,
    PeptideHierarchyInput
)
from src.lcseq.pipeline.base import PipelineComponent
from src.lcseq.pipeline.pipeline import Pipeline

__all__ = [
    "ProcessableInput",
    "SinglePeptideInput",
    "PeptideSetInput",
    "PeptideHierarchyInput",
    "PipelineComponent",
    "Pipeline"
]
