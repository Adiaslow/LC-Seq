# src/chromatographicpeakpicking/core/interfaces/writer.py
"""This module defines the generic interface for data writing algorithms.

Classes:
    WriteResult: Base class for write operation results.
    Writer: Generic interface for data writing algorithms.
"""
from abc import ABC, abstractmethod
from typing import Dict, Generic, TypeVar, Union, BinaryIO, TextIO
from pathlib import Path
from src.chromatographicpeakpicking.core.types.config import BaseConfig
from src.chromatographicpeakpicking.core.types.validation import ValidationResult

# Type variables for configuration and data
C = TypeVar('C', bound=BaseConfig)
D = TypeVar('D')  # Data type

class WriteResult:
    """Base class for write operation results.

    Attributes:
        success: Whether the write operation was successful
        metadata: Additional metadata about the write operation
    """
    def __init__(self, success: bool, metadata: Dict[str, Union[float, str]]):
        self.success = success
        self.metadata = metadata

class Writer(Generic[C, D], ABC):
    """Generic interface for data writing algorithms.

    Type Parameters:
        C: Configuration type (must be a BaseConfig)
        D: Data type to write
    """
    @abstractmethod
    def configure(self, config: C) -> ValidationResult:
        """Configure the writer with given parameters."""
        raise NotImplementedError

    @abstractmethod
    def validate_config(self, config: C) -> ValidationResult:
        """Validate the configuration."""
        raise NotImplementedError

    @abstractmethod
    def write(self, data: D, target: Union[str, Path, BinaryIO, TextIO]) -> WriteResult:
        """Write data to the target and return operation results.

        Args:
            data: Data to write
            target: Output target, can be a file path (as string or Path) or file-like object

        Returns:
            WriteResult containing operation success status and metadata

        Raises:
            IOError: If writing to target fails
            ValueError: If data format is invalid for this writer
        """
        raise NotImplementedError

    @abstractmethod
    def can_write(self, data: D, target: Union[str, Path, BinaryIO, TextIO]) -> bool:
        """Check if this writer can handle the given data and target.

        Args:
            data: Data to check
            target: Output target to check

        Returns:
            True if this writer can handle the data and target, False otherwise
        """
        raise NotImplementedError
