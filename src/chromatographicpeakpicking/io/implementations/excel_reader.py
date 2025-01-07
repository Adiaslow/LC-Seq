# src/chromatographicpeakpicking/io/implementations/excel_reader.py
"""Excel reader implementation."""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Union, BinaryIO, TextIO, Optional
import pandas as pd

from src.chromatographicpeakpicking.core.interfaces.reader import Reader, ReadResult
from src.chromatographicpeakpicking.core.types.validation import ValidationResult
from src.chromatographicpeakpicking.core.types.config import BaseConfig

@dataclass
class ExcelReaderConfig(BaseConfig):
    """Configuration for Excel reader.

    Attributes:
        sheet_name: Name or index of sheet to read
        has_headers: Whether the sheet has header row
        expected_columns: List of expected column names
        dtype_map: Mapping of column names to their expected data types
        skip_rows: Number of rows to skip at start of sheet
    """
    sheet_name: Optional[str] = None
    has_headers: bool = True
    expected_columns: Optional[List[str]] = None
    dtype_map: Dict[str, str] = field(default_factory=dict)
    skip_rows: int = 0

class ExcelReader(Reader[ExcelReaderConfig, pd.DataFrame]):
    """Reader implementation for Excel files.

    Reads Excel files (xlsx, xls) into pandas DataFrames with configurable
    options for sheet selection and data types.
    """
    def __init__(self):
        self._config: Optional[ExcelReaderConfig] = None

    def configure(self, config: ExcelReaderConfig) -> ValidationResult:
        """Configure the Excel reader.

        Args:
            config: Configuration parameters for Excel reading

        Returns:
            ValidationResult indicating if configuration is valid
        """
        validation = self.validate_config(config)
        if validation.is_valid:
            self._config = config
        return validation

    def validate_config(self, config: ExcelReaderConfig) -> ValidationResult:
        """Validate the configuration.

        Checks:
            - Skip rows is non-negative
            - Expected columns format if provided
            - Data type mappings are valid pandas dtypes
        """
        errors = []

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
        """Read Excel data into a pandas DataFrame.

        Args:
            source: Excel file path or file-like object

        Returns:
            ReadResult containing DataFrame and metadata

        Raises:
            IOError: If reading fails
            ValueError: If Excel format is invalid or doesn't match expectations
        """
        if not self._config:
            raise ValueError("Reader must be configured before use")

        try:
            # Get Excel file info first
            with pd.ExcelFile(source) as xls:
                sheet_name = self._config.sheet_name or xls.sheet_names[0]
                excel_metadata = {
                    "sheet_name": sheet_name,
                    "total_sheets": len(xls.sheet_names),
                    "available_sheets": xls.sheet_names
                }

                # Read the specified sheet with explicit parameters
                df = pd.read_excel(
                    xls,
                    sheet_name=sheet_name
                )

            if self._config.expected_columns:
                missing_cols = set(self._config.expected_columns) - set(df.columns)
                if missing_cols:
                    raise ValueError(f"Missing expected columns: {missing_cols}")

            metadata = {
                "num_rows": len(df),
                "num_cols": len(df.columns),
                "memory_usage": df.memory_usage(deep=True).sum(),
                **excel_metadata
            }

            return ReadResult(df, metadata)

        except Exception as e:
            raise IOError(f"Failed to read Excel file: {str(e)}") from e

    def can_read(self, source: Union[str, Path, BinaryIO, TextIO]) -> bool:
        """Check if source appears to be a valid Excel file.

        Args:
            source: Source to check

        Returns:
            True if source appears to be readable Excel file, False otherwise
        """
        if isinstance(source, (str, Path)):
            path = str(source).lower()
            return path.endswith(('.xlsx', '.xls', '.xlsm'))

        # For file-like objects, try to use pandas to check
        try:
            pd.ExcelFile(source)
            return True
        except Exception:
            return False
