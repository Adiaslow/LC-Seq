# tests/core/test_chromatogram.py
"""Tests for Chromatogram functionality."""
import numpy as np
import pytest
from src.lcseq.core.chromatogram import Chromatogram

def test_chromatogram_creation(sample_chromatogram):
    """Test creation and basic properties of a Chromatogram."""
    assert isinstance(sample_chromatogram.times, np.ndarray)
    assert isinstance(sample_chromatogram.intensities, np.ndarray)
    assert len(sample_chromatogram.times) == len(sample_chromatogram.intensities)
    assert sample_chromatogram.times[0] == 0
    assert sample_chromatogram.times[-1] == 10

def test_chromatogram_slice():
    """Test chromatogram slicing functionality."""
    times = np.array([0, 1, 2, 3, 4, 5])
    intensities = np.array([0, 1, 2, 1, 0, 0])
    chrom = Chromatogram(times=times, intensities=intensities)

    # Test valid slice
    slice1 = chrom.get_slice(1, 3)
    assert len(slice1.times) == 3
    assert np.array_equal(slice1.times, [1, 2, 3])
    assert np.array_equal(slice1.intensities, [1, 2, 1])

    # Test slice with boundaries outside range
    slice2 = chrom.get_slice(-1, 6)
    assert len(slice2.times) == len(times)
    assert np.array_equal(slice2.intensities, intensities)

def test_invalid_chromatogram():
    """Test creation of invalid Chromatograms."""
    # Test mismatched lengths
    with pytest.raises(ValueError):
        Chromatogram(
            times=np.array([1, 2, 3]),
            intensities=np.array([1, 2])
        )

    # Test non-numeric data
    with pytest.raises(ValueError):
        Chromatogram(
            times=np.array(['a', 'b']),
            intensities=np.array([1, 2])
        )

    # Test negative times
    with pytest.raises(ValueError):
        Chromatogram(
            times=np.array([-1, 0, 1]),
            intensities=np.array([1, 2, 3])
        )
