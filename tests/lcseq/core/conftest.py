import pytest
import numpy as np
from src.lcseq.core.chromatogram import Chromatogram
from src.lcseq.core.building_block import BuildingBlock


@pytest.fixture
def sample_chromatogram():
    """Fixture providing a sample chromatogram for testing."""
    times = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    intensities = np.array([100.0, 200.0, 300.0, 200.0, 100.0])
    return Chromatogram(times=times, intensities=intensities)


@pytest.fixture
def sample_building_block():
    """Fixture providing a sample building block for testing."""
    identifier = "test_block"
    properties = {"test_key": "test_value"}
    return BuildingBlock(identifier=identifier, properties=properties)
