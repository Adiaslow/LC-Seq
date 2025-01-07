# src/chromatographicpeakpicking/core/interfaces/reader.py
"""This module defines the generic interface for data reading algorithms.

Classes:
    ReadResult: Base class for read operation results.
    Reader: Generic interface for data reading algorithms.
"""
from abc import ABC, abstractmethod
from typing import Dict, Generic, TypeVar, Union, BinaryIO, TextIO
from pathlib import Path
from src.chromatographicpeakpicking.core.types.config import BaseConfig
from src.chromatographicpeakpicking.core.types.validation import ValidationResult

# Type variables for configuration and result
C = TypeVar('C', bound=BaseConfig)
R = TypeVar('R')  # Result type

class ReadResult(Generic[R]):
    """Base class for read operation results.

    Attributes:
        data: The read data
        metadata: Additional metadata about the read operation
    """
    def __init__(self, data: R, metadata: Dict[str, Union[float, str]]):
        self.data = data
        self.metadata = metadata

class Reader(Generic[C, R], ABC):
    """Generic interface for data reading algorithms.

    Type Parameters:
        C: Configuration type (must be a BaseConfig)
        R: Result type
    """
    @abstractmethod
    def configure(self, config: C) -> ValidationResult:
        """Configure the reader with given parameters."""
        raise NotImplementedError

    @abstractmethod
    def validate_config(self, config: C) -> ValidationResult:
        """Validate the configuration."""
        raise NotImplementedError

    @abstractmethod
    def read(self, source: Union[str, Path, BinaryIO, TextIO]) -> ReadResult[R]:
        """Read data from the source and return results with metadata.

        Args:
            source: Input source, can be a file path (as string or Path) or file-like object

        Returns:
            ReadResult containing the read data and operation metadata

        Raises:
            IOError: If reading from source fails
            ValueError: If source format is invalid
        """
        raise NotImplementedError

    @abstractmethod
    def can_read(self, source: Union[str, Path, BinaryIO, TextIO]) -> bool:
        """Check if this reader can handle the given source.

        Args:
            source: Input source to check

        Returns:
            True if this reader can handle the source, False otherwise
        """
        raise NotImplementedError
