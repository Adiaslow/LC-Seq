from pathlib import Path
from src.lcseq.io.readers import ColumnMapping, PeptideDataReader
from src.lcseq.io.writers import PeptideDataWriter
from src.lcseq.utils.validators import DataValidator

# Load column mapping from config
mapping = ColumnMapping.from_config(Path('tests/data/raw_data_column_mapping.yaml'))

# Create reader
reader = PeptideDataReader(mapping)

# Read and validate data
data = reader.read_csv(Path('tests/data/raw_data_subset.csv'))

# Write to YAML
writer = PeptideDataWriter()
writer.write_yaml(data, Path('tests/data/prepared_data.yaml'))
