# src/lcseq/io/readers.py
from dataclasses import dataclass
from typing import Dict, List, Callable, Optional
import pandas as pd
import yaml
from pathlib import Path

@dataclass
class ColumnMapping:
    """Defines how input columns map to output YAML structure."""
    building_block_columns: Dict[str, List[str]]
    peptide_property_columns: List[str]
    chromatogram_column: str
    identifier_column: str
    num_building_blocks: int

    @classmethod
    def from_config(cls, config_path: Path) -> 'ColumnMapping':
        """Create mapping from a YAML configuration file."""
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return cls(
            building_block_columns=config['building_block_columns'],
            peptide_property_columns=config['peptide_property_columns'],
            chromatogram_column=config['chromatogram_column'],
            identifier_column=config['identifier_column'],
            num_building_blocks=config['num_building_blocks']
        )

class ChromatogramDataParser:
    """Parser for different chromatogram data formats."""

    @staticmethod
    def parse_colon_semicolon(data: str) -> Dict[str, List[float]]:
        """Parse format: time:counts;scaled_counts, time:counts;scaled_counts, ..."""
        points = data.split(', ')
        times = []
        intensities = []
        scaled_intensities = []

        for point in points:
            time, counts = point.split(':')
            raw, scaled = counts.split(';')
            times.append(float(time))
            intensities.append(float(raw))
            scaled_intensities.append(float(scaled))

        # Sort by time
        sorted_data = sorted(zip(times, intensities, scaled_intensities))
        return {
            'times': [x[0] for x in sorted_data],
            'intensities': [x[1] for x in sorted_data],
            'scaled_intensities': [x[2] for x in sorted_data]
        }

    @staticmethod
    def parse_simple_csv(data: str) -> Dict[str, List[float]]:
        """Parse simple time,intensity format."""
        points = data.split(',')
        times, intensities = zip(*(point.split(',') for point in points))
        return {
            'times': [float(t) for t in times],
            'intensities': [float(i) for i in intensities]
        }

class PeptideDataReader:
    """Main class for reading and parsing peptide data."""

    def __init__(
        self,
        column_mapping: ColumnMapping,
        chromatogram_parser: Callable = ChromatogramDataParser.parse_colon_semicolon
    ):
        self.column_mapping = column_mapping
        self.chromatogram_parser = chromatogram_parser

    def read_csv(self, file_path: Path) -> Dict:
        """Read and parse CSV file into internal dictionary format."""
        df = pd.read_csv(file_path)
        return self._parse_dataframe(df)

    def _parse_dataframe(self, df: pd.DataFrame) -> Dict:
        """Parse DataFrame into internal dictionary format."""
        return {
            'building_blocks': self._parse_building_blocks(df),
            'peptides': self._parse_peptides(df),
            'metadata': self._parse_metadata(df)
        }

    def _parse_building_blocks(self, df: pd.DataFrame) -> Dict:
        building_blocks = {}

        for bb_idx in range(self.column_mapping.num_building_blocks):
            bb_data = {}
            for prop_type, columns in self.column_mapping.building_block_columns.items():
                bb_data[prop_type] = df[columns[bb_idx]].iloc[0]
            building_blocks[f'BB{bb_idx + 1}'] = bb_data

        return building_blocks

    def _parse_peptides(self, df: pd.DataFrame) -> List[Dict]:
        """Parse DataFrame into peptide entries with chromatogram data.

        Returns a list of dictionaries, each containing peptide information
        including sequence, properties, and chromatogram data in flow format.
        """
        peptides = []
        for _, row in df.iterrows():
            # Parse the chromatogram data
            parsed_data = self.chromatogram_parser(
                row[self.column_mapping.chromatogram_column]
            )

            # Create chromatogram data without extra nesting
            chromatogram_data = {
                'times': parsed_data['times'],
                'intensities': parsed_data['intensities'],
                'scaled_intensities': parsed_data['scaled_intensities']
            }

            peptide = {
                'identifier': row[self.column_mapping.identifier_column],
                'sequence': [
                    f'BB{i+1}'
                    for i in range(self.column_mapping.num_building_blocks)
                ],
                'properties': {
                    col: row[col]
                    for col in self.column_mapping.peptide_property_columns
                },
                'chromatogram': chromatogram_data
            }
            peptides.append(peptide)

        return peptides

    def _parse_metadata(self, df: pd.DataFrame) -> Dict:
        """Extract metadata from the DataFrame."""
        return {
            'num_peptides': len(df),
            'num_building_blocks': self.column_mapping.num_building_blocks,
            'property_columns': self.column_mapping.peptide_property_columns
        }
