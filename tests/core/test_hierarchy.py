# tests/core/test_hierarchy.py
"""Tests for PeptideHierarchy functionality."""
"""
import pytest
from src.lcseq.core.hierarchy import PeptideHierarchy
from src.lcseq.core.peptide import Peptide

def test_hierarchy_creation(sample_peptide):
    ""Test creation and basic properties of a PeptideHierarchy.""
    hierarchy = PeptideHierarchy(root=sample_peptide)
    assert hierarchy.root == sample_peptide
    assert len(hierarchy.children) == 0

def test_hierarchy_operations(sample_peptide, sample_building_blocks):
    ""Test operations on PeptideHierarchy.""
    hierarchy = PeptideHierarchy(root=sample_peptide)

    # Create child peptide
    child_sequence = [
        sample_building_blocks["Ala"],
        sample_building_blocks["Leu"]
    ]
    child_peptide = Peptide(
        sequence=child_sequence,
        properties={"identifier": "ALA-LEU"}
    )

    # Add child
    hierarchy.add_child(child_peptide) # type: ignore
    assert child_peptide in hierarchy.children
    assert len(hierarchy.children) == 1

    # Remove child
    hierarchy.remove_child(child_peptide)
    assert child_peptide not in hierarchy.children
    assert len(hierarchy.children) == 0

def test_invalid_hierarchy(sample_peptide):
    ""Test creation of invalid PeptideHierarchy.""
    # Test None root
    with pytest.raises(ValueError):
        PeptideHierarchy(root=None) # type: ignore

    # Test adding invalid child
    hierarchy = PeptideHierarchy(root=sample_peptide)
    with pytest.raises(ValueError):
        hierarchy.add_child(None) # type: ignore

    # Test adding root as child
    with pytest.raises(ValueError):
        hierarchy.add_child(sample_peptide)
"""
