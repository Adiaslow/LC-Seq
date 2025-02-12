# tests/pipeline/test_gpp_pipe.py
"""Tests for GPPPipeline functionality."""
import logging
import pytest
from src.lcseq.pipelines import GPP

def test_gpp_pipeline_initialization():
    """Test GPPPipeline initialization."""
    pipeline = GPP("tests/data/prepared_data.yaml")
    assert pipeline is not None
    assert hasattr(pipeline, "run"), "Pipeline should have a run method"

def test_gpp_single_processing(pipeline_single_input, caplog):
    """Test GPPPipeline processing with single peptide input."""
    pipeline = GPP("tests/data/prepared_data.yaml", plot_chromatograms=True)
    with caplog.at_level(logging.INFO):
        result = pipeline.run(pipeline_single_input)

    assert result is not None
    assert hasattr(result, "peptide"), "Result should have a peptide attribute"
    assert result.peptide.encodings[0].chromatogram is not None # type: ignore

def test_gpp_set_processing(pipeline_set_input):
    """Test GPPPipeline processing with peptide set input."""
    pipeline = GPP("tests/data/prepared_data.yaml", plot_chromatograms=False)
    result = pipeline.run(pipeline_set_input)

    assert result is not None
    assert len(result.peptides) == len(pipeline_set_input.peptides) # type: ignore
