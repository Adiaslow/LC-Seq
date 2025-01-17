# tests/core/test_peptide.py
"""Tests for Peptide functionality."""
import pytest
from src.lcseq.core.peptide import Peptide, PeptideEncoding
from src.lcseq.core.building_block import BuildingBlock

def test_peptide_creation(sample_peptide):
    """Test creation and basic properties of a Peptide."""
    assert len(sample_peptide.sequence) == 3
    assert sample_peptide.properties["identifier"] == "ALA-LEU-PHE"
    assert len(sample_peptide.encodings) == 1

def test_peptide_encoding(sample_peptide, sample_chromatogram):
    """Test peptide encoding functionality."""
    encoding = sample_peptide.encodings[0]
    assert encoding.blocks == sample_peptide.sequence
    assert encoding.chromatogram == sample_chromatogram
    assert "retention_time" in encoding.properties

    # Test invalid encoding
    with pytest.raises(ValueError):
        PeptideEncoding(blocks=["invalid"]) # type: ignore

def test_peptide_equality(sample_peptide, sample_building_blocks, sample_chromatogram):
    """Test equality comparison of Peptides."""
    sequence = [
        sample_building_blocks["Ala"],
        sample_building_blocks["Leu"],
        sample_building_blocks["Phe"]
    ]
    peptide2 = Peptide(
        sequence=sequence,
        properties={"identifier": "ALA-LEU-PHE"}
    )
    encoding = PeptideEncoding(
        blocks=sequence,
        chromatogram=sample_chromatogram,
        properties={"retention_time": 5.0}
    )
    peptide2.add_encoding(encoding)
    assert sample_peptide == peptide2
    assert hash(sample_peptide) == hash(peptide2)

def test_invalid_peptide(sample_building_blocks):
    """Test creation of invalid Peptides."""
    # Test empty sequence
    with pytest.raises(ValueError):
        Peptide(sequence=[], properties={})

    # Test None sequence
    with pytest.raises(ValueError):
        Peptide(sequence=None, properties={})  # type: ignore

    # Test invalid building block in sequence
    with pytest.raises(ValueError):
        Peptide(sequence=[sample_building_blocks["Ala"], "invalid"], properties={}) # type: ignore

    # Test invalid encoding addition
    valid_peptide = Peptide(sequence=[sample_building_blocks["Ala"]], properties={})
    with pytest.raises(ValueError):
        valid_peptide.add_encoding("invalid")  # type: ignore

def test_peptide_operations(sample_peptide):
    """Test various peptide operations."""
    # Test sequence manipulation
    assert len(sample_peptide.sequence) == 3
    assert all(block.identifier in ["Ala", "Leu", "Phe"]
              for block in sample_peptide.sequence)

    # Test property access and modification
    sample_peptide.properties["new_property"] = "test"
    assert "new_property" in sample_peptide.properties
    assert sample_peptide.properties["new_property"] == "test"

    # Test encoding manipulation
    original_encoding = sample_peptide.encodings[0]
    assert original_encoding in sample_peptide.encodings

    # Test encoding removal
    sample_peptide.remove_encoding(original_encoding)
    assert original_encoding not in sample_peptide.encodings
