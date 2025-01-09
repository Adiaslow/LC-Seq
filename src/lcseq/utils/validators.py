# src/lcseq/utils/validators.py
from dataclasses import dataclass
from typing import Dict, List
import pandas as pd
from pathlib import Path
from src.lcseq.io.readers import ColumnMapping

@dataclass
class DataValidator:
    """Validates input data against expected format."""

    @staticmethod
    def validate_column_mapping(df: pd.DataFrame, mapping: 'ColumnMapping') -> List[str]:
        """Validate that all mapped columns exist in the DataFrame."""
        errors = []

        # Check building block columns
        for prop_type, columns in mapping.building_block_columns.items():
            for col in columns:
                if col not in df.columns:
                    errors.append(f"Missing building block column: {col}")

        # Check peptide property columns
        for col in mapping.peptide_property_columns:
            if col not in df.columns:
                errors.append(f"Missing peptide property column: {col}")

        # Check chromatogram column
        if mapping.chromatogram_column not in df.columns:
            errors.append(f"Missing chromatogram column: {mapping.chromatogram_column}")

        # Check identifier column
        if mapping.identifier_column not in df.columns:
            errors.append(f"Missing identifier column: {mapping.identifier_column}")

        return errors

    @staticmethod
    def validate_chromatogram_data(data: str, format_type: str) -> List[str]:
        """Validate chromatogram data format."""
        errors = []

        if format_type == 'colon_semicolon':
            try:
                points = data.split(', ')
                for point in points:
                    time, counts = point.split(':')
                    raw, scaled = counts.split(';')
                    float(time)
                    float(raw)
                    float(scaled)
            except Exception as e:
                errors.append(f"Invalid chromatogram data format: {str(e)}")

        return errors
