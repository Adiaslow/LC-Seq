# tests/test_baseline_correctors/test_swm.py
import pytest
from src.chromatographicpeakpicking.implementations.correctors.swm import SWMCorrector, SWMConfig
from src.chromatographicpeakpicking.core.prototypes.chromatogram import Chromatogram
import numpy as np

def test_swm_initialization():
    corrector = SWMCorrector()
    assert corrector is not None

def test_swm_correction():
    time = np.array([0, 1, 2, 3, 4])
    intensity = np.array([1, 2, 3, 4, 5])
    chromatogram = Chromatogram(time=time, intensity=intensity)

    corrector = SWMCorrector()
    result = corrector.correct(chromatogram)
    assert result is not None
    assert len(result.intensity) == len(intensity)
