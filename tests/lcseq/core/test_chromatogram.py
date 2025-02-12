# tests/lcseq/core/test_chromatogram.py

import numpy as np
import pytest
from src.lcseq.core.chromatogram import Chromatogram


def test_chromatogram_initialization():
    """Test basic initialization of Chromatogram."""
    times = np.array([1.0, 2.0, 3.0])
    intensities = np.array([100.0, 200.0, 300.0])
    chrom = Chromatogram(times=times, intensities=intensities)

    assert np.array_equal(chrom.times, times)
    assert np.array_equal(chrom.intensities, intensities)
    assert isinstance(chrom.properties, dict)
    assert len(chrom.properties) == 0


def test_chromatogram_with_properties():
    """Test Chromatogram initialization with properties."""
    times = np.array([1.0, 2.0, 3.0])
    intensities = np.array([100.0, 200.0, 300.0])
    properties = {"baseline": np.array([10.0, 20.0, 30.0])}

    chrom = Chromatogram(times=times, intensities=intensities, properties=properties)

    assert np.array_equal(chrom.properties["baseline"], properties["baseline"])


def test_chromatogram_validation():
    """Test input validation for Chromatogram."""
    with pytest.raises(ValueError):
        # Different lengths for times and intensities
        Chromatogram(
            times=np.array([1.0, 2.0]), intensities=np.array([100.0, 200.0, 300.0])
        )

    with pytest.raises(ValueError):
        # Empty arrays
        Chromatogram(times=np.array([]), intensities=np.array([]))

    with pytest.raises(ValueError):
        # Non-numeric data
        Chromatogram(times=np.array(["a", "b"]), intensities=np.array([100.0, 200.0]))


def test_chromatogram_properties_manipulation():
    """Test adding and modifying properties."""
    chrom = Chromatogram(
        times=np.array([1.0, 2.0, 3.0]), intensities=np.array([100.0, 200.0, 300.0])
    )

    # Add new property
    baseline = np.array([10.0, 20.0, 30.0])
    chrom.properties["baseline"] = baseline
    assert np.array_equal(chrom.properties["baseline"], baseline)

    # Modify existing property
    new_baseline = np.array([15.0, 25.0, 35.0])
    chrom.properties["baseline"] = new_baseline
    assert np.array_equal(chrom.properties["baseline"], new_baseline)
