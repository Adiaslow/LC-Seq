# src/chromatographicpeakpicking/io/implementations/csv_reader.py
"""CSV reader implementation."""
from dataclasses import dataclass, field
import csv
from pathlib import Path
from typing import Dict, List, Optional, Union, BinaryIO, TextIO
import pandas as pd

from src.chromatographicpeakpicking.core.interfaces.reader import Reader, ReadResult
from src.chromatographicpeakpicking.core.types.validation import ValidationResult
from src.chromatographicpeakpicking.core.types.config import BaseConfig

@dataclass
class CSVReaderConfig(BaseConfig):
    """Configuration for CSV reader.

    Attributes:
        delimiter: CSV delimiter character
        has_headers: Whether the CSV has header row
        encoding: File encoding
        expected_columns: List of expected column names
        dtype_map: Mapping of column names to their expected data types
        skip_rows: Number of rows to skip at start of file
    """
    delimiter: str = ","
    has_headers: bool = True
    encoding: str = "utf-8"
    expected_columns: Optional[List[str]] = None
    dtype_map: Dict[str, str] = field(default_factory=dict)
    skip_rows: int = 0

class CSVReader(Reader[CSVReaderConfig, pd.DataFrame]):
    """Reader implementation for CSV files.

    Reads CSV files into pandas DataFrames with configurable options for
    delimiter, encoding, and data types.
    """
    def __init__(self):
        self._config: Optional[CSVReaderConfig] = None

    def configure(self, config: CSVReaderConfig) -> ValidationResult:
        """Configure the CSV reader.

        Args:
            config: Configuration parameters for CSV reading

        Returns:
            ValidationResult indicating if configuration is valid
        """
        validation = self.validate_config(config)
        if validation.is_valid:
            self._config = config
        return validation

    def validate_config(self, config: CSVReaderConfig) -> ValidationResult:
        """Validate the configuration.

        Checks:
            - Delimiter is single character
            - Encoding is valid
            - Skip rows is non-negative
            - Expected columns format if provided
            - Data type mappings are valid pandas dtypes
        """
        errors = []

        if len(config.delimiter) != 1:
            errors.append("Delimiter must be a single character")

        try:
            "test".encode(config.encoding)
        except LookupError:
            errors.append(f"Invalid encoding: {config.encoding}")

        if config.skip_rows < 0:
            errors.append("skip_rows must be non-negative")

        if config.expected_columns:
            if not all(isinstance(col, str) for col in config.expected_columns):
                errors.append("All expected column names must be strings")

        for dtype in config.dtype_map.values():
            try:
                pd.api.types.pandas_dtype(dtype)
            except TypeError:
                errors.append(f"Invalid pandas dtype: {dtype}")

        return ValidationResult(not bool(errors), errors)

    def read(self, source: Union[str, Path, BinaryIO, TextIO]) -> ReadResult[pd.DataFrame]:
            """Read CSV data into a pandas DataFrame.

            Args:
                source: CSV file path or file-like object

            Returns:
                ReadResult containing DataFrame and metadata

            Raises:
                IOError: If reading fails
                ValueError: If CSV format is invalid or doesn't match expectations
            """
            if not self._config:
                raise ValueError("Reader must be configured before use")

            try:
                df = pd.read_csv(
                    filepath_or_buffer=source,
                    delimiter=self._config.delimiter,
                    header=0 if self._config.has_headers else None,
                    encoding=self._config.encoding,
                    dtype={k: pd.api.types.pandas_dtype(v) for k,v in self._config.dtype_map.items()} if self._config.dtype_map else None,
                    skiprows=self._config.skip_rows
                )

                if self._config.expected_columns:
                    missing_cols = set(self._config.expected_columns) - set(df.columns)
                    if missing_cols:
                        raise ValueError(f"Missing expected columns: {missing_cols}")

                metadata = {
                    "num_rows": len(df),
                    "num_cols": len(df.columns),
                    "memory_usage": df.memory_usage(deep=True).sum()
                }

                return ReadResult(df, metadata)

            except Exception as e:
                raise IOError(f"Failed to read CSV: {str(e)}") from e

    def can_read(self, source: Union[str, Path, BinaryIO, TextIO]) -> bool:
            """Check if source appears to be a valid CSV file.

            Args:
                source: Source to check

            Returns:
                True if source appears to be readable CSV, False otherwise
            """
            if isinstance(source, (str, Path)):
                path = str(source)
                return path.lower().endswith('.csv')

            # For file-like objects, try to read content
            try:
                if isinstance(source, BinaryIO):
                    sample = source.read(1024).decode('utf-8')
                else:
                    sample = source.read(1024)
                source.seek(0)  # Reset position
                dialect = csv.Sniffer().sniff(sample)
                return True
            except Exception:
                return False
