# src/lcseq/pipeline/components/io/__init__.py
"""
This module provides a pipeline component for handling input and output data.
It includes classes for standard input and output, and test input and output.
"""

from src.lcseq.pipeline.components.io.standard_input import StandardInput
# Local application imports
from src.lcseq.pipeline.components.io.standard_output import StandardOutput
from src.lcseq.pipeline.components.io.test_input import TestInput
from src.lcseq.pipeline.components.io.test_output import TestOutput

__all__: list[str] = [
    "StandardInput",
    "StandardOutput",
    "TestInput",
    "TestOutput",
]
