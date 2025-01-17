# tests/core/test_building_block.py
"""Tests for BuildingBlock functionality."""
import pytest
from src.lcseq.core.building_block import BuildingBlock, BuildingBlockRegistry

def test_building_block_creation(sample_building_block):
    """Test creation and basic properties of a BuildingBlock."""
    assert sample_building_block.identifier == "Ala"
    assert sample_building_block.properties["name"] == "Alanine"
    assert sample_building_block.properties["smiles"] == "CC(N)C(=O)O"
    assert sample_building_block.properties["stereochem"] == "L"
    assert sample_building_block.properties["molecular_weight"] == pytest.approx(89.09)

def test_building_block_equality(sample_building_block):
    """Test equality comparison of BuildingBlocks."""
    block2 = BuildingBlock(
        identifier="Ala",
        properties={
            "name": "Alanine",
            "smiles": "CC(N)C(=O)O",
            "stereochem": "L",
            "molecular_weight": 89.09,
        }
    )
    assert sample_building_block == block2
    assert hash(sample_building_block) == hash(block2)

def test_building_block_registry():
    """Test BuildingBlockRegistry functionality."""
    BuildingBlockRegistry.clear()

    block = BuildingBlock(
        identifier="Ala",
        properties={"name": "Alanine", "smiles": "CC(N)C(=O)O"}
    )

    # Test registration
    BuildingBlockRegistry.register(block)
    assert "Ala" in BuildingBlockRegistry._blocks

    # Test retrieval
    retrieved = BuildingBlockRegistry.get("Ala")
    assert retrieved == block
    assert retrieved is not block  # Should be a deep copy

    # Test missing block
    with pytest.raises(KeyError):
        BuildingBlockRegistry.get("NonExistentBlock")

    # Test clearing registry
    BuildingBlockRegistry.clear()
    assert len(BuildingBlockRegistry._blocks) == 0

def test_invalid_building_block():
    """Test creation of invalid BuildingBlocks."""
    # Test empty identifier
    with pytest.raises(ValueError):
        BuildingBlock("", {})

    # Test None identifier
    with pytest.raises(ValueError):
        BuildingBlock(None, {})  # type: ignore

    # Test None properties
    with pytest.raises(ValueError):
        BuildingBlock("Test", None)  # type: ignore

    # Test empty properties dictionary
    with pytest.raises(ValueError):
        BuildingBlock("Test", {})
