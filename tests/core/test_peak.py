"""Tests for the Peak class."""

# Standard library imports
from typing import Dict, List

import pytest

# Local application imports
from src.lcseq.core.peak import Peak


@pytest.fixture
def test_peak() -> Peak:
    """Create a test peak.

    Returns:
        A test peak with known properties.
    """
    return Peak(
        start_time=10.0,
        end_time=15.0,
        apex_time=12.5,
        start_intensity=100.0,
        end_intensity=150.0,
        apex_intensity=500.0,
    )


def test_peak_initialization(test_peak: Peak) -> None:
    """Test peak initialization.

    Args:
        test_peak: Test peak fixture.
    """
    assert test_peak.start_time == 10.0
    assert test_peak.end_time == 15.0
    assert test_peak.apex_time == 12.5
    assert test_peak.start_intensity == 100.0
    assert test_peak.end_intensity == 150.0
    assert test_peak.apex_intensity == 500.0
    assert isinstance(test_peak.properties, dict)


def test_peak_properties(test_peak: Peak) -> None:
    """Test peak property management.

    Args:
        test_peak: Test peak fixture.
    """
    # Add some properties
    test_peak.properties["width"] = 5.0
    test_peak.properties["area"] = 2500.0
    test_peak.properties["symmetry"] = 0.8

    assert test_peak.properties["width"] == 5.0
    assert test_peak.properties["area"] == 2500.0
    assert test_peak.properties["symmetry"] == 0.8


def test_peak_validation() -> None:
    """Test peak validation during initialization."""
    # Test valid peak
    valid_peak = Peak(
        start_time=10.0,
        end_time=15.0,
        apex_time=12.5,
        start_intensity=100.0,
        end_intensity=150.0,
        apex_intensity=500.0,
    )
    assert valid_peak is not None

    # Test invalid time order
    with pytest.raises(ValueError):
        Peak(
            start_time=15.0,  # Start time after end time
            end_time=10.0,
            apex_time=12.5,
            start_intensity=100.0,
            end_intensity=150.0,
            apex_intensity=500.0,
        )

    # Test apex time outside bounds
    with pytest.raises(ValueError):
        Peak(
            start_time=10.0,
            end_time=15.0,
            apex_time=16.0,  # Apex time after end time
            start_intensity=100.0,
            end_intensity=150.0,
            apex_intensity=500.0,
        )

    # Test negative intensities
    with pytest.raises(ValueError):
        Peak(
            start_time=10.0,
            end_time=15.0,
            apex_time=12.5,
            start_intensity=-100.0,  # Negative intensity
            end_intensity=150.0,
            apex_intensity=500.0,
        )
