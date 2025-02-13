"""Tests for the SynthesisStatus enum."""

# Local application imports
from src.lcseq.core.synthesis_status import SynthesisStatus


def test_synthesis_status_values() -> None:
    """Test that SynthesisStatus has the expected values."""
    assert SynthesisStatus.UNKNOWN.value == "UNKNOWN"
    assert SynthesisStatus.SUCCESS.value == "SUCCESS"
    assert SynthesisStatus.FAILURE.value == "FAILURE"


def test_synthesis_status_comparison() -> None:
    """Test comparison of SynthesisStatus values."""
    # Test equality
    assert SynthesisStatus.SUCCESS == SynthesisStatus.SUCCESS
    assert SynthesisStatus.FAILURE == SynthesisStatus.FAILURE
    assert SynthesisStatus.UNKNOWN == SynthesisStatus.UNKNOWN

    # Test inequality
    assert SynthesisStatus.SUCCESS != SynthesisStatus.FAILURE
    assert SynthesisStatus.SUCCESS != SynthesisStatus.UNKNOWN
    assert SynthesisStatus.FAILURE != SynthesisStatus.UNKNOWN


def test_synthesis_status_string_representation() -> None:
    """Test string representation of SynthesisStatus values."""
    assert str(SynthesisStatus.UNKNOWN) == "UNKNOWN"
    assert str(SynthesisStatus.SUCCESS) == "SUCCESS"
    assert str(SynthesisStatus.FAILURE) == "FAILURE"


def test_synthesis_status_from_string() -> None:
    """Test creating SynthesisStatus from strings."""
    assert SynthesisStatus("UNKNOWN") == SynthesisStatus.UNKNOWN
    assert SynthesisStatus("SUCCESS") == SynthesisStatus.SUCCESS
    assert SynthesisStatus("FAILURE") == SynthesisStatus.FAILURE
