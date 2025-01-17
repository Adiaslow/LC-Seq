# tests/core/conftest.py
import pytest
import numpy as np
from src.lcseq.core.building_block import BuildingBlock, BuildingBlockRegistry
from src.lcseq.core.peptide import Peptide, PeptideEncoding
from src.lcseq.core.chromatogram import Chromatogram
from src.lcseq.core.hierarchy import PeptideHierarchy

@pytest.fixture
def sample_building_block():
    """Create a sample building block for testing."""
    return BuildingBlock(
        identifier="Ala",
        properties={
            "name": "Alanine",
            "smiles": "CC(N)C(=O)O",
            "stereochem": "L",
            "molecular_weight": 89.09,
        }
    )

@pytest.fixture
def sample_building_blocks():
    """Create a set of sample building blocks for testing."""
    blocks = {
        "Ala": BuildingBlock(
            identifier="Ala",
            properties={
                "name": "Alanine",
                "smiles": "CC(N)C(=O)O",
                "stereochem": "L",
                "molecular_weight": 89.09,
            }
        ),
        "Leu": BuildingBlock(
            identifier="Leu",
            properties={
                "name": "Leucine",
                "smiles": "CC(C)CC(N)C(=O)O",
                "stereochem": "L",
                "molecular_weight": 131.17,
            }
        ),
        "Phe": BuildingBlock(
            identifier="Phe",
            properties={
                "name": "Phenylalanine",
                "smiles": "NC(Cc1ccccc1)C(=O)O",
                "stereochem": "L",
                "molecular_weight": 165.19,
            }
        )
    }
    return blocks

@pytest.fixture
def sample_chromatogram():
    """Create a sample chromatogram for testing."""
    times = np.linspace(0, 10, 100)
    intensities = np.exp(-(times - 5)**2)  # Gaussian peak
    return Chromatogram(times=times, intensities=intensities)

@pytest.fixture
def sample_peptide(sample_building_blocks, sample_chromatogram):
    """Create a sample peptide for testing."""
    sequence = [
        sample_building_blocks["Ala"],
        sample_building_blocks["Leu"],
        sample_building_blocks["Phe"]
    ]
    peptide = Peptide(
        sequence=sequence,
        properties={"identifier": "ALA-LEU-PHE"}
    )
    encoding = PeptideEncoding(
        blocks=sequence,
        chromatogram=sample_chromatogram,
        properties={"retention_time": 5.0}
    )
    peptide.add_encoding(encoding)
    return peptide
