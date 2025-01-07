# src/chromatographicpeakpicking/pipeline/stages/csv_input_stage.py
"""This module implements the CSVInputStage class, which handles reading CSV data."""

from pathlib import Path
from typing import Any, Dict

from src.chromatographicpeakpicking.core.pipeline.stages.input_stage import InputStage
from src.chromatographicpeakpicking.core.interfaces.pipeline_stage import PipelineStageResult
from src.chromatographicpeakpicking.core.pipeline.pipeline import PipelineConfig
from src.chromatographicpeakpicking.io.implementations.csv_reader import CSVReader, CSVReaderConfig
from src.chromatographicpeakpicking.core.types.validation import (
    ValidationResult, ValidationMessage, ValidationLevel
)

class DefaultCSVInputStage(InputStage):
    """Pipeline stage for reading CSV data using CSVReader implementation."""

    def __init__(self, config: CSVReaderConfig):
        """Initialize CSV input stage with reader configuration.

        Args:
            config: Configuration for CSV reading

        Raises:
            ValueError: If the configuration is invalid
        """
        super().__init__()
        self.reader = CSVReader()
        validation_result = self.reader.configure(config)
        if not validation_result.is_valid:
            error_messages = [
                msg.message for msg in validation_result.messages
                if msg.level == ValidationLevel.ERROR
            ]
            raise ValueError(f"Invalid CSV reader configuration: {'; '.join(error_messages)}")

    def _parse_input(self, input_path: str) -> Any:
        """Parse CSV input file using configured CSVReader.

        Args:
            input_path: Path to CSV file

        Returns:
            pandas DataFrame containing the CSV data

        Raises:
            FileNotFoundError: If input file doesn't exist
            ValueError: If CSV format or content is invalid
            IOError: If reading fails
        """
        path = Path(input_path)
        if not path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        if not self.reader.can_read(path):
            raise ValueError(f"File is not a valid CSV: {input_path}")

        try:
            result = self.reader.read(path)
            return result.data

        except Exception as e:
            raise IOError(f"Failed to read CSV file: {str(e)}") from e

    def _extract_numeric_metrics(self, metadata: Dict[str, Any]) -> Dict[str, float]:
        """Extract numeric metrics from metadata.

        Args:
            metadata: Dictionary containing mixed-type metadata

        Returns:
            Dictionary containing only float metrics
        """
        numeric_metrics = {}
        for key, value in metadata.items():
            if isinstance(value, (int, float)):
                numeric_metrics[key] = float(value)
        return numeric_metrics

    def configure(self, config: PipelineConfig) -> ValidationResult:
        """Configure the pipeline stage."""
        validation_result = self.reader.configure(self.config)
        if not validation_result.is_valid:
            error_messages = [
                msg.message for msg in validation_result.messages
                if msg.level == ValidationLevel.ERROR
            ]
            return ValidationResult(False, [
                ValidationMessage("error", f"Invalid CSV reader configuration: {'; '.join(error_messages)}")
            ])
        return ValidationResult(True, [])

    def process(self, data: str) -> PipelineStageResult:
        """Process the input CSV file.

        Args:
            data: Path to input CSV file

        Returns:
            PipelineStageResult containing:
            - success: Whether processing succeeded
            - data: Parsed DataFrame if successful
            - metrics: Dictionary of numeric metrics
            - error_message: Error description if failed
        """
        input_path = data
        try:
            result = self.reader.read(input_path)
            numeric_metrics = self._extract_numeric_metrics(result.metadata)

            return PipelineStageResult(
                success=True,
                data=result.data,
                metrics=numeric_metrics
            )

        except Exception as e:
            return PipelineStageResult(
                success=False,
                data=None,
                metrics={},
                error_message=str(e)
            )
