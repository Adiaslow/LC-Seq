"""Tests for the CSVInputStage class."""
import pytest
import pandas as pd
from pathlib import Path
import json
from src.chromatographicpeakpicking.pipeline.stages.default_csv_input_stage import (
    DefaultCSVInputStage
)
from src.chromatographicpeakpicking.io.implementations.csv_reader import CSVReaderConfig
from src.chromatographicpeakpicking.core.types.config import (
    ConfigMetadata,
    ConfigValidation
)
from src.chromatographicpeakpicking.core.types.validation import ValidationLevel

@pytest.fixture
def config_metadata():
    """Create a ConfigMetadata instance for testing."""
    return ConfigMetadata(
        name="csv_reader_config",
        version="1.0",
        description="Configuration for CSV reader",
        defaults={
            "delimiter": ",",
            "has_headers": True,
            "encoding": "utf-8",
            "skip_rows": 0
        },
        schema={
            "type": "object",
            "properties": {
                "delimiter": {"type": "string"},
                "has_headers": {"type": "boolean"},
                "encoding": {"type": "string"},
                "expected_columns": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "dtype_map": {
                    "type": "object",
                    "additionalProperties": {"type": "string"}
                },
                "skip_rows": {"type": "integer", "minimum": 0}
            }
        },
        validation_level=ConfigValidation.STRICT
    )

@pytest.fixture
def valid_config(config_metadata):
    """Create a valid CSVReaderConfig."""
    return CSVReaderConfig(
        metadata=config_metadata,
        delimiter=',',
        has_headers=True,
        encoding='utf-8',
        expected_columns=['SMILES', 'BB1 Name', 'BB2 Name', 'BB3 Name',
                         'Scaffold', 'Cyclized RT (min)', 'AlogP', 'LogK',
                         'Success', 'Times', 'Counts', 'Deduplicated Counts'],
        dtype_map={},
        skip_rows=0
    )

@pytest.fixture
def sample_csv_path(tmp_path):
    """Create a sample CSV file for testing."""
    csv_content = """SMILES,BB1 Name,BB2 Name,BB3 Name,Scaffold,Cyclized RT (min),AlogP,LogK,Success,Times,Counts,Deduplicated Counts
null_product,AgxNull,AgxNull,AgxNull,xxx,0,,0,False,"[10.25, 10.75]","[154.0, 178.0]","[117.0, 133.0]"
"""
    csv_file = tmp_path / "test_compounds.csv"
    csv_file.write_text(csv_content)
    return str(csv_file)

@pytest.fixture
def csv_input_stage(valid_config):
    """Create a configured CSVInputStage instance."""
    return DefaultCSVInputStage(valid_config)

def test_initialization(valid_config):
    """Test successful initialization with valid config."""
    stage = DefaultCSVInputStage(valid_config)
    assert stage.reader is not None
    assert isinstance(stage.reader._config, CSVReaderConfig)
    assert stage.reader._config.metadata.name == "csv_reader_config"

def test_initialization_invalid_config(config_metadata):
    """Test initialization with invalid config."""
    invalid_config = CSVReaderConfig(
        metadata=config_metadata,
        delimiter=',,',  # Invalid: must be single character
        has_headers=True,
        encoding='utf-8',
        expected_columns=None,
        dtype_map={},
        skip_rows=0
    )
    with pytest.raises(ValueError) as exc_info:
        DefaultCSVInputStage(invalid_config)
    assert "Invalid CSV reader configuration" in str(exc_info.value)

def test_parse_input_success(csv_input_stage, sample_csv_path):
    """Test successful parsing of input file."""
    result = csv_input_stage._parse_input(sample_csv_path)
    assert isinstance(result, pd.DataFrame)
    assert not result.empty
    assert 'SMILES' in result.columns
    assert result['SMILES'].iloc[0] == 'null_product'

def test_parse_input_file_not_found(csv_input_stage):
    """Test handling of non-existent file."""
    with pytest.raises(FileNotFoundError) as exc_info:
        csv_input_stage._parse_input("nonexistent.csv")
    assert "Input file not found" in str(exc_info.value)

