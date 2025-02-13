# tests/lcseq/core/conftest.py
"""
This module contains the fixtures for the core module.
"""

# Standard library imports
import numpy as np
from typing import Any, Dict

# Third party imports
import pytest

# Local application imports
from src.lcseq.core.chromatogram import Chromatogram
from src.lcseq.core.building_block import BuildingBlock


@pytest.fixture
def sample_chromatogram() -> Chromatogram:
    """Fixture providing a sample chromatogram for testing."""
    times: np.ndarray = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    intensities: np.ndarray = np.array([100.0, 200.0, 300.0, 200.0, 100.0])
    return Chromatogram(times=times, intensities=intensities)


@pytest.fixture
def sample_building_block() -> BuildingBlock:
    """Fixture providing a sample building block for testing."""
    identifier: str = "test_block"
    properties: Dict[str, Any] = {"test_key": "test_value"}
    return BuildingBlock(identifier=identifier, properties=properties)
