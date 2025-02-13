# tests/pipeline/test_standard_pipe.py
"""
Tests for GPPPipeline functionality.
"""

# Standard library imports
import logging
import pytest

# Local application imports
from src.lcseq.pipelines import GPPPipe
from src.lcseq.pipeline.input_types import SinglePeptideInput, PeptideSetInput


def test_gpp_pipeline_initialization() -> None:
    """Test GPPPipeline initialization."""
    pipeline: GPPPipe = GPPPipe("tests/data/prepared_data.yaml")
    assert pipeline is not None
    assert hasattr(pipeline, "run"), "Pipeline should have a run method"


def test_gpp_single_processing(
    pipeline_single_input: SinglePeptideInput, caplog: pytest.LogCaptureFixture
) -> None:
    """Test GPPPipeline processing with single peptide input."""
    pipeline: GPPPipe = GPPPipe(
        "tests/data/prepared_data.yaml", plot_chromatograms=True
    )
    with caplog.at_level(logging.INFO):
        result = pipeline.run(pipeline_single_input)

    assert result is not None
    assert hasattr(result, "peptide"), "Result should have a peptide attribute"
    assert result.peptide.encodings[0].chromatogram is not None  # type: ignore


def test_gpp_set_processing(
    pipeline_set_input: PeptideSetInput, caplog: pytest.LogCaptureFixture
) -> None:
    """Test GPPPipeline processing with peptide set input."""
    pipeline: GPPPipe = GPPPipe(
        "tests/data/prepared_data.yaml", plot_chromatograms=False
    )
    with caplog.at_level(logging.INFO):
        result = pipeline.run(pipeline_set_input)

    assert result is not None
    assert len(result.peptides) == len(pipeline_set_input.peptides)  # type: ignore
