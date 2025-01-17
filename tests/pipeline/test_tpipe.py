# tests/pipeline/test_tpipe.py
"""Tests for TPipe functionality - a basic pass-through pipeline for testing."""
from src.lcseq.pipelines.tpipe import TPipe

def test_tpipe_initialization():
    """Test TPipe initialization."""
    pipeline = TPipe("tests/data/prepared_data.yaml")
    assert pipeline is not None
    assert len(pipeline.components) == 6  # Verify we have all test components

def test_tpipe_single_processing(pipeline_single_input):
    """Test TPipe processing with single peptide input."""
    pipeline = TPipe("tests/data/prepared_data.yaml")
    result = pipeline.run(pipeline_single_input)
    assert result == pipeline_single_input

def test_tpipe_set_processing(pipeline_set_input):
    """Test TPipe processing with peptide set input."""
    pipeline = TPipe("tests/data/prepared_data.yaml")
    result = pipeline.run(pipeline_set_input)
    assert result == pipeline_set_input

def test_tpipe_hierarchy_processing(pipeline_hierarchy_input):
    """Test TPipe processing with peptide hierarchy input."""
    pipeline = TPipe("tests/data/prepared_data.yaml")
    result = pipeline.run(pipeline_hierarchy_input)
    assert result == pipeline_hierarchy_input