def test_parse_input_invalid_csv(csv_input_stage, tmp_path):
    """Test handling of invalid CSV file."""
    invalid_file = tmp_path / "invalid.txt"
    invalid_file.write_text("not,a,valid\ncsv,file")
    with pytest.raises(ValueError) as exc_info:
        csv_input_stage._parse_input(str(invalid_file))
    assert "not a valid CSV" in str(exc_info.value)

def test_extract_numeric_metrics(csv_input_stage):
    """Test extraction of numeric metrics from metadata."""
    test_metadata = {
        'num_rows': 100,
        'num_cols': 12,
        'memory_usage': 1024.5,
        'encoding': 'utf-8',
        'has_headers': True
    }

    metrics = csv_input_stage._extract_numeric_metrics(test_metadata)
    assert len(metrics) == 3
    assert metrics['num_rows'] == 100.0
    assert metrics['num_cols'] == 12.0
    assert metrics['memory_usage'] == 1024.5
    assert 'encoding' not in metrics
    assert 'has_headers' not in metrics

def test_process_success(csv_input_stage, sample_csv_path):
    """Test successful processing of CSV file."""
    result = csv_input_stage.process(sample_csv_path)

    assert result.success
    assert isinstance(result.data, pd.DataFrame)
    assert not result.data.empty
    assert isinstance(result.metrics, dict)
    assert 'num_rows' in result.metrics
    assert 'num_cols' in result.metrics
    assert result.error_message is None

def test_process_failure_nonexistent_file(csv_input_stage):
    """Test processing of non-existent file."""
    result = csv_input_stage.process("nonexistent.csv")

    assert not result.success
    assert result.data is None
    assert result.metrics == {}
    assert "Input file not found" in result.error_message

def test_config_validation_levels(config_metadata):
    """Test different configuration validation levels."""
    # Test STRICT validation
    strict_config = CSVReaderConfig(
        metadata=config_metadata,
        delimiter=',',
        has_headers=True,
        encoding='utf-8',
        expected_columns=['SMILES'],
        dtype_map={},
        skip_rows=0
    )
    assert strict_config.metadata.validation_level == ConfigValidation.STRICT

    # Test with modified validation level
    permissive_metadata = ConfigMetadata(
        name="csv_reader_config",
        version="1.0",
        description="Configuration for CSV reader",
        defaults=config_metadata.defaults,
        schema=config_metadata.schema,
        validation_level=ConfigValidation.PERMISSIVE
    )
    permissive_config = CSVReaderConfig(
        metadata=permissive_metadata,
        delimiter=',',
        has_headers=True,
        encoding='utf-8'
    )
    assert permissive_config.metadata.validation_level == ConfigValidation.PERMISSIVE

def test_actual_data_format(csv_input_stage):
    """Test processing with actual test data format."""
    # Create a CSV with the actual data format
    csv_content = '''SMILES,BB1 Name,BB2 Name,BB3 Name,Scaffold,Cyclized RT (min),AlogP,LogK,Success,Times,Counts,Deduplicated Counts
null_product,AgxNull,AgxNull,AgxNull,xxx,0,,0,False,"[10.25, 10.75]","[154.0, 178.0]","[117.0, 133.0]"'''

    test_file = Path("test_actual.csv")
    test_file.write_text(csv_content)

    try:
        result = csv_input_stage.process(str(test_file))

        assert result.success
        assert isinstance(result.data, pd.DataFrame)

        # Verify specific columns and data types
        df = result.data
        assert df['SMILES'].iloc[0] == 'null_product'
        assert df['Success'].iloc[0] == False
        assert df['LogK'].iloc[0] == 0

        # Verify list columns are strings containing valid JSON
        times = json.loads(df['Times'].iloc[0])
        counts = json.loads(df['Counts'].iloc[0])
        dedup_counts = json.loads(df['Deduplicated Counts'].iloc[0])

        assert isinstance(times, list)
        assert isinstance(counts, list)
        assert isinstance(dedup_counts, list)
        assert times == [10.25, 10.75]
        assert counts == [154.0, 178.0]
        assert dedup_counts == [117.0, 133.0]

    finally:
        test_file.unlink()  # Clean up the test file
