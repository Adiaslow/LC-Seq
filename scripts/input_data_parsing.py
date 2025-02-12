# scripts/input_data_parsing.py
"""
This script is used to parse the input data and save it to a YAML file.
"""

# Standard library imports
from pathlib import Path

# Local application imports
from src.lcseq.io.readers import ColumnMapping, PeptideDataReader
from src.lcseq.io.writers import PeptideDataWriter

# Load column mapping from config
mapping = ColumnMapping.from_config(Path('tests/data/raw_data_column_mapping.yaml'))

# Create reader
reader = PeptideDataReader(mapping)

# Read and validate data
data = reader.read_csv(Path('tests/data/raw_data_subset.csv'))

# Write to YAML
writer = PeptideDataWriter()
writer.write_yaml(data, Path('tests/data/prepared_data.yaml'))
