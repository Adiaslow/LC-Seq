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
            'times': [x[0]/60 for x in sorted_data],
            'intensities': [x[1] for x in sorted_data],
            'scaled_intensities': [x[2] for x in sorted_data]
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
        self._position_to_blocks = {}  # Will store block mapping during parsing

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
        """Parse building blocks into new hierarchical format."""
        building_blocks = {}

        # Parse blocks by position
        for position in range(1, self.column_mapping.num_building_blocks + 1):
            position_key = f'BB{position}'
            building_blocks[position_key] = {}

            idx = position - 1  # Array index for column names
            name_col = self.column_mapping.building_block_columns['name'][idx]
            smiles_col = self.column_mapping.building_block_columns['smiles'][idx]
            stereochem_col = self.column_mapping.building_block_columns['stereochem'][idx]

            # Get unique blocks for this position
            unique_blocks = df[[name_col, smiles_col, stereochem_col]].drop_duplicates()

            for _, block in unique_blocks.iterrows():
                name = block[name_col]
                if pd.isna(name) or name == '-':  # type: ignore
                    continue

                # Store block data under its name
                building_blocks[position_key][name] = {
                    'smiles': block[smiles_col],
                    'stereochem': block[stereochem_col].rstrip(',') # type: ignore
                }

        return building_blocks

    def _parse_peptides(self, df: pd.DataFrame) -> List[Dict]:
        """Parse DataFrame into peptide entries with sequence and properties."""
        peptides = []

        for idx, row in df.iterrows():
            try:
                # Get identifier from specified column
                identifier = row[self.column_mapping.identifier_column]

                # Parse chromatogram data
                chrom_data = row[self.column_mapping.chromatogram_column]
                parsed_chrom = self.chromatogram_parser(chrom_data)

                # Get sequence from name columns
                sequence = []
                for bb_idx in range(self.column_mapping.num_building_blocks):
                    name_col = self.column_mapping.building_block_columns['name'][bb_idx]
                    bb_name = row[name_col]
                    if pd.notna(bb_name) and bb_name != '-':  # type: ignore
                        sequence.append(bb_name)

                peptide = {
                    'identifier': identifier,
                    'sequence': sequence,
                    'properties': {
                        col: float(row[col]) if pd.notna(row[col]) else None  # type: ignore
                        for col in self.column_mapping.peptide_property_columns
                    },
                    'chromatogram': parsed_chrom
                }
                peptides.append(peptide)

            except Exception as e:
                print(f"Error processing row {idx}: {str(e)}")
                continue

        return peptides

    def _parse_metadata(self, df: pd.DataFrame) -> Dict:
        """Extract metadata from the DataFrame."""
        return {
            'num_peptides': len(df),
            'num_building_blocks': self.column_mapping.num_building_blocks,
            'property_columns': self.column_mapping.peptide_property_columns
        }
