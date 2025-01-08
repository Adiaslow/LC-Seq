# tests/test_core/test_hierarchy.py
import pytest
import logging
from pathlib import Path
from typing import List
from src.chromatographicpeakpicking.core.prototypes.hierarchy import Hierarchy
from src.chromatographicpeakpicking.core.prototypes.peptide import Peptide
from src.chromatographicpeakpicking.core.prototypes.building_block import BuildingBlock
from src.chromatographicpeakpicking.core.types.config import GlobalConfig

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@pytest.fixture
def test_compounds():
    """Define test compounds"""
    return [
        ["Leu", "Phe", "Val"],
        ["βHomoleu", "Nvl", "LA03"],
        ["Leu-LeuMe-Pro", "Leu-LA03-Pro", "LeuMe-DLeuMe-Pro"]
    ]

@pytest.fixture
def global_config():
    """Create global configuration with AgxNull as null building block"""
    logger.debug("Creating global config")
    return GlobalConfig(null_building_block=BuildingBlock("AgxNull"))

@pytest.fixture
def hierarchy(global_config):
    """Create empty hierarchy instance"""
    logger.debug("Creating hierarchy instance")
    return Hierarchy(global_config=global_config)

def create_building_block(name: str) -> BuildingBlock:
    """Helper function to create a BuildingBlock with minimal attributes"""
    return BuildingBlock(name=name)

def create_peptide_from_blocks(blocks: List[str]) -> Peptide:
    """Helper function to create a Peptide from a list of building block names"""
    logger.debug(f"Creating peptide from blocks: {blocks}")
    return Peptide(
        sequence=[create_building_block(name) for name in blocks],
        chromatograms=[],
        properties={},
        metadata={}
    )

def test_hierarchy_creation(hierarchy, test_compounds):
    """Test that hierarchy is correctly created with test compounds"""
    logger.debug("Starting hierarchy creation test")

    # Create peptides from test compounds
    peptides = []
    for compound in test_compounds:
        logger.debug(f"Processing compound: {compound}")
        peptide = create_peptide_from_blocks(compound)
        peptides.append(peptide)

    # Add peptides to hierarchy
    logger.debug("Adding peptides to hierarchy")
    hierarchy.add_peptides(peptides)

    # Verify structure
    level_3_peptides = list(hierarchy.get_peptides_by_level(3))
    assert len(level_3_peptides) == len(test_compounds)

def test_simple_hierarchy(hierarchy):
    """Test with a single, simple peptide"""
    logger.debug("Starting simple hierarchy test")

    # Create a single peptide
    peptide = create_peptide_from_blocks(["Leu", "Phe", "Val"])

    # Add to hierarchy
    logger.debug("Adding single peptide to hierarchy")
    hierarchy.add_peptide(peptide)

    # Basic verification
    assert len(list(hierarchy.get_peptides_by_level(3))) == 1

def test_peptide_equality():
    """Test that peptides with same sequence are considered equal"""
    peptide1 = create_peptide_from_blocks(["Leu", "Phe", "Val"])
    peptide2 = create_peptide_from_blocks(["Leu", "Phe", "Val"])
    peptide3 = create_peptide_from_blocks(["Leu", "Val", "Phe"])

    assert peptide1 == peptide2
    assert peptide1 != peptide3
    assert hash(peptide1) == hash(peptide2)
    assert hash(peptide1) != hash(peptide3)
