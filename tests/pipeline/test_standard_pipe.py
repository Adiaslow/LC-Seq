# tests/pipeline/test_standard_pipe.py
"""Tests for StandardPipe functionality."""
import logging
import pytest
from src.lcseq.pipelines.standard import StandardPipe

def test_standard_pipe_initialization(test_data):
    """Test StandardPipe initialization."""
    pipeline = StandardPipe("tests/data/prepared_data.yaml")
    assert pipeline is not None
    assert hasattr(pipeline, "run"), "Pipeline should have a run method"

def test_standard_single_processing(pipeline_single_input, caplog):
    """Test StandardPipe processing with single peptide input."""
    pipeline = StandardPipe("tests/data/prepared_data.yaml", plot_chromatograms=True)
    with caplog.at_level(logging.INFO):
        result = pipeline.run(pipeline_single_input)

    assert result is not None
    assert hasattr(result, "peptide"), "Result should have a peptide attribute"
    assert result.peptide.encodings[0].chromatogram is not None # type: ignore

def test_standard_set_processing(pipeline_set_input):
    """Test StandardPipe processing with peptide set input."""
    pipeline = StandardPipe("tests/data/prepared_data.yaml", plot_chromatograms=False)
    result = pipeline.run(pipeline_set_input)

    assert result is not None
    assert len(result.peptides) == len(pipeline_set_input.peptides) # type: ignore
